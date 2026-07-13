from __future__ import annotations

import os
import re
from contextlib import contextmanager
from typing import Any, Iterator, TypeAlias


MYSQL_HOST = os.getenv("SMS_DB_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("SMS_DB_PORT", "3307"))
MYSQL_USER = os.getenv("SMS_DB_USER", "root")
MYSQL_PASSWORD = os.getenv("SMS_DB_PASSWORD", "")
MYSQL_DATABASE = os.getenv("SMS_DB_NAME", "student_management")
DbConnection: TypeAlias = Any


def _load_pymysql() -> Any:
    try:
        import pymysql
    except ImportError as exc:
        raise RuntimeError(
            "MySQL requires PyMySQL. Install it with "
            "`python -m pip install -r requirements.txt`."
        ) from exc
    return pymysql


def _validate_database_name() -> None:
    if not re.fullmatch(r"[A-Za-z0-9_]+", MYSQL_DATABASE):
        raise ValueError("SMS_DB_NAME can only contain letters, numbers, and underscores.")


def open_connection(*, include_database: bool = True) -> DbConnection:
    """Open a MySQL connection using the configured Workbench server details."""
    _validate_database_name()
    pymysql = _load_pymysql()
    options: dict[str, Any] = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": False,
    }
    if include_database:
        options["database"] = MYSQL_DATABASE
    return pymysql.connect(**options)


@contextmanager
def connection(*, include_database: bool = True) -> Iterator[DbConnection]:
    conn = open_connection(include_database=include_database)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
