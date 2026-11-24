# Prompt iteration log

Model quality observations are **pending** until real model outputs are evaluated. No comparative model results are claimed here. Automated constraint tests are separate from subjective AI-quality evaluation.

## V1 – Baseline

- **Prompt:** `prompts/prompt_v1.txt`
- **Changes made:** Basic timetable request using the student profile.
- **Reason:** Establish a minimal prompt baseline.
- **Expected improvement:** A first-pass timetable covering the supplied exams and subjects.
- **Actual observations:** Pending until tested with real model outputs.

## V2 – Constraint-aware

- **Prompt:** `prompts/prompt_v2.txt`
- **Changes made:** Added exam proximity, difficulty, user priority, weekly availability, time windows, breaks, commitments, and no-overlap rules.
- **Reason:** Make scheduling constraints explicit and direct the model's allocation.
- **Expected improvement:** Better priority distribution and fewer schedule conflicts.
- **Actual observations:** Pending until tested with real model outputs.

## V3 – Optimized

- **Prompt:** `prompts/prompt_v3.txt`
- **Changes made:** Added input validation, conflict handling, structured JSON, strict time requirements, subject coverage, revision and mock planning, workload distribution, and insufficient-time handling.
- **Reason:** Improve parseability, transparency, and handling of edge cases.
- **Expected improvement:** More structured output with clearer assumptions and fewer unverifiable claims.
- **Actual observations:** Pending until tested with real model outputs.
