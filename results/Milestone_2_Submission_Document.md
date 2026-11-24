# SCSE4041 Prompt Engineering – Milestone 2 Submission Document

**Team ID:** PE-B65-56  
**Batch:** B65-80  
**Team Name:** PromptPioneers  
**Project Title:** AI-Powered Timetable and Study Plan Generator  
**Team Leader:** Saksham Kumar (S24CSEU2007)

---

## 1. Team Information and Contribution Table

| Enrollment No. | Student Name | Assigned Role & Contributions | Agreement / Sign-off |
| :--- | :--- | :--- | :---: |
| **S24CSEU2007** | **Saksham Kumar (Leader)** | System architecture, deterministic constraint validation engine, OpenAI API integration, and project coordinator. | Agreed |
| **S24CSEU2030** | Team Member 2 | Prompt engineering design, V1/V2/V3 prompt iteration progression, and JSON output schema definition. | Agreed |
| **S24CSEU2003** | Team Member 3 | Test harness implementation, 12 test scenario design (normal/edge/invalid), and iteration log documentation. | Agreed |
| **S24CSEU2002** | Team Member 4 | Priority scoring heuristic development (exam urgency, difficulty, priority), and revision planning module. | Agreed |
| **S24CSEU2005** | Team Member 5 | Streamlit multi-page dashboard UI, student profile forms, Plotly visualizations, and session state handling. | Agreed |
| **S24CSEU0764** | Team Member 6 | Multi-format export manager (CSV/JSON/PDF with ReportLab), reel video demo recording, and technical documentation. | Agreed |

---

## 2. Project Overview & Problem Statement

Creating balanced academic study plans is cognitively demanding for students facing multiple upcoming exams, varying topic proficiencies, and fixed commitments. Standard LLM prompts frequently hallucinate schedules that contain time collisions, break daily workload limits, or ignore imminent deadlines.

**StudyPlan AI** solves this problem by combining an iterative prompt engineering workflow with an independent Python constraint validation engine. The solution enables students to:
- Configure comprehensive academic profiles (subjects, exam dates, difficulty, priorities, commitments).
- View transparent priority metrics based on mathematically formulated urgency.
- Generate collision-free study schedules via OpenAI API Mode or zero-cost Prompt Mode.
- Inspect and compare 3 versioned prompt iterations in a dedicated Prompt Engineering Lab.
- Programmatically validate all AI outputs against strict scheduling rules before reliance.
- Generate spaced revision and mock-test sessions as exam dates approach.
- Export finalized timetables to PDF, CSV, and JSON.

---

## 3. Working Modules Inventory

All modules in the prototype are fully implemented, tested, and operational:
1. **Student Profile Configuration:** Dynamic input forms for subjects, exams, daily study hours, preferred study windows, and recurring commitments.
2. **Exam Urgency & Priority Scoring Engine:** Calculates transparent urgency scores (45% exam proximity, 30% difficulty, 25% personal priority).
3. **AI Study Plan Generator:** Generates comprehensive daily schedules supporting both API Mode (GPT-4o-mini) and Prompt Mode (ChatGPT/Claude/Gemini).
4. **Prompt Engineering Lab:** Interactive prompt viewer with unified diff comparison across V1 Baseline, V2 Constraint-Aware, and V3 Optimized.
5. **Deterministic Timetable Constraint Validator:** Rigorous Python validation checking for overlapping sessions, commitment conflicts, preferred window adherence, and exam coverage gaps.
6. **Revision & Mock-Test Planner:** Automatically suggests targeted revision intervals and practice mocks prior to exam dates.
7. **Automated Testing & Evaluation Suite:** In-app scenario runner executing 12 comprehensive test cases with live pass/fail reporting and CSV export.
8. **Multi-Format Export Manager:** Instant downloadable exports in PDF (via ReportLab), CSV, and JSON formats.

---

## 4. Prompt Engineering Iteration Log

### Version 1: Baseline Prompt (`prompt_v1.txt`)
- **Objective:** Establish a raw baseline for timetable creation without complex constraints.
- **Prompt Structure:** Simple role-based directive asking for a balanced day-wise timetable.
- **Deficiencies Identified:** Unstructured text/markdown tables, overlapping study sessions, lack of consideration for daily limits or recurring commitments.

### Version 2: Constraint-Aware Prompt (`prompt_v2.txt`)
- **Objective:** Introduce explicit scheduling rules and exam proximity weighting.
- **Prompt Structure:** Role directive combined with bulleted constraint specifications (priorities, study windows, break insertions, commitment avoidance).
- **Improvements & Deficiencies:** Significantly reduced time collisions, but output format remained non-standardized (mix of text and tables) preventing automated software ingestion.

### Version 3: Optimized Structured-Output Prompt (`prompt_v3.txt`)
- **Objective:** Ensure deterministic parseability, rigorous input validation, and explicit handling of edge cases.
- **Prompt Structure:** System prompt with strict JSON output schema, mandatory 24-hour time formatting, explicit duration consistency rules, and instructions to flag schedule deficits explicitly.
- **Result:** 100% programmatic parseability and zero hallucinated time formats.

---

## 5. Testing & Evaluation Matrix (12 Test Cases)

| Test ID | Scenario Description | Expected Output | Actual Output | Result |
| :---: | :--- | :--- | :--- | :---: |
| **TC-01** | Normal profile with two dated subjects | Timetable generated and passes validator | 196 sessions; validator valid=True | **PASS** |
| **TC-02** | Three difficult, high-priority subjects | Plan schedules sessions for all hard subjects | 60 study sessions; all three hard subjects represented | **PASS** |
| **TC-03** | One hard subject with an exam tomorrow | Session scheduled today before exam | 7 session/break rows dated today | **PASS** |
| **TC-04** | Strict 1-hour daily study limit | No day exceeds 1 hour of study | max planned study/day=1h; daily-limit issue=False | **PASS** |
| **TC-05** | Twelve subjects with staggered dates | All 12 subjects scheduled proportionally | 12 input subjects; 12 scheduled subjects | **PASS** |
| **TC-06** | Daily recurring commitment (09:00–11:00) | Zero study sessions scheduled during class | commitment conflicts detected=0 | **PASS** |
| **TC-07** | Subject submitted without an exam date | Validation flags missing exam date | missing exam date detected=True | **PASS** |
| **TC-08** | Zero daily study hours entered | Profile validation flags non-positive hours | zero available hours detected=True | **PASS** |
| **TC-09** | Invalid calendar date (2026-02-30) | System rejects invalid calendar date | invalid calendar date detected=True | **PASS** |
| **TC-10** | Two sessions overlapping by 30 minutes | Timetable validator detects collision | overlap detected=True | **PASS** |
| **TC-11** | Unrealistic 16-hour daily study request | System flags excessive cognitive workload | 16-hour request warning detected=True | **PASS** |
| **TC-12** | Exam tomorrow with 0 sessions allocated | System warns of inadequate exam preparation | little/no preparation warning detected=True | **PASS** |

---

## 6. Key Takeaways and Responsible AI Integration

- **Never Trust AI Outputs Blindly:** Generative LLMs frequently make subtle mathematical or scheduling errors. Deterministic Python validation provides an essential verification layer.
- **Clear Prompt Contracts:** Moving from ambiguous narrative prompts to strict JSON schemas dramatically increases system reliability and integration readiness.
- **Accessibility & Transparency:** Offering both local heuristic planning and an external API option ensures the tool remains universally usable without recurring financial or subscription barriers.
