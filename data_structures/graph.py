"""Undirected graph used to connect students and courses."""

from __future__ import annotations

from collections import deque


class Graph:
    def __init__(self) -> None:
        self.adjacency: dict[str, set[str]] = {}

    def add_vertex(self, vertex: str) -> None:
        self.adjacency.setdefault(vertex, set())

    def insert(self, vertex: str) -> None:
        """Insert a vertex into the graph."""
        self.add_vertex(vertex)

    def add_edge(self, first: str, second: str) -> None:
        self.add_vertex(first)
        self.add_vertex(second)
        self.adjacency[first].add(second)
        self.adjacency[second].add(first)

    def has_edge(self, first: str, second: str) -> bool:
        return second in self.adjacency.get(first, set())

    def remove_edge(self, first: str, second: str) -> None:
        self.adjacency.get(first, set()).discard(second)
        self.adjacency.get(second, set()).discard(first)

    def remove_vertex(self, vertex: str) -> bool:
        if vertex not in self.adjacency:
            return False
        for neighbor in self.adjacency.pop(vertex, set()):
            self.adjacency[neighbor].discard(vertex)
        return True

    def delete(self, vertex: str) -> bool:
        """Delete a vertex and all of its relationships."""
        return self.remove_vertex(vertex)

    def search(self, vertex: str) -> bool:
        """Return True when a vertex exists."""
        return vertex in self.adjacency

    def update(self, old_vertex: str, new_vertex: str) -> bool:
        """Rename a vertex without losing its relationships."""
        if old_vertex not in self.adjacency or new_vertex in self.adjacency:
            return False
        neighbors = self.adjacency.pop(old_vertex)
        self.adjacency[new_vertex] = neighbors
        for neighbor in neighbors:
            self.adjacency[neighbor].discard(old_vertex)
            self.adjacency[neighbor].add(new_vertex)
        return True

    def neighbors(self, vertex: str) -> list[str]:
        return sorted(self.adjacency.get(vertex, set()))

    def breadth_first(self, start: str) -> list[str]:
        if start not in self.adjacency:
            return []
        visited = {start}
        queue = deque([start])
        order: list[str] = []
        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in self.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def has_path(self, first: str, second: str) -> bool:
        return second in self.breadth_first(first)

    def display(self) -> dict[str, list[str]]:
        """Return a readable copy of the graph."""
        return {
            vertex: self.neighbors(vertex)
            for vertex in sorted(self.adjacency)
        }
