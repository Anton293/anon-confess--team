"""Module for working with the database postgresSQL."""
from src.core.config import settings


def get_redis_url() -> str:
    return str(settings.REDIS_URL)

