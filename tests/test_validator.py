import unittest
from datetime import date, timedelta

from modules.constraint_validator import validate_profile, validate_timetable


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.today = date.today()
        self.profile = {
            "subjects": [{"name": "Math", "exam_date": self.today + timedelta(days=10), "difficulty": "Hard", "priority": "High"}],
            "daily_hours": 2, "preferred_start": "09:00", "preferred_end": "18:00", "study_days": [self.today.strftime("%A")], "commitments": [],
        }

    def test_overlap_is_reported(self):
        rows = [
            {"Date": self.today.isoformat(), "Start Time": "09:00", "End Time": "10:00", "Subject": "Math", "Topic/Task": "One", "Session Type": "Learning"},
            {"Date": self.today.isoformat(), "Start Time": "09:30", "End Time": "10:30", "Subject": "Math", "Topic/Task": "Two", "Session Type": "Practice"},
        ]
        result = validate_timetable(rows, self.profile)
        self.assertTrue(any(item["check"] == "Overlaps" for item in result["issues"]))

    def test_zero_daily_hours_is_reported(self):
        profile = {**self.profile, "daily_hours": 0}
        self.assertTrue(any(item["check"] == "Available hours" for item in validate_profile(profile)))

    def test_missing_exam_date_is_reported(self):
        profile = {**self.profile, "subjects": [{"name": "Math", "exam_date": ""}]}
        self.assertTrue(any(item["check"] == "Exam date" for item in validate_profile(profile)))

    def test_commitment_conflict_is_reported(self):
        profile = {**self.profile, "commitments": [{"day": "Every day", "start": "09:00", "end": "11:00", "activity": "Class"}]}
        rows = [{"Date": self.today.isoformat(), "Start Time": "09:30", "End Time": "10:00", "Subject": "Math", "Topic/Task": "One", "Session Type": "Learning"}]
        result = validate_timetable(rows, profile)
        self.assertTrue(any(item["check"] == "Commitments" for item in result["issues"]))

    def test_invalid_schedule_never_labeled_valid(self):
        rows = [{"Date": self.today.isoformat(), "Start Time": "09:00", "End Time": "10:00", "Subject": "Math", "Topic/Task": "One", "Session Type": "Learning"}, {"Date": self.today.isoformat(), "Start Time": "09:30", "End Time": "10:30", "Subject": "Math", "Topic/Task": "Two", "Session Type": "Practice"}]
        self.assertFalse(validate_timetable(rows, self.profile)["valid"])


if __name__ == "__main__":
    unittest.main()
