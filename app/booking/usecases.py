from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .exceptions import BookingNotFound, SlotAlreadyBooked
from .models import BookingModel
from .repository import BookingRepository, booking_repository
from .schemas import BookingCreate


class CreateBookingUseCase:
    def __init__(self, repository: BookingRepository) -> None:
        self._repository = repository

    def execute(self, session: Session, data: BookingCreate) -> BookingModel:
        if self._repository.find_active_by_slot(
            session, data.booking_date, data.booking_time
        ):
            raise SlotAlreadyBooked(data.booking_date, data.booking_time)

        booking = BookingModel(**data.model_dump(), status="active")
        try:
            return self._repository.add(session, booking)
        except IntegrityError:
            session.rollback()
            raise SlotAlreadyBooked(
                data.booking_date, data.booking_time
            ) from None


class ListBookingsUseCase:
    def __init__(self, repository: BookingRepository) -> None:
        self._repository = repository

    def execute(
        self, session: Session, booking_date: date | None
    ) -> list[BookingModel]:
        return self._repository.list(session, booking_date)


class GetBookingUseCase:
    def __init__(self, repository: BookingRepository) -> None:
        self._repository = repository

    def execute(self, session: Session, booking_id: int) -> BookingModel:
        booking = self._repository.get(session, booking_id)
        if booking is None:
            raise BookingNotFound(booking_id)
        return booking


class CancelBookingUseCase:
    def __init__(self, repository: BookingRepository) -> None:
        self._repository = repository

    def execute(self, session: Session, booking_id: int) -> BookingModel:
        booking = self._repository.get(session, booking_id)
        if booking is None:
            raise BookingNotFound(booking_id)

        if booking.status != "cancelled":
            booking.status = "cancelled"
            self._repository.save(session, booking)
        return booking


def get_create_booking_use_case() -> CreateBookingUseCase:
    return CreateBookingUseCase(booking_repository)


def get_list_bookings_use_case() -> ListBookingsUseCase:
    return ListBookingsUseCase(booking_repository)


def get_get_booking_use_case() -> GetBookingUseCase:
    return GetBookingUseCase(booking_repository)


def get_cancel_booking_use_case() -> CancelBookingUseCase:
    return CancelBookingUseCase(booking_repository)
