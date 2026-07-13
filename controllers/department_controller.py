from __future__ import annotations

from database.queries import execute, execute_insert, fetch_all, fetch_one
from models.department import Department


class DepartmentController:
    def add_department(self, name: str, description: str = "") -> Department:
        name = name.strip()
        if not name:
            raise ValueError("Department name is required.")
        dept_id = execute_insert(
            "INSERT INTO departments (name, description) VALUES (?, ?)",
            (name, description.strip()),
        )
        return self.get_department(dept_id)

    def get_department(self, department_id: int) -> Department:
        row = fetch_one("SELECT * FROM departments WHERE id = ?", (department_id,))
        if row is None:
            raise ValueError("Department not found.")
        return Department.from_row(row)

    def list_departments(self) -> list[Department]:
        rows = fetch_all("SELECT * FROM departments ORDER BY name")
        return [Department.from_row(row) for row in rows]

    def search_departments(self, keyword: str) -> list[Department]:
        keyword = keyword.strip()
        if not keyword:
            return self.list_departments()
        like_keyword = f"%{keyword}%"
        rows = fetch_all(
            """
            SELECT * FROM departments
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY name
            """,
            (like_keyword, like_keyword),
        )
        return [Department.from_row(row) for row in rows]

    def update_department(self, department_id: int, name: str, description: str = "") -> Department:
        name = name.strip()
        if not name:
            raise ValueError("Department name is required.")
        execute(
            "UPDATE departments SET name = ?, description = ? WHERE id = ?",
            (name, description.strip(), department_id),
        )
        return self.get_department(department_id)

    def delete_department(self, department_id: int) -> bool:
        row = fetch_one("SELECT id FROM departments WHERE id = ?", (department_id,))
        if row is None:
            return False
        execute("DELETE FROM departments WHERE id = ?", (department_id,))
        return True
