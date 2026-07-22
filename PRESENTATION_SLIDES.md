# 📢 Slide-by-Slide Presentation Guide

This guide contains the structure, content, visual design recommendations, and speaker notes for your **DSA II PBL Project Defense**. You can copy this content directly into PowerPoint or Canva.

---

## 🗂️ Presentation Outline

* **Slide 1:** Title & Team Intro
* **Slide 2:** Problem Statement & Project Goal
* **Slide 3:** High-Level System Architecture
* **Slide 4:** Data Structure 1: Hash Table (Separate Chaining)
* **Slide 5:** Hash Table Optimization: Dynamic Rehashing
* **Slide 6:** Data Structure 2: Enrollment Graph (Adjacency List)
* **Slide 7:** Graph Algorithm: Breadth-First Search (BFS)
* **Slide 8:** Data Structure 3: Grade Decision Tree
* **Slide 9:** Integration Workflow: Student Enrollment & GPA Calculation
* **Slide 10:** Persistent Storage: Zero-Dependency File Database
* **Slide 11:** Console Demo Scenarios (RBAC)
* **Slide 12:** Project Accomplishments & Future Work
* **Slide 13:** Q&A & Conclusion

---

### 🎨 Design & Theme Advice
* **Palette:** Sleek dark blue and white, with teal/cyan accents (matching the RUPP Faculty of Engineering colors).
* **Typography:** Clean sans-serif fonts (e.g., *Inter*, *Roboto*, or *Outfit*).
* **Code Snippets:** Keep code blocks short (max 6-8 lines per slide), clean, and well-highlighted.

---

## 🎴 Slide 1: Title & Team Intro

* **Slide Title:** Design and Implementation of an ITE Student Management System
* **Subtitle:** Project-Based Learning (PBL) for Data Structures and Algorithms II
* **Visuals:** RUPP & Faculty of Engineering logos side-by-side.
* **Content:**
  * **Lecturer:** Chhoeum Vantha, Ph.D.
  * **Team Members:**
    * *Team Leader:* [Leader Name] — System Integration & Design
    * *Member 1:* [Name] — Custom Hash Table Implementation
    * *Member 2:* [Name] — Graph & Breadth-First Search
    * *Member 3:* [Name] — Binary Decision Tree & GPA Report
    * *Member 4:* [Name] — Testing & Quality Assurance
* **Speaker Notes:**
  > "Good morning Dr. Vantha and fellow classmates. Today, our team is presenting our Data Structures and Algorithms II final project: the Design and Implementation of an ITE Student Management System. Our goal was to build a system from scratch using custom implementations of Hash Tables, Graphs, and Decision Trees without relying on high-level Python libraries or external database packages."

---

## 🎴 Slide 2: Problem Statement & Project Goal

* **Slide Title:** The Problem & Solution Goal
* **Visuals:** Two columns: Left column with warning icons (Problems), Right column with checkmarks (Goals).
* **Content:**
  * **The Problem:**
    * Hardcoded lists/arrays result in slow $O(N)$ lookup speeds for students and courses.
    * Tracking complex student-to-course relationships is difficult using static lists.
    * Standard conditional chains (`if-elif-else`) are prone to errors and hard to scale.
    * Traditional setups require heavy database servers (SQL/NoSQL) which are overkill for basic tools.
  * **The Goal:**
    * Build an integrated system with zero dependencies using textbook data structures.
    * Guarantee $O(1)$ query lookup speeds using a custom Hash Table.
    * Model connections using a custom Graph.
    * Automate academic grading using a custom Binary Decision Tree.
* **Speaker Notes:**
  > "Traditional database management applications often rely on heavy, black-box software or perform slow linear searches over lists. For our project, we wanted to address these challenges directly: ensuring constant-time searches, modeling complex enrollment relationships, and building a grading tree that behaves cleanly, all without using any database engines."

---

## 🎴 Slide 3: High-Level System Architecture

* **Slide Title:** System Architecture & Data Flow
* **Visuals:** A block diagram representing data flowing from the console UI, to the coordinator, to the memory structures, and finally to storage.
* **Content:**
  * **User Interface:** Interactive terminal menu featuring Role-Based Access Control (RBAC).
  * **System Coordinator:** Coordinates data operations and persistence.
  * **Memory Layer:**
    * **Hash Table:** Stores primary entities (`Students`, `Courses`, `Users`).
    * **Graph:** Stores relationships (`Enrollments`).
    * **Decision Tree:** Processes inputs to return grades and GPAs.
  * **Persistence Layer:** Serializes objects to `data.py` atomically.
* **Speaker Notes:**
  > "Here is our high-level architecture. The application is modular. The console layer in `main.py` provides menus for Admin, Teacher, Student, and Parent. All instructions pass through our coordinator class, which routes student details to our Hash Table, records registrations in the Graph, maps scores using the Decision Tree, and persists everything to our file-based database."

---

## 🎴 Slide 4: Data Structure 1: Hash Table (Separate Chaining)

* **Slide Title:** Custom Hash Table Design
* **Visuals:** A conceptual diagram of a hash table array (indices 0 to N) pointing to linked lists (separate chaining).
* **Content:**
  * **Separate Chaining:** Handles hash index collisions by using linked bucket lists.
  * **Hash Function:** Uses Python's native `hash(key) % capacity` to yield non-negative indices.
  * **Textbook Operations:** 
    * `insert(key, value)`
    * `search(key)`
    * `delete(key)`
* **Code Snippet:**
  ```python
  def _hash(self, key):
      return hash(key) % self.capacity

  def search(self, key):
      index = self._hash(key)
      for stored_key, value in self.buckets[index]:
          if stored_key == key:
              return value
      return None
  ```
* **Speaker Notes:**
  > "Our first core structure is the HashTable. To prevent hash collisions, we implemented Separate Chaining. Each bucket starts as an empty list. When a key is inserted, its hash value dictates the index. If multiple keys land on the same index, they are appended to the bucket's list. Lookups scan only the items inside the target bucket, preserving an average time complexity of O(1)."

---

## 🎴 Slide 5: Hash Table Optimization: Dynamic Rehashing

* **Slide Title:** Maintaining O(1) Speed: Dynamic Rehashing
* **Visuals:** Before and after diagrams of a hash table resizing from capacity 101 to 203.
* **Content:**
  * **The Problem:** As records increase, buckets fill up, and search times degrade to linear scans ($O(N)$).
  * **The Solution:** Implement automatic rehashing.
  * **Load Factor Threshold:** $\text{Load Factor} = \text{size} / \text{capacity} \ge 0.75$.
  * **Expansion Strategy:** Resize capacity using $N_{\text{new}} = \text{capacity} \times 2 + 1$ (expanding through odd numbers to spread hashes).
  * **Rehash Phase:** Every record is rehashed and redistributed.
* **Speaker Notes:**
  > "A common mistake in simple hash tables is keeping a fixed size. As data grows, collisions increase. To maintain true constant-time speed, we implemented dynamic resizing. When the load factor reaches 75%, we double the capacity and add one to maintain an odd size. We then traverse our old array, recalculate the hashes for all entries, and place them into the new bucket array."

---

## 🎴 Slide 6: Data Structure 2: Enrollment Graph (Adjacency List)

* **Slide Title:** Modeling Enrollments via Graph
* **Visuals:** An undirected graph diagram showing student nodes (e.g., `student:S001`) connected to course nodes (e.g., `course:CS101`).
* **Content:**
  * **Graph Model:** Undirected graph representing student-course relationships.
  * **Adjacency List:** Modeled as a dictionary mapping each node to a list of its neighbors.
  * **Collision Prevention:** Node names are prefixed (`student:` and `course:`) to keep the ID namespaces clean.
  * **Edge Insertion:** Enrolling a student in a course adds a bidirectional connection:
    * `student` $\leftrightarrow$ `course`
* **Speaker Notes:**
  > "Our second data structure is the Enrollment Graph. In database systems, relationships are typically modeled with foreign keys. In our application, we represent them as an undirected graph. Nodes represent students and courses, separated by prefixes. When a student enrolls in a course, a bidirectional edge is created in our adjacency lists."

---

## 🎴 Slide 7: Graph Algorithm: Breadth-First Search (BFS)

* **Slide Title:** BFS Enrollment Pathfinding
* **Visuals:** A flowchart showing BFS queue traversal (FIFO queue, Visited set, Parent dictionary).
* **Content:**
  * **Objective:** Find the shortest enrollment path connecting two entities.
  * **Queue Traversal:** Explores neighbors layer-by-layer.
  * **Visited Set:** Avoids infinite loops from cycles.
  * **Parent Dictionary:** Backtracks from the target to rebuild the path.
* **Code Snippet:**
  ```python
  while front < len(queue):
      current = queue[front]
      front += 1
      if current == target:
          # Rebuild and return shortest path
      for neighbor in self.neighbors(current):
          if neighbor not in visited:
              visited.add(neighbor)
              parent[neighbor] = current
              queue.append(neighbor)
  ```
* **Speaker Notes:**
  > "To inspect paths in our graph, we implemented Breadth-First Search. This allows us to answer questions like: 'How is student A connected to course B?' or 'Which students share enrollment paths?'. The algorithm uses a queue to traverse node levels, a visited set to avoid cycles, and records parent links to reconstruct the shortest connection path."

---

## 🎴 Slide 8: Data Structure 3: Grade Decision Tree

* **Slide Title:** Grade Evaluation Decision Tree
* **Visuals:** A binary decision tree starting at root Node 90 branching down to nodes 80, 70, 60, and leaves (A, B, C, D, F).
* **Content:**
  * **Data Representation:** Binary decision tree of threshold evaluation nodes.
  * **Branch Nodes:** Contain score thresholds (e.g., 90) and branches.
    * `yes_branch`: Score $\ge$ threshold.
    * `no_branch`: Score $<$ threshold.
  * **Leaf Nodes:** Contain the final result (Grade, GPA, and description).
  * **Recursive Descent:** Program traverses the tree until a leaf node is reached.
* **Speaker Notes:**
  > "Our third structure is the Grade Decision Tree. Instead of using generic code blocks, we model grade translation as a binary decision tree. The tree starts at the root threshold of 90. If the student's score is 90 or above, it follows the 'yes' branch to leaf Grade A. If below 90, it proceeds down the 'no' branch to check lower thresholds recursively until it lands on the correct grade leaf."

---

## 🎴 Slide 9: Integration Workflow: Student Enrollment & GPA Calculation

* **Slide Title:** Data Operations Integration
* **Visuals:** A sequence layout illustrating the steps to calculate a credit-weighted GPA.
* **Content:**
  1. Retrieve student records from the `HashTable` ($O(1)$).
  2. Find enrolled courses by querying neighbors in the `Graph` ($O(1)$).
  3. Look up course credit weights from the `HashTable` ($O(1)$).
  4. Pass scores to the `GradeDecisionTree` to compute the course GPA.
  5. Calculate the cumulative GPA:
  $$\text{Cumulative GPA} = \frac{\sum (\text{GPA}_i \times \text{Credits}_i)}{\sum \text{Credits}_i}$$
* **Speaker Notes:**
  > "This slide illustrates how the structures integrate. When calculating a student's GPA, we fetch the Student object from the HashTable, retrieve their course list from the Graph, fetch the course credits, calculate each course's GPA using the Decision Tree, and finally compute the credit-weighted cumulative GPA."

---

## 🎴 Slide 10: Persistent Storage: Zero-Dependency File Database

* **Slide Title:** Atomic File Persistence
* **Visuals:** A diagram showing memory objects writing to `.data.py.tmp`, followed by an atomic replacement step to update `data.py`.
* **Content:**
  * **Concept:** Saves all records to disk without any SQL database engine.
  * **Python Serialization:** Converts records into Python-formatted structures using `pformat`.
  * **Atomic Write Safety:**
    1. System writes changes to a temporary file (`.data.py.tmp`).
    2. File is swapped atomically to overwrite `data.py`.
    3. Prevents database corruption in the event of an unexpected crash.
* **Speaker Notes:**
  > "To keep the project clean and portable, we avoided external databases. Instead, we serialize our data memory tables into formatted Python strings. To prevent data corruption during writes, we use an atomic save procedure: the data is written to a temporary file first, and only on a successful write is the original file replaced."

---

## 🎴 Slide 11: Console Demo Scenarios (RBAC)

* **Slide Title:** Role-Based Access Scenarios
* **Visuals:** A table listing the roles and their available features.
* **Content:**
  | Role | Username / PW | Features |
  | :--- | :--- | :--- |
  | **Admin** | `admin` / `admin123` | Insert/Delete/Update Students & Courses, Enrollments, BFS Paths |
  | **Teacher** | `teacher` / `teacher123` | View Students/Courses, Enroll Students, Record Scores |
  | **Student** | `student` / `student123` | View Information, Enrolled Courses, GPA, and Report Card |
  | **Parent** | `parent` / `parent123` | View Student Information, GPA, and Academic Report |
* **Speaker Notes:**
  > "Our user interface supports Role-Based Access Control. Administrators have full system controls, Teachers can enroll students and enter scores, while Students and Parents can access and inspect academic report cards. Each user has a tailored workspace."

---

## 🎴 Slide 12: Project Accomplishments & Future Work

* **Slide Title:** Accomplishments & Future Roadmap
* **Visuals:** Two sections: Left (Accomplished), Right (Future Roadmap).
* **Content:**
  * **What We Accomplished:**
    * Completed custom, textbook-standard implementations of all three data structures.
    * Dynamic HashTable resizing maintains search speeds as records grow.
    * Enforced validation constraints to ensure ID integrity.
    * Interactive console system with zero third-party dependencies.
  * **Future Improvements:**
    * Upgrade file persistence from `data.py` script writes to secure JSON files.
    * Replace plaintext password storage with cryptographic hashing (e.g. `hashlib.sha256`).
* **Speaker Notes:**
  > "In summary, we successfully built and verified all data structures, optimized the Hash Table with dynamic resizing, and verified our pathfinding algorithms. For future steps, we plan to transition the database serialization from Python files to JSON, and implement cryptographic password hashing to enhance user security."

---

## 🎴 Slide 13: Q&A & Conclusion

* **Slide Title:** Questions & Answers
* **Visuals:** Large text saying "Thank You!" alongside team contact details.
* **Content:**
  * **Project Repository:** [Github/ITE-DSA-Management]
  * **Team Roles Summary:**
    * *Hash Table:* [Name]
    * *Graph & BFS:* [Name]
    * *Decision Tree:* [Name]
    * *Integration & Presenter:* [Leader Name]
* **Speaker Notes:**
  > "Thank you Dr. Vantha and everyone for your time. We are now open to any questions you may have about our code, implementations, or algorithmic details."
