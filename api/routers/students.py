from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Student, User
from api.schemas import StudentCreate, StudentRead, StudentReport, StudentUpdate
from api.security import get_current_user, require_roles
from api.services import build_report, find_student

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[StudentRead])
def list_students(
    search: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("administrator", "teacher")),
) -> list[Student]:
    statement = select(Student)
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(Student.student_id.ilike(pattern), Student.name.ilike(pattern))
        )
    return list(
        db.scalars(statement.order_by(Student.student_id).offset(offset).limit(limit))
    )


@router.post("", response_model=StudentRead, status_code=201)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("administrator")),
) -> Student:
    student = Student(**payload.model_dump())
    db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Student ID already exists")
    db.refresh(student)
    return student


@router.get("/{student_id}", response_model=StudentRead)
def get_student(
    student_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Student:
    student = find_student(db, student_id)
    if user.role in {"student", "parent"} and user.student_id != student.id:
        raise HTTPException(403, "You may only access your linked student")
    return student


@router.patch("/{student_id}", response_model=StudentRead)
def update_student(
    student_id: str,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("administrator")),
) -> Student:
    student = find_student(db, student_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(student, field, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=204)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("administrator")),
) -> Response:
    student = find_student(db, student_id)
    linked = db.scalar(
        select(func.count()).select_from(User).where(User.student_id == student.id)
    )
    if linked:
        raise HTTPException(409, "Student is linked to a user account")
    db.delete(student)
    db.commit()
    return Response(status_code=204)


@router.get("/{student_id}/report", response_model=StudentReport)
def report(
    student_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StudentReport:
    student = find_student(db, student_id)
    if user.role in {"student", "parent"} and user.student_id != student.id:
        raise HTTPException(403, "You may only access your linked student")
    return build_report(db, student_id)

