from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db, close_db
from app.routers import bookings, auth, movies

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan replaces the old @app.on_event("startup") pattern,
    Everything before 'yield' runs at startup.
    Everything after 'yield' runs at shutdown.
    This ensures DB connections are opened AND closed properly.
    """
    await  init_db()
    yield
    await close_db()


app = FastAPI(
    title="Movie Booking API",
    description="Book cinema tickets via REST API",
    version="1.0.0",
    lifespan=lifespan,
)

# Register routers -each router knows its own prefix
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(bookings.router)

@app.get("/health")
async def health():
    """Quick endpoint to verify the app is alive"""
    return {"status": "ok"}

