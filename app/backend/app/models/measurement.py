import uuid
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Measurement(Base):
    __tablename__ = "measurements"
    __table_args__ = (Index("ix_measurements_device_time", "device_id", "measurement_time"),)

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    measurement_id = Column(String(36), nullable=False, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    water_quality_turbidity = Column(Float, nullable=True)
    ec = Column(Float, nullable=True)
    water_quality_ph = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    rainfall_mm = Column(Float, nullable=True)
    rainfall_1h_mm = Column(Float, nullable=True)
    measurement_time = Column(DateTime(timezone=True), server_default=func.now())
    is_processed = Column(Boolean, default=False)
    raw_data = Column(String, nullable=True)
    device = relationship("Device", back_populates="measurements")
