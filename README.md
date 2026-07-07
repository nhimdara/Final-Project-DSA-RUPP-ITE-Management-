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
