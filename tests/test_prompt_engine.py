import unittest

from modules.ai_service import parse_timetable_response
from modules.prompt_engine import PROMPT_FILES, build_prompt, get_template


class PromptEngineTests(unittest.TestCase):
    def test_versions_are_separate_and_load(self):
        self.assertEqual(len(PROMPT_FILES), 3)
        for version in PROMPT_FILES:
            self.assertTrue(get_template(version))

    def test_profile_is_inserted(self):
        prompt = build_prompt("V3 – Optimized", {"student_name": "Test Person"})
        self.assertIn("Test Person", prompt)
        self.assertNotIn("{{STUDENT_DATA}}", prompt)

    def test_json_timetable_is_parsed(self):
        response = '{"timetable":[{"date":"2026-12-01","start_time":"09:00","end_time":"09:50","subject":"Math","topic_task":"Review","session_type":"Revision","duration_minutes":50}]}'
        frame = parse_timetable_response(response)
        self.assertEqual(frame.iloc[0]["Subject"], "Math")
        self.assertEqual(frame.iloc[0]["Duration (minutes)"], 50)

    def test_malformed_ai_response_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_timetable_response("Not a timetable")


if __name__ == "__main__":
    unittest.main()
