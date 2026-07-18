# Project Structure

```text
StudentManagementSystem/
|-- data.py
|-- main.py
|-- README.md
`-- data_structures/
    |-- __init__.py
    `-- student_management.py
```

- `main.py` contains only the simple console menu.
- `data.py` contains the initial users, students, courses, enrollments, and scores.
- `student_management.py` combines all data structures, records, and operations.

The application uses data structures directly. It has no MVC layers and no
database dependency.
