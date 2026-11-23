from fastapi import APIRouter

from app.booking.router import router as booking_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(booking_router)