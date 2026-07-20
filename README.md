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
