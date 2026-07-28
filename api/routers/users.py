from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import User
from api.schemas import UserCreate, UserRead
from api.security import hash_password, require_roles
from api.services import find_student

router = APIRouter(prefix="/users", tags=["users"])
VALID_ROLES = {"administrator", "teacher", "student", "parent"}


@router.post("", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("administrator")),
) -> User:
    role = payload.role.strip().lower()
    if role not in VALID_ROLES:
        raise HTTPException(422, f"Role must be one of: {', '.join(sorted(VALID_ROLES))}")
    student = (
        find_student(db, payload.linked_student_id)
        if payload.linked_student_id
        else None
    )
    if role in {"student", "parent"} and student is None:
        raise HTTPException(422, "Student and parent accounts require a linked student")
    user = User(
        username=payload.username.strip().lower(),
        password_hash=hash_password(payload.password),
        role=role,
        student=student,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Username already exists")
    db.refresh(user)
    return user

