from .models import BookingModel
from .schemas import BookingOut


def booking_to_out(booking: BookingModel) -> BookingOut:
    return BookingOut.model_validate(booking)


def bookings_to_out(bookings: list[BookingModel]) -> list[BookingOut]:
    return [booking_to_out(booking) for booking in bookings]
