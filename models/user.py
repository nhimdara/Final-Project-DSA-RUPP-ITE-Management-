from __future__ import annotations

from dataclasses import dataclass
from hashlib import pbkdf2_hmac, sha256
from hmac import compare_digest
from secrets import token_hex
from typing import Optional

from models.row_mapping import RowMapping, row_to_dict


PASSWORD_SALT = "rupp-ite-student-management"
PASSWORD_ALGORITHM = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 260_000
ROLES = ("admin", "teacher", "student", "parent")


def _legacy_hash_password(password: str) -> str:
    return sha256(f"{PASSWORD_SALT}:{password}".encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    salt = token_hex(16)
    digest = pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"{PASSWORD_ALGORITHM}${PASSWORD_ITERATIONS}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith(f"{PASSWORD_ALGORITHM}$"):
        try:
            algorithm, iterations, salt, expected_digest = password_hash.split("$", 3)
            if algorithm != PASSWORD_ALGORITHM:
                return False
            actual_digest = pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                int(iterations),
            ).hex()
        except (TypeError, ValueError):
            return False
        return compare_digest(actual_digest, expected_digest)
    return compare_digest(_legacy_hash_password(password), password_hash)


@dataclass(slots=True)
class User:
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    role: str = "student"
    full_name: str = ""
    linked_student_id: Optional[str] = None
    created_at: str = ""

    @classmethod
    def from_row(cls, row: RowMapping) -> "User":
        data = row_to_dict(row)
        return cls(
            id=data.get("id"),
            username=data.get("username", ""),
            password_hash=data.get("password_hash", ""),
            role=data.get("role", "student"),
            full_name=data.get("full_name", ""),
            linked_student_id=data.get("linked_student_id"),
            created_at=data.get("created_at", ""),
        )

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_teacher(self) -> bool:
        return self.role == "teacher"

    @property
    def is_student(self) -> bool:
        return self.role == "student"

    @property
    def is_parent(self) -> bool:
        return self.role == "parent"

    def public_dict(self) -> dict[str, str | int | None]:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "full_name": self.full_name,
            "linked_student_id": self.linked_student_id,
            "created_at": self.created_at,
        }
