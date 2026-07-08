# Student Management System

Console-based Student Management System built from the included diagrams.

## Features

- Login and logout for administrator, teacher, student, and parent roles
- Student, course, department, teacher, and user management
- Score input with grade calculation through a decision tree
- Fast student lookup through a hash table cache
- Academic relationship graph support for university, departments, courses, and students
- Performance summaries and text report generation
- SQLite persistence in `database/student_management.db`
- Optional XAMPP/MySQL persistence through PyMySQL

## Run

```powershell
python main.py
```

If `python` opens the Windows Store shortcut, use:

```powershell
uv run python main.py
```

Default demo accounts:

| Role | Username | Password |
| --- | --- | --- |
| Administrator | `admin` | `admin123` |
| Teacher | `teacher` | `teacher123` |
| Student | `student` | `student123` |
| Parent | `parent` | `parent123` |

Generated reports are saved in `reports/generated`.

## Run With XAMPP MySQL

Start MySQL in XAMPP, then install the MySQL driver:

```powershell
uv pip install -r requirements.txt
```

Use these environment variables before running the app:

```powershell
$env:SMS_DB_DRIVER="mysql"
$env:SMS_DB_HOST="127.0.0.1"
$env:SMS_DB_PORT="3306"
$env:SMS_DB_USER="root"
$env:SMS_DB_PASSWORD=""
$env:SMS_DB_NAME="student_management"
python main.py
```

The app creates the database and tables automatically. You can also import
`database/schema_mysql.sql` in phpMyAdmin if you want to create the tables manually.
