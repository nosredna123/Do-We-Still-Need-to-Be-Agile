# M6b Structured Planning Content: Human Review Sample

Status: human review approved; M6b structured fields may feed M9 separately.

This sample is a review index over the official `m6b_llm_planning_content.json`. It contains no additional LLM outputs and does not alter the generated records. Reviewers must inspect the raw input subjects, parsed categories, literal evidence quotes, and `insufficient_evidence` fields together.

| Case | Semester | Input subjects | Evidence quotes | Review purpose |
|---|---:|---:|---:|---|
| TEAM_08 | 2025.2 | 0 | 0 | Unavailable case; verify no call and explicit `unavailable_not_measured`. |
| TEAM_09 | 2025.2 | 1 | 0 | Sparse case; verify generic subject is not inflated into planning evidence. |
| TEAM_01 | 2026.1 | 1 | 0 | Single-subject case in the second semester; verify category absences. |
| TEAM_01 | 2025.2 | 7 | 0 | Mixed but weak evidence case; verify empty categories and reasons. |
| TEAM_02 | 2026.1 | 11 | 1 | Small positive evidence case; verify quote exactness and category support. |
| TEAM_03 | 2026.1 | 25 | 4 | Mid-volume case; inspect whether categories remain literal and non-semantic. |
| TEAM_04 | 2026.1 | 10 | 7 | High-evidence case; inspect possible over-classification and quote linkage. |
| TEAM_05 | 2026.1 | 40 | 7 | Largest input case; inspect completeness, unsupported inference, and provenance. |

## Review checklist

- [x] Every non-empty category is supported by one or more literal quotes.
- [x] Every quote is an exact substring of the cited T1 commit subject.
- [x] Every quote uses the exact source commit hash.
- [x] No response contains a numeric planning-quality score.
- [x] Empty categories have an explicit `insufficient_evidence` reason when appropriate.
- [x] `planning_evidence_present` does not imply architectural quality.
- [x] Missing T1 subjects remain `unavailable_not_measured`, never a low score.
- [x] M6b fields enter M9 separately; no composite score is created.

Review decision: approved by the user on 2026-09-24. M6b remains exploratory and
its structured fields must not be interpreted as architectural quality.
