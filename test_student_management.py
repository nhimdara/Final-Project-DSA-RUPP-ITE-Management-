"""Regression tests for the custom data structures and enrollment rules."""

import tempfile
import unittest
from pathlib import Path

from data_structures.student_management import Graph, HashTable, StudentManagementSystem


class HashTableTests(unittest.TestCase):
    def test_collision_insert_search_update_and_delete(self):
        table = HashTable(capacity=1)  # every key must use the same bucket

        table.insert("first", 1)
        table.insert("second", 2)
        table.insert("first", 3)

        self.assertEqual(table.search("first"), 3)
        self.assertEqual(table.search("second"), 2)
        self.assertEqual(len(table), 2)
        self.assertTrue(table.delete("first"))
        self.assertIsNone(table.search("first"))


class GraphTests(unittest.TestCase):
    def test_add_edge_reports_duplicate(self):
        graph = Graph()

        self.assertTrue(graph.add_edge("student:S001", "course:CS101"))
        self.assertFalse(graph.add_edge("student:S001", "course:CS101"))
        self.assertEqual(graph.neighbors("student:S001"), ["course:CS101"])
        self.assertEqual(graph.neighbors("course:CS101"), ["student:S001"])


class EnrollmentTests(unittest.TestCase):
    def test_duplicate_enrollment_has_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            data_file = Path(directory) / "data.py"
            system = StudentManagementSystem(data_file=data_file)

            with self.assertRaisesRegex(ValueError, "already enrolled"):
                system.enroll("S001", "CS101")


if __name__ == "__main__":
    unittest.main()
