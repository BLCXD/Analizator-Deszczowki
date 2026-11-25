from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class DeviceBase(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=100, json_schema_extra={"example": "device-001"})
    name: str = Field(..., min_length=1, max_length=255, json_schema_extra={"example": "Rainwater station"})


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class Device(DeviceBase):
    id: int
    user_id: Optional[int] = None
    is_active: bool
    status: str
    device_code: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DevicePair(BaseModel):
    device_id: str
    device_code: str


class DevicePairByCode(BaseModel):
    device_code: str = Field(..., min_length=3, max_length=100)


class DeviceClaim(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=100)
    claim_proof: str = Field(..., min_length=32, max_length=128)


class DevicePairResult(BaseModel):
    device_secret: str = Field(..., example="abcdef123456")


class DeviceAuth(BaseModel):
    device_id: str
    device_secret: str = Field(..., min_length=32, max_length=256)


class DeviceAuthResult(BaseModel):
    access_token: str
    token_type: str = "bearer"
