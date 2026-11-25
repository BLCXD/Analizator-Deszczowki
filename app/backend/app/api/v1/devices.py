from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session
from typing import List, Union
from datetime import timedelta
import secrets
import hmac
import hashlib
import os
from pathlib import Path
from app.db.session import get_db
from app.api.v1.auth import get_current_user
from app.services.device import (
    create_device,
    can_access_device,
    get_device_by_id,
    get_devices_by_user,
    update_device,
    delete_device,
    update_heartbeat,
    generate_device_code,
    exchange_code_for_secret,
    authenticate_device,
)
from app.schemas.device import DeviceCreate, DeviceUpdate, Device, DevicePair, DevicePairResult, DeviceAuth, DeviceAuthResult, DevicePairByCode, DeviceClaim
from app.models.user import User
from app.models.device import Device as DeviceModel
from app.core.config import DEVICE_SECRET_SALT
from app.core.security import create_access_token

router = APIRouter()


def _consume_device_claim_key() -> None:
    key_path = os.getenv("DEVICE_CLAIM_KEY_PATH", "")
    if key_path:
        Path(key_path).unlink(missing_ok=True)

@router.post("/", response_model=Device, status_code=status.HTTP_201_CREATED)
def register_device(
    device_in: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
\
\
       
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    existing_device = get_device_by_id(db, device_in.device_id)
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this ID already exists"
        )
    return create_device(db=db, device_in=device_in, user_id=current_user.id)

@router.get("/", response_model=List[Device])
def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Union[User, dict] = Depends(get_current_user)
):
\
\
       
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")

    return get_devices_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{device_id}", response_model=Device)
def get_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: Union[User, dict] = Depends(get_current_user)
):
\
\
       
    device = get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    if not can_access_device(device, current_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    return device


@router.get("/{device_id}/status", response_model=dict)
def get_device_status(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: Union[User, dict] = Depends(get_current_user),
):
    device = get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if not can_access_device(device, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return {"device_id": device.device_id, "status": device.status, "last_seen": device.last_seen}

@router.put("/{device_id}", response_model=Device)
def update_device_endpoint(
    device_id: str,
    device_in: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
\
\
       
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    device = get_device_by_id(db, device_id)
    if not device or device.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    return update_device(db=db, device_id=device.id, device_in=device_in)

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device_endpoint(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
\
\
       
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    device = get_device_by_id(db, device_id)
    if not device or device.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    delete_device(db=db, device_id=device.id)
    return None

@router.post("/{device_id}/heartbeat", response_model=Device)
def device_heartbeat(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: Union[User, dict] = Depends(get_current_user)
):
\
\
       
    device = get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    if not can_access_device(device, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update heartbeat for this device"
        )
    return update_heartbeat(db=db, device_id=device_id)


@router.get("/{device_id}/stream-ticket", response_model=dict)
def create_device_stream_ticket(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: Union[User, dict] = Depends(get_current_user),
):
                                                                              
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    device = get_device_by_id(db, device_id)
    if not device or device.user_id != current_user.id or not device.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    ticket = create_access_token(
        data={"sub": device_id, "type": "stream"},
        expires_delta=timedelta(seconds=60),
    )
    return {"ticket": ticket, "expires_in": 60}


@router.post("/{device_id}/unpair", response_model=dict)
def unpair_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    device = get_device_by_id(db, device_id)
    if not device or device.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    # Unpair disables device authentication while preserving account ownership.
    device.device_code = None
    device.device_secret_hash = None
    db.commit()
    db.refresh(device)
    return {"detail": "Device unpaired"}


@router.post("/{device_id}/code", response_model=dict)
def generate_pairing_code(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
\
\
\
       
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    device = get_device_by_id(db, device_id)
    if not device or device.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    code = generate_device_code(db, device_id, current_user.id)
    if not code:
        if device.device_secret_hash is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device already has a secret (already paired)"
            )
        if device.device_code is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pairing code already generated"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate pairing code"
        )

    return {"device_code": code}


@router.post("/pair", response_model=DevicePairResult)
def pair_device_endpoint(
    pair_data: DevicePair,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    result = exchange_code_for_secret(db, pair_data.device_id, pair_data.device_code, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid device ID, code, device not owned by user, or already has secret"
        )

    device, secret = result
    return DevicePairResult(device_secret=secret)


@router.post("/claim", response_model=DevicePairResult, status_code=status.HTTP_201_CREATED)
def claim_device_endpoint(
    payload: DeviceClaim,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_device_claim_proof: str = Header(default=""),
):
    """Claim an unowned Pi using a one-time out-of-band proof verified by its local agent."""
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    claim_key_path = os.getenv("DEVICE_CLAIM_KEY_PATH", "")
    try:
        if claim_key_path and os.path.exists(claim_key_path):
            with open(claim_key_path, encoding="utf-8") as key_file:
                claim_key = key_file.read().strip()
        else:
            claim_key = os.getenv("DEVICE_CLAIM_KEY", "")
    except OSError:
        claim_key = ""
    expected_proof = hmac.new(claim_key.encode(), payload.device_id.encode(), hashlib.sha256).hexdigest()
    if len(claim_key) < 32 or not secrets.compare_digest(payload.claim_proof, expected_proof) or not secrets.compare_digest(payload.claim_proof, x_device_claim_proof):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid device claim proof")
    secret = secrets.token_urlsafe(32)
    secret_hash = hmac.new(DEVICE_SECRET_SALT.encode(), secret.encode(), hashlib.sha256).hexdigest()
    changed = db.query(DeviceModel).filter(
        DeviceModel.device_id == payload.device_id,
        DeviceModel.user_id.is_(None),
        DeviceModel.device_secret_hash.is_(None),
    ).update({
        DeviceModel.user_id: current_user.id,
        DeviceModel.device_secret_hash: secret_hash,
    }, synchronize_session=False)
    if changed != 1:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Device is unavailable or already claimed")
    db.commit()
    _consume_device_claim_key()
    return DevicePairResult(device_secret=secret)


@router.post("/{device_id}/pair-by-code", response_model=DevicePairResult)
def pair_device_by_code(
    device_id: str,
    pair_data: DevicePairByCode,
    db: Session = Depends(get_db)
):
    """Pair an unpaired device using a one-time code (used by the device itself, no user session)."""
    device = get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    if device.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device is not assigned to any user. Pair it from the dashboard first."
        )
    if device.device_secret_hash is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device is already paired"
        )
    if device.device_code is None or device.device_code != pair_data.device_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pairing code"
        )

    secret = secrets.token_urlsafe(32)
    secret_hash = hmac.new(DEVICE_SECRET_SALT.encode(), secret.encode(), hashlib.sha256).hexdigest()
    device.device_secret_hash = secret_hash
    device.device_code = None
    db.commit()
    db.refresh(device)
    return DevicePairResult(device_secret=secret)
\
\
\
       
    if isinstance(current_user, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account required")
    result = exchange_code_for_secret(db, pair_data.device_id, pair_data.device_code, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid device ID, code, device not owned by user, or already has secret"
        )

    device, secret = result
    return DevicePairResult(device_secret=secret)


@router.post("/auth", response_model=DeviceAuthResult)
def authenticate_device_endpoint(
    auth_data: DeviceAuth,
    db: Session = Depends(get_db)
):
\
\
\
       
    device = authenticate_device(db, auth_data.device_id, auth_data.device_secret)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device credentials"
        )

    from datetime import datetime, timedelta
    from jose import jwt
    from app.core.config import SECRET_KEY, ALGORITHM

    access_token_expires = timedelta(minutes=30)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"sub": device.device_id, "exp": expire, "type": "device"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return DeviceAuthResult(access_token=encoded_jwt, token_type="bearer")
