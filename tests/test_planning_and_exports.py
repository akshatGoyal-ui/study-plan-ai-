import json
import unittest
from datetime import date, timedelta

import pandas as pd

from modules.constraint_validator import validate_timetable
from modules.export_manager import plan_json, timetable_csv, timetable_pdf
from modules.revision_planner import create_revision_plan
from modules.timetable_generator import generate_local_plan


class PlanningAndExportTests(unittest.TestCase):
    def setUp(self):
        self.today = date.today()
        self.profile = {
            "student_name": "Test Student",
            "subjects": [{"name": "Math", "exam_date": self.today + timedelta(days=14), "difficulty": "Hard", "priority": "High", "completed_topics": "Algebra; Calculus"}],
            "daily_hours": 2, "preferred_start": "08:00", "preferred_end": "15:00",
            "session_minutes": 50, "break_minutes": 10,
            "study_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "commitments": [{"day": "Every day", "start": "09:00", "end": "11:00", "activity": "Class"}],
        }

    def test_local_plan_respects_commitment_and_weekly_window(self):
        frame = generate_local_plan(self.profile, self.today)
        self.assertFalse(frame.empty)
        self.assertTrue(all(row["End Time"] <= "09:00" or row["Start Time"] >= "11:00" for _, row in frame.iterrows()))
        self.assertTrue(all(date.fromisoformat(day).strftime("%A") in self.profile["study_days"] for day in frame["Date"]))
        self.assertTrue(validate_timetable(frame, self.profile, self.today)["valid"])

    def test_local_plan_rejects_profiles_with_no_upcoming_exams(self):
        profile = {**self.profile, "subjects": [{"name": "Math", "exam_date": self.today, "difficulty": "Hard", "priority": "High"}]}
        with self.assertRaisesRegex(ValueError, "No future exam dates"):
            generate_local_plan(profile, self.today)

    def test_revision_plan_uses_completed_topics_and_valid_times(self):
        frame = create_revision_plan(self.profile, self.today)
        self.assertFalse(frame.empty)
        self.assertTrue(any("Algebra" in task or "Calculus" in task or "mock test" in task.lower() for task in frame["Topic/Task"]))
        self.assertTrue(validate_timetable(frame, self.profile, self.today)["valid"])

    def test_csv_json_and_pdf_exports_have_valid_signatures(self):
        frame = pd.DataFrame([{"Date": self.today.isoformat(), "Start Time": "11:00", "End Time": "11:50", "Subject": "Math", "Topic/Task": "Review", "Session Type": "Revision", "Duration (minutes)": 50}])
        csv_bytes = timetable_csv(frame)
        self.assertTrue(csv_bytes.startswith(b"\xef\xbb\xbfDate"))
        json_value = json.loads(plan_json(self.profile, frame))
        self.assertEqual(json_value["timetable"][0]["Subject"], "Math")
        self.assertTrue(timetable_pdf(frame).startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
