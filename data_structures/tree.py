from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class GradeResult:
    score: float
    grade: str
    message: str


@dataclass(slots=True)
class DecisionNode:
    threshold: Optional[float] = None
    grade: Optional[str] = None
    message: str = ""
    passed: Optional["DecisionNode"] = None
    failed: Optional["DecisionNode"] = None

    def decide(self, score: float) -> GradeResult:
        if self.grade is not None:
            return GradeResult(score=score, grade=self.grade, message=self.message)
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
            passed=DecisionNode(grade="A", message="Excellent"),
            failed=DecisionNode(
                threshold=80,
                passed=DecisionNode(grade="B", message="Very good"),
                failed=DecisionNode(
                    threshold=70,
                    passed=DecisionNode(grade="C", message="Good"),
                    failed=DecisionNode(
                        threshold=60,
                        passed=DecisionNode(grade="D", message="Needs improvement"),
                        failed=DecisionNode(grade="F", message="Fail"),
                    ),
                ),
            ),
        )

    def calculate(self, score: float) -> GradeResult:
        if score < 0 or score > 100:
            raise ValueError("Score must be between 0 and 100.")
        return self.root.decide(score)
