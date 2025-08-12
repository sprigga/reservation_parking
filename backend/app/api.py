from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from .database import get_db
from . import models, schemas

router = APIRouter()

# -------- Parking Spots --------
@router.get("/spots", response_model=List[schemas.ParkingSpotRead])
def list_spots(db: Session = Depends(get_db)):
    spots = db.execute(select(models.ParkingSpot).order_by(models.ParkingSpot.spot_number)).scalars().all()
    return spots

# (Optional) Create spot - for seeding/management
@router.post("/spots", response_model=schemas.ParkingSpotRead, status_code=status.HTTP_201_CREATED)
def create_spot(spot: schemas.ParkingSpotCreate, db: Session = Depends(get_db)):
    # ensure unique spot_number
    exists = db.execute(
        select(func.count()).select_from(models.ParkingSpot).where(models.ParkingSpot.spot_number == spot.spot_number)
    ).scalar()
    if exists:
        raise HTTPException(status_code=409, detail="Spot number already exists")
    obj = models.ParkingSpot(spot_number=spot.spot_number)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# -------- Reservations --------
@router.get("/reservations", response_model=List[schemas.ReservationRead])
def list_reservations(
    spot_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    stmt = select(models.Reservation)
    if spot_id is not None:
        stmt = stmt.where(models.Reservation.spot_id == spot_id)
    stmt = stmt.order_by(models.Reservation.start_time)
    items = db.execute(stmt).scalars().all()
    return items

@router.post("/reservations", response_model=schemas.ReservationRead, status_code=status.HTTP_201_CREATED)
def create_reservation(payload: schemas.ReservationCreate, db: Session = Depends(get_db)):
    # Ensure spot exists
    spot = db.execute(select(models.ParkingSpot).where(models.ParkingSpot.id == payload.spot_id)).scalar_one_or_none()
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")

    # Overlap check: (new_start < existing_end) AND (new_end > existing_start)
    overlap_count = db.execute(
        select(func.count()).select_from(models.Reservation).where(
            and_(
                models.Reservation.spot_id == payload.spot_id,
                payload.start_time < models.Reservation.end_time,
                payload.end_time > models.Reservation.start_time,
            )
        )
    ).scalar()

    if overlap_count and overlap_count > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The selected time range overlaps with an existing reservation for this spot.")

    obj = models.Reservation(
        name=payload.name,
        household=payload.household,
        phone=payload.phone,
        spot_id=payload.spot_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/reservations/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Reservation, reservation_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reservation not found")
    db.delete(obj)
    db.commit()
    return None
