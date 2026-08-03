from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers import enrollments as controller
from app.controllers.grades import grade_for
from app.database import get_db
from app.schemas import EnrollmentCreate, EnrollmentResponse, ScoreUpdate

router = APIRouter(tags=["Academics"])


def enrollment_response(item) -> EnrollmentResponse:
    grade = gpa = None
    if item.score is not None:
        grade, gpa = grade_for(item.score)
    return EnrollmentResponse(student_id=item.student_id, course_code=item.course_code,
                              score=item.score, grade=grade, gpa=gpa)


@router.post("/enrollments", response_model=EnrollmentResponse,
             status_code=status.HTTP_201_CREATED)
def enroll(body: EnrollmentCreate, db: Session = Depends(get_db)):
    return enrollment_response(controller.create_enrollment(db, body))


@router.put("/enrollments/{student_id}/{course_code}/score",
            response_model=EnrollmentResponse)
def record_score(student_id: str, course_code: str, body: ScoreUpdate,
                 db: Session = Depends(get_db)):
    return enrollment_response(controller.set_score(db, student_id, course_code, body.score))


@router.delete("/enrollments/{student_id}/{course_code}",
               status_code=status.HTTP_204_NO_CONTENT)
def unenroll(student_id: str, course_code: str, db: Session = Depends(get_db)) -> Response:
    item = controller.get_enrollment(db, student_id, course_code)
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/students/{student_id}/report")
def report(student_id: str, db: Session = Depends(get_db)):
    return controller.student_report(db, student_id)
