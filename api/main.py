from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import tasks

app = FastAPI(title="TodoSmart API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])


@app.get("/health")
async def health():
    return {"status": "ok"}
