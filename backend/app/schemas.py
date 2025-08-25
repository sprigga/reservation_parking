from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from typing import Optional

# ---- Users ----
class UserBase(BaseModel):
    username: str = Field(..., max_length=50)

class UserRead(UserBase):
    id: int
    is_admin: bool
    is_active: bool
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ---- Parking Spots ----
class ParkingSpotBase(BaseModel):
    spot_number: str = Field(..., max_length=32)

class ParkingSpotCreate(ParkingSpotBase):
    active: bool = True

class ParkingSpotUpdate(BaseModel):
    spot_number: Optional[str] = Field(None, max_length=32)
    active: Optional[bool] = None

class ParkingSpotRead(ParkingSpotBase):
    id: int
    active: bool

    class Config:
        from_attributes = True

# ---- Reservations ----
class ReservationBase(BaseModel):
    name: str = Field(..., max_length=64)
    household: str = Field(..., max_length=64)
    phone: str = Field(..., max_length=32)
    spot_id: int
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def check_time_order(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be greater than start_time")
        return self

class ReservationCreate(ReservationBase):
    pass

class ReservationRead(ReservationBase):
    id: int

    class Config:
        from_attributes = True
