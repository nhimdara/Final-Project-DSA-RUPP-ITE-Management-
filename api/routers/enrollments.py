from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Enrollment, User
from api.schemas import EnrollmentCreate, EnrollmentRead, ScoreUpdate
from api.security import require_roles
from api.services import find_course, find_student, grade_for

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


def enrollment_view(enrollment: Enrollment) -> EnrollmentRead:
    grade, point = grade_for(enrollment.score)
    return EnrollmentRead(
        id=enrollment.id,
        student_id=enrollment.student.student_id,
        course_code=enrollment.course.code,
        course_name=enrollment.course.name,
        credits=enrollment.course.credits,
        score=enrollment.score,
        grade=grade,
        grade_point=point,
    )


@router.post("", response_model=EnrollmentRead, status_code=201)
def enroll(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("administrator", "teacher")),
) -> EnrollmentRead:
    student = find_student(db, payload.student_id)
    course = find_course(db, payload.course_code)
    enrollment = Enrollment(student=student, course=course)
    db.add(enrollment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Student is already enrolled in this course")
    db.refresh(enrollment)
    return enrollment_view(enrollment)


@router.put("/{enrollment_id}/score", response_model=EnrollmentRead)
def record_score(
    enrollment_id: int,
    payload: ScoreUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("administrator", "teacher")),
) -> EnrollmentRead:
    enrollment = db.get(Enrollment, enrollment_id)
    if enrollment is None:
        raise HTTPException(404, "Enrollment not found")
    enrollment.score = payload.score
    db.commit()
    db.refresh(enrollment)
    return enrollment_view(enrollment)


@router.delete("/{enrollment_id}", status_code=204)
def unenroll(
    enrollment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("administrator", "teacher")),
) -> Response:
    enrollment = db.get(Enrollment, enrollment_id)
    if enrollment is None:
        raise HTTPException(404, "Enrollment not found")
    db.delete(enrollment)
    db.commit()
    return Response(status_code=204)
