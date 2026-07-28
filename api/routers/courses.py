from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Course, User
from api.schemas import CourseCreate, CourseRead, CourseUpdate
from api.security import get_current_user, require_roles
from api.services import find_course

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseRead])
def list_courses(
    search: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Course]:
    statement = select(Course)
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(Course.code.ilike(pattern), Course.name.ilike(pattern))
        )
    return list(db.scalars(statement.order_by(Course.code).offset(offset).limit(limit)))


@router.post("", response_model=CourseRead, status_code=201)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("administrator")),
) -> Course:
    course = Course(**payload.model_dump())
    db.add(course)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Course code already exists")
    db.refresh(course)
    return course


@router.get("/{code}", response_model=CourseRead)
def get_course(
    code: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Course:
    return find_course(db, code)


@router.patch("/{code}", response_model=CourseRead)
def update_course(
    code: str,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("administrator")),
) -> Course:
    course = find_course(db, code)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, field, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{code}", status_code=204)
def delete_course(
    code: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("administrator")),
) -> Response:
    db.delete(find_course(db, code))
    db.commit()
    return Response(status_code=204)

