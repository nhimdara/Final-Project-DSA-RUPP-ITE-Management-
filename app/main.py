from fastapi import FastAPI

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


@app.get("/", tags=["System"])
def root():
    return {"name": app.title, "version": app.version, "docs": "/docs"}


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}
