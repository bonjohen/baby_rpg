from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import auth, character_state, characters, inventory, world
from app.seed import seed_all

CLIENT_DIR = Path(__file__).resolve().parent.parent / "client"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_all()
    yield


app = FastAPI(title="Baby RPG", version="0.1.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(characters.router)
app.include_router(character_state.router)
app.include_router(inventory.router)
app.include_router(world.router)

# Serve client static files
app.mount("/static", StaticFiles(directory=str(CLIENT_DIR)), name="static")


@app.get("/")
async def index():
    return FileResponse(str(CLIENT_DIR / "index.html"))


@app.get("/health")
async def health():
    return {"status": "ok"}
