# Royal University of Phnom Penh (RUPP)
## Faculty of Engineering
### Department of Telecommunication & Electronic Engineering

---

# Data Structures and Algorithms II (DSA II)
## PBL Progress Report (Weeks 1 – 3)

* **Lecturer:** Chhoeum Vantha, Ph.D.
* **Project Title:** Design and Implementation of an ITE Student Management System Using Hash Tables, Graphs, and Decision Trees
* **Duration:** 4 Weeks
* **Current Stage:** Week 3 (Finalize Phase)
* **Team Composition:** 5 Students (1 Leader, 4 Members)

---

## 📅 Executive Summary & Timeline Overview

| Week | Phase | Key Activities & Status |
| :---: | :--- | :--- |
| **Week 1** | **Planning** | ✅ Problem identification, system architecture design, data structure selection, role assignment. |
| **Week 2** | **Development** | ✅ Implemented custom `HashTable`, `Graph` (BFS), `GradeDecisionTree`, and Console RBAC menus. |
| **Week 3** | **Finalize (Current)** | ✅ System optimization (`HashTable` rehashing, `Graph` vertex degree analytics, ID validation), slide outline preparation. |
| **Week 4** | **Evaluation** | ⏳ Rehearsal, final slide submission, live demonstration, and defense. |

---

## 📝 Detailed Progress Report

### 🔹 Week 1: Planning Phase
* **Objective:** Understand the problem, design system architecture, and assign team responsibilities.
* **Key Achievements:**
  1. **Problem Identification:** Identified issues with standard linear searching ($O(N)$ overhead), disorganized student records, manual grade calculation errors, and untraced student-course enrollments.
  2. **System Architecture Design:** Designed a modular, console-based application requiring zero third-party database dependencies by implementing 3 custom data structures:
     - **Hash Table:** For $O(1)$ fast record lookups.
     - **Undirected Graph:** For modeling student-course relationships.
     - **Binary Decision Tree:** For score-to-grade mapping.
  3. **Role Assignment:** Assigned tasks among 5 team members (Leader: Integration & Presentation; Member 1: Hash Table; Member 2: Graph & BFS; Member 3: Decision Tree; Member 4: Testing & Demo).

---

### 🔹 Week 2: Development Phase
* **Objective:** Build custom data structures, implement core business logic, and test functionality.
* **Key Achievements:**
  1. **Data Structure 1 — Custom Hash Table (`HashTable`):**
     - Implemented an array of buckets with **separate chaining** to resolve key collisions.
     - Created $O(1)$ insertion, search, deletion, and retrieval for `Students`, `Courses`, and `Users`.
  2. **Data Structure 2 — Enrollment Graph (`Graph`):**
     - Constructed an **Undirected Adjacency List Graph** connecting student vertices (`student:ID`) to course vertices (`course:CODE`).
     - Implemented **Breadth-First Search (BFS)** using a queue to find the shortest enrollment path connecting two endpoints.
  3. **Data Structure 3 — Grade Decision Tree (`GradeDecisionTree`):**
     - Built a binary decision tree with threshold nodes (`90`, `80`, `70`, `60`) mapping scores ($0-100$) recursively to letter grades (`A/B/C/D/F`) and 4.0 GPA points.
  4. **Console & Access Control (`main.py`):**
     - Built role-based access menus for **Administrator**, **Teacher**, **Student**, and **Parent**.
  5. **Data Persistence (`data.py`):**
     - Created an automatic persistence mechanism to save modified records across application restarts.

---

### 🔹 Week 3: Finalize Phase (Current Progress)
* **Objective:** Refine system based on testing, optimize code performance, and prepare presentation.
* **Key Achievements:**
  1. **Algorithmic Optimization — Dynamic Rehashing:**
     - Enhanced `HashTable` with automatic capacity doubling ($\text{capacity} \times 2 + 1$) and **rehashing** when the load factor reaches $\ge 0.75$, guaranteeing true $O(1)$ performance as data expands.
  2. **Feature Enhancement — Graph Vertex Degree Analytics:**
     - Implemented graph degree calculations to compute course popularity (vertex degree = number of enrolled students) and added Option 16 to the Administrator menu.
  3. **Data Validation & Stability:**
     - Sanitized Student IDs and Course Codes to prevent colons (`:`), ensuring graph vertex resolution and BFS pathfinding never fail.
  4. **Presentation Preparation:**
     - Mapped project features directly to Dr. Vantha's assessment rubric (Graph 5%, Hash Table 5%, Tree 5%, Presentation 25%, Teamwork 5%).
     - Completed the 12–15 slide outline following Slide 7 guidelines.

---

## 🎯 Plan for Week 4 (Evaluation Phase)

1. **Slide Design:** Assemble final presentation slides in Canva/PowerPoint with system architecture diagrams and code snippets.
2. **Presentation Rehearsal:** Practice the 15-minute presentation defense with all 5 team members.
3. **Live Demo Preparation:** Prepare the live terminal demonstration script (`python main.py`).
4. **Final Deliverable Submission:** Submit the final soft code repository and slide presentation.
