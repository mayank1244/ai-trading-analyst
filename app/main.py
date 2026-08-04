"""FastAPI Main Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config.settings import settings
from app.database.session import init_db
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting {}...", settings.APP_NAME)
    await init_db()
    yield
    logger.info("Shutting down {}...", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered market research assistant for Indian stock market (NSE/BSE)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "status": "online",
        "docs": "/docs",
    }
