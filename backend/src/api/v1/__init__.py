"""
Add API routers here. 
TODO: add api this!!!
"""
from fastapi import APIRouter
from src.api.v1.endpoints import example

api_router = APIRouter()
api_router.include_router(example.router, prefix="/base", tags=["base"])
