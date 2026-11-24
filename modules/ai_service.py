"""Optional OpenAI adapter and tolerant timetable response parser."""

import json
import os
import re
from typing import Any

import pandas as pd

from config import SESSION_TYPES
from modules.prompt_engine import build_prompt

ALIASES = {
    "date": "Date", "day": "Date", "start": "Start Time", "start time": "Start Time", "start_time": "Start Time",
    "end": "End Time", "end time": "End Time", "end_time": "End Time", "subject": "Subject",
    "task": "Topic/Task", "topic": "Topic/Task", "topic/task": "Topic/Task", "topic_task": "Topic/Task", "task/topic": "Topic/Task",
    "session type": "Session Type", "session_type": "Session Type", "type": "Session Type", "duration": "Duration (minutes)", "duration (minutes)": "Duration (minutes)", "duration_minutes": "Duration (minutes)",
}


def resolve_api_key(secrets: Any = None) -> str | None:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if key:
        return key
    if secrets is not None:
        try:
            value = secrets.get("OPENAI_API_KEY", "")
        except (KeyError, AttributeError, TypeError):
            value = ""
        if value:
            return str(value).strip() or None
    return None


def _extract_payload(text: str) -> Any:
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.IGNORECASE | re.DOTALL)
    if match:
        cleaned = match.group(1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    lines = [line.strip() for line in cleaned.splitlines() if line.strip().startswith("|")]
    if len(lines) >= 3:
        header = [x.strip() for x in lines[0].strip("|").split("|")]
        data = []
        for line in lines[2:]:
            values = [x.strip() for x in line.strip("|").split("|")]
            if len(values) == len(header):
                data.append(dict(zip(header, values)))
        if data:
            return data
    raise ValueError("Could not find a JSON timetable or Markdown table. Paste the complete response and try again.")


def parse_timetable_response(text: str) -> pd.DataFrame:
    payload = _extract_payload(text)
    if isinstance(payload, dict):
        payload = payload.get("timetable", payload.get("sessions", payload.get("schedule")))
    if not isinstance(payload, list) or not payload:
        raise ValueError("The response must contain a non-empty list under 'timetable' or 'sessions'.")
    normalized = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Every timetable entry must be an object with named fields.")
        row = {}
        for key, value in item.items():
            canonical = ALIASES.get(str(key).strip().casefold())
            if canonical:
                row[canonical] = value
        missing = [k for k in ("Date", "Start Time", "End Time", "Subject", "Topic/Task") if not row.get(k)]
        if missing:
            raise ValueError("A timetable entry is missing: " + ", ".join(missing))
        row.setdefault("Session Type", "Learning")
        if row["Session Type"] not in SESSION_TYPES:
            row["Session Type"] = "Learning"
        row.setdefault("Duration (minutes)", "")
        normalized.append(row)
    frame = pd.DataFrame(normalized)
    for index, row in frame.iterrows():
        try:
            from datetime import datetime
            start = datetime.strptime(str(row["Start Time"]).strip(), "%H:%M")
            end = datetime.strptime(str(row["End Time"]).strip(), "%H:%M")
            if not str(row["Duration (minutes)"]).strip():
                frame.at[index, "Duration (minutes)"] = int((end - start).total_seconds() // 60)
        except ValueError:
            # Keep malformed time values so the validator can report precise row errors.
            if not str(row["Duration (minutes)"]).strip():
                frame.at[index, "Duration (minutes)"] = 0
    return frame[["Date", "Start Time", "End Time", "Subject", "Topic/Task", "Session Type", "Duration (minutes)"]]


def generate_with_api(profile: dict[str, Any], api_key: str, version: str = "V3 – Optimized") -> str:
    """Call the optional API. Missing package/network/model errors are surfaced to the UI."""
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("The OpenAI package is not installed. Install dependencies from requirements.txt.") from exc
    prompt = build_prompt(version, profile)
    try:
        response = OpenAI(api_key=api_key).chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = response.choices[0].message.content
    except Exception as exc:
        raise RuntimeError(f"OpenAI request failed: {exc}") from exc
    if not content or not content.strip():
        raise RuntimeError("The API returned an empty response.")
    return content
