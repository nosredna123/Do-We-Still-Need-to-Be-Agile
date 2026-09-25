# M5 V8 to V9 Analysis

## V8 baseline

The V8 M5 artifact is `paper_v8/data/m5_coordination_friction_trajectory.csv`, with one global row per temporal marker and a constant `coordination_friction` score of 8 for T1, T2, and T3. The V8 analysis notebook identifies the score as the result of one opaque LLM call per marker over the concatenated transcript corpus. The lake contains technical transcript chunks, not independent session observations.

## V8 ambiguities and decisions

- The constant LLM score does not provide a changing trajectory, subtype counts, denominators, or auditable evidence.
- Transcript chunks are processing units created by segmentation; they are not independent observations.
- The transcript contract contains two source sessions per observed marker and only semester `2025.2`; semester `2026.1` is unavailable and is not imputed.
- Transcript records have no `ID_Equipe`, so M5 cannot be joined to team-semester M3 or M4 outcomes.
- Lexical matches are candidate textual evidence. They are not diagnoses of coordination failure and do not support causal, correlational, hypothesis-test, or confidence-interval claims.

## V9 decision

M5 is replaced by a deterministic, no-LLM transformation over `data/lake/transcript_sessions.parquet`. The producer reconstructs one global corpus per temporal marker and publishes:

- M5a: candidate friction-marker density per 1,000 corpus tokens;
- M5b: composition across alignment, handoff, integration, blocker, and rework markers;
- M5c: transcript chunks, source sessions, characters, tokens, markers, and observed-semester coverage;
- an audit queue containing source-chunk provenance and literal text for human review.

The versioned Portuguese lexicon is `m5-friction-lexicon-pt-v1`. Matching counts regex occurrences in each chunk, while aggregation remains global by marker. No LLM call is required.

## V8 to V9 traceability matrix

| v8_recommendation | v9_decision | status | evidence | limitation_or_approval |
|---|---|---|---|---|
| Replace the constant LLM score with a changing qualitative trajectory. | Compute deterministic lexical marker density per 1,000 corpus tokens. | applied | `m5_marker_density.csv` | Candidate textual evidence; no causal interpretation. |
| Separate alignment, handoff, integration, blocker, and rework evidence. | Publish subtype counts and shares by temporal marker. | applied | `m5_marker_composition.csv`, `m5_lexicon.json` | Regex matches require human qualitative review. |
| Declare corpus and session/chunk coverage. | Publish chunk, source-session, character, token, marker, and semester coverage. | applied | `m5_corpus_coverage.csv`, metadata | Only `2025.2` is observed; no semester is imputed. |
| Preserve evidence for audit rather than treating chunks as observations. | Publish a provenance-preserving source-chunk audit queue. | applied | `m5_evidence_audit_trail.csv` | The queue is not a statistical sample. |
| Avoid incompatible team-level associations. | Keep M5 at global-corpus grain and prohibit M3/M4 correlation. | applied | `verify_m5.ipynb`, metadata limitations | Temporal contrast only. |

## Validation evidence

- `paper_v9/tests/test_m5.py`: focused real-contract and resume tests.
- `paper_v9/verification_notebooks/verify_m5.ipynb`: executed end-to-end; validates contract, traceability, schemas, composition conservation, coverage, audit evidence, figures, and preliminary RQ2 interpretation.
- Article-ready figures are generated from official CSV outputs in HTML, PDF, SVG, and PNG formats.

## Interpretation boundary

M5 contributes a descriptive textual axis to RQ2. It can show how candidate coordination-friction language varies across observed temporal markers in the global transcript corpus. It does not measure team performance, effort, productivity, quality, or causal coordination failure, and it cannot be correlated with M3/M4 because the analysis grains and identifiers are incompatible.
