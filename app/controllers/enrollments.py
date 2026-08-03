from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.controllers.courses import get_course
from app.controllers.grades import grade_for
from app.controllers.students import get_student
from app.models import Enrollment
from app.schemas import EnrollmentCreate


def get_enrollment(db: Session, student_id: str, course_code: str) -> Enrollment:
    key = (student_id.strip().upper(), course_code.strip().upper())
    enrollment = db.get(Enrollment, key)
    if enrollment is None:
        raise HTTPException(404, "Enrollment not found.")
    return enrollment


def create_enrollment(db: Session, body: EnrollmentCreate) -> Enrollment:
    student_id, course_code = body.student_id.strip().upper(), body.course_code.strip().upper()
    get_student(db, student_id)
    get_course(db, course_code)
    if db.get(Enrollment, (student_id, course_code)):
        raise HTTPException(409, "Student is already enrolled in this course.")
    enrollment = Enrollment(student_id=student_id, course_code=course_code)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def set_score(db: Session, student_id: str, course_code: str, score: float) -> Enrollment:
    enrollment = get_enrollment(db, student_id, course_code)
    enrollment.score = score
    db.commit()
    db.refresh(enrollment)
    return enrollment


def student_report(db: Session, student_id: str) -> dict:
    student = get_student(db, student_id)
    query = (
        select(Enrollment)
        .options(joinedload(Enrollment.course))
        .where(Enrollment.student_id == student.student_id)
        .order_by(Enrollment.course_code)
    )
    enrollments = list(db.scalars(query))
    total_points = total_credits = 0.0
    courses = []
    for item in enrollments:
        grade = gpa = None
        if item.score is not None:
            grade, gpa = grade_for(item.score)
            total_points += gpa * item.course.credits
            total_credits += item.course.credits
        courses.append({"code": item.course.code, "name": item.course.name,
                        "credits": item.course.credits, "score": item.score,
                        "grade": grade, "gpa": gpa})
    return {"student": {"student_id": student.student_id, "name": student.name,
                         "department": student.department, "year": student.year},
            "courses": courses,
            "overall_gpa": round(total_points / total_credits, 2) if total_credits else None}
