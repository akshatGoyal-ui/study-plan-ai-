"""Python-side checks for student inputs and generated timetables."""

from collections import defaultdict
from datetime import date, datetime, time
from typing import Any

import pandas as pd

from modules.priority_analyzer import parse_date
from config import SESSION_TYPES

REQUIRED_COLUMNS = ("Date", "Start Time", "End Time", "Subject", "Topic/Task", "Session Type")


def _time(value: Any) -> time | None:
    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)
    if isinstance(value, datetime):
        return value.time().replace(second=0, microsecond=0)
    if isinstance(value, str):
        for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p"):
            try:
                return datetime.strptime(value.strip(), fmt).time()
            except ValueError:
                continue
    return None


def _date(value: Any) -> date | None:
    return parse_date(value)


def validate_profile(profile: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    subjects = profile.get("subjects") or []
    if not subjects:
        issues.append({"check": "Subject coverage", "severity": "error", "message": "Add at least one subject.", "suggestion": "Use Student Information to add a subject and exam date."})
    seen: set[str] = set()
    for index, subject in enumerate(subjects, start=1):
        name = str(subject.get("name", "")).strip()
        exam = _date(subject.get("exam_date"))
        if not name:
            issues.append({"check": "Subject name", "severity": "error", "message": f"Subject {index} has no name.", "suggestion": "Enter a distinct subject name."})
        elif name.casefold() in seen:
            issues.append({"check": "Subject name", "severity": "warning", "message": f"'{name}' is listed more than once.", "suggestion": "Merge duplicate subject entries."})
        seen.add(name.casefold())
        if subject.get("exam_date") in (None, ""):
            issues.append({"check": "Exam date", "severity": "error", "message": f"{name or f'Subject {index}'} has no exam date.", "suggestion": "Enter the exam date or remove the incomplete subject."})
        elif exam is None:
            issues.append({"check": "Exam date", "severity": "error", "message": f"{name or f'Subject {index}'} has an invalid exam date.", "suggestion": "Use a valid calendar date."})
        elif exam < date.today():
            issues.append({"check": "Exam date", "severity": "warning", "message": f"The exam for {name or f'Subject {index}'} is in the past.", "suggestion": "Update the date if this is a future exam."})
        elif exam == date.today():
            issues.append({"check": "Preparation time", "severity": "warning", "message": f"The exam for {name or f'Subject {index}'} is today; no full preparation days remain.", "suggestion": "Use a short focused review only if time allows."})
    try:
        daily_hours = float(profile.get("daily_hours", 0))
    except (TypeError, ValueError):
        daily_hours = 0
    if daily_hours <= 0:
        issues.append({"check": "Available hours", "severity": "error", "message": "Daily study availability must be greater than zero.", "suggestion": "Set a realistic positive number of hours."})
    elif daily_hours > 12:
        issues.append({"check": "Workload", "severity": "warning", "message": f"{daily_hours:g} hours per day is an unusually high study request.", "suggestion": "Consider reducing daily hours and preserving sleep and recovery."})
    start, end = _time(profile.get("preferred_start")), _time(profile.get("preferred_end"))
    if start is None or end is None or start >= end:
        issues.append({"check": "Study window", "severity": "error", "message": "Preferred study start and end times are invalid or reversed.", "suggestion": "Choose a same-day window with start earlier than end."})
    if not profile.get("study_days"):
        issues.append({"check": "Weekly availability", "severity": "error", "message": "No study days are selected.", "suggestion": "Select at least one available day."})
    for index, item in enumerate(profile.get("commitments") or [], start=1):
        busy_start, busy_end = _time(item.get("start")), _time(item.get("end"))
        if busy_start is None or busy_end is None or busy_start >= busy_end:
            issues.append({"check": "Commitment times", "severity": "error", "message": f"Commitment {index} has an invalid or reversed time range.", "suggestion": "Use valid 24-hour times with the end later than the start."})
    return issues


def validate_timetable(
    rows: list[dict[str, Any]] | pd.DataFrame,
    profile: dict[str, Any],
    today: date | None = None,
) -> dict[str, Any]:
    """Return detected issues and a pass count. Break rows count for overlap/window checks, not study-hour totals."""
    today = today or date.today()
    frame = rows.copy() if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    issues: list[dict[str, str]] = []
    profile_issues = validate_profile(profile)
    issues.extend(profile_issues)
    if frame.empty:
        issues.append({"check": "Timetable presence", "severity": "error", "message": "No timetable sessions were provided.", "suggestion": "Generate a local plan, request an API plan, or paste an AI response."})
        return {"issues": issues, "checks_passed": 0, "checks_total": 10 + len(profile_issues), "valid": False, "daily_hours": {}}
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        issues.append({"check": "Required fields", "severity": "error", "message": "Missing timetable fields: " + ", ".join(missing), "suggestion": "Include date, start/end time, subject, task, and session type."})
        return {"issues": issues, "checks_passed": 0, "checks_total": 10 + len(profile_issues), "valid": False, "daily_hours": {}}

    start_window, end_window = _time(profile.get("preferred_start")), _time(profile.get("preferred_end"))
    max_daily = max(0.0, float(profile.get("daily_hours", 0) or 0)) * 60
    study_days = set(profile.get("study_days") or [])
    commitments = profile.get("commitments") or []
    parsed: list[dict[str, Any]] = []
    daily_study: defaultdict[date, float] = defaultdict(float)
    subjects = {str(s.get("name", "")).strip().casefold() for s in profile.get("subjects", []) if str(s.get("name", "")).strip()}

    for idx, row in frame.iterrows():
        d = _date(row.get("Date"))
        start, end = _time(row.get("Start Time")), _time(row.get("End Time"))
        label = str(row.get("Subject", "")).strip()
        typ = str(row.get("Session Type", "Learning")).strip()
        if d is None:
            issues.append({"check": "Date format", "severity": "error", "message": f"Row {idx + 1} has an invalid date.", "suggestion": "Use an ISO date such as YYYY-MM-DD."})
            continue
        if start is None or end is None:
            issues.append({"check": "Time format", "severity": "error", "message": f"Row {idx + 1} has an invalid start or end time.", "suggestion": "Use valid 24-hour times such as 09:30."})
            continue
        start_dt = datetime.combine(d, start)
        end_dt = datetime.combine(d, end)
        duration = (end_dt - start_dt).total_seconds() / 60
        if duration <= 0:
            issues.append({"check": "Duration", "severity": "error", "message": f"Row {idx + 1} has zero/negative duration or end before start.", "suggestion": "Set an end time after the start time on the same date."})
            continue
        parsed.append({"row": idx + 1, "date": d, "start": start_dt, "end": end_dt, "subject": label, "type": typ, "duration": duration})
        if typ not in SESSION_TYPES:
            issues.append({"check": "Session type", "severity": "warning", "message": f"Row {idx + 1} has an unrecognized session type '{typ}'.", "suggestion": "Use Learning, Practice, Revision, Mock Test, or Break."})
        if typ.casefold() != "break":
            daily_study[d] += duration
            if not label:
                issues.append({"check": "Subject coverage", "severity": "error", "message": f"Row {idx + 1} has no subject.", "suggestion": "Assign each study session to a subject."})
            elif subjects and label.casefold() not in subjects:
                issues.append({"check": "Subject coverage", "severity": "warning", "message": f"Row {idx + 1} refers to unknown subject '{label}'.", "suggestion": "Use a subject from the student profile."})
        if start_window and end_window and (start < start_window or end > end_window):
            issues.append({"check": "Study window", "severity": "error", "message": f"Row {idx + 1} falls outside preferred study hours.", "suggestion": "Move this session inside the selected study window."})
        if study_days and d.strftime("%A") not in study_days:
            issues.append({"check": "Weekly availability", "severity": "error", "message": f"Row {idx + 1} is scheduled on an unavailable day ({d.strftime('%A')}).", "suggestion": "Move it to a selected study day."})
        for item in commitments:
            weekday = item.get("day", "Every day")
            if weekday not in ("Every day", d.strftime("%A")):
                continue
            busy_start, busy_end = _time(item.get("start")), _time(item.get("end"))
            if busy_start and busy_end:
                c_start, c_end = datetime.combine(d, busy_start), datetime.combine(d, busy_end)
                if start_dt < c_end and c_start < end_dt:
                    issues.append({"check": "Commitments", "severity": "error", "message": f"Row {idx + 1} conflicts with commitment '{item.get('activity', 'commitment')}'.", "suggestion": "Move the session outside the commitment."})

    by_date: defaultdict[date, list[dict[str, Any]]] = defaultdict(list)
    for session in parsed:
        by_date[session["date"]].append(session)
    for d, sessions in by_date.items():
        ordered = sorted(sessions, key=lambda x: x["start"])
        for left, right in zip(ordered, ordered[1:]):
            if right["start"] < left["end"]:
                issues.append({"check": "Overlaps", "severity": "error", "message": f"Sessions on {d.isoformat()} overlap (rows {left['row']} and {right['row']}).", "suggestion": "Shift one session so the two time ranges do not intersect."})
        total = daily_study[d]
        if total > max_daily + 0.01:
            issues.append({"check": "Daily limit", "severity": "error", "message": f"{d.isoformat()} has {total / 60:.1f} study hours; the daily limit is {max_daily / 60:.1f}.", "suggestion": "Reduce or redistribute study sessions."})
        if total > 10 * 60:
            issues.append({"check": "Excessive workload", "severity": "warning", "message": f"{d.isoformat()} contains more than 10 hours of study.", "suggestion": "Spread this workload across more days."})

    if not parsed:
        issues.append({"check": "Valid sessions", "severity": "error", "message": "No rows have valid dates and times.", "suggestion": "Correct the date/time values and try again."})
    # Cross-check subjects against the timetable and flag exams with no remaining prep days.
    covered = {x["subject"].casefold() for x in parsed if x["type"].casefold() != "break"}
    for name in sorted(subjects - covered):
        issues.append({"check": "Subject coverage", "severity": "warning", "message": f"No study session is planned for {name}.", "suggestion": "Add at least one session for every subject."})
    for subject in profile.get("subjects", []):
        exam = _date(subject.get("exam_date"))
        if exam and (exam - today).days <= 1 and subject.get("name", "").casefold() not in covered:
            issues.append({"check": "Preparation time", "severity": "warning", "message": f"{subject.get('name')} has little or no preparation time before its exam.", "suggestion": "Prioritize a short focused review and confirm the exam date."})

    checks_total = 10
    checks_with_issues = {issue["check"] for issue in issues}
    checks_passed = max(0, checks_total - len(checks_with_issues))
    return {"issues": issues, "checks_passed": checks_passed, "checks_total": checks_total, "valid": not any(i["severity"] == "error" for i in issues), "daily_hours": {d.isoformat(): round(m / 60, 2) for d, m in daily_study.items()}}
