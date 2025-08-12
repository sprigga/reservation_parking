from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, func, Index
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id = Column(Integer, primary_key=True, index=True)
    spot_number = Column(String(32), nullable=False, unique=True, index=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    reservations = relationship("Reservation", back_populates="spot", cascade="all, delete-orphan")

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    household = Column(String(64), nullable=False)
    phone = Column(String(32), nullable=False)

    spot_id = Column(Integer, ForeignKey("parking_spots.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    spot = relationship("ParkingSpot", back_populates="reservations")

    __table_args__ = (
        Index("idx_reservations_overlap", "spot_id", "start_time", "end_time"),
    )
