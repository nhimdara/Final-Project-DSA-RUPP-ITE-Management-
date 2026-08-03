from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.controllers import courses as controller
from app.database import get_db
from app.schemas import CourseCreate, CourseResponse, CourseUpdate

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=list[CourseResponse])
def list_courses(search: str | None = Query(None), db: Session = Depends(get_db)):
    return controller.list_courses(db, search)


@router.get("/{code}", response_model=CourseResponse)
def get_course(code: str, db: Session = Depends(get_db)):
    return controller.get_course(db, code)


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(body: CourseCreate, db: Session = Depends(get_db)):
    return controller.create_course(db, body)


@router.put("/{code}", response_model=CourseResponse)
def update_course(code: str, body: CourseUpdate, db: Session = Depends(get_db)):
    return controller.update_course(db, code, body)


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(code: str, db: Session = Depends(get_db)) -> Response:
    controller.delete_course(db, code)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
