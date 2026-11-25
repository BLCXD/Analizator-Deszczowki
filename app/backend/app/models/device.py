from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from datetime import datetime, timedelta, timezone


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    device_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    device_code = Column(String, unique=True, index=True, nullable=True)
    device_secret_hash = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_seen = Column(DateTime(timezone=True), nullable=True)
    measurements = relationship("Measurement", back_populates="device", cascade="all, delete-orphan")

    @property
    def status(self) -> str:
        if not self.is_active:
            return "offline"
        if self.last_seen is None:
            return "unknown"
        last_seen = self.last_seen
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        return "online" if datetime.now(timezone.utc) - last_seen <= timedelta(seconds=180) else "offline"
