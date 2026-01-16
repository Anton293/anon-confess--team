from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os

import logging
logging.basicConfig(level=logging.INFO)


app = FastAPI()


origins = [
    "http://localhost", # TODO: remove this in production
    "http://localhost:3000", # TODO: remove this in production
    "http://127.0.0.1:8000",
    "https://demo.harkushyn.com",
    "https://harkushyn.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


secret_key = os.getenv("SESSION_SECRET_KEY", "dev-secret-key-unsafe")
if not secret_key or secret_key == "dev-secret-key-unsafe":
    logging.warning("WARNING: Using unsafe session secret key!")

if os.getenv("APP_ENV") == "production" and (not secret_key or secret_key == "dev-secret-key-unsafe"):
    logging.error("In production, SESSION_SECRET_KEY must be set to a secure value!")
    raise ValueError("In production, SESSION_SECRET_KEY must be set to a secure value!")


app.add_middleware(SessionMiddleware, secret_key=secret_key)


# API endpoints on /api/

@app.get("/")
async def root():
    """head page API"""
    return {"message": "Hello World!"}


@app.get("/health")
async def health_check():
    """Healthcheck"""
    return {"status": "OK"}
