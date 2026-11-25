from sqlalchemy.orm import Session
from app.models.measurement import Measurement as SQLMeasurement
from app.models.device import Device
from app.schemas.measurement import MeasurementCreate, Measurement
from typing import List, Optional
from datetime import datetime

def get_measurement(db: Session, measurement_id: str) -> Optional[SQLMeasurement]:
    return db.query(SQLMeasurement).filter(SQLMeasurement.measurement_id == measurement_id).first()

def get_measurements_by_device(
    db: Session,
    device_id: int,
    skip: int = 0,
    limit: int = 100,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[SQLMeasurement]:
    query = db.query(SQLMeasurement).filter(SQLMeasurement.device_id == device_id)

    if start_time:
        query = query.filter(SQLMeasurement.measurement_time >= start_time)
    if end_time:
        query = query.filter(SQLMeasurement.measurement_time <= end_time)

    return query.order_by(SQLMeasurement.measurement_time.desc()).offset(skip).limit(limit).all()

def get_latest_measurement_by_device(db: Session, device_id: int) -> Optional[SQLMeasurement]:
    return db.query(SQLMeasurement).filter(SQLMeasurement.device_id == device_id).order_by(SQLMeasurement.measurement_time.desc()).first()

def create_measurement(db: Session, measurement_in: MeasurementCreate) -> Measurement:
    device = db.query(Device).filter(Device.device_id == measurement_in.device_id).first()
    if not device:
        raise ValueError(f"Device with device_id {measurement_in.device_id} not found")

    measurement_data = measurement_in.model_dump(exclude={'device_id'})
    measurement_id = measurement_data.get('measurement_id')

    if measurement_id:
        existing_measurement = db.query(SQLMeasurement).filter(
            SQLMeasurement.measurement_id == measurement_id
        ).first()

        if existing_measurement:
            return Measurement.model_validate(existing_measurement)

    db_measurement = SQLMeasurement(
        **measurement_data,
        device_id=device.id,
        is_processed=False
    )
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return Measurement.model_validate(db_measurement)

def get_measurements_since_timestamp(
    db: Session,
    device_id: int,
    since: datetime
) -> List[SQLMeasurement]:
                                                                                    
    return db.query(SQLMeasurement).filter(
        SQLMeasurement.device_id == device_id,
        SQLMeasurement.measurement_time > since
    ).order_by(SQLMeasurement.measurement_time).all()

def mark_measurements_as_processed(db: Session, measurement_ids: List[int]) -> int:
                                                                   
    result = db.query(SQLMeasurement).filter(
        SQLMeasurement.id.in_(measurement_ids)
    ).update({SQLMeasurement.is_processed: True}, synchronize_session=False)
    db.commit()
    return result
