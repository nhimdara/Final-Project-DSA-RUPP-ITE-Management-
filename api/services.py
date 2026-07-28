from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from api.models import Course, Enrollment, Student
from api.schemas import EnrollmentRead, StudentReport


def grade_for(score: float | None) -> tuple[str | None, float | None]:
    if score is None:
        return None, None
    if score >= 90:
        return "A", 4.0
    if score >= 80:
        return "B", 3.0
    if score >= 70:
        return "C", 2.0
    if score >= 60:
        return "D", 1.0
    return "F", 0.0


def find_student(db: Session, student_id: str) -> Student:
    student = db.scalar(
        select(Student).where(Student.student_id == student_id.strip().upper())
    )
    if student is None:
        raise HTTPException(404, "Student not found")
    return student


def find_course(db: Session, code: str) -> Course:
    course = db.scalar(select(Course).where(Course.code == code.strip().upper()))
    if course is None:
        raise HTTPException(404, "Course not found")
    return course


def build_report(db: Session, student_id: str) -> StudentReport:
    student = db.scalar(
        select(Student)
        .options(selectinload(Student.enrollments).selectinload(Enrollment.course))
        .where(Student.student_id == student_id.strip().upper())
    )
    if student is None:
        raise HTTPException(404, "Student not found")

    rows: list[EnrollmentRead] = []
    weighted_points = 0.0
    graded_credits = 0
    for enrollment in sorted(student.enrollments, key=lambda item: item.course.code):
        grade, point = grade_for(enrollment.score)
        rows.append(
            EnrollmentRead(
                id=enrollment.id,
                student_id=student.student_id,
                course_code=enrollment.course.code,
                course_name=enrollment.course.name,
                credits=enrollment.course.credits,
                score=enrollment.score,
                grade=grade,
                grade_point=point,
            )
        )
        if point is not None:
            weighted_points += point * enrollment.course.credits
            graded_credits += enrollment.course.credits
    gpa = round(weighted_points / graded_credits, 2) if graded_credits else None
    return StudentReport(student=student, enrollments=rows, gpa=gpa)

