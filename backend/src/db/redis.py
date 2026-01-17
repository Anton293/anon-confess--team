from src.core.config import settings


def get_redis_url() -> str:
    return settings.REDIS_URL
