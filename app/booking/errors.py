from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .exceptions import BookingNotFound, SlotAlreadyBooked


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BookingNotFound)
    async def booking_not_found_handler(
        request: Request, exc: BookingNotFound
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": "Booking not found"})

    @app.exception_handler(SlotAlreadyBooked)
    async def slot_already_booked_handler(
        request: Request, exc: SlotAlreadyBooked
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409, content={"detail": "Slot is already booked"}
        )
