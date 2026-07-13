# Student Management System Structure

```text
StudentManagementSystem/
|-- main.py
|-- README.md
|-- requirements.txt
|-- STRUCTURE.md
|
|-- assets/
|   `-- diagrams/
|       |-- flowchart.png
|       |-- system_diagram.png
|       `-- usecase.png
|
|-- controllers/
|   |-- __init__.py
|   |-- admin_controller.py
|   |-- auth_controller.py
|   |-- course_controller.py
|   |-- department_controller.py
|   |-- performance_controller.py
|   |-- report_controller.py
|   |-- score_controller.py
|   |-- search_controller.py
|   |-- student_controller.py
|   |-- teacher_controller.py
|   `-- user_controller.py
|
|-- data_structures/
|   |-- __init__.py
|   |-- graph.py
|   |-- hash_table.py
|   `-- tree.py
|
|-- database/
|   |-- __init__.py
|   |-- db.py
|   |-- schema.sql
|   |-- schema_mysql.sql
|   `-- student_management.db
|
|-- models/
|   |-- __init__.py
|   |-- admin.py
|   |-- course.py
|   |-- department.py
|   |-- report.py
|   |-- row_mapping.py
|   |-- score.py
|   |-- student.py
|   |-- teacher.py
|   `-- user.py
|
|-- reports/
|   |-- __init__.py
|   `-- report_generator.py
|
|-- services/
|   |-- __init__.py
|   `-- authentication_service.py
|
`-- views/
    |-- __init__.py
    |-- admin_view.py
    |-- course_view.py
    |-- dashboard_view.py
    |-- department_view.py
    |-- login_view.py
    |-- menu.py
    |-- performance_view.py
    |-- report_view.py
    |-- student_view.py
    `-- teacher_view.py
```

## Directory Roles

- `assets/` stores project diagrams and other static resources.
- `controllers/` handles application actions and coordinates models with views.
- `data_structures/` contains the graph, hash table, and tree implementations used by the project.
- `database/` contains database connections, schemas, and the SQLite database file.
- `models/` defines the application's data entities and row mappings.
- `reports/` contains report generation logic.
- `services/` contains shared business services such as authentication.
- `views/` contains the user-interface screens and menus.
- `main.py` is the application entry point.
