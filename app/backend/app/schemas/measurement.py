from pydantic import AliasPath, BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class MeasurementBase(BaseModel):
    water_quality_turbidity: Optional[float] = Field(None, ge=0, description="Turbidity in NTU")
    ec: Optional[float] = Field(None, ge=0, le=3000, description="Electrical conductivity in µS/cm")
    water_quality_ph: Optional[float] = Field(None, gt=0, lt=14, description="pH level")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Humidity percentage")
    rainfall_mm: Optional[float] = Field(None, ge=0, description="Cumulative rainfall in millimeters")
    rainfall_1h_mm: Optional[float] = Field(None, ge=0, description="Rainfall in the last hour, millimeters")
    raw_data: Optional[str] = None
    measurement_id: str = Field(..., min_length=1, max_length=36, description="Globally unique source measurement ID")
    measurement_time: Optional[datetime] = None

class MeasurementCreate(MeasurementBase):
    device_id: str

class Measurement(MeasurementBase):
    id: int
    device_id: str = Field(validation_alias=AliasPath("device", "device_id"))
    is_processed: bool = False

    model_config = ConfigDict(from_attributes=True)
