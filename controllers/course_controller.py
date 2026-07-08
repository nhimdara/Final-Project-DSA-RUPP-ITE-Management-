from __future__ import annotations

from database.db import execute, execute_insert, fetch_all, fetch_one
from models.course import Course


COURSE_SELECT = """
SELECT
    c.id,
    c.code,
    c.name,
    c.department_id,
    COALESCE(d.name, '') AS department_name,
    c.teacher_id,
    COALESCE(t.name, '') AS teacher_name,
    c.credits
FROM courses c
LEFT JOIN departments d ON d.id = c.department_id
LEFT JOIN teachers t ON t.id = c.teacher_id
"""


class CourseController:
    @staticmethod
    def _normalize_optional_id(value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            return None
        return value

    @staticmethod
    def _validate_positive(value: int, label: str) -> None:
        if value <= 0:
            raise ValueError(f"{label} must be greater than zero.")

    def add_course(
        self,
        code: str,
        name: str,
        department_id: int,
        teacher_id: int | None = None,
        credits: int = 3,
    ) -> Course:
        code = code.strip().upper()
        name = name.strip()
        if not code or not name:
            raise ValueError("Course code and name are required.")
        self._validate_positive(department_id, "Department ID")
        self._validate_positive(credits, "Credits")
        teacher_id = self._normalize_optional_id(teacher_id)
        course_id = execute_insert(
            """
            INSERT INTO courses (code, name, department_id, teacher_id, credits)
            VALUES (?, ?, ?, ?, ?)
            """,
            (code, name, department_id, teacher_id, credits),
        )
        return self.get_course(course_id)

    def get_course(self, course_id: int) -> Course:
        row = fetch_one(f"{COURSE_SELECT} WHERE c.id = ?", (course_id,))
        if row is None:
            raise ValueError("Course not found.")
        return Course.from_row(row)

    def list_courses(self) -> list[Course]:
        rows = fetch_all(f"{COURSE_SELECT} ORDER BY d.name, c.code")
        return [Course.from_row(row) for row in rows]

    def courses_for_department(self, department_id: int) -> list[Course]:
        rows = fetch_all(
            f"{COURSE_SELECT} WHERE c.department_id = ? ORDER BY c.code",
            (department_id,),
        )
        return [Course.from_row(row) for row in rows]

    def courses_for_student(self, student_id: str) -> list[Course]:
        rows = fetch_all(
            f"""
            {COURSE_SELECT}
            WHERE c.department_id = (
                SELECT department_id FROM students WHERE id = ?
            )
            ORDER BY c.code
            """,
            (student_id,),
        )
        return [Course.from_row(row) for row in rows]

    def search_courses(self, keyword: str) -> list[Course]:
        keyword = keyword.strip()
        if not keyword:
            return self.list_courses()
        like_keyword = f"%{keyword}%"
        rows = fetch_all(
            f"""
            {COURSE_SELECT}
            WHERE c.code LIKE ? OR c.name LIKE ? OR d.name LIKE ?
            ORDER BY c.code
            """,
            (like_keyword, like_keyword, like_keyword),
        )
        return [Course.from_row(row) for row in rows]

    def update_course(
        self,
        course_id: int,
        code: str,
        name: str,
        department_id: int,
        teacher_id: int | None = None,
        credits: int = 3,
    ) -> Course:
        code = code.strip().upper()
        name = name.strip()
        if not code or not name:
            raise ValueError("Course code and name are required.")
        self._validate_positive(department_id, "Department ID")
        self._validate_positive(credits, "Credits")
        teacher_id = self._normalize_optional_id(teacher_id)
        execute(
            """
            UPDATE courses
            SET code = ?, name = ?, department_id = ?, teacher_id = ?, credits = ?
            WHERE id = ?
            """,
            (code, name, department_id, teacher_id, credits, course_id),
        )
        return self.get_course(course_id)

    def delete_course(self, course_id: int) -> bool:
        row = fetch_one("SELECT id FROM courses WHERE id = ?", (course_id,))
        if row is None:
            return False
        execute("DELETE FROM courses WHERE id = ?", (course_id,))
        return True
