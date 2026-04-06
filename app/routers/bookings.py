from fastapi import APIRouter, Depends, HTTPException
from app.models.movie import ShowTime
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import BookingCreate, bookingResponse
from app.dependencies import get_current_user
from app.models.user import User
from tortoise.transactions import in_transaction


router = APIRouter(prefix="/bookings", tags=["Bookings"])


router.post("/", response_model=bookingResponse, status_code=201)
async def create_booking(
        data: BookingCreate,
        current_user: User = Depends(get_current_user)
):
    """This is the most critical endpoint - money changes hands here.
    We use a DB transaction to ensure atomicty:
    either BOTH the seat count update AND the booking insert succed,
    or NEITHER does. No partial states.
    """

    async with in_transaction():
        # select_for_update() locks the row until transction ends.
        # Without this, two concurrent requests could both see
        # available_seats=1, both pass the check, and double-book.
        showtime = await ShowTime.select_for_update().get_or_none(
            id=data.showtime_id
        )
        if not showtime:
            raise HTTPException(status_code=404, detail="Showtime not found")
        
        if showtime.available_seats < data.seats_booked:
            raise HTTPException(
                status_code=400,
                detail=f"Only {showtime.available_seats} seats available"
            )
        

        total_price = showtime.price * data.seats_booked

        # Decrement seats BEFORE creating booking record.
        # Both happen inside the. transaction so they're atomic.
        showtime.available_seats -= data.seats_booked
        await showtime.save(update_fields=["available_seats"])
        # update_fields limits the UPDATE to just one column - more efficient
        # and avoids accidentally overwriting other fields

        booking = await Booking.create(
            user=current_user,
            showtime=showtime,
            seats_booked=data.seats_booked,
            total_price=total_price,
            status="confirmed",
        )

        return booking
    
@router.delete("/{booking_id}", status_code=204)
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user)
):
    async with in_transaction():
        booking = await Booking.get_or_none(
            id=booking_id, user=current_user
        )
        # Filtering by user ensures users can only cancel their OWN bookings.
        if not booking:
            raise HTTPException(status_code=400, detail="Booking not found")
        if booking.status == "cancelled":
            raise HTTPException(status_code=400, detail="Already cancelled")
        

        # Return seats to pool
        showtime = await ShowTime.select_for_update().get(
            id=booking.showtime.id
        )

        showtime.available_seats += booking.seats_booked
        await showtime.save(update_fields=["available_seats"])

        booking.status = "cancelled"
        await booking.save(update_fields=["status"])