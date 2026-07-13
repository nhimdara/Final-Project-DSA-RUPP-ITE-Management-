# Project Structure

```text
StudentManagementSystem/
|-- data.py
|-- main.py
|-- README.md
`-- data_structures/
    |-- __init__.py
    |-- graph.py
    |-- hash_table.py
    |-- student_management.py
    `-- tree.py
```

- `main.py` contains only the simple console menu.
- `data.py` contains the initial users, students, courses, enrollments, and scores.
- `student_management.py` contains student/course records and all operations.
- `hash_table.py` stores students and courses.
- `graph.py` stores student-course enrollment relationships.
- `tree.py` calculates GPA values from scores.

The application uses data structures directly. It has no MVC layers and no
database dependency.
