from datetime import date, time, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

BookingStatus = Literal["active", "cancelled"]

MAX_DAYS_AHEAD = 30
OPENING_HOUR = 12
CLOSING_HOUR = 22


class BookingCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    phone: str = Field(pattern=r"^\+7\d{10}$")
    booking_date: date
    booking_time: time
    guests: int = Field(ge=1, le=10)

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, value: date) -> date:
        today = date.today()
        if value < today:
            raise ValueError("booking_date must not be in the past")
        if value > today + timedelta(days=MAX_DAYS_AHEAD):
            raise ValueError(
                f"booking_date must be within {MAX_DAYS_AHEAD} days from today"
            )
        return value

    @field_validator("booking_time")
    @classmethod
    def validate_booking_time(cls, value: time) -> time:
        if value.minute or value.second or value.microsecond:
            raise ValueError("booking_time must be a whole hour")
        if not OPENING_HOUR <= value.hour <= CLOSING_HOUR:
            raise ValueError(
                f"booking_time must be between {OPENING_HOUR}:00 and {CLOSING_HOUR}:00"
            )
        return value


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    booking_date: date
    booking_time: time
    guests: int
    status: BookingStatus
