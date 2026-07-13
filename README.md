# Student Management System

Console-based Student Management System built from the included diagrams.

## Features

- Login and logout for administrator, teacher, student, and parent roles
- Student, course, department, teacher, and user management
- Score input with grade calculation through a decision tree
- Fast student lookup through a hash table cache
- Academic relationship graph support for university, departments, courses, and students
- Performance summaries and text report generation
- MySQL persistence through PyMySQL, compatible with MySQL Workbench

## MySQL Workbench Setup

MySQL Workbench is the graphical client; the application connects to the
MySQL Server used by Workbench. Start MySQL Server, then install the driver:

```powershell
py -m pip install -r requirements.txt
```

The application uses these defaults:

| Setting | Default |
| --- | --- |
| Host | `127.0.0.1` |
| Port | `3306` |
| User | `root` |
| Password | empty |
| Database | `student_management` |

If your Workbench connection uses a password or different settings, set them
in the same PowerShell window before starting the application:

```powershell
$env:SMS_DB_HOST="127.0.0.1"
$env:SMS_DB_PORT="3306"
$env:SMS_DB_USER="root"
$env:SMS_DB_PASSWORD="your_mysql_password"
$env:SMS_DB_NAME="student_management"
```

Do not save a real database password in the source code. On first startup, the
application creates the database and tables from `database/schema_mysql.sql`
and inserts the demo records. Refresh the Schemas panel in Workbench to see
the `student_management` database.

For a manual Workbench setup, open and execute
`database/student_management_workbench.sql`. This standalone script creates
the database, tables, and demo records.

## Run

```powershell
python main.py
```

If `python` opens the Windows Store shortcut, use the Windows Python launcher:

```powershell
py -3 main.py
```

Default demo accounts:

| Role | Username | Password |
| --- | --- | --- |
| Administrator | `admin` | `admin123` |
| Teacher | `teacher` | `teacher123` |
| Student | `student` | `student123` |
| Parent | `parent` | `parent123` |

Generated reports are saved in `reports/generated`.
