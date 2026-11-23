from datetime import date, time

from sqlalchemy import Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class BookingModel(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        Index(
            "uq_bookings_active_slot",
            "booking_date",
            "booking_time",
            unique=True,
            sqlite_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(12))
    booking_date: Mapped[date]
    booking_time: Mapped[time]
    guests: Mapped[int]
    status: Mapped[str] = mapped_column(String(9), default="active")
