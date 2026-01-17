from fastapi import APIRouter, Depends
from db.postgres import get_database_url
from db.redis import get_redis_url


router = APIRouter()


@router.post("/")
async def create_example():
    """
    Docstring for create_example
    """
    return {"message": "example /v1/ endpoint", "redis_url": get_redis_url()}


