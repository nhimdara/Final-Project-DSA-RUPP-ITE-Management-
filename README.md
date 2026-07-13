# Simple Student Management System

A small console project that uses data structures directly. It does not use
MVC, a database, or third-party packages.

## Data structures

- `HashTable` stores students and courses and provides fast ID/code lookup.
- `Graph` connects students to the courses in which they are enrolled.
- `GradeDecisionTree` converts numeric scores into GPA values.

## Features

- Login with administrator, teacher, student, and parent roles
- Insert, delete, search, update, and display students
- Insert, delete, search, update, and display courses
- Enroll a student in a course
- Record scores and calculate GPA on a 4.0 scale
- Print a student's course report
- Let students view their enrolled courses and credit-weighted GPA
- Let teachers select a course and input scores for its enrolled students
- Ask student and parent users for a valid student ID before displaying records
- Let student and parent accounts view student information and GPA separately

Data is kept in memory, so it resets when the program exits.
Initial users, students, courses, enrollments, and scores are stored in
`data.py`. Edit that file to change the data loaded at startup.

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
