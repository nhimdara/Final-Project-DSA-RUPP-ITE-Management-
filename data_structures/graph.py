from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass, field

from models.course import Course
from models.department import Department
from models.student import Student


@dataclass(slots=True)
class Graph:
    adjacency: dict[str, set[str]] = field(default_factory=dict)

    def add_vertex(self, vertex: str) -> None:
        self.adjacency.setdefault(vertex, set())

    def add_edge(self, source: str, target: str) -> None:
        self.add_vertex(source)
        self.add_vertex(target)
        self.adjacency[source].add(target)

    def neighbors(self, vertex: str) -> list[str]:
        return sorted(self.adjacency.get(vertex, set()))

    def vertices(self) -> list[str]:
        return sorted(self.adjacency)

    def breadth_first(self, start: str) -> list[str]:
        if start not in self.adjacency:
            return []
        visited = {start}
        queue: deque[str] = deque([start])
        order: list[str] = []
        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in self.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def has_path(self, source: str, target: str) -> bool:
        return target in self.breadth_first(source)

    def as_dict(self) -> dict[str, list[str]]:
        return {vertex: self.neighbors(vertex) for vertex in self.vertices()}


def build_academic_graph(
    departments: Iterable[Department],
    courses: Iterable[Course],
    students: Iterable[Student],
) -> Graph:
    graph = Graph()
    graph.add_vertex("University")

    for department in departments:
        department_label = f"Department:{department.name}"
        graph.add_edge("University", department_label)

    for course in courses:
        department_label = f"Department:{course.department_name}"
        course_label = f"Course:{course.code}"
        graph.add_edge(department_label, course_label)

    for student in students:
        department_label = f"Department:{student.department_name}"
        student_label = f"Student:{student.id}"
        graph.add_edge(department_label, student_label)

    return graph
