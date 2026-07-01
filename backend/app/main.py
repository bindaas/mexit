from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import SessionLocal, engine
from .models import SYSTEM_USER_ID, Base, User
from .schemas import HealthResponse

# Resource routers register here as they're added, e.g.:
# from .routers import tasks
# app.include_router(tasks.router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.id == SYSTEM_USER_ID).first() is None:
            db.add(User(id=SYSTEM_USER_ID, email="system@local"))
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


# Root Dockerfile's prod build copies the frontend's built dist/ in as
# static/, sibling to app/. Mounted last so it never shadows API routes above.
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
