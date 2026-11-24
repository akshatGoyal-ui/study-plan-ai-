import unittest

from modules.evaluation import run_scenarios


class ScenarioTests(unittest.TestCase):
    def test_all_scenarios_execute_actual_validation(self):
        results = run_scenarios()
        self.assertEqual(len(results), 12)
        self.assertTrue(all(row["Pass/Fail"] == "PASS" for row in results), results)


if __name__ == "__main__":
    unittest.main()
