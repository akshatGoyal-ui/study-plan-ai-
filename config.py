"""Shared application configuration."""

from pathlib import Path

APP_NAME = "StudyPlan AI"
TEAM_NAME = "PromptPioneers"
TEAM_LEADER = "Saksham Kumar"
PROJECT_TITLE = "AI-Powered Timetable and Study Plan Generator"
PROJECT_DIR = Path(__file__).resolve().parent
DIFFICULTIES = {"Easy": 2, "Medium": 5, "Hard": 8}
PRIORITIES = {"Low": 2, "Medium": 5, "High": 8}
SESSION_TYPES = ("Learning", "Practice", "Revision", "Mock Test", "Break")
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
