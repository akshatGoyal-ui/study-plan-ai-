"""Transparent local timetable heuristic; it does not call or imitate an AI model."""

from datetime import date, datetime, time, timedelta
from typing import Any

import pandas as pd

from modules.priority_analyzer import analyze_subjects, parse_date


def _as_time(value: Any, fallback: time) -> time:
    if isinstance(value, time):
        return value
    try:
        return datetime.strptime(str(value), "%H:%M").time()
    except ValueError:
        return fallback


def _minute(value: time) -> int:
    return value.hour * 60 + value.minute


def _hhmm(value: int) -> str:
    return f"{value // 60:02d}:{value % 60:02d}"


def generate_local_plan(profile: dict[str, Any], today: date | None = None) -> pd.DataFrame:
    """Create a deterministic, rule-based draft within each day's declared constraints."""
    today = today or date.today()
    subjects = analyze_subjects(profile.get("subjects", []), today)
    if not subjects:
        raise ValueError("Add at least one subject with a valid exam date before generating a plan.")
    study_days = set(profile.get("study_days") or [])
    if not study_days:
        raise ValueError("Select at least one available study day.")
    daily_hours = float(profile.get("daily_hours") or 0)
    if daily_hours <= 0:
        raise ValueError("Daily study hours must be greater than zero.")
    start = _as_time(profile.get("preferred_start"), time(9, 0))
    end = _as_time(profile.get("preferred_end"), time(21, 0))
    if start >= end:
        raise ValueError("The preferred study start must be earlier than the end.")
    session = max(15, int(profile.get("session_minutes", 50)))
    break_minutes = max(0, int(profile.get("break_minutes", 10)))
    exams = [parse_date(s.get("exam_date")) for s in subjects]
    future_exams = [d for d in exams if d is not None and d > today]
    if not future_exams:
        raise ValueError("No future exam dates remain. Update the exam dates before generating a study timetable.")
    end_date = max(future_exams)
    horizon = max(0, (end_date - today).days)
    if horizon > 365:
        raise ValueError("The local planner supports exams up to 365 days ahead. Adjust the dates or use Prompt/API Mode.")
    commitments = profile.get("commitments") or []
    rows: list[dict[str, Any]] = []
    rotations = {s["name"]: 0 for s in subjects}
    last_subject = None

    for offset in range(horizon):
        day = today + timedelta(days=offset)
        weekday = day.strftime("%A")
        if weekday not in study_days:
            continue
        daily_limit = int(daily_hours * 60)
        available_start, available_end = _minute(start), _minute(end)
        if available_end <= available_start:
            continue
        busy = []
        for item in commitments:
            if item.get("day") not in ("Every day", weekday):
                continue
            c_start, c_end = _as_time(item.get("start"), start), _as_time(item.get("end"), end)
            busy.append((_minute(c_start), _minute(c_end)))
        busy.sort()
        day_used = 0
        cursor = available_start
        gap_index = 0
        while day_used < daily_limit and cursor + session <= available_end:
            while gap_index < len(busy) and busy[gap_index][1] <= cursor:
                gap_index += 1
            conflict = next((b for b in busy[gap_index:] if cursor < b[1] and b[0] < cursor + session), None)
            if conflict:
                cursor = conflict[1]
                continue
            if cursor + session > available_end:
                break
            eligible = [s for s in subjects if (parse_date(s.get("exam_date")) or day) >= day]
            if not eligible:
                break
            # Dynamic urgency is recomputed each day. Rotate ties to avoid one-subject clumping.
            scored = analyze_subjects(eligible, day)
            chosen = max(scored, key=lambda s: (s["priority_score"] - min(rotations[s["name"]], 4) * 0.22, s["priority_score"]))
            if last_subject == chosen["name"] and len(scored) > 1:
                alternatives = [s for s in scored if s["name"] != last_subject]
                chosen = max(alternatives, key=lambda s: s["priority_score"] - min(rotations[s["name"]], 4) * 0.22)
            count = rotations[chosen["name"]]
            cycle = ("Learning", "Practice", "Revision", "Practice", "Revision", "Mock Test")
            kind = cycle[count % len(cycle)]
            subject_exam = parse_date(chosen.get("exam_date"))
            if subject_exam and (subject_exam - day).days <= 2 and kind == "Learning":
                kind = "Revision"
            task = {
                "Learning": f"Review core concepts: {chosen['name']}",
                "Practice": f"Solve practice questions: {chosen['name']}",
                "Revision": f"Quick revision and recall: {chosen['name']}",
                "Mock Test": f"Timed mock test: {chosen['name']}",
            }[kind]
            actual = min(session, daily_limit - day_used)
            if actual < 15:
                break
            row_start, row_end = cursor, cursor + actual
            rows.append({"Date": day.isoformat(), "Start Time": _hhmm(row_start), "End Time": _hhmm(row_end), "Subject": chosen["name"], "Topic/Task": task, "Session Type": kind, "Duration (minutes)": actual})
            day_used += actual
            cursor = row_end
            rotations[chosen["name"]] += 1
            last_subject = chosen["name"]
            if day_used < daily_limit and break_minutes > 0 and cursor + break_minutes < available_end:
                # Insert a break only if it fits and does not run into a commitment.
                if not any(cursor < b_end and b_start < cursor + break_minutes for b_start, b_end in busy):
                    rows.append({"Date": day.isoformat(), "Start Time": _hhmm(cursor), "End Time": _hhmm(cursor + break_minutes), "Subject": "—", "Topic/Task": "Rest break", "Session Type": "Break", "Duration (minutes)": break_minutes})
                    cursor += break_minutes
        # Rotation continues across days; subject assignments are based on due date and score.
    return pd.DataFrame(rows, columns=["Date", "Start Time", "End Time", "Subject", "Topic/Task", "Session Type", "Duration (minutes)"])
