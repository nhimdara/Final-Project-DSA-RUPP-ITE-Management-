from __future__ import annotations

from typing import Optional

from database.queries import execute, execute_insert, fetch_all, fetch_one
from models.user import ROLES, User, hash_password, verify_password


def _normalize_linked_student_id(student_id: Optional[str]) -> Optional[str]:
    if student_id is None:
        return None
    return student_id.strip().upper() or None


class AuthenticationService:
    def authenticate(self, username: str, password: str) -> Optional[User]:
        username = username.strip().lower()
        if not username or not password:
            return None
        row = fetch_one("SELECT * FROM users WHERE LOWER(username) = ?", (username,))
        if row is None:
            return None
        user = User.from_row(row)
        if not verify_password(password, user.password_hash):
            return None
        return user

    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        full_name: str,
        linked_student_id: Optional[str] = None,
    ) -> User:
        username = username.strip().lower()
        role = role.strip().lower()
        full_name = full_name.strip()
        if not username:
            raise ValueError("Username is required.")
        if not password:
            raise ValueError("Password is required.")
        if role not in ROLES:
            raise ValueError(f"Role must be one of: {', '.join(ROLES)}.")
        if not full_name:
            raise ValueError("Full name is required.")
        user_id = execute_insert(
            """
            INSERT INTO users (username, password_hash, role, full_name, linked_student_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                username,
                hash_password(password),
                role,
                full_name,
                _normalize_linked_student_id(linked_student_id),
            ),
        )
        return self.get_user(user_id)

    def get_user(self, user_id: int) -> User:
        row = fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
        if row is None:
            raise ValueError("User not found.")
        return User.from_row(row)

    def list_users(self) -> list[User]:
        rows = fetch_all("SELECT * FROM users ORDER BY role, username")
        return [User.from_row(row) for row in rows]

    def change_password(self, user_id: int, new_password: str) -> None:
        if not new_password:
            raise ValueError("Password is required.")
        execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hash_password(new_password), user_id),
        )
