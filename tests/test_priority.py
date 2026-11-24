import unittest
from datetime import date, timedelta

from modules.priority_analyzer import analyze_subjects


class PriorityTests(unittest.TestCase):
    def test_nearer_harder_high_priority_subject_scores_higher(self):
        today = date.today()
        rows = analyze_subjects([
            {"name": "Soon", "exam_date": today + timedelta(days=2), "difficulty": "Hard", "priority": "High"},
            {"name": "Later", "exam_date": today + timedelta(days=30), "difficulty": "Easy", "priority": "Low"},
        ], today)
        self.assertGreater(rows[0]["priority_score"], rows[1]["priority_score"])

    def test_missing_and_invalid_dates_are_skipped(self):
        rows = analyze_subjects([{"name": "No date"}, {"name": "Bad", "exam_date": "not-a-date"}])
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
