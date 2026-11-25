from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import logging
import os
import smtplib
from app.services.notifications import notify_user
from urllib.parse import quote
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services import auth as auth_service
from app.services.device import authenticate_device, get_device_by_id
from app.core.security import create_access_token, verify_token, SECRET_KEY, ALGORITHM
from app.core.security import verify_password, get_password_hash
from app.core import config as config_module
from app.core.config import AUTH_RATE_LIMIT, AUTH_RATE_WINDOW_SECONDS, RATE_LIMIT_DB_PATH
from app.core.rate_limit import RateLimiter, request_bucket
from app.schemas.user import Token, UserCreate, PasswordResetRequest, PasswordResetConfirm, UserProfileUpdate
from app.schemas.device import DeviceAuth
from datetime import datetime, timedelta, timezone
from jose import jwt
from sqlalchemy.exc import IntegrityError

router = APIRouter()
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

_limiter = None


def _get_limiter():
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter(config_module.RATE_LIMIT_DB_PATH)
    return _limiter


def _check_rate_limit(request: Request, route: str):
    client_host = request.client.host if request.client else None
    bucket = request_bucket(SECRET_KEY, client_host, route)
    allowed, retry_after = _get_limiter().hit(
        bucket, AUTH_RATE_LIMIT, AUTH_RATE_WINDOW_SECONDS
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Zbyt wiele prób. Spróbuj ponownie później.",
            headers={"Retry-After": str(retry_after)},
        )


def rate_limit(route: str):
    def dependency(request: Request):
        _check_rate_limit(request, route)
    return dependency


def _send_password_reset_email(email: str, token: str) -> bool:
    base_url = (os.getenv('PUBLIC_APP_URL') or os.getenv('APP_URL') or 'http://localhost:5000').rstrip('/')
    reset_url = f'{base_url}/auth/password-reset/confirm#token={quote(token, safe="")}'
    subject = 'Reset hasła — Analizator Deszczówki'
    return notify_user(
        email,
        subject,
        ['Otrzymaliśmy prośbę o reset hasła.', 'Link jest ważny przez 30 minut i może być użyty tylko raz.',
         'Jeśli to nie Ty, zignoruj tę wiadomość.'],
        action=('Ustaw nowe hasło', reset_url),
    )


def _deliver_password_reset_email(email, token):
    try:
        _send_password_reset_email(email, token)
    except (OSError, smtplib.SMTPException, ValueError):
        logger.error('Password reset email delivery failed')

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    token_type = payload.get("type", "user")

    if token_type == "device":
        device_id: str = payload.get("sub")
        if device_id is None:
            raise credentials_exception
        device = get_device_by_id(db, device_id=device_id)
        if device is None or not device.is_active:
            raise credentials_exception
        return {
            "id": device.id,
            "device_id": device.device_id,
            "is_active": device.is_active,
            "type": "device"
        }
    elif token_type in (None, "user"):
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = auth_service.get_user_by_email(db, email=email)
        if user is None or not user.is_active:
            raise credentials_exception
        return user
    else:
        raise credentials_exception

@router.post("/register", response_model=Token, dependencies=[Depends(rate_limit("register"))])
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        user = auth_service.create_user(db, user_in)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists") from exc
    access_token = create_access_token(data={"sub": user.email, "type": "user"})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token, dependencies=[Depends(rate_limit("login"))])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "type": "user"})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/password-reset/request', status_code=status.HTTP_202_ACCEPTED,
             dependencies=[Depends(rate_limit("password-reset"))])
def request_password_reset(
    payload: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    reset = auth_service.create_password_reset(db, payload.email)
    if reset:
        background_tasks.add_task(_deliver_password_reset_email, *reset)
    return {'message': 'Jeśli konto istnieje, wysłaliśmy instrukcję resetu hasła.'}


@router.post('/password-reset/confirm', dependencies=[Depends(rate_limit("password-reset"))])
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    if not auth_service.consume_password_reset(db, payload.token, payload.new_password):
        raise HTTPException(status_code=400, detail='Link resetu jest nieprawidłowy lub wygasł')
    return {'message': 'Hasło zostało zmienione. Możesz się zalogować.'}

@router.get("/me", response_model=dict)
def read_current_user(current_user: dict = Depends(get_current_user)):
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
    }


@router.patch("/me", response_model=dict)
def update_current_user(payload: UserProfileUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    if payload.new_password:
        if not payload.current_password or not verify_password(payload.current_password, current_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nieprawidłowe obecne hasło")
        current_user.hashed_password = get_password_hash(payload.new_password)
    current_user.first_name = payload.first_name.strip()
    current_user.last_name = payload.last_name.strip()
    current_user.phone = payload.phone.strip()
    db.commit()
    db.refresh(current_user)
    return {"id": current_user.id, "email": current_user.email, "is_active": current_user.is_active,
            "first_name": current_user.first_name, "last_name": current_user.last_name, "phone": current_user.phone}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    user_id = current_user.id

    success = auth_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None


@router.post("/device/login", response_model=dict)
def device_login(auth_data: DeviceAuth, db: Session = Depends(get_db)):
\
\
\
\
       
    device = authenticate_device(db, auth_data.device_id, auth_data.device_secret)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    expire = datetime.now(timezone.utc) + access_token_expires
    to_encode = {"sub": device.device_id, "exp": expire, "type": "device"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": encoded_jwt, "token_type": "bearer"}
