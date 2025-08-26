from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, delete

from .database import get_db
from . import models, schemas
from .auth import create_access_token, verify_password, get_current_user, require_admin

router = APIRouter()

# -------- Helper Functions --------
def cleanup_expired_reservations(db: Session):
    """清理超過24小時的過期預約紀錄"""
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    
    # 刪除結束時間超過24小時的預約
    result = db.execute(
        delete(models.Reservation).where(models.Reservation.end_time < cutoff_time)
    )
    
    deleted_count = result.rowcount
    if deleted_count > 0:
        db.commit()
        print(f"Cleaned up {deleted_count} expired reservations")
    
    return deleted_count

# -------- Auth --------
@router.post("/auth/login", response_model=schemas.TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.execute(select(models.User).where(models.User.username == form_data.username)).scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    token = create_access_token({"sub": user.username})
    return schemas.TokenResponse(access_token=token)

@router.get("/auth/me", response_model=schemas.UserRead)
async def me(current_user: models.User = Depends(get_current_user)):
    return current_user

# -------- Parking Spots --------
@router.get("/spots", response_model=List[schemas.ParkingSpotRead])
def list_spots(include_inactive: bool = False, db: Session = Depends(get_db)):
    stmt = select(models.ParkingSpot)
    if not include_inactive:
        stmt = stmt.where(models.ParkingSpot.active == True)  # noqa: E712
    spots = db.execute(stmt.order_by(models.ParkingSpot.spot_number)).scalars().all()
    return spots

@router.post("/spots", response_model=schemas.ParkingSpotRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_spot(spot: schemas.ParkingSpotCreate, db: Session = Depends(get_db)):
    exists = db.execute(
        select(func.count()).select_from(models.ParkingSpot).where(models.ParkingSpot.spot_number == spot.spot_number)
    ).scalar()
    if exists:
        raise HTTPException(status_code=409, detail="Spot number already exists")
    obj = models.ParkingSpot(spot_number=spot.spot_number, active=spot.active)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.patch("/spots/{spot_id}", response_model=schemas.ParkingSpotRead, dependencies=[Depends(require_admin)])
def update_spot(spot_id: int, payload: schemas.ParkingSpotUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.ParkingSpot, spot_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Spot not found")
    if payload.spot_number is not None:
        exists = db.execute(
            select(func.count()).select_from(models.ParkingSpot).where(
                and_(models.ParkingSpot.spot_number == payload.spot_number, models.ParkingSpot.id != spot_id)
            )
        ).scalar()
        if exists:
            raise HTTPException(status_code=409, detail="Spot number already exists")
        obj.spot_number = payload.spot_number
    if payload.active is not None:
        obj.active = payload.active
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
    # 在獲取預約列表時自動清理過期預約
    cleanup_expired_reservations(db)
    
    stmt = select(models.Reservation)
    if spot_id is not None:
        stmt = stmt.where(models.Reservation.spot_id == spot_id)
    stmt = stmt.order_by(models.Reservation.start_time)
    items = db.execute(stmt).scalars().all()
    return items

@router.post("/reservations", response_model=schemas.ReservationRead, status_code=status.HTTP_201_CREATED)
def create_reservation(payload: schemas.ReservationCreate, db: Session = Depends(get_db)):
    # 在創建新預約時自動清理過期預約
    cleanup_expired_reservations(db)
    
    spot = db.execute(select(models.ParkingSpot).where(models.ParkingSpot.id == payload.spot_id)).scalar_one_or_none()
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")
    if not spot.active:
        raise HTTPException(status_code=400, detail="Parking spot is inactive")

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

@router.delete("/reservations/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Reservation, reservation_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reservation not found")
    db.delete(obj)
    db.commit()
    return None

@router.post("/reservations/cleanup", dependencies=[Depends(require_admin)])
def manual_cleanup_reservations(db: Session = Depends(get_db)):
    """管理員手動清理過期預約紀錄"""
    deleted_count = cleanup_expired_reservations(db)
    return {"message": f"Cleaned up {deleted_count} expired reservations", "deleted_count": deleted_count}
