# Student Management System

This project now has two interfaces:

- A professional FastAPI REST API backed by a relational database.
- The original educational console application demonstrating custom data
  structures.

## FastAPI system

The API includes:

- SQLAlchemy 2 database models and transactions
- SQLite by default; PostgreSQL can be selected with `DATABASE_URL`
- JWT bearer authentication with Argon2 password hashing
- Administrator, teacher, student, and parent authorization
- Student and course CRUD with validation, search, and pagination
- Enrollment, score recording, letter grades, and credit-weighted GPA reports
- Automatic one-time import of the demo data from `data.py`
- Interactive OpenAPI and ReDoc documentation
- Integration tests for authentication, authorization, and academic workflows

### Install and run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
uvicorn api.main:app --reload
```

Environment variables may be set in the shell before starting the server.
Replace `SECRET_KEY` in any deployed environment. The default database is
created as `student_management.db` in the project directory.

Open:

- API documentation: <http://127.0.0.1:8000/docs>
- Alternative documentation: <http://127.0.0.1:8000/redoc>
- Health check: <http://127.0.0.1:8000/health>

Use the `/api/v1/auth/token` form in Swagger to sign in, or click
**Authorize**. The existing demo administrator login is `admin` / `admin123`.

Run the automated tests with:

```powershell
pytest -q
```

### Main API routes

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/auth/token` | Sign in and receive a JWT |
| `GET` | `/api/v1/auth/me` | View the signed-in account |
| `GET/POST` | `/api/v1/students` | Search/list or create students |
| `GET/PATCH/DELETE` | `/api/v1/students/{student_id}` | Student CRUD |
| `GET` | `/api/v1/students/{student_id}/report` | Courses, grades, and GPA |
| `GET/POST` | `/api/v1/courses` | Search/list or create courses |
| `GET/PATCH/DELETE` | `/api/v1/courses/{code}` | Course CRUD |
| `POST` | `/api/v1/enrollments` | Enroll a student |
| `PUT` | `/api/v1/enrollments/{id}/score` | Record or replace a score |
| `DELETE` | `/api/v1/enrollments/{id}` | Remove an enrollment |
| `POST` | `/api/v1/users` | Create a role-controlled user |

For production, use a PostgreSQL URL such as
`postgresql+psycopg://user:password@host/database` and install the
`psycopg[binary]` driver.

## Original console system

A small console project that uses data structures directly. It does not use
MVC or third-party packages. It remains available for the DSA demonstration.

## Combined data structures

The main implementations are combined in `data_structures/student_management.py`:

- `HashTable` stores students, courses, and users for fast key lookup.
- `Graph` connects students to the courses in which they are enrolled.
- `GradeDecisionTree` converts numeric scores into grades and GPA values.
- `StudentManagementSystem` coordinates all three structures.

## Features

- Login with administrator, teacher, student, and parent roles
- Insert, delete, search, update, and display students
- Insert, delete, search, update, and display courses
- Enroll a student in a course
- Reject duplicate enrollment with a clear error
- Record scores and calculate GPA on a 4.0 scale
- Display the score-to-grade decision tree from the administrator menu
- Display the enrollment graph from the administrator menu
- Print a student's course report
- Let students view their enrolled courses and credit-weighted GPA
- Let teachers select a course and input scores for its enrolled students
- Ask student and parent users for a valid student ID before displaying records
- Let student and parent accounts view student information and GPA separately

Users, students, courses, enrollments, and scores are stored in `data.py`.
Changes made through the console are written back to that file automatically,
so they remain available after the program restarts.

## Demo accounts

| Role | Username | Password |
| --- | --- | --- |
| Administrator | `admin` | `admin123` |
| Teacher | `teacher` | `teacher123` |
| Student | `student` | `student123` |
| Parent | `parent` | `parent123` |

The generic student and parent accounts ask for a student ID after login. Use
`S001` or `S002` with the initial data. Courses `DS101` and `MATH101`,
enrollments, and example scores are included so every menu can be tested.

## Run the console application

```powershell
python main.py
```

The program only needs Python 3.9 or newer.

## System diagrams

- [Use-case diagram](assets/diagrams/usecase.png) ([editable SVG](assets/diagrams/usecase.svg))
- [System architecture diagram](assets/diagrams/system_diagram.png) ([editable SVG](assets/diagrams/system_diagram.svg))
- [Application flowchart](assets/diagrams/flowchart.png) ([editable SVG](assets/diagrams/flowchart.svg))

## Algorithm notes

- `HashTable` is a custom array-of-buckets implementation using separate
  chaining. Python's `hash()` only calculates the bucket index; storage,
  collision handling, lookup, update, and deletion are implemented manually.
- Exact student-ID and course-code lookups use the hash table. Free-text
  substring searches are intentionally linear because they may match any part
  of a name, ID, or course code.
- The grading tree implements the documented A/B/C/D/F 4.0 scale. Courses with
  no recorded score are displayed as pending and are excluded from GPA; they
  are not treated as failures.
