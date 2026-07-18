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
        "name": "Chan Mean",
        "department": "Information Technology",
        "year": 2,
    },
    {
        "student_id": "S002",
        "name": "Sok Dara",
        "department": "Information Technology",
        "year": 2,
    },
    {
        "student_id": "S003",
        "name": "Keo Rotha",
        "department": "Computer Science",
        "year": 2,
    },
    {
        "student_id": "S004",
        "name": "Chea Boring",
        "department": "Information Technology",
        "year": 2,
    },
    {
        "student_id": "S005",
        "name": "Nguon Sovann",
        "department": "Computer Science",
        "year": 2,
    },
    {
        "student_id": "S006",
        "name": "Lim Heng",
        "department": "Information Technology",
        "year": 3,
    },
    {
        "student_id": "S007",
        "name": "Vann Chanthou",
        "department": "Computer Science",
        "year": 3,
    },
    {
        "student_id": "S008",
        "name": "Te Tepnorin",
        "department": "Information Technology",
        "year": 3,
    },
    {
        "student_id": "S009",
        "name": "San Sreypich",
        "department": "Information Technology",
        "year": 1,
    },
    {
        "student_id": "S010",
        "name": "Bun Tharith",
        "department": "Computer Science",
        "year": 1,
    },
    {
        "student_id": "S011",
        "name": "Ouk Kalyan",
        "department": "Computer Science",
        "year": 4,
    },
    {
        "student_id": "S012",
        "name": "Meas Samnang",
        "department": "Information Technology",
        "year": 4,
    },
    {
        "student_id": "S013",
        "name": "Phon Makara",
        "department": "Telecommunication Engineering",
        "year": 2,
    },
    {
        "student_id": "S014",
        "name": "Seng Sreyneath",
        "department": "Information Technology",
        "year": 2,
    },
    {
        "student_id": "S015",
        "name": "Khim Visal",
        "department": "Computer Science",
        "year": 2,
    },
)

COURSES = (
    {"code": "CS101", "name": "Data Structures", "credits": 3},
    {"code": "MATH101", "name": "Discrete Mathematics", "credits": 3},
    {"code": "ENG01", "name": "English", "credits": 2},
    {"code": "DB101", "name": "Database", "credits":3},
    {"code": "APL101", "name": "Application Programing", "credit": 4}
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
