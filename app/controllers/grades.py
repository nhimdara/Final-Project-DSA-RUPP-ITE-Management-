def grade_for(score: float) -> tuple[str, float]:
    if score >= 90:
        return "A", 4.0
    if score >= 80:
        return "B", 3.0
    if score >= 70:
        return "C", 2.0
    if score >= 60:
        return "D", 1.0
    return "F", 0.0
