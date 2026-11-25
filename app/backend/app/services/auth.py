import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.device import Device
from app.models.password_reset import PasswordResetToken
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email.strip().lower()).first()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email.strip().lower(), hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_password_reset(db: Session, email: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    token = secrets.token_urlsafe(32)
    db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()
    db.add(PasswordResetToken(
        token_hash=hashlib.sha256(token.encode()).hexdigest(),
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    ))
    db.commit()
    return user.email, token


def consume_password_reset(db: Session, token: str, new_password: str) -> bool:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).with_for_update().first()
    now = datetime.now(timezone.utc)
    if not record or record.used_at is not None:
        return False
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        return False

    user = db.query(User).filter(User.id == record.user_id).with_for_update().first()
    if not user:
        return False
    user.hashed_password = get_password_hash(new_password)
    record.used_at = now
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.token_hash != token_hash,
    ).delete(synchronize_session=False)
    db.commit()
    return True


def delete_user(db: Session, user_id: int) -> bool:
\
\
\
       
    user = get_user(db, user_id=user_id)
    if user:
        db.query(Device).filter(Device.user_id == user_id).update(
            {Device.user_id: None}, synchronize_session=False
        )
        db.delete(user)
        db.commit()
        return True
    return False
