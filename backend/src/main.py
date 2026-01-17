from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from datetime import datetime
import os
from redis import asyncio as aioredis


from src.api.v1 import api_router
from src.core.config import settings
from src.core.logger import logger


logger.info("app_started", service="backend")

app = FastAPI(title=settings.PROJECT_NAME, root_path="/api")
app.include_router(api_router, prefix=settings.API_V1_STR)
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# CHECK START

if settings.APP_ENV != "production":
    logger.warning(
        "Application is running in non-production mode.",
        env=settings.APP_ENV
    )

# END CHECK


# API endpoints on /api/
@app.get("/")
async def root():
    """head page of the API"""
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

    redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)

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
        logger.error("Health check failed", error=str(e))
        report["checks"]["redis"]["status"] = "ERROR"
        report["checks"]["redis"]["details"]["exception"] = str(e)
        report["status"] = "ERROR"

    finally:
        await redis.close()

    return report

