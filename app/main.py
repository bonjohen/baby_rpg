from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.seed import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_all()
    yield


app = FastAPI(title="Baby RPG", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}
