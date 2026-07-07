from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, Optional, TypeAlias

from models.user import hash_password


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "student_management.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"
SqlValue: TypeAlias = str | int | float | bytes | bool | None
SqlParams: TypeAlias = Iterable[SqlValue]


def open_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    conn = open_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database(seed: bool = True) -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        if DB_PATH.exists() and _database_needs_rebuild():
            _backup_database("legacy")
        _create_schema(seed=seed)
    except sqlite3.DatabaseError as exc:
        if "file is not a database" not in str(exc).lower():
            raise
        _backup_database("invalid")
        _create_schema(seed=seed)


def _backup_database(reason: str) -> None:
    backup_path = DB_PATH.with_name(f"{DB_PATH.stem}.{reason}-{datetime.now():%Y%m%d%H%M%S}.bak")
    DB_PATH.replace(backup_path)


def _database_needs_rebuild() -> bool:
    conn: sqlite3.Connection | None = None
    try:
        conn = open_connection()
        tables = {
            row["name"]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        }
        if "students" in tables:
            columns = {row["name"]: row for row in conn.execute("PRAGMA table_info(students)").fetchall()}
            student_id = columns.get("id")
            student_id_type = str(student_id["type"] if student_id is not None else "").upper()
            if student_id_type and student_id_type != "TEXT":
                return True
        if "courses" in tables:
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(courses)").fetchall()}
            if "code" not in columns:
                return True
        if "teachers" in tables:
            columns = {row["name"]: row for row in conn.execute("PRAGMA table_info(teachers)").fetchall()}
            legacy_department = columns.get("department")
            if legacy_department is not None and legacy_department["notnull"]:
                return True
    except sqlite3.DatabaseError:
        return False
    finally:
        if conn is not None:
            conn.close()
    return False


def _create_schema(seed: bool) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with connection() as conn:
        conn.executescript(schema)
        _migrate_existing_schema(conn)
        if seed:
            seed_sample_data(conn)


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}


def _ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
    if column_name not in _table_columns(conn, table_name):
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def _migrate_existing_schema(conn: sqlite3.Connection) -> None:
    migrations = {
        "users": {
            "linked_student_id": "TEXT",
            "created_at": "TEXT DEFAULT ''",
        },
        "teachers": {
            "email": "TEXT",
            "phone": "TEXT DEFAULT ''",
            "department_id": "INTEGER",
            "user_id": "INTEGER",
        },
        "courses": {
            "department_id": "INTEGER",
            "teacher_id": "INTEGER",
            "credits": "INTEGER NOT NULL DEFAULT 3",
        },
        "students": {
            "gender": "TEXT DEFAULT ''",
            "date_of_birth": "TEXT DEFAULT ''",
            "email": "TEXT DEFAULT ''",
            "phone": "TEXT DEFAULT ''",
            "address": "TEXT DEFAULT ''",
            "department_id": "INTEGER",
            "year": "INTEGER NOT NULL DEFAULT 1",
            "parent_name": "TEXT DEFAULT ''",
            "parent_phone": "TEXT DEFAULT ''",
        },
        "scores": {
            "semester": "TEXT NOT NULL DEFAULT 'Semester 1'",
            "academic_year": "TEXT NOT NULL DEFAULT '2026'",
            "recorded_by": "INTEGER",
            "recorded_at": "TEXT DEFAULT ''",
        },
        "report_history": {
            "generated_by": "INTEGER",
            "generated_at": "TEXT DEFAULT ''",
            "file_path": "TEXT DEFAULT ''",
        },
    }
    for table_name, columns in migrations.items():
        existing_tables = {
            row["name"]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        }
        if table_name not in existing_tables:
            continue
        for column_name, definition in columns.items():
            _ensure_column(conn, table_name, column_name, definition)


def fetch_one(sql: str, params: SqlParams = ()) -> Optional[sqlite3.Row]:
    with connection() as conn:
        return conn.execute(sql, tuple(params)).fetchone()


def fetch_all(sql: str, params: SqlParams = ()) -> list[sqlite3.Row]:
    with connection() as conn:
        return conn.execute(sql, tuple(params)).fetchall()


def _last_insert_id(cursor: sqlite3.Cursor) -> int:
    lastrowid = cursor.lastrowid
    if lastrowid is None:
        raise RuntimeError("SQLite did not return a row id for the insert.")
    return int(lastrowid)


def execute(sql: str, params: SqlParams = ()) -> int:
    with connection() as conn:
        cursor = conn.execute(sql, tuple(params))
        return _last_insert_id(cursor)


def execute_many(sql: str, rows: Iterable[SqlParams]) -> None:
    with connection() as conn:
        conn.executemany(sql, [tuple(row) for row in rows])


def seed_sample_data(conn: sqlite3.Connection) -> None:
    user_count_row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
    user_count = int(user_count_row[0]) if user_count_row is not None else 0
    if user_count:
        return

    departments = [
        ("IT Department", "Information Technology program"),
        ("CS Department", "Computer Science program"),
        ("BBA Department", "Business Administration program"),
    ]
    conn.executemany("INSERT INTO departments (name, description) VALUES (?, ?)", departments)

    dept_ids = {
        row["name"]: row["id"]
        for row in conn.execute("SELECT id, name FROM departments").fetchall()
    }

    admin_cursor = conn.execute(
        """
        INSERT INTO users (username, password_hash, role, full_name)
        VALUES (?, ?, ?, ?)
        """,
        ("admin", hash_password("admin123"), "admin", "System Administrator"),
    )
    admin_id = _last_insert_id(admin_cursor)

    teacher_user_cursor = conn.execute(
        """
        INSERT INTO users (username, password_hash, role, full_name)
        VALUES (?, ?, ?, ?)
        """,
        ("teacher", hash_password("teacher123"), "teacher", "Demo Teacher"),
    )
    teacher_user_id = _last_insert_id(teacher_user_cursor)

    teacher_cursor = conn.execute(
        """
        INSERT INTO teachers (name, email, phone, department_id, user_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("Demo Teacher", "teacher@example.com", "012345678", dept_ids["IT Department"], teacher_user_id),
    )
    teacher_id = _last_insert_id(teacher_cursor)

    courses = [
        ("IT101", "Python Programming", dept_ids["IT Department"], teacher_id, 3),
        ("IT202", "Database Systems", dept_ids["IT Department"], teacher_id, 3),
        ("CS210", "Web Development", dept_ids["CS Department"], None, 3),
        ("CS330", "Data Structures", dept_ids["CS Department"], None, 3),
        ("BBA101", "Accounting", dept_ids["BBA Department"], None, 3),
    ]
    conn.executemany(
        """
        INSERT INTO courses (code, name, department_id, teacher_id, credits)
        VALUES (?, ?, ?, ?, ?)
        """,
        courses,
    )

    students = [
        ("S001", "Dara Sok", "Male", "2005-02-14", "dara@example.com", "011111111", "Phnom Penh", dept_ids["IT Department"], 1, "Sok Vanna", "012222222"),
        ("S002", "Sokha Chan", "Female", "2004-11-20", "sokha@example.com", "012333333", "Kandal", dept_ids["CS Department"], 2, "Chan Sophea", "012444444"),
        ("S003", "Rina Mao", "Female", "2005-05-10", "rina@example.com", "012555555", "Siem Reap", dept_ids["BBA Department"], 1, "Mao Dara", "012666666"),
    ]
    conn.executemany(
        """
        INSERT INTO students
            (id, name, gender, date_of_birth, email, phone, address, department_id, year, parent_name, parent_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        students,
    )

    conn.execute(
        """
        INSERT INTO users (username, password_hash, role, full_name, linked_student_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("student", hash_password("student123"), "student", "Dara Sok", "S001"),
    )
    conn.execute(
        """
        INSERT INTO users (username, password_hash, role, full_name, linked_student_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("parent", hash_password("parent123"), "parent", "Sok Vanna", "S001"),
    )

    course_ids = {
        row["code"]: row["id"]
        for row in conn.execute("SELECT id, code FROM courses").fetchall()
    }
    scores = [
        ("S001", course_ids["IT101"], 92, "A", "Semester 1", "2026", admin_id),
        ("S001", course_ids["IT202"], 84, "B", "Semester 1", "2026", admin_id),
        ("S002", course_ids["CS210"], 76, "C", "Semester 1", "2026", admin_id),
        ("S003", course_ids["BBA101"], 68, "D", "Semester 1", "2026", admin_id),
    ]
    conn.executemany(
        """
        INSERT INTO scores (student_id, course_id, score, grade, semester, academic_year, recorded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        scores,
    )
