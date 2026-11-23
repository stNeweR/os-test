from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from .mapper import booking_to_out, bookings_to_out
from .schemas import BookingCreate, BookingOut
from .usecases import (
    CancelBookingUseCase,
    CreateBookingUseCase,
    GetBookingUseCase,
    ListBookingsUseCase,
    get_cancel_booking_use_case,
    get_create_booking_use_case,
    get_get_booking_use_case,
    get_list_bookings_use_case,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", status_code=201, response_model=BookingOut)
def create_booking(
    payload: BookingCreate,
    session: Session = Depends(get_db),
    use_case: CreateBookingUseCase = Depends(get_create_booking_use_case),
) -> BookingOut:
    return booking_to_out(use_case.execute(session, payload))


@router.get("", response_model=list[BookingOut])
def list_bookings(
    booking_date: date | None = Query(default=None, alias="date"),
    session: Session = Depends(get_db),
    use_case: ListBookingsUseCase = Depends(get_list_bookings_use_case),
) -> list[BookingOut]:
    return bookings_to_out(use_case.execute(session, booking_date))


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    session: Session = Depends(get_db),
    use_case: GetBookingUseCase = Depends(get_get_booking_use_case),
) -> BookingOut:
    return booking_to_out(use_case.execute(session, booking_id))


@router.delete("/{booking_id}", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    session: Session = Depends(get_db),
    use_case: CancelBookingUseCase = Depends(get_cancel_booking_use_case),
) -> BookingOut:
    return booking_to_out(use_case.execute(session, booking_id))
