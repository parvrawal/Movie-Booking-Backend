from tortoise import fields
from tortoise.models import Model

class User(Model):
    """
    Why a separate User model?
    Authentication is a cross-cutting concern - bookings, reviews,
    and admin action all need to know WHO is acting.
    """
    id = fields.IntField(pk=True)
    # pk=True -> this becomes the PRIMARY KEY column

    username = fields.CharField(max_length=50, unique=True)
    # unique=True -> DB-level UNIQUE constraint, no just app-level

    email = fields.CharField(max_length=100, unique=True)

    hashed_password = fields.CharField(max_length=120)
    # We NEVER store plaintext passwords. bcrypt hashes are always 60 chars
    # but 120 gives room for other alogirthms later

    is_admin = fields.BooleanField(default=False)
    # Simple role fields. In a larger app you'd use a roles table

    created_at = fields.DatetimeField(auto_now_add=True)
    # auto_now_add=True -> set once on INSERT, never updated

    class Meta:
        table = "users"
        # Explicite table name. Tortoise default to lowercase class name
        # but being explicit avoids surpises during migrations.

        