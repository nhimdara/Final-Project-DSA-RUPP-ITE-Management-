from __future__ import annotations

import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Iterator, Optional, TypeAlias

from models.user import hash_password


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "student_management.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"
MYSQL_SCHEMA_PATH = BASE_DIR / "schema_mysql.sql"
DB_DRIVER = os.getenv("SMS_DB_DRIVER", "sqlite").strip().lower()
MYSQL_HOST = os.getenv("SMS_DB_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("SMS_DB_PORT", "3306"))
MYSQL_USER = os.getenv("SMS_DB_USER", "root")
MYSQL_PASSWORD = os.getenv("SMS_DB_PASSWORD", "")
MYSQL_DATABASE = os.getenv("SMS_DB_NAME", "student_management")
SqlValue: TypeAlias = str | int | float | bytes | bool | None
SqlParams: TypeAlias = Iterable[SqlValue]
DbConnection: TypeAlias = sqlite3.Connection | Any


def is_mysql_backend() -> bool:
    return DB_DRIVER in {"mysql", "mariadb", "xampp"}


def _load_pymysql() -> Any:
    try:
        import pymysql
    except ImportError as exc:
        raise RuntimeError(
            "MySQL/XAMPP mode requires PyMySQL. Install it with "
            "`uv pip install PyMySQL` or `python -m pip install PyMySQL`."
        ) from exc
    return pymysql


def _validate_mysql_database_name() -> None:
    if not re.fullmatch(r"[A-Za-z0-9_]+", MYSQL_DATABASE):
        raise ValueError("SMS_DB_NAME can only contain letters, numbers, and underscores.")


def open_connection() -> DbConnection:
    if is_mysql_backend():
        _validate_mysql_database_name()
        pymysql = _load_pymysql()
        return pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def connection() -> Iterator[DbConnection]:
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
    if is_mysql_backend():
        _ensure_mysql_database()
        _create_schema(seed=seed)
        return

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


def _ensure_mysql_database() -> None:
    _validate_mysql_database_name()
    pymysql = _load_pymysql()
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        conn.close()


def _backup_database(reason: str) -> None:
    backup_path = DB_PATH.with_name(f"{DB_PATH.stem}.{reason}-{datetime.now():%Y%m%d%H%M%S}.bak")
    DB_PATH.replace(backup_path)


def _database_needs_rebuild() -> bool:
    conn: sqlite3.Connection | None = None
    try:
        conn = open_connection()
        tables = _table_names(conn)
        if "students" in tables:
            columns = {
                row["name"]: row
                for row in conn.execute("PRAGMA table_info(students)").fetchall()
            }
            student_id = columns.get("id")
            student_id_type = str(student_id["type"] if student_id is not None else "").upper()
            if student_id_type and student_id_type != "TEXT":
                return True
        if "courses" in tables:
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(courses)").fetchall()}
            if "code" not in columns:
                return True
        if "teachers" in tables:
            columns = {
                row["name"]: row
                for row in conn.execute("PRAGMA table_info(teachers)").fetchall()
            }
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
    schema_path = MYSQL_SCHEMA_PATH if is_mysql_backend() else SCHEMA_PATH
    schema = schema_path.read_text(encoding="utf-8")
    with connection() as conn:
        _execute_script(conn, schema)
        if not is_mysql_backend():
            _migrate_existing_schema(conn)
        if seed:
            seed_sample_data(conn)


def _execute_script(conn: DbConnection, schema: str) -> None:
    if not is_mysql_backend():
        conn.executescript(schema)
        return

    for statement in _split_sql_script(schema):
        cursor = _execute_conn(conn, statement)
        _close_cursor(cursor)


def _split_sql_script(schema: str) -> list[str]:
    cleaned_lines = [
        line
        for line in schema.splitlines()
        if line.strip() and not line.lstrip().startswith("--")
    ]
    return [
        statement.strip()
        for statement in "\n".join(cleaned_lines).split(";")
        if statement.strip()
    ]


def _table_names(conn: sqlite3.Connection) -> set[str]:
    return {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    }


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}


def _ensure_column(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    definition: str,
) -> None:
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
    existing_tables = _table_names(conn)
    for table_name, columns in migrations.items():
        if table_name not in existing_tables:
            continue
        for column_name, definition in columns.items():
            _ensure_column(conn, table_name, column_name, definition)


def fetch_one(sql: str, params: SqlParams = ()) -> Optional[Any]:
    with connection() as conn:
        return _fetch_one_conn(conn, sql, params)


def fetch_all(sql: str, params: SqlParams = ()) -> list[Any]:
    with connection() as conn:
        return _fetch_all_conn(conn, sql, params)


def _prepare_sql(sql: str) -> str:
    if not is_mysql_backend():
        return sql
    return sql.replace("?", "%s")


def _execute_conn(conn: DbConnection, sql: str, params: SqlParams = ()) -> Any:
    if is_mysql_backend():
        cursor = conn.cursor()
        cursor.execute(_prepare_sql(sql), tuple(params))
        return cursor
    return conn.execute(sql, tuple(params))


def _executemany_conn(conn: DbConnection, sql: str, rows: Iterable[SqlParams]) -> Any:
    prepared_rows = [tuple(row) for row in rows]
    if is_mysql_backend():
        cursor = conn.cursor()
        cursor.executemany(_prepare_sql(sql), prepared_rows)
        return cursor
    return conn.executemany(sql, prepared_rows)


def _fetch_one_conn(conn: DbConnection, sql: str, params: SqlParams = ()) -> Any:
    cursor = _execute_conn(conn, sql, params)
    try:
        return cursor.fetchone()
    finally:
        _close_cursor(cursor)


def _fetch_all_conn(conn: DbConnection, sql: str, params: SqlParams = ()) -> list[Any]:
    cursor = _execute_conn(conn, sql, params)
    try:
        return cursor.fetchall()
    finally:
        _close_cursor(cursor)


def _close_cursor(cursor: Any) -> None:
    close = getattr(cursor, "close", None)
    if callable(close):
        close()


def _last_insert_id(cursor: Any) -> int:
    lastrowid = cursor.lastrowid
    if lastrowid is None:
        raise RuntimeError("The database did not return a row id for the insert.")
    return int(lastrowid)


def execute_insert(sql: str, params: SqlParams = ()) -> int:
    with connection() as conn:
        cursor = _execute_conn(conn, sql, params)
        try:
            return _last_insert_id(cursor)
        finally:
            _close_cursor(cursor)


def execute(sql: str, params: SqlParams = ()) -> int:
    with connection() as conn:
        cursor = _execute_conn(conn, sql, params)
        try:
            return cursor.rowcount
        finally:
            _close_cursor(cursor)


def execute_many(sql: str, rows: Iterable[SqlParams]) -> None:
    with connection() as conn:
        cursor = _executemany_conn(conn, sql, rows)
        _close_cursor(cursor)


def seed_sample_data(conn: DbConnection) -> None:
    user_count_row = _fetch_one_conn(conn, "SELECT COUNT(*) AS count FROM users")
    user_count = int(user_count_row["count"]) if user_count_row is not None else 0
    if user_count:
        return

    departments = [
        ("IT Department", "Information Technology program"),
        ("CS Department", "Computer Science program"),
        ("BBA Department", "Business Administration program"),
    ]
    cursor = _executemany_conn(
        conn,
        "INSERT INTO departments (name, description) VALUES (?, ?)",
        departments,
    )
    _close_cursor(cursor)

    dept_ids = {
        row["name"]: row["id"]
        for row in _fetch_all_conn(conn, "SELECT id, name FROM departments")
    }

    admin_cursor = _execute_conn(
        conn,
        """
        INSERT INTO users (username, password_hash, role, full_name)
        VALUES (?, ?, ?, ?)
        """,
        ("admin", hash_password("admin123"), "admin", "System Administrator"),
    )
    admin_id = _last_insert_id(admin_cursor)
    _close_cursor(admin_cursor)

    teacher_user_cursor = _execute_conn(
        conn,
        """
        INSERT INTO users (username, password_hash, role, full_name)
        VALUES (?, ?, ?, ?)
        """,
        ("teacher", hash_password("teacher123"), "teacher", "Demo Teacher"),
    )
    teacher_user_id = _last_insert_id(teacher_user_cursor)
    _close_cursor(teacher_user_cursor)

    teacher_cursor = _execute_conn(
        conn,
        """
        INSERT INTO teachers (name, email, phone, department_id, user_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Demo Teacher",
            "teacher@example.com",
            "012345678",
            dept_ids["IT Department"],
            teacher_user_id,
        ),
    )
    teacher_id = _last_insert_id(teacher_cursor)
    _close_cursor(teacher_cursor)

    courses = [
        ("IT101", "Python Programming", dept_ids["IT Department"], teacher_id, 3),
        ("IT202", "Database Systems", dept_ids["IT Department"], teacher_id, 3),
        ("CS210", "Web Development", dept_ids["CS Department"], None, 3),
        ("CS330", "Data Structures", dept_ids["CS Department"], None, 3),
        ("BBA101", "Accounting", dept_ids["BBA Department"], None, 3),
    ]
    cursor = _executemany_conn(
        conn,
        """
        INSERT INTO courses (code, name, department_id, teacher_id, credits)
        VALUES (?, ?, ?, ?, ?)
        """,
        courses,
    )
    _close_cursor(cursor)

    students = [
        (
            "S001",
            "Dara Sok",
            "Male",
            "2005-02-14",
            "dara@example.com",
            "011111111",
            "Phnom Penh",
            dept_ids["IT Department"],
            1,
            "Sok Vanna",
            "012222222",
        ),
        (
            "S002",
            "Sokha Chan",
            "Female",
            "2004-11-20",
            "sokha@example.com",
            "012333333",
            "Kandal",
            dept_ids["CS Department"],
            2,
            "Chan Sophea",
            "012444444",
        ),
        (
            "S003",
            "Rina Mao",
            "Female",
            "2005-05-10",
            "rina@example.com",
            "012555555",
            "Siem Reap",
            dept_ids["BBA Department"],
            1,
            "Mao Dara",
            "012666666",
        ),
    ]
    cursor = _executemany_conn(
        conn,
        """
        INSERT INTO students
            (id, name, gender, date_of_birth, email, phone, address,
             department_id, year, parent_name, parent_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        students,
    )
    _close_cursor(cursor)

    cursor = _execute_conn(
        conn,
        """
        INSERT INTO users (username, password_hash, role, full_name, linked_student_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("student", hash_password("student123"), "student", "Dara Sok", "S001"),
    )
    _close_cursor(cursor)
    cursor = _execute_conn(
        conn,
        """
        INSERT INTO users (username, password_hash, role, full_name, linked_student_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("parent", hash_password("parent123"), "parent", "Sok Vanna", "S001"),
    )
    _close_cursor(cursor)

    course_ids = {
        row["code"]: row["id"]
        for row in _fetch_all_conn(conn, "SELECT id, code FROM courses")
    }
    scores = [
        ("S001", course_ids["IT101"], 92, "A", "Semester 1", "2026", admin_id),
        ("S001", course_ids["IT202"], 84, "B", "Semester 1", "2026", admin_id),
        ("S002", course_ids["CS210"], 76, "C", "Semester 1", "2026", admin_id),
        ("S003", course_ids["BBA101"], 68, "D", "Semester 1", "2026", admin_id),
    ]
    cursor = _executemany_conn(
        conn,
        """
        INSERT INTO scores
            (student_id, course_id, score, grade, semester, academic_year, recorded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        scores,
    )
    _close_cursor(cursor)
