# M6b Structured Planning-Content Protocol

## Gate and status

This document presents the protocol for M6b Task 4.2. It does not authorize execution. No new LLM call is made until this protocol, the prompt, the cost estimate, and the pilot sample are explicitly approved.

M6b is an exploratory descriptive extraction of declarative planning content from T1 commit subjects. It is not an architectural-quality score, a productivity measure, or a causal predictor. M6a remains the deterministic structural measure.

## Objective and unit

For each observed team-semester with T1 commit subjects, classify only content explicitly present in the supplied chronological subjects:

- `planning_evidence_present`: whether the supplied text contains usable planning evidence;
- `goals`: explicit goals or intended outcomes;
- `architecture_or_design`: explicit architecture, component, interface, data, or design decisions;
- `task_decomposition`: explicit tasks, implementation steps, or division of work;
- `risk_or_dependency`: explicit risks, blockers, dependencies, or constraints;
- `evidence_quotes`: literal quotes copied exactly from the input subjects and linked to categories;
- `insufficient_evidence`: explicit reason when a category or the entire input lacks evidence.

The unit is one team-semester (`ID_Equipe`, `Semestre`). T1 subjects are concatenated in timestamp order for that team-semester, but the original commit hash and timestamp remain in the payload for provenance. No team-semester is assigned a low score when subjects are absent.

## Model and execution constraints

- Proposed model: `gpt-4o-mini`.
- Proposed temperature: `0.0`.
- One request per eligible team-semester; no parallel calls are required.
- No calls for team-semesters with no T1 subjects. Those rows receive `insufficient_evidence` with `reason: no_t1_commit_subjects`.
- The raw request, raw response, payload hash, prompt version, model, temperature, token usage, status, and validation errors must be persisted.
- Responses must be valid JSON and must not contain claims unsupported by literal input text.
- A response is invalid if an evidence quote is not an exact substring of the supplied input, if a category contains unsupported claims, or if required fields are missing.

## Exact user prompt

```text
You are extracting structured planning evidence from software-project commit subjects.

Judge only the supplied T1 commit subjects. Do not infer intent, quality, architecture,
effort, success, or missing information. Do not assign a numeric quality score.
Use only literal evidence from the input. Every non-empty category must include one or
more exact evidence_quotes copied from the supplied subjects. If the text does not
support a category, return an empty list and explain the absence in insufficient_evidence.

Return only valid JSON matching this schema:
{
  "planning_evidence_present": boolean,
  "goals": [{"text": string, "evidence_quote_ids": [string]}],
  "architecture_or_design": [{"text": string, "evidence_quote_ids": [string]}],
  "task_decomposition": [{"text": string, "evidence_quote_ids": [string]}],
  "risk_or_dependency": [{"text": string, "evidence_quote_ids": [string]}],
  "evidence_quotes": [{"quote_id": string, "quote": string, "category": string, "commit_hash": string}],
  "insufficient_evidence": [{"category": string, "reason": string}]
}

The allowed categories are: goals, architecture_or_design, task_decomposition,
risk_or_dependency. A quote must be copied exactly from one supplied subject.

Team-semester: <ID_Equipe>|<Semestre>
T1 commit subjects, in timestamp order:
<JSON array of {commit_hash, timestamp, subject}>
```

## Response schema and validation

The validator must require exactly the seven top-level fields shown above, boolean `planning_evidence_present`, arrays for every list field, unique `quote_id` values, allowed categories, and non-empty reasons for `insufficient_evidence`. Each quote must match an input subject exactly and reference an existing commit hash. The validator must reject extra unsupported top-level fields and any response that uses a numeric planning score.

## Pilot design

The proposed pilot covers three cases without making calls:

1. `2025.2|TEAM_01`: seven T1 subjects with mixed descriptive content;
2. `2025.2|TEAM_09`: one T1 subject, a sparse-evidence case;
3. `2025.2|TEAM_02`: no T1 subjects, an explicit unavailable case.

The pilot is intended to check payload shape, missingness handling, quote traceability, and response validation after approval. It is not a statistical validation sample and cannot establish model agreement or metric quality.

## Expected outputs after approval

- `paper_v9/data/metrics/m6b_llm_planning_content.json`: all 14 team-semester records, including unavailable cases;
- `paper_v9/data/metrics/m6_llm_planning_content.metadata.json`: model, prompt version, payload hashes, token usage, statuses, and costs;
- `paper_v9/data/metrics/m6b_llm_planning_sample_for_review.md`: stratified human-review sample;
- cached responses and raw payloads under the approved v9 LLM artifact location.

M6b must not feed M9 until the structured responses and the human-review sample receive a separate approval.
