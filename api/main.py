import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, categories, stats, todos

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Scheduler for reminders — only start if BOT_TOKEN is set
    try:
        from config import settings
        from db import get_client
        from scheduler import setup_scheduler
        from aiogram import Bot

        bot = Bot(token=settings.bot_token)
        db = await get_client()
        setup_scheduler(bot, db)
    except Exception as exc:
        logging.warning("Scheduler not started: %s", exc)
    yield


app = FastAPI(title="TodoSmart API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,       prefix="/api/auth",       tags=["auth"])
app.include_router(todos.router,      prefix="/api/todos",      tags=["todos"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(stats.router,      prefix="/api/stats",      tags=["stats"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": "2.0.0"}
