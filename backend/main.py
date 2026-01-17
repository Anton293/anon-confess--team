from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from datetime import datetime
import os
from redis import asyncio as aioredis

import logging
logging.basicConfig(level=logging.INFO)


REDIS_URL = os.getenv("REDIS_URL")
DATABASE_URL = os.getenv("DATABASE_URL")

if not REDIS_URL:
    logging.error("REDIS_URL environment variable is not set!")
    raise ValueError("REDIS_URL environment variable is not set!")


async def get_redis():
    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()




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

if "http://localhost" in origins or "http://localhost:3000" in origins:
    logging.warning("WARNING: CORS is allowing localhost origins. This should be removed in production!")


app.add_middleware(SessionMiddleware, secret_key=secret_key)


# API endpoints on /api/
@app.get("/")
async def root():
    """head page"""
    return {"message": "Hello World!"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    report = {
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "redis": {
                "status": "OK",
                "details": {}
            }
        }
    }

    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)

    try:
        # ping
        pong = await redis.ping()
        if not pong:
            report["checks"]["redis"]["status"] = "ERROR"
            report["checks"]["redis"]["details"]["ping"] = "failed"
            report["status"] = "ERROR"
            return report

        report["checks"]["redis"]["details"]["ping"] = "ok"

        # info
        info = await redis.info(section="persistence")

        loading = info.get("loading", 0)
        report["checks"]["redis"]["details"]["loading"] = bool(loading)

        if loading:
            report["checks"]["redis"]["status"] = "ERROR"
            report["status"] = "ERROR"
            report["checks"]["redis"]["details"]["reason"] = "redis is loading data from disk"

        # додатково корисні штуки
        report["checks"]["redis"]["details"]["rdb_last_save_time"] = info.get(
            "rdb_last_save_time"
        )
        report["checks"]["redis"]["details"]["aof_enabled"] = bool(
            info.get("aof_enabled", 0)
        )

    except Exception as e:
        logging.exception("Healthcheck failed")
        report["checks"]["redis"]["status"] = "ERROR"
        report["checks"]["redis"]["details"]["exception"] = str(e)
        report["status"] = "ERROR"

    finally:
        await redis.close()

    return report

