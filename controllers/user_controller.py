from __future__ import annotations

from typing import Optional

from database.db import SqlValue, execute, fetch_one
from models.user import ROLES, User, hash_password
from services.authentication_service import AuthenticationService


class UserController:
    def __init__(self, service: Optional[AuthenticationService] = None) -> None:
        self.service = service or AuthenticationService()

    def list_users(self) -> list[User]:
        return self.service.list_users()

    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        full_name: str,
        linked_student_id: Optional[str] = None,
    ) -> User:
        return self.service.create_user(username, password, role, full_name, linked_student_id)

    @staticmethod
    def _normalize_linked_student_id(student_id: Optional[str]) -> Optional[str]:
        if student_id is None:
            return None
        return student_id.strip().upper() or None

    def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        role: Optional[str] = None,
        full_name: Optional[str] = None,
        linked_student_id: Optional[str] = None,
        password: Optional[str] = None,
    ) -> User:
        assignments: list[str] = []
        params: list[SqlValue] = []
        if username is not None:
            username = username.strip().lower()
            if not username:
                raise ValueError("Username is required.")
            assignments.append("username = ?")
            params.append(username)
        if role is not None:
            role = role.strip().lower()
            if role not in ROLES:
                raise ValueError(f"Role must be one of: {', '.join(ROLES)}.")
            assignments.append("role = ?")
            params.append(role)
        if full_name is not None:
            full_name = full_name.strip()
            if not full_name:
                raise ValueError("Full name is required.")
            assignments.append("full_name = ?")
            params.append(full_name)
        if linked_student_id is not None:
            assignments.append("linked_student_id = ?")
            params.append(self._normalize_linked_student_id(linked_student_id))
        if password:
            assignments.append("password_hash = ?")
            params.append(hash_password(password))
        if not assignments:
            return self.get_user(user_id)
        params.append(user_id)
        execute(f"UPDATE users SET {', '.join(assignments)} WHERE id = ?", params)
        return self.get_user(user_id)

    def get_user(self, user_id: int) -> User:
        return self.service.get_user(user_id)

    def delete_user(self, user_id: int) -> bool:
        row = fetch_one("SELECT id FROM users WHERE id = ?", (user_id,))
        if row is None:
            return False
        execute("DELETE FROM users WHERE id = ?", (user_id,))
        return True
