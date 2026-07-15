"""Initial data loaded by the Student Management System.

Edit these collections to change the records available whenever the program
starts. Changes made through the console are kept in memory only.
"""

from __future__ import annotations


USERS = (
    {
        "username": "admin",
        "password": "admin123",
        "role": "administrator",
        "student_id": "",
    },
    {
        "username": "teacher",
        "password": "teacher123",
        "role": "teacher",
        "student_id": "",
    },
    {
        "username": "student",
        "password": "student123",
        "role": "student",
        "student_id": "",
    },
    {
        "username": "parent",
        "password": "parent123",
        "role": "parent",
        "student_id": "",
    },
)

STUDENTS = (
    {
        "student_id": "S001",
        "name": "Demo Student",
        "department": "Computer Science",
        "year": 1,
    },
    {
        "student_id": "S002",
        "name": "Alex Morgan",
        "department": "Information Technology",
        "year": 2,
    },
    {
        "student_id": "S003",
        "name": "Jamie Lee",
        "department": "Software Engineering",
        "year": 3,
    }
)

COURSES = (
    {"code": "CS101", "name": "Data Structures", "credits": 3},
    {"code": "MATH101", "name": "Discrete Mathematics", "credits": 3},
)

ENROLLMENTS = (
    {"student_id": "S001", "course_code": "CS101"},
    {"student_id": "S001", "course_code": "MATH101"},
    {"student_id": "S002", "course_code": "CS101"},
)

SCORES = (
    {"student_id": "S001", "course_code": "CS101", "score": 88},
    {"student_id": "S001", "course_code": "MATH101", "score": 92},
    {"student_id": "S002", "course_code": "CS101", "score": 76},
)
