"""Import the existing data.py records into the SQL database."""

from sqlalchemy import select

from app.controllers.auth import hash_password
from app.database import SessionLocal
from app.models import Course, Enrollment, Student, User
from data import COURSES, ENROLLMENTS, SCORES, STUDENTS, USERS


def seed() -> None:
    with SessionLocal() as db:
        for item in STUDENTS:
            student_id = item["student_id"].upper()
            if db.get(Student, student_id) is None:
                db.add(Student(student_id=student_id, name=item["name"], year=item["year"]))
        for item in COURSES:
            code = item["code"].upper()
            if db.get(Course, code) is None:
                db.add(Course(code=code, name=item["name"], credits=item["credits"]))
        for item in USERS:
            if db.get(User, item["username"]) is None:
                db.add(User(username=item["username"], password_hash=hash_password(item["password"]),
                            role=item["role"], student_id=item.get("student_id") or None))
        db.flush()
        scores = {(item["student_id"].upper(), item["course_code"].upper()): item["score"]
                  for item in SCORES}
        for item in ENROLLMENTS:
            key = (item["student_id"].upper(), item["course_code"].upper())
            if db.get(Enrollment, key) is None:
                db.add(Enrollment(student_id=key[0], course_code=key[1], score=scores.get(key)))
        db.commit()
        counts = {model.__tablename__: len(list(db.scalars(select(model))))
                  for model in (User, Student, Course, Enrollment)}
        print("Database seeded:", counts)


if __name__ == "__main__":
    seed()
