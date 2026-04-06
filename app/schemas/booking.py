from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class BookingCreate(BaseModel):
    showtime_id: int
    seats_booked: int

class bookingResponse(BaseModel):
    id: int
    showtime_id: int
    seats_booked: int
    total_price: Decimal
    status: str
    booked_str: str
    booked_at: datetime


    class Config:
        from_attributes = True
        