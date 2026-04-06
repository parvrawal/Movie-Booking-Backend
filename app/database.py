from tortoise import Tortoise
from app.config import settings

# This dict is the single source of truth for Tortoise AND Aerich
# We import it in both main.py and pyproject.toml

TORTOISE_ORM = {
    "connection": {
        "default": settings.database_url
        # "default" is the connection name. You can have multiple
        # (e.g., "replica") for read replica.
    },
    "app": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.movie",
                "app.models.booking",
                "aerich.models",  # <- Aerich needs its own model table
            ],
            "default_connection": "default",
        }
    },
}


async def init_db():
    """Called once at app startup."""
    await Tortoise.init(config=TORTOISE_ORM)
    # generate_schemas=False because Aerich manges the schma.
    # We only auto-generate in tests.
    await Tortoise.generate_schemas(safe=True)


async def close_db():
    """Called at app shutdown to close all DB connections cleanly"""
    await Tortoise.close_connections()
