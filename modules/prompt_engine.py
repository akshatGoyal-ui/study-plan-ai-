"""Versioned prompt construction, comparison and iteration metadata."""

import difflib
import json
from pathlib import Path
from typing import Any

from config import PROJECT_DIR

PROMPT_FILES = {"V1 – Baseline": "prompt_v1.txt", "V2 – Constraint-aware": "prompt_v2.txt", "V3 – Optimized": "prompt_v3.txt"}


def get_template(version: str) -> str:
    filename = PROMPT_FILES.get(version)
    if not filename:
        raise ValueError(f"Unknown prompt version: {version}")
    return (PROJECT_DIR / "prompts" / filename).read_text(encoding="utf-8")


def build_prompt(version: str, profile: dict[str, Any]) -> str:
    payload = json.dumps(profile, ensure_ascii=False, indent=2, default=str)
    return get_template(version).replace("{{STUDENT_DATA}}", payload)


def compare_prompts(first: str, second: str) -> str:
    return "\n".join(difflib.unified_diff(first.splitlines(), second.splitlines(), fromfile="selected", tofile="next version", lineterm=""))


def iteration_log() -> list[dict[str, str]]:
    return [
        {"version": "V1 – Baseline", "changes": "Basic timetable generation from the student profile.", "reason": "Establish a minimal baseline prompt.", "expected": "A timetable broadly matched to the submitted subjects and dates.", "observations": "Pending until evaluated with real model outputs."},
        {"version": "V2 – Constraint-aware", "changes": "Added exam proximity, difficulty and priority, weekly availability, study window, breaks, commitments, and non-overlap rules.", "reason": "Make scheduling constraints explicit and improve prioritization.", "expected": "Fewer scheduling conflicts and better allocation to urgent or difficult subjects.", "observations": "Pending until evaluated with real model outputs."},
        {"version": "V3 – Optimized", "changes": "Added a strict schema, time validation, coverage, revision and practice allocation, overload handling, assumptions, conflict detection, and error handling.", "reason": "Make outputs parseable and robust to incomplete data and tight schedules.", "expected": "More verifiable output with clearer coverage and constraint handling.", "observations": "Pending until evaluated with real model outputs."},
    ]
