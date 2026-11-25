from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.device import Device as DBDevice
from app.models.measurement import Measurement as DBMeasurement
from app.models.user import User
from app.schemas.device import Device, DeviceUpdate
from app.schemas.measurement import Measurement
from app.services.device import delete_device, update_device

router = APIRouter()


def require_admin(current_user=Depends(get_current_user)):
    if not isinstance(current_user, User) or not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return current_user


@router.get("/users")
def list_users(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000),
               _: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id).offset(skip).limit(limit).all()
    return [{"id": u.id, "email": u.email, "first_name": u.first_name, "last_name": u.last_name,
             "phone": u.phone, "is_active": u.is_active, "is_admin": u.is_admin, "created_at": u.created_at}
            for u in users]


@router.patch("/users/{user_id}/active")
def set_user_active(user_id: int, is_active: bool, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin and not is_active:
        raise HTTPException(status_code=400, detail="Administrator account cannot be deactivated")
    user.is_active = is_active
    db.commit()
    return {"id": user.id, "is_active": user.is_active}


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_user(user_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Administrator accounts cannot be deleted")
    db.query(DBDevice).filter(DBDevice.user_id == user_id).update(
        {DBDevice.user_id: None}, synchronize_session=False
    )
    db.delete(user)
    db.commit()


@router.get("/devices", response_model=list[Device])
def list_all_devices(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000),
                     _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(DBDevice).order_by(DBDevice.id).offset(skip).limit(limit).all()


@router.put("/devices/{device_id}", response_model=Device)
def admin_update_device(device_id: str, payload: DeviceUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    device = db.query(DBDevice).filter(DBDevice.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return update_device(db, device.id, payload)


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_device(device_id: str, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    device = db.query(DBDevice).filter(DBDevice.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    delete_device(db, device.id)


@router.get("/devices/{device_id}/measurements", response_model=List[Measurement])
def admin_device_measurements(
    device_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
                                                                                    
    device = db.query(DBDevice).filter(DBDevice.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    rows = (
        db.query(DBMeasurement)
        .filter(DBMeasurement.device_id == device.id)
        .order_by(DBMeasurement.measurement_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return rows


@router.get("/users/{user_id}/devices", response_model=List[Device])
def admin_user_devices(
    user_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
                                                                 
    return (
        db.query(DBDevice)
        .filter(DBDevice.user_id == user_id)
        .order_by(DBDevice.device_id)
        .all()
    )
