from __future__ import annotations

from typing import Any, Iterable, Optional, TypeAlias

from database.db import DbConnection, connection


SqlValue: TypeAlias = str | int | float | bytes | bool | None
SqlParams: TypeAlias = Iterable[SqlValue]


def prepare_sql(sql: str) -> str:
    return sql.replace("?", "%s")


def execute_on_connection(conn: DbConnection, sql: str, params: SqlParams = ()) -> Any:
    cursor = conn.cursor()
    cursor.execute(prepare_sql(sql), tuple(params))
    return cursor


def execute_many_on_connection(
    conn: DbConnection,
    sql: str,
    rows: Iterable[SqlParams],
) -> Any:
    cursor = conn.cursor()
    cursor.executemany(prepare_sql(sql), [tuple(row) for row in rows])
    return cursor


def close_cursor(cursor: Any) -> None:
    close = getattr(cursor, "close", None)
    if callable(close):
        close()


def last_insert_id(cursor: Any) -> int:
    if cursor.lastrowid is None:
        raise RuntimeError("The database did not return a row id for the insert.")
    return int(cursor.lastrowid)


def fetch_one_on_connection(conn: DbConnection, sql: str, params: SqlParams = ()) -> Any:
    cursor = execute_on_connection(conn, sql, params)
    try:
        return cursor.fetchone()
    finally:
        close_cursor(cursor)


def fetch_all_on_connection(
    conn: DbConnection,
    sql: str,
    params: SqlParams = (),
) -> list[Any]:
    cursor = execute_on_connection(conn, sql, params)
    try:
        return cursor.fetchall()
    finally:
        close_cursor(cursor)


def fetch_one(sql: str, params: SqlParams = ()) -> Optional[Any]:
    with connection() as conn:
        return fetch_one_on_connection(conn, sql, params)


def fetch_all(sql: str, params: SqlParams = ()) -> list[Any]:
    with connection() as conn:
        return fetch_all_on_connection(conn, sql, params)


def execute_insert(sql: str, params: SqlParams = ()) -> int:
    with connection() as conn:
        cursor = execute_on_connection(conn, sql, params)
        try:
            return last_insert_id(cursor)
        finally:
            close_cursor(cursor)


def execute(sql: str, params: SqlParams = ()) -> int:
    with connection() as conn:
        cursor = execute_on_connection(conn, sql, params)
        try:
            return cursor.rowcount
        finally:
            close_cursor(cursor)


def execute_many(sql: str, rows: Iterable[SqlParams]) -> None:
    with connection() as conn:
        cursor = execute_many_on_connection(conn, sql, rows)
        close_cursor(cursor)
