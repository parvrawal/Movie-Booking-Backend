from fastapi import APIRouter, Depends, HTTPException
from app.models.movie import Movie, ShowTime
from app.schemas.movie import (
    MovieCreate, MovieResponse,
    ShowTimeCreate, ShowtimeResponse
)
from app.dependencies import get_current_user, get_admin_user
from app.models.user import User


router = APIRouter(prefix="/movies", tags=["Movies"])

@router.get("/", response_model=list[MovieResponse])
async def list_movies():
    """Public endpoint - no auth needed. Return all movies"""
    return await Movie.all()

@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: int):
    movie = await Movie.get_or_none(id=movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.post("/", response_model=MovieResponse, status_code=201)
async def create_movie(
    movie_data: MovieCreate,
    admin: User = Depends(get_admin_user) # only admins can create movies

):
    return await Movie.create(**movie_data.model_dump())
    # model_dump() converts the pydantic schema to a plain dict.
    # **unpacking passes each field as a keyword argument to Movie.create()


@router.delete("/{movie_id}", status_code=204)
async def delete_movie(
    movie_id: int,
    admin: User = Depends(get_admin_user)
):
    movie = await Movie.get_or_none(id=movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    await movie.delete()


#----Showtimes---

@router.get("/{movie_id}/showtimes", response_model=list[ShowtimeResponse])
async def list_showtimes(moive_id: int):
    return await ShowTime.filter(moive_id=moive_id).all()

@router.post("/{movie_id}/showtimes", response_model=ShowtimeResponse, status_code=201)
async def create_showtime(
    movie_id: int,
    data: ShowTimeCreate,
    admin: User = Depends(get_admin_user)
):
    movie = await Movie.get_or_none(id=movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return await ShowTime.create(
        movie_id=movie_id,
        hall_name=data.hall_name,
        start_time=data.start_time,
        total_seats=data.total_seats,
        available_seats=data.total_seats, # starts fully available
        price=data.price
    )