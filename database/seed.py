from __future__ import annotations

from database.db import DbConnection
from database.queries import (
    close_cursor,
    execute_many_on_connection,
    execute_on_connection,
    fetch_all_on_connection,
    fetch_one_on_connection,
    last_insert_id,
)
from models.user import hash_password


def seed_sample_data(conn: DbConnection) -> None:
    row = fetch_one_on_connection(conn, "SELECT COUNT(*) AS count FROM users")
    if row is not None and int(row["count"]):
        return

    cursor = execute_many_on_connection(
        conn,
        "INSERT INTO departments (name, description) VALUES (?, ?)",
        [
            ("IT Department", "Information Technology program"),
            ("CS Department", "Computer Science program"),
            ("BBA Department", "Business Administration program"),
        ],
    )
    close_cursor(cursor)
    department_ids = {
        row["name"]: row["id"]
        for row in fetch_all_on_connection(conn, "SELECT id, name FROM departments")
    }

    cursor = execute_on_connection(
        conn,
        """INSERT INTO users (username, password_hash, role, full_name)
           VALUES (?, ?, ?, ?)""",
        ("admin", hash_password("admin123"), "admin", "System Administrator"),
    )
    admin_id = last_insert_id(cursor)
    close_cursor(cursor)

    cursor = execute_on_connection(
        conn,
        """INSERT INTO users (username, password_hash, role, full_name)
           VALUES (?, ?, ?, ?)""",
        ("teacher", hash_password("teacher123"), "teacher", "Demo Teacher"),
    )
    teacher_user_id = last_insert_id(cursor)
    close_cursor(cursor)

    cursor = execute_on_connection(
        conn,
        """INSERT INTO teachers (name, email, phone, department_id, user_id)
           VALUES (?, ?, ?, ?, ?)""",
        (
            "Demo Teacher",
            "teacher@example.com",
            "012345678",
            department_ids["IT Department"],
            teacher_user_id,
        ),
    )
    teacher_id = last_insert_id(cursor)
    close_cursor(cursor)

    cursor = execute_many_on_connection(
        conn,
        """INSERT INTO courses (code, name, department_id, teacher_id, credits)
           VALUES (?, ?, ?, ?, ?)""",
        [
            ("IT101", "Python Programming", department_ids["IT Department"], teacher_id, 3),
            ("IT202", "Database Systems", department_ids["IT Department"], teacher_id, 3),
            ("CS210", "Web Development", department_ids["CS Department"], None, 3),
            ("CS330", "Data Structures", department_ids["CS Department"], None, 3),
            ("BBA101", "Accounting", department_ids["BBA Department"], None, 3),
        ],
    )
    close_cursor(cursor)

    cursor = execute_many_on_connection(
        conn,
        """INSERT INTO students
               (id, name, gender, date_of_birth, email, phone, address,
                department_id, year, parent_name, parent_phone)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                "S001", "Dara Sok", "Male", "2005-02-14", "dara@example.com",
                "011111111", "Phnom Penh", department_ids["IT Department"], 1,
                "Sok Vanna", "012222222",
            ),
            (
                "S002", "Sokha Chan", "Female", "2004-11-20", "sokha@example.com",
                "012333333", "Kandal", department_ids["CS Department"], 2,
                "Chan Sophea", "012444444",
            ),
            (
                "S003", "Rina Mao", "Female", "2005-05-10", "rina@example.com",
                "012555555", "Siem Reap", department_ids["BBA Department"], 1,
                "Mao Dara", "012666666",
            ),
        ],
    )
    close_cursor(cursor)

    for user in (
        ("student", hash_password("student123"), "student", "Dara Sok", "S001"),
        ("parent", hash_password("parent123"), "parent", "Sok Vanna", "S001"),
    ):
        cursor = execute_on_connection(
            conn,
            """INSERT INTO users
                   (username, password_hash, role, full_name, linked_student_id)
               VALUES (?, ?, ?, ?, ?)""",
            user,
        )
        close_cursor(cursor)

    course_ids = {
        row["code"]: row["id"]
        for row in fetch_all_on_connection(conn, "SELECT id, code FROM courses")
    }
    cursor = execute_many_on_connection(
        conn,
        """INSERT INTO scores
               (student_id, course_id, score, grade, semester, academic_year, recorded_by)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [
            ("S001", course_ids["IT101"], 92, "A", "Semester 1", "2026", admin_id),
            ("S001", course_ids["IT202"], 84, "B", "Semester 1", "2026", admin_id),
            ("S002", course_ids["CS210"], 76, "C", "Semester 1", "2026", admin_id),
            ("S003", course_ids["BBA101"], 68, "D", "Semester 1", "2026", admin_id),
        ],
    )
    close_cursor(cursor)
