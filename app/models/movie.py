from tortoise import fields
from tortoise.models import Model

class Movie(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    description = fields.TextField()
    # TextField vs CharField: TextField has no length limit (maps to TEXT in PG)
    # Use it for long content, CharField for short indexed strings

    duration_minutes = fields.IntField()
    genre = fields.CharField(max_length=50)
    release_data = fields.DateField()
    poster_url = fields.CharField(max_length=500, null=True)
    # null=True -< column is NULLABLE in the database
    # without this, inserting a Movie without a poster_url would fail

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "movies"


class ShowTime(Model):
    """
    Why separate Shorttime for Movie?
    One Movie can play many times in many halls.
    Showtime is the intersection of movie + time + hall
    This is the "event" users actually book tickets for
    """

    id = fields.IntField(pk=True)

    movie = fields.ForeignKeyField(
        "models.Movie",
        related_name="showtimes",
        on_delete=fields.CASCADE
    )

    # ForeignKeyField creates a movie_id FK column in the DB
    # related_name="showtimes" lets you do: movie.showtimes.all()
    # on_delete=CASCADE -> if the movie id deleted, all its showtine are too.

    hall_name = fields.CharField(max_length=50)
    start_time = fields.DatetimeField()

    total_seats = fields.IntField()
    available_seats = fields.IntField()
    # We track available_seats as counter rather than querying
    # all booking rows each time. Much faster at scale
    # The tradeoff: we must keep it in sync with actual bookings

    price = fields.DecimalField(max_digits=8, decimal_places=2)
    # DecimalFields for money - NEVER use floatField for currency
    # Floats have binary precision errors (0.1 + 0.2 # 0.3)

    class Meta:
        table = "showtimes"
        