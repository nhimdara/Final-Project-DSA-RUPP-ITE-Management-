from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Course
from app.schemas import CourseCreate, CourseUpdate


def list_courses(db: Session, search: str | None = None) -> list[Course]:
    query = select(Course).order_by(Course.code)
    if search:
        term = f"%{search.strip()}%"
        query = query.where(or_(Course.code.ilike(term), Course.name.ilike(term)))
    return list(db.scalars(query))


def get_course(db: Session, code: str) -> Course:
    course = db.get(Course, code.strip().upper())
    if course is None:
        raise HTTPException(404, "Course not found.")
    return course


def create_course(db: Session, body: CourseCreate) -> Course:
    code = body.code.strip().upper()
    if db.get(Course, code):
        raise HTTPException(409, "Course code already exists.")
    course = Course(code=code, name=body.name.strip(), credits=body.credits)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, code: str, body: CourseUpdate) -> Course:
    course = get_course(db, code)
    course.name, course.credits = body.name.strip(), body.credits
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, code: str) -> None:
    db.delete(get_course(db, code))
    db.commit()
