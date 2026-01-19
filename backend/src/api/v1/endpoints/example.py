from fastapi import APIRouter, Depends
from src.db.postgres import add_user
from src.db.redis import get_redis_url


router = APIRouter()


@router.get("/")
async def create_example():
    """
    Docstring for create_example
    """
    return {"message": "example /v1/ endpoint", "redis_url": get_redis_url()} # /api/v1/base/


