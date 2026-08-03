from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.controllers import students as controller
from app.controllers.auth import allow_roles, current_user, require_student_access
from app.database import get_db
from app.models import User
from app.schemas import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("", response_model=list[StudentResponse])
def list_students(search: str | None = Query(None), db: Session = Depends(get_db),
                  _user: User = Depends(allow_roles("administrator", "teacher"))):
    return controller.list_students(db, search)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    require_student_access(student_id, user)
    return controller.get_student(db, student_id)


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(body: StudentCreate, db: Session = Depends(get_db),
                   _user: User = Depends(allow_roles("administrator"))):
    return controller.create_student(db, body)


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: str, body: StudentUpdate, db: Session = Depends(get_db),
                   _user: User = Depends(allow_roles("administrator"))):
    return controller.update_student(db, student_id, body)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: str, db: Session = Depends(get_db),
                   _user: User = Depends(allow_roles("administrator"))) -> Response:
    controller.delete_student(db, student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
