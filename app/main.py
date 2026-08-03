from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes import auth, courses, enrollments, students

app = FastAPI(
    title="Student Management System API",
    description="Database-backed API with separated routes, controllers, schemas, and models.",
    version="2.0.0",
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(students.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(enrollments.router, prefix="/api/v1")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(static_dir / "index.html")


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}
