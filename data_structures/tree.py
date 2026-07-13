from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class GradeResult:
    score: float
    grade: str
    gpa: float
    message: str


@dataclass(slots=True)
class DecisionNode:
    threshold: Optional[float] = None
    grade: Optional[str] = None
    gpa: Optional[float] = None
    message: str = ""
    passed: Optional["DecisionNode"] = None
    failed: Optional["DecisionNode"] = None

    def decide(self, score: float) -> GradeResult:
        if self.grade is not None:
            if self.gpa is None:
                raise ValueError("A grade decision must include a GPA value.")
            return GradeResult(
                score=score, grade=self.grade, gpa=self.gpa, message=self.message
            )
        if self.threshold is None:
            raise ValueError("Decision node must have either a threshold or a grade.")
        next_node = self.passed if score >= self.threshold else self.failed
        if next_node is None:
            raise ValueError("Decision tree is incomplete.")
        return next_node.decide(score)


class GradeDecisionTree:
    """Tree decision logic from the diagram: score thresholds produce grades."""

    def __init__(self) -> None:
        self.root = DecisionNode(
            threshold=90,
            passed=DecisionNode(grade="A", gpa=4.0, message="Excellent"),
            failed=DecisionNode(
                threshold=80,
                passed=DecisionNode(grade="B", gpa=3.0, message="Very good"),
                failed=DecisionNode(
                    threshold=70,
                    passed=DecisionNode(grade="C", gpa=2.0, message="Good"),
                    failed=DecisionNode(
                        threshold=60,
                        passed=DecisionNode(
                            grade="D", gpa=1.0, message="Needs improvement"
                        ),
                        failed=DecisionNode(grade="F", gpa=0.0, message="Fail"),
                    ),
                ),
            ),
        )

    def calculate(self, score: float) -> GradeResult:
        if score < 0 or score > 100:
            raise ValueError("Score must be between 0 and 100.")
        return self.root.decide(score)
