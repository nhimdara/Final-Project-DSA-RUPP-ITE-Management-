<<<<<<< HEAD
<<<<<<< HEAD
# Simple Student Management System
=======
# Student Management System API
>>>>>>> origin/dev

A layered FastAPI application using SQLAlchemy, Alembic, Pydantic, and SQLite.

## Features

- Login with administrator, teacher, student, and parent roles
- Insert, delete, search, update, and display students
- Insert, delete, search, update, and display courses
- Enroll a student in a course
- Reject duplicate enrollment with a clear error
- Record scores and calculate GPA on a 4.0 scale
- Generate a student's academic report and credit-weighted GPA
- Search students and courses
- Validate requests using Pydantic schemas
- Persist records in a relational database
- Version endpoints under `/api/v1`

The `data.py` file contains legacy initial records used only by the idempotent
database seed command. Runtime changes are stored in the configured database.

## Demo accounts

| Role | Username | Password |
| --- | --- | --- |
| Administrator | `admin` | `admin123` |
| Teacher | `teacher` | `teacher123` |
| Student | `student` | `student123` |
| Parent | `parent` | `parent123` |

## Run

Install the API dependencies and start the development server:

```powershell
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m scripts.seed_database
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` for the web dashboard. Open
`http://127.0.0.1:8000/docs` for the interactive Swagger UI or
`http://127.0.0.1:8000/redoc` for ReDoc. The API exposes student and course
CRUD, login, enrollment, scoring, GPA, and academic-report endpoints.
The API uses SQLite by default and stores its data in `student_management.db`.
Set the `DATABASE_URL` environment variable to use another SQLAlchemy-supported
database. Alembic manages schema changes; `scripts/seed_database.py` imports the
existing records from `data.py` and is safe to run more than once.

The API follows a conventional layered structure:

```text
app/
  controllers/   business logic and database operations
  models/        SQLAlchemy database models
  routes/        FastAPI endpoint definitions
  schemas/       Pydantic request and response models
  database.py    engine and session configuration
  main.py        application setup
migrations/      Alembic database migrations
scripts/         database seed commands
```

All application endpoints are versioned under `/api/v1`.

<<<<<<< HEAD
- `HashTable` is a custom array-of-buckets implementation using separate
  chaining. Python's `hash()` only calculates the bucket index; storage,
  collision handling, lookup, update, and deletion are implemented manually.
- Exact student-ID and course-code lookups use the hash table. Free-text
  substring searches are intentionally linear because they may match any part
  of a name, ID, or course code.
- The grading tree implements the documented A/B/C/D/F 4.0 scale. Courses with
  no recorded score are displayed as pending and are excluded from GPA; they
  are not treated as failures.
- The enrollment graph uses breadth-first search with a queue to find a
  shortest path. For example, a path between two students shows the courses
  and other students that connect them.
=======
# Simple Student Management System

A small console project that uses data structures directly. It does not use
MVC, a database, or third-party packages.

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
`S001` or `S002` with the initial data. Courses `CS101` and `MATH101`,
enrollments, and example scores are included so every menu can be tested.

## Run

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
  of a name, department, ID, or code.
- The grading tree implements the documented A/B/C/D/F 4.0 scale. Courses with
  no recorded score are displayed as pending and are excluded from GPA; they
  are not treated as failures.
>>>>>>> 010243d87f91d0817bcec308e41046eb1ea346bd
=======
## Authentication and permissions

Login at `/api/v1/auth/login` to receive a bearer token. The web dashboard
stores the token for the browser session and sends it with every API request.

- Administrators can manage students, courses, enrollments, and scores.
- Teachers can view students and courses, manage enrollments and scores, and
  view academic reports.
- Students can view courses and only their own linked profile and report.
- Parents must provide an existing student ID when logging in, and can view
  courses and only the selected student's profile and report for that session.

For deployment, copy `.env.example` to `.env` and replace `TOKEN_SECRET` with a
long random value. The student demo account is linked to `S001`; the generic
parent demo account selects an existing student ID during login.
>>>>>>> origin/dev
