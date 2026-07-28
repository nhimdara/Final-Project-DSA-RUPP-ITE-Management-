from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.config import settings
from api.database import Base, SessionLocal, engine
from api.routers import auth, courses, enrollments, students, users
from api.seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    if settings.auto_seed:
        with SessionLocal() as db:
            seed_database(db)
    yield


app = FastAPI(
    title="Student Management System API",
    version="1.0.0",
    description="Database-backed API with JWT authentication and role-based access.",
    lifespan=lifespan,
)

for router in (auth.router, students.router, courses.router, enrollments.router, users.router):
    app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "name": "Student Management System API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "healthy"}

