"""CSV, JSON and PDF exports for generated study plans."""

from datetime import datetime
import json
from typing import Any

import pandas as pd


def timetable_csv(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8-sig")


def plan_json(profile: dict[str, Any], timetable: pd.DataFrame) -> bytes:
    body = {"student_profile": profile, "timetable": timetable.to_dict(orient="records"), "exported_at": datetime.now().astimezone().isoformat()}
    return json.dumps(body, ensure_ascii=False, indent=2, default=str).encode("utf-8")


def timetable_pdf(frame: pd.DataFrame) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:
        raise RuntimeError("PDF export requires reportlab. Install dependencies from requirements.txt.") from exc
    import io
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=0.45 * inch, leftMargin=0.45 * inch, topMargin=0.45 * inch, bottomMargin=0.45 * inch)
    styles = getSampleStyleSheet()
    content = [Paragraph("StudyPlan AI — Study Timetable", styles["Title"]), Spacer(1, 10)]
    data = [list(frame.columns)]
    for row in frame.fillna("").itertuples(index=False, name=None):
        data.append([Paragraph(str(value), styles["BodyText"]) for value in row])
    table = Table(data, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#DCE5ED")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F7FA")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    content.append(table)
    doc.build(content)
    return buffer.getvalue()
