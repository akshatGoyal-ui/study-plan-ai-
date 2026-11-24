"""Executable deterministic validation scenarios, separate from subjective AI review."""

import json
from datetime import date, timedelta
from typing import Any, Callable

from modules.constraint_validator import validate_profile, validate_timetable
from modules.timetable_generator import generate_local_plan


def _profile(today: date, subjects: list[dict[str, Any]] | None = None, **overrides: Any) -> dict[str, Any]:
    value = {
        "student_name": "Evaluation Student",
        "subjects": subjects if subjects is not None else [
            {"name": "Algorithms", "exam_date": today + timedelta(days=21), "difficulty": "Medium", "priority": "High"},
            {"name": "Databases", "exam_date": today + timedelta(days=28), "difficulty": "Easy", "priority": "Medium"},
        ],
        "daily_hours": 3, "preferred_start": "09:00", "preferred_end": "20:00",
        "session_minutes": 50, "break_minutes": 10, "study_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "commitments": [],
    }
    value.update(overrides)
    return value


def run_scenarios(today: date | None = None) -> list[dict[str, Any]]:
    today = today or date.today()
    definitions: list[tuple[str, str, str, Callable[[], tuple[Any, str, bool]]]] = []

    def add(test_id: str, case_input: str, expected: str, fn: Callable[[], tuple[Any, str, bool]]) -> None:
        definitions.append((test_id, case_input, expected, fn))

    def scenario_normal():
        p = _profile(today)
        plan = generate_local_plan(p, today)
        result = validate_timetable(plan, p, today)
        ok = result["valid"] and not plan.empty
        return p, f"{len(plan)} sessions; validator valid={result['valid']}", ok

    add("TC-01", "Normal profile with two dated subjects", "A non-empty local timetable passes the Python constraint validator.", scenario_normal)

    def scenario_hard():
        subjects = [{"name": n, "exam_date": today + timedelta(days=d), "difficulty": "Hard", "priority": "High"} for n, d in (("AI", 10), ("Networks", 14), ("Security", 20))]
        p = _profile(today, subjects, daily_hours=2)
        plan = generate_local_plan(p, today)
        study_rows = plan[plan["Session Type"] != "Break"]
        represented = set(study_rows["Subject"])
        ok = not study_rows.empty and represented == {"AI", "Networks", "Security"} and all(x["difficulty"] == "Hard" for x in p["subjects"])
        return p, f"{len(study_rows)} study sessions; all three hard subjects represented={represented == {'AI','Networks','Security'}}", ok

    add("TC-02", "Three difficult, high-priority subjects", "The local plan includes study sessions for AI, Networks, and Security.", scenario_hard)

    def scenario_tomorrow():
        p = _profile(today, [{"name": "Physics", "exam_date": today + timedelta(days=1), "difficulty": "Hard", "priority": "High"}])
        plan = generate_local_plan(p, today)
        ok = not plan.empty and set(plan["Date"]) == {today.isoformat()}
        return p, f"{len(plan)} session/break rows dated today", ok

    add("TC-03", "One hard subject with an exam tomorrow", "At least one session is scheduled today, before tomorrow's exam.", scenario_tomorrow)

    def scenario_limited():
        p = _profile(today, daily_hours=1, session_minutes=45, break_minutes=10)
        plan = generate_local_plan(p, today)
        result = validate_timetable(plan, p, today)
        ok = bool(result["daily_hours"]) and max(result["daily_hours"].values()) <= 1 and not any(i["check"] == "Daily limit" for i in result["issues"])
        return p, f"max planned study/day={max(result['daily_hours'].values(), default=0):g}h; daily-limit issue={not ok}", ok

    add("TC-04", "One available study hour per day", "No scheduled day's study time exceeds one hour.", scenario_limited)

    def scenario_many():
        subjects = [{"name": f"Subject {i}", "exam_date": today + timedelta(days=14 + i), "difficulty": "Medium", "priority": "Medium"} for i in range(1, 13)]
        p = _profile(today, subjects)
        plan = generate_local_plan(p, today)
        study_rows = plan[plan["Session Type"] != "Break"]
        scheduled_subjects = set(study_rows["Subject"]) if not study_rows.empty else set()
        ok = not study_rows.empty and scheduled_subjects.issubset({s["name"] for s in subjects})
        return p, f"{len(subjects)} input subjects; {len(scheduled_subjects)} scheduled subjects (break rows excluded)", ok

    add("TC-05", "Twelve subjects with staggered exams", "The local planner returns study sessions mapped to the supplied subjects.", scenario_many)

    def scenario_commitment():
        p = _profile(today, commitments=[{"day": "Every day", "start": "09:00", "end": "11:00", "activity": "Class"}])
        plan = generate_local_plan(p, today)
        result = validate_timetable(plan, p, today)
        conflicts = [i for i in result["issues"] if i["check"] == "Commitments"]
        ok = not conflicts and not plan.empty
        return p, f"commitment conflicts detected={len(conflicts)}; local plan starts after class", ok

    add("TC-06", "Daily class commitment from 09:00 to 11:00", "The generated timetable has no overlap with the daily class commitment.", scenario_commitment)

    def scenario_no_dates():
        p = _profile(today, [{"name": "Chemistry", "exam_date": "", "difficulty": "Medium", "priority": "Medium"}])
        issues = validate_profile(p)
        found = any(i["check"] == "Exam date" for i in issues)
        return p, f"missing exam date detected={found}", found

    add("TC-07", "Subject provided without an exam date", "Profile validation detects and reports a missing exam date.", scenario_no_dates)

    def scenario_zero_hours():
        p = _profile(today, daily_hours=0)
        issues = validate_profile(p)
        found = any(i["check"] == "Available hours" for i in issues)
        return p, f"zero available hours detected={found}", found

    add("TC-08", "Zero available study hours", "Profile validation reports that daily study hours must be positive.", scenario_zero_hours)

    def scenario_invalid_date():
        p = _profile(today, [{"name": "Biology", "exam_date": "2026-02-30", "difficulty": "Easy", "priority": "Low"}])
        issues = validate_profile(p)
        found = any(i["check"] == "Exam date" and "invalid" in i["message"] for i in issues)
        return p, f"invalid calendar date detected={found}", found

    add("TC-09", "Invalid calendar exam date 2026-02-30", "Profile validation detects the invalid calendar date.", scenario_invalid_date)

    def scenario_overlap():
        p = _profile(today)
        rows = [
            {"Date": today.isoformat(), "Start Time": "09:00", "End Time": "10:00", "Subject": "Algorithms", "Topic/Task": "Review", "Session Type": "Learning"},
            {"Date": today.isoformat(), "Start Time": "09:30", "End Time": "10:30", "Subject": "Databases", "Topic/Task": "Review", "Session Type": "Practice"},
        ]
        result = validate_timetable(rows, p, today)
        found = any(i["check"] == "Overlaps" for i in result["issues"])
        return {"profile": p, "timetable": rows}, f"overlap detected={found}", found

    add("TC-10", "Two timetable sessions overlap by 30 minutes", "Timetable validation detects the 30-minute session overlap.", scenario_overlap)

    def scenario_high_hours():
        p = _profile(today, daily_hours=16)
        issues = validate_profile(p)
        found = any(i["check"] == "Workload" and i["severity"] == "warning" for i in issues)
        return p, f"16-hour request warning detected={found}", found

    add("TC-11", "Extremely high request of 16 study hours/day", "Profile validation warns about the 16-hour daily workload.", scenario_high_hours)

    def scenario_insufficient():
        p = _profile(today, [
            {"name": "Exam Tomorrow", "exam_date": today + timedelta(days=1), "difficulty": "Hard", "priority": "High"},
            {"name": "Later Exam", "exam_date": today + timedelta(days=14), "difficulty": "Easy", "priority": "Low"},
        ])
        rows = [{"Date": today.isoformat(), "Start Time": "09:00", "End Time": "10:00", "Subject": "Later Exam", "Topic/Task": "Review", "Session Type": "Revision"}]
        result = validate_timetable(rows, p, today)
        found = any(i["check"] == "Preparation time" for i in result["issues"])
        return {"profile": p, "timetable": rows}, f"little/no preparation warning detected={found}", found

    add("TC-12", "Exam tomorrow with no session for that subject", "Timetable validation warns about the omitted subject with an exam tomorrow.", scenario_insufficient)

    results = []
    for test_id, case_input, expected_output, fn in definitions:
        try:
            actual_input, actual_output, passed = fn()
            results.append({"Test ID": test_id, "Input": case_input + "\n" + json.dumps(actual_input, default=str, ensure_ascii=False), "Expected Output": expected_output, "Actual Output": actual_output, "Pass/Fail": "PASS" if passed else "FAIL"})
        except Exception as exc:
            results.append({"Test ID": test_id, "Input": case_input, "Expected Output": expected_output, "Actual Output": f"Execution error: {type(exc).__name__}: {exc}", "Pass/Fail": "FAIL"})
    return results
