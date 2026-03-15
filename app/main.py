from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import auth, characters, world
from app.seed import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_all()
    yield


app = FastAPI(title="Baby RPG", version="0.1.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(characters.router)
app.include_router(world.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
