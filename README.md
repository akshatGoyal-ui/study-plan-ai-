# StudyPlan AI

**AI-Powered Timetable and Study Plan Generator** · SCSE4041 mini-project  
**Team:** PromptPioneers · **Team leader:** Saksham Kumar

StudyPlan AI helps college students organize study time around subjects, examination dates, difficulty, personal priority, available hours, existing commitments, preferred study hours, and break preferences. It combines three prompt-engineering iterations with deterministic Python scoring and timetable validation.

## Problem statement

Students often plan each subject independently and overlook exam proximity, competing commitments, revision, and realistic daily limits. StudyPlan AI collects those constraints in one place, creates a timetable, and makes validation results visible so a model response is never treated as automatically correct.

## Features

- **Student profile:** Add or remove subjects, exam dates, difficulty, priority, completed topics, weekly availability, preferred hours, session and break lengths, and recurring commitments.
- **Exam analysis:** Calculate days remaining and a transparent priority score: 45% exam urgency, 30% difficulty, and 25% user priority. This is a Python calculation, not an AI result.
- **Three prompt versions:** Baseline (V1), constraint-aware (V2), and optimized structured-output (V3); view, copy, compare, and inspect the iteration log.
- **Prompt Mode:** Copy the generated prompt into ChatGPT and paste its JSON or Markdown timetable response back for parsing and validation.
- **Optional API Mode:** Call OpenAI when a key is supplied in `OPENAI_API_KEY`, Streamlit secrets, or the session-only password input. A ChatGPT subscription does not provide API usage automatically.
- **Local planner:** Generate an explicitly labeled deterministic, rule-based draft without an API key. It is a heuristic and does not simulate or claim an AI response.
- **Constraint validation:** Check input completeness, exam dates, session time formats and durations, overlaps, preferred hours, weekly availability, commitments, daily limits, subject coverage, workload, and near-exam preparation gaps.
- **Revision planner:** Suggest quick revision and mock-test sessions near upcoming exams, informed by completed topic names.
- **Dashboard and exports:** See subject allocation, upcoming exams, planned study hours, revision completion, and download CSV, PDF, or JSON.
- **Testing page:** Execute twelve deterministic scenarios using actual validator and planner functions and export the scenario results as CSV. AI output quality is not automatically scored; it requires human review of real responses.

## Technology stack

Python 3.10+ · Streamlit · Pandas · Plotly · Python `datetime` · ReportLab for PDF · OpenAI Python SDK (optional API mode)

## Architecture

```text
app.py / pages/          Streamlit dashboard and eight feature pages
modules/                 Priority scoring, planning, prompt engine, API parsing,
                         validation, revision allocation, evaluation, and exports
prompts/                 Separate V1, V2, and V3 prompt templates
tests/                   unittest suite and scenario inventory
results/                 Prompt iteration log; model observations start as pending
```

The app uses Streamlit session state to retain entered profile and plan data while the session is open. It does not include a database or persistent account storage.

## Installation

Open PowerShell in the `StudyPlan-AI` directory. Create and activate a virtual environment, then install the listed dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the application

```powershell
streamlit run app.py
```

Streamlit will print the local URL. The application is usable without an OpenAI key through the local planner and Prompt Mode.

## API configuration (optional)

Set an environment variable for the current PowerShell session:

```powershell
$env:OPENAI_API_KEY = "your-api-key"
streamlit run app.py
```

Or create `.streamlit/secrets.toml` (this file is ignored by Git):

```toml
OPENAI_API_KEY = "your-api-key"
```

API access, model availability, and charges depend on the user's OpenAI API account. The model can be changed by setting `OPENAI_MODEL`; the default is `gpt-4o-mini`. Never commit an API key.

## How to use Prompt Mode

1. Save a student profile with named subjects, valid exam dates, available days, hours, preferred study window, and any commitments.
2. Open **Generate Study Plan** and choose **Prompt Mode**.
3. Select V1, V2, or V3 and copy the complete prompt using the code block's copy control.
4. Paste it into ChatGPT. V3 requests a JSON object with a `timetable` array; other versions may return a Markdown table.
5. Paste the full response into the app and parse it. Review the Python constraint validation before relying on the timetable.

## How to use API Mode

Configure an API key as above, open **Generate Study Plan**, choose **API Mode**, and request a timetable. The app sends the V3 prompt, parses the response, and runs the same Python validation. API errors and malformed outputs are shown; no synthetic AI response is substituted.

## Testing

Run the unit tests from the project directory:

```powershell
python -m unittest discover -s tests -v
```

The **Testing & Evaluation** page independently executes twelve scenarios and provides a CSV of test ID, input, expected output, actual output, and pass/fail. These tests check deterministic logic; they do not establish prompt/model quality. Record human observations in `results/iteration_log.md` only after reviewing real V1/V2/V3 outputs.

`tests/test_cases.csv` contains the twelve scenario results recorded when this project was built. Use the page's CSV download to generate a fresh run against the current code.

## Project pages

1. Home / Dashboard
2. Student Information
3. Exam & Subject Analysis
4. Generate Study Plan
5. Prompt Engineering Lab
6. Timetable Validator
7. Revision Planner
8. Testing & Evaluation
9. Project Information

## GitHub upload

From the `StudyPlan-AI` directory:

```powershell
git init
git add .
git commit -m "Build StudyPlan AI mini-project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/StudyPlan-AI.git
git push -u origin main
```

Create the empty GitHub repository first and replace the remote URL with its HTTPS or SSH URL. Check `git status` before pushing; `.streamlit/secrets.toml`, `.env`, virtual environments, and bytecode are excluded by `.gitignore`.

## Known limitations

- Plans remain in Streamlit session state and are not saved to a user account or file automatically.
- Priority and local scheduling are transparent heuristics; they cannot know syllabus size or guarantee exam readiness.
- Preparation-time warnings use available profile data and simple near-exam coverage checks. They cannot estimate the actual effort required for a syllabus.
- External API mode requires a separately configured, available, and billed API account.
- Prompt-quality observations are pending until real model responses are reviewed.
