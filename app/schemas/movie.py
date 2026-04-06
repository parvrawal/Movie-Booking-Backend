from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal


class MovieCreate(BaseModel):
    title: str
    description: str
    duration_minutes: int
    genre: str
    release_date: date
    poster_url: str | None = None

class MovieResponse(MovieCreate):
    # Inheriting MovieCreate reuses all fields
    # We just add the DB-generated ones: 
    id: int
    create_at: datetime

    class Config:
        from_attributes = True

class ShowTimeCreate(BaseModel):
    movie_id: int
    hall_name: str
    start_time: datetime
    total_seats: int
    price: Decimal

class ShowtimeResponse(BaseModel):
    id: int
    movie_id: int
    hall_name: str
    start_time: datetime
    total_seats: int
    available_seats: int
    price: Decimal

    class Config:
        from_attributes = True

        