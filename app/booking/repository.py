from datetime import date, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import BookingModel


class BookingRepository:
    def add(self, session: Session, booking: BookingModel) -> BookingModel:
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking

    def get(self, session: Session, booking_id: int) -> BookingModel | None:
        return session.get(BookingModel, booking_id)

    def list(
        self, session: Session, booking_date: date | None = None
    ) -> list[BookingModel]:
        statement = select(BookingModel).order_by(
            BookingModel.booking_date,
            BookingModel.booking_time,
            BookingModel.id,
        )
        if booking_date is not None:
            statement = statement.where(BookingModel.booking_date == booking_date)
        return list(session.scalars(statement))

    def find_active_by_slot(
        self, session: Session, booking_date: date, booking_time: time
    ) -> BookingModel | None:
        statement = select(BookingModel).where(
            BookingModel.booking_date == booking_date,
            BookingModel.booking_time == booking_time,
            BookingModel.status == "active",
        )
        return session.scalars(statement).first()

    def save(self, session: Session, booking: BookingModel) -> BookingModel:
        session.commit()
        session.refresh(booking)
        return booking


booking_repository = BookingRepository()
