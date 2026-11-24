"""Revision and mock-test allocation from exam dates and completed topics."""

from datetime import date, datetime, time, timedelta
from typing import Any

import pandas as pd

from modules.priority_analyzer import analyze_subjects, parse_date


def create_revision_plan(profile: dict[str, Any], today: date | None = None) -> pd.DataFrame:
    today = today or date.today()
    start_value = profile.get("preferred_start", "09:00")
    try:
        start = start_value if isinstance(start_value, time) else datetime.strptime(str(start_value), "%H:%M").time()
    except ValueError:
        start = time(9, 0)
    start_minute = start.hour * 60 + start.minute
    end_value = profile.get("preferred_end", "18:00")
    try:
        end_time = end_value if isinstance(end_value, time) else datetime.strptime(str(end_value), "%H:%M").time()
    except ValueError:
        end_time = time(18, 0)
    end_minute = end_time.hour * 60 + end_time.minute
    session = max(15, int(profile.get("session_minutes", 50)))
    daily_limit = int(float(profile.get("daily_hours") or 0) * 60)
    available_days = set(profile.get("study_days") or [])
    commitments = profile.get("commitments") or []
    capacity: dict[str, int] = {}
    cursors: dict[str, int] = {}
    rows = []
    for subject in analyze_subjects(profile.get("subjects", []), today):
        exam = parse_date(subject.get("exam_date"))
        if exam is None or exam <= today:
            continue
        topics = [x.strip() for x in str(subject.get("completed_topics", "")).replace(",", ";").split(";") if x.strip()]
        focus = topics or [f"Core topics in {subject['name']}"]
        candidates = sorted({max(today, exam - timedelta(days=n)) for n in (7, 3, 1) if exam - timedelta(days=n) >= today})
        candidates = [day for day in candidates if day.strftime("%A") in available_days]
        for index, day in enumerate(candidates):
            key = day.isoformat()
            used = capacity.get(key, 0)
            if used + session > daily_limit:
                continue
            minute = max(start_minute, cursors.get(key, start_minute))
            busy_ranges = []
            for item in commitments:
                if item.get("day") in ("Every day", day.strftime("%A")):
                    try:
                        c_start = datetime.strptime(str(item.get("start")), "%H:%M")
                        c_end = datetime.strptime(str(item.get("end")), "%H:%M")
                        busy_ranges.append((c_start.hour * 60 + c_start.minute, c_end.hour * 60 + c_end.minute))
                    except ValueError:
                        continue
            # Move past any overlapping commitment; repeat in case commitments touch.
            changed = True
            while changed:
                changed = False
                for c_start, c_end in sorted(busy_ranges):
                    if minute < c_end and c_start < minute + session:
                        minute = c_end
                        changed = True
            if minute + session > end_minute or used + session > daily_limit:
                continue
            kind = "Mock Test" if index == len(candidates) - 1 else "Revision"
            if len(candidates) == 1:
                kind = "Mock Test" if (exam - day).days == 1 else "Revision"
            topic = f"Timed mock test: {subject['name']}" if kind == "Mock Test" else f"Quick revision: {focus[min(index, len(focus) - 1)]}"
            rows.append({"Date": day.isoformat(), "Start Time": f"{minute // 60:02d}:{minute % 60:02d}", "End Time": f"{(minute + session) // 60:02d}:{(minute + session) % 60:02d}", "Subject": subject["name"], "Topic/Task": topic, "Session Type": kind, "Duration (minutes)": session})
            capacity[key] = used + session
            cursors[key] = minute + session
    return pd.DataFrame(rows, columns=["Date", "Start Time", "End Time", "Subject", "Topic/Task", "Session Type", "Duration (minutes)"])
