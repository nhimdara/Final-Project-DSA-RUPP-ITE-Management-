# Student Management System API

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

Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI or
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
