from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Student
from app.schemas import StudentCreate, StudentUpdate


def list_students(db: Session, search: str | None = None) -> list[Student]:
    query = select(Student).order_by(Student.student_id)
    if search:
        term = f"%{search.strip()}%"
        query = query.where(or_(Student.student_id.ilike(term), Student.name.ilike(term)))
    return list(db.scalars(query))


def get_student(db: Session, student_id: str) -> Student:
    student = db.get(Student, student_id.strip().upper())
    if student is None:
        raise HTTPException(404, "Student not found.")
    return student


def create_student(db: Session, body: StudentCreate) -> Student:
    student_id = body.student_id.strip().upper()
    if db.get(Student, student_id):
        raise HTTPException(409, "Student ID already exists.")
    student = Student(student_id=student_id, name=body.name.strip(), year=body.year)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(db: Session, student_id: str, body: StudentUpdate) -> Student:
    student = get_student(db, student_id)
    student.name, student.year = body.name.strip(), body.year
    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student_id: str) -> None:
    db.delete(get_student(db, student_id))
    db.commit()
