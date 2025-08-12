from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class ParkingSpotBase(BaseModel):
    spot_number: str = Field(..., max_length=32)

class ParkingSpotCreate(ParkingSpotBase):
    pass

class ParkingSpotRead(ParkingSpotBase):
    id: int

    class Config:
        from_attributes = True

class ReservationBase(BaseModel):
    name: str = Field(..., max_length=64)
    household: str = Field(..., max_length=64)
    phone: str = Field(..., max_length=32)
    spot_id: int
    start_time: datetime
    end_time: datetime

    @field_validator("end_time")
    @classmethod
    def validate_time_order(cls, v: datetime, values):
        start = values.get("start_time")
        if start and v <= start:
            raise ValueError("end_time must be greater than start_time")
        return v

class ReservationCreate(ReservationBase):
    pass

class ReservationRead(ReservationBase):
    id: int

    class Config:
        from_attributes = True
