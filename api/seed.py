from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.models import Course, Enrollment, Student, User
from api.security import hash_password
from data import COURSES, ENROLLMENTS, SCORES, STUDENTS, USERS


def seed_database(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(User)):
        return

    students = {
        item["student_id"]: Student(
            student_id=item["student_id"],
            name=item["name"],
            year=item["year"],
        )
        for item in STUDENTS
    }
    courses = {
        item["code"]: Course(
            code=item["code"], name=item["name"], credits=item["credits"]
        )
        for item in COURSES
    }
    db.add_all([*students.values(), *courses.values()])
    db.flush()

    score_map = {
        (item["student_id"], item["course_code"]): item["score"] for item in SCORES
    }
    db.add_all(
        Enrollment(
            student=students[item["student_id"]],
            course=courses[item["course_code"]],
            score=score_map.get((item["student_id"], item["course_code"])),
        )
        for item in ENROLLMENTS
    )
    db.add_all(
        User(
            username=item["username"].lower(),
            password_hash=hash_password(item["password"]),
            role=item["role"],
            student=students.get(item.get("student_id", "")),
        )
        for item in USERS
    )
    db.commit()

