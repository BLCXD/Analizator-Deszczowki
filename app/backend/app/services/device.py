from sqlalchemy.orm import Session
from app.models.device import Device
from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceUpdate
from typing import List, Optional, Tuple
import secrets
import hashlib
import hmac
from app.core.config import DEVICE_SECRET_SALT

def get_device_by_id(db: Session, device_id: str) -> Optional[Device]:
    return db.query(Device).filter(Device.device_id == device_id).first()


def can_access_device(device: Device, current_user: User | dict) -> bool:
    if isinstance(current_user, dict):
        return device.id == current_user.get("id")
    return device.user_id == current_user.id


def get_devices_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Device]:
    return db.query(Device).filter(Device.user_id == user_id).offset(skip).limit(limit).all()

def create_device(db: Session, device_in: DeviceCreate, user_id: int) -> Device:
    db_device = Device(
        device_id=device_in.device_id,
        name=device_in.name,
        user_id=user_id
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def update_device(db: Session, device_id: int, device_in: DeviceUpdate) -> Optional[Device]:
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if db_device:
        update_data = device_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_device, field, value)
        db.commit()
        db.refresh(db_device)
    return db_device

def delete_device(db: Session, device_id: int) -> Optional[Device]:
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if db_device:
        db.delete(db_device)
        db.commit()
    return db_device

def update_heartbeat(db: Session, device_id: str) -> Optional[Device]:
    db_device = db.query(Device).filter(Device.device_id == device_id).first()
    if db_device:
        from sqlalchemy.sql import func
        db_device.last_seen = func.now()
        db.commit()
        db.refresh(db_device)
    return db_device


def generate_device_code(db: Session, device_id: str, user_id: int) -> Optional[str]:
                                                                                                      
    db_device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.user_id == user_id
    ).first()
    if not db_device:
        return None
    if db_device.device_secret_hash is not None:
        return None
    if db_device.device_code is not None:
        return None

    code = secrets.token_urlsafe(4)[:6]
    while db.query(Device).filter(Device.device_code == code).first():
        code = secrets.token_urlsafe(4)[:6]

    db_device.device_code = code
    db.commit()
    db.refresh(db_device)
    return code


def exchange_code_for_secret(db: Session, device_id: str, device_code: str, user_id: int) -> Optional[Tuple[Device, str]]:
                                                               
    db_device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.user_id == user_id
    ).first()
    if not db_device:
        return None
    if db_device.device_code is None or db_device.device_code != device_code:
        return None

    secret = secrets.token_urlsafe(32)
    secret_hash = hmac.new(DEVICE_SECRET_SALT.encode(), secret.encode(), hashlib.sha256).hexdigest()
    db_device.device_secret_hash = secret_hash
    db_device.device_code = None
    db.commit()
    db.refresh(db_device)
    return db_device, secret


def authenticate_device(db: Session, device_id: str, device_secret: Optional[str] = None) -> Optional[Device]:
                                                                              
    db_device = db.query(Device).filter(Device.device_id == device_id).first()
    if not db_device or not db_device.is_active or not device_secret or not db_device.device_secret_hash:
        return None
    secret_hash = hmac.new(DEVICE_SECRET_SALT.encode(), device_secret.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(secret_hash, db_device.device_secret_hash):
        legacy_hash = hashlib.sha256(device_secret.encode()).hexdigest()
        if not hmac.compare_digest(legacy_hash, db_device.device_secret_hash):
            return None
        db_device.device_secret_hash = secret_hash
        db.commit()
    return db_device
