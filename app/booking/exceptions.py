from datetime import date, time


class BookingError(Exception):
    """Base class for booking domain errors."""


class BookingNotFound(BookingError):
    def __init__(self, booking_id: int) -> None:
        self.booking_id = booking_id
        super().__init__(f"Booking {booking_id} not found")


class SlotAlreadyBooked(BookingError):
    def __init__(self, booking_date: date, booking_time: time) -> None:
        self.booking_date = booking_date
        self.booking_time = booking_time
        super().__init__(f"Slot {booking_date} {booking_time} is already booked")
