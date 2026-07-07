from __future__ import annotations

from database.db import execute, fetch_all, fetch_one
from models.teacher import Teacher


TEACHER_SELECT = """
SELECT
    t.id,
    t.name,
    t.email,
    t.phone,
    t.department_id,
    COALESCE(d.name, '') AS department_name,
    t.user_id
FROM teachers t
LEFT JOIN departments d ON d.id = t.department_id
"""


class TeacherController:
    def add_teacher(
        self,
        name: str,
        email: str = "",
        phone: str = "",
        department_id: int | None = None,
        user_id: int | None = None,
    ) -> Teacher:
        if not name.strip():
            raise ValueError("Teacher name is required.")
        teacher_id = execute(
            """
            INSERT INTO teachers (name, email, phone, department_id, user_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name.strip(), email.strip() or None, phone.strip(), department_id, user_id),
        )
        return self.get_teacher(teacher_id)

    def get_teacher(self, teacher_id: int) -> Teacher:
        row = fetch_one(f"{TEACHER_SELECT} WHERE t.id = ?", (teacher_id,))
        if row is None:
            raise ValueError("Teacher not found.")
        return Teacher.from_row(row)

    def list_teachers(self) -> list[Teacher]:
        rows = fetch_all(f"{TEACHER_SELECT} ORDER BY t.name")
        return [Teacher.from_row(row) for row in rows]

    def update_teacher(
        self,
        teacher_id: int,
        name: str,
        email: str = "",
        phone: str = "",
        department_id: int | None = None,
        user_id: int | None = None,
    ) -> Teacher:
        if not name.strip():
            raise ValueError("Teacher name is required.")
        execute(
            """
            UPDATE teachers
            SET name = ?, email = ?, phone = ?, department_id = ?, user_id = ?
            WHERE id = ?
            """,
            (name.strip(), email.strip() or None, phone.strip(), department_id, user_id, teacher_id),
        )
        return self.get_teacher(teacher_id)

    def delete_teacher(self, teacher_id: int) -> bool:
        row = fetch_one("SELECT id FROM teachers WHERE id = ?", (teacher_id,))
        if row is None:
            return False
        execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
        return True
