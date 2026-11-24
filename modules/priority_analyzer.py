"""Transparent, deterministic exam priority scoring."""

from datetime import date, datetime
from typing import Any

from config import DIFFICULTIES, PRIORITIES


def parse_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return date.fromisoformat(value.strip()[:10])
        except ValueError:
            for fmt in ("%d/%m/%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(value.strip(), fmt).date()
                except ValueError:
                    continue
    return None


def analyze_subjects(subjects: list[dict[str, Any]], today: date | None = None) -> list[dict[str, Any]]:
    """Score using urgency (45%), difficulty (30%), and user priority (25%)."""
    today = today or date.today()
    analyzed = []
    for subject in subjects:
        name = str(subject.get("name", "")).strip()
        exam = parse_date(subject.get("exam_date"))
        difficulty = str(subject.get("difficulty", "Medium"))
        priority = str(subject.get("priority", "Medium"))
        if not name or exam is None:
            continue
        days = (exam - today).days
        # Nearer exams rise sharply; past exams remain visible with maximum urgency.
        urgency = 10.0 if days <= 0 else max(1.0, min(10.0, 30.0 / (days + 1)))
        difficulty_value = float(DIFFICULTIES.get(difficulty, DIFFICULTIES["Medium"]))
        priority_value = float(PRIORITIES.get(priority, PRIORITIES["Medium"]))
        score = 0.45 * urgency + 0.30 * difficulty_value + 0.25 * priority_value
        analyzed.append({
            **subject,
            "name": name,
            "exam_date_parsed": exam,
            "days_remaining": days,
            "urgency_component": round(urgency, 2),
            "difficulty_component": difficulty_value,
            "priority_component": priority_value,
            "priority_score": round(score, 2),
        })
    return sorted(analyzed, key=lambda row: (row["days_remaining"], -row["priority_score"]))


def score_formula() -> str:
    return "Score = 0.45 × urgency + 0.30 × difficulty + 0.25 × user priority (each component scaled 1–10). Urgency = min(10, max(1, 30 ÷ (days remaining + 1))); exams today or earlier receive urgency 10."
