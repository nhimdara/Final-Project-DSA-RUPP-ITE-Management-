from __future__ import annotations

from pathlib import Path

from database.db import MYSQL_DATABASE, connection
from database.queries import close_cursor, execute_on_connection
from database.seed import seed_sample_data


MYSQL_SCHEMA_PATH = Path(__file__).resolve().parent / "schema_mysql.sql"


def initialize_database(seed: bool = True) -> None:
    _ensure_database()
    _create_schema(seed=seed)


def _ensure_database() -> None:
    with connection(include_database=False) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        finally:
            close_cursor(cursor)


def _create_schema(seed: bool) -> None:
    schema = MYSQL_SCHEMA_PATH.read_text(encoding="utf-8")
    with connection() as conn:
        for statement in _split_sql_script(schema):
            cursor = execute_on_connection(conn, statement)
            close_cursor(cursor)
        if seed:
            seed_sample_data(conn)


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
