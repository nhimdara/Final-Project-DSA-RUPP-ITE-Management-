"""FastAPI interface for the Student Management System."""

from __future__ import annotations

from contextlib import asynccontextmanager
from threading import Lock
from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

from data_structures.student_management import StudentManagementSystem


class LoginRequest(BaseModel):
    username: str
    password: str


class StudentCreate(BaseModel):
    student_id: str
    name: str
    year: int = Field(ge=1)


class StudentUpdate(BaseModel):
    name: str
    year: int = Field(ge=1)


class CourseCreate(BaseModel):
    name: str
    credits: int = Field(ge=1)
    code: str | None = None


class CourseUpdate(BaseModel):
    name: str
    credits: int = Field(ge=1)
    new_code: str | None = None


class EnrollmentCreate(BaseModel):
    student_id: str
    course_code: str


class ScoreCreate(EnrollmentCreate):
    score: float = Field(ge=0, le=100)


system: StudentManagementSystem | None = None
write_lock = Lock()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global system
    system = StudentManagementSystem()
    yield


app = FastAPI(
    title="Student Management System API",
    description="REST API backed by the project's hash table, graph, and grade decision tree.",
    version="1.0.0",
    lifespan=lifespan,
)


def get_system() -> StudentManagementSystem:
    """Return the initialized service (also supports direct endpoint unit tests)."""
    global system
    if system is None:
        system = StudentManagementSystem()
    return system


def student_json(student: Any) -> dict[str, Any]:
    return {
        "student_id": student.student_id,
        "name": student.name,
        "department": student.department,
        "year": student.year,
    }


def course_json(course: Any) -> dict[str, Any]:
    return {"code": course.code, "name": course.name, "credits": course.credits}


def run(action):
    """Translate domain validation errors into useful HTTP responses."""
    try:
        return action()
    except ValueError as exc:
        message = str(exc)
        code = status.HTTP_404_NOT_FOUND if "not found" in message.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=message) from exc


@app.get("/", tags=["System"])
def root():
    return {"name": app.title, "docs": "/docs", "health": "/health"}


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}


@app.post("/login", tags=["Authentication"])
def login(body: LoginRequest):
    user = get_system().authenticate(body.username, body.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
    return {"username": user.username, "role": user.role, "student_id": user.student_id}


@app.get("/students", tags=["Students"])
def list_students(search: str | None = Query(default=None)):
    service = get_system()
    students = service.search_students(search) if search is not None else service.display_students()
    return [student_json(item) for item in students]


@app.get("/students/{student_id}", tags=["Students"])
def get_student(student_id: str):
    student = get_system().search_student_by_id(student_id.strip().upper())
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' was not found.")
    return student_json(student)


@app.post("/students", status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(body: StudentCreate):
    with write_lock:
        run(lambda: get_system().insert_student(body.student_id, body.name, body.year))
    return get_student(body.student_id)


@app.put("/students/{student_id}", tags=["Students"])
def update_student(student_id: str, body: StudentUpdate):
    with write_lock:
        run(lambda: get_system().update_student(student_id, body.name, body.year))
    return get_student(student_id)


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Students"])
def delete_student(student_id: str):
    with write_lock:
        deleted = get_system().delete_student(student_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' was not found.")


@app.get("/courses", tags=["Courses"])
def list_courses(search: str | None = Query(default=None)):
    service = get_system()
    courses = service.search_courses(search) if search is not None else service.display_courses()
    return [course_json(item) for item in courses]


@app.get("/courses/{course_code}", tags=["Courses"])
def get_course(course_code: str):
    matches = [item for item in get_system().display_courses() if item.code == course_code.strip().upper()]
    if not matches:
        raise HTTPException(status_code=404, detail=f"Course '{course_code}' was not found.")
    return course_json(matches[0])


@app.post("/courses", status_code=status.HTTP_201_CREATED, tags=["Courses"])
def create_course(body: CourseCreate):
    with write_lock:
        if body.code:
            run(lambda: get_system().insert_course(body.code, body.name, body.credits))
            code = body.code
        else:
            code = run(lambda: get_system().insert_course_automatically(body.name, body.credits))
    return get_course(code)


@app.put("/courses/{course_code}", tags=["Courses"])
def update_course(course_code: str, body: CourseUpdate):
    with write_lock:
        run(lambda: get_system().update_course(course_code, body.name, body.credits, body.new_code))
    return get_course(body.new_code or course_code)


@app.delete("/courses/{course_code}", status_code=status.HTTP_204_NO_CONTENT, tags=["Courses"])
def delete_course(course_code: str):
    with write_lock:
        deleted = get_system().delete_course(course_code)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Course '{course_code}' was not found.")


@app.post("/enrollments", status_code=status.HTTP_201_CREATED, tags=["Academics"])
def enroll(body: EnrollmentCreate):
    with write_lock:
        run(lambda: get_system().enroll(body.student_id, body.course_code))
    return {"student_id": body.student_id.upper(), "course_code": body.course_code.upper(), "enrolled": True}


@app.put("/scores", tags=["Academics"])
def record_score(body: ScoreCreate):
    with write_lock:
        run(lambda: get_system().record_score(body.student_id, body.course_code, body.score))
    result = get_system().grade_tree.calculate(body.score)
    return {"student_id": body.student_id.upper(), "course_code": body.course_code.upper(), "score": body.score, "grade": result.grade, "gpa": result.gpa}


@app.get("/students/{student_id}/courses", tags=["Academics"])
def student_courses(student_id: str):
    courses = run(lambda: get_system().student_courses(student_id))
    return [course_json(item) for item in courses]


@app.get("/courses/{course_code}/students", tags=["Academics"])
def course_students(course_code: str):
    students = run(lambda: get_system().course_students(course_code))
    return [student_json(item) for item in students]


@app.get("/students/{student_id}/report", tags=["Academics"])
def student_report(student_id: str):
    return {"report": run(lambda: get_system().student_report(student_id))}


@app.get("/students/{student_id}/gpa", tags=["Academics"])
def student_gpa(student_id: str):
    return {"report": run(lambda: get_system().student_gpa_report(student_id))}


@app.get("/enrollment-graph", tags=["Academics"])
def enrollment_graph():
    return get_system().display_relationships()


@app.get("/grade-tree", tags=["Academics"])
def grade_tree():
    return {"tree": get_system().grade_tree.display()}
