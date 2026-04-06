from tortoise import fields
from tortoise import Model
from enum import Enum

class BookingStatus(str, Enum):
    confirmed = "confirmed"
    pending = "pending"
    cancelled = "cancelled"


class Booking(Model):
    id = fields.IntField(pk=True)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="bookings",
        on_delete=fields.CASCADE
    )

    showtime = fields.ForeignKeyField(
        "models.Showtime",
        related_name="bookings",
        on_delete=fields.CASCADE
    )
    

    seats_booked = fields.IntField()

    total_price = fields.DecimalField(max_digits=10, decimal_places=2)
    # Stored separately even though it's computable (seats * price)
    # Why? Price can change later. you want the price AT TIME OF BOOKING

    status = fields.CharEnumField(
        enum_type=BookingStatus,
        max_length=20,
        default=BookingStatus.confirmed
    )

    # Enum is DB prevents garbage values like "cnfirmed" or "CONFIRMED"

    booked_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "bookings"

