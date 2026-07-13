from __future__ import annotations

from database.queries import execute, fetch_all, fetch_one
from data_structures.hash_table import HashTable
from models.student import Student


STUDENT_SELECT = """
SELECT
    s.id,
    s.name,
    s.gender,
    s.date_of_birth,
    s.email,
    s.phone,
    s.address,
    s.department_id,
    COALESCE(d.name, '') AS department_name,
    s.year,
    s.parent_name,
    s.parent_phone
FROM students s
LEFT JOIN departments d ON d.id = s.department_id
"""


class StudentController:
    def __init__(self) -> None:
        self._student_table: HashTable[str, Student] = HashTable()
        self.refresh_cache()

    def refresh_cache(self) -> None:
        students = [Student.from_row(row) for row in fetch_all(f"{STUDENT_SELECT} ORDER BY s.id")]
        self._student_table = HashTable.from_items(students, key=lambda student: student.id)

    @staticmethod
    def _normalize_department_id(department_id: int | None) -> int | None:
        if department_id is None:
            return None
        if department_id <= 0:
            return None
        return department_id

    @staticmethod
    def _validate_year(year: int) -> None:
        if year < 1:
            raise ValueError("Year must be greater than zero.")

    def add_student(self, student: Student) -> Student:
        student_id = student.id.strip().upper()
        if not student_id or not student.name.strip():
            raise ValueError("Student ID and name are required.")
        self._validate_year(student.year)
        if self._student_table.contains(student_id):
            raise ValueError("Duplicate student ID found.")
        execute(
            """
            INSERT INTO students
                (id, name, gender, date_of_birth, email, phone, address,
                 department_id, year, parent_name, parent_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student_id,
                student.name.strip(),
                student.gender.strip(),
                student.date_of_birth.strip(),
                student.email.strip(),
                student.phone.strip(),
                student.address.strip(),
                self._normalize_department_id(student.department_id),
                student.year,
                student.parent_name.strip(),
                student.parent_phone.strip(),
            ),
        )
        self.refresh_cache()
        return self.get_student(student_id)

    def get_student(self, student_id: str) -> Student:
        student_id = student_id.strip().upper()
        cached = self._student_table.get(student_id)
        if cached is not None:
            return cached
        row = fetch_one(f"{STUDENT_SELECT} WHERE s.id = ?", (student_id,))
        if row is None:
            raise ValueError("Student not found.")
        student = Student.from_row(row)
        self._student_table.insert(student.id, student)
        return student

    def list_students(self) -> list[Student]:
        return sorted(self._student_table.values(), key=lambda student: student.id)

    def search_students(self, keyword: str) -> list[Student]:
        keyword = keyword.strip().lower()
        if not keyword:
            return self.list_students()
        return [student for student in self.list_students() if keyword in student.searchable_text()]

    def update_student(self, student: Student) -> Student:
        student_id = student.id.strip().upper()
        if not student_id or not student.name.strip():
            raise ValueError("Student ID and name are required.")
        self._validate_year(student.year)
        execute(
            """
            UPDATE students
            SET name = ?,
                gender = ?,
                date_of_birth = ?,
                email = ?,
                phone = ?,
                address = ?,
                department_id = ?,
                year = ?,
                parent_name = ?,
                parent_phone = ?
            WHERE id = ?
            """,
            (
                student.name.strip(),
                student.gender.strip(),
                student.date_of_birth.strip(),
                student.email.strip(),
                student.phone.strip(),
                student.address.strip(),
                self._normalize_department_id(student.department_id),
                student.year,
                student.parent_name.strip(),
                student.parent_phone.strip(),
                student_id,
            ),
        )
        self.refresh_cache()
        return self.get_student(student_id)

    def delete_student(self, student_id: str) -> bool:
        student_id = student_id.strip().upper()
        if not self._student_table.contains(student_id):
            return False
        execute("DELETE FROM students WHERE id = ?", (student_id,))
        self._student_table.delete(student_id)
        return True
