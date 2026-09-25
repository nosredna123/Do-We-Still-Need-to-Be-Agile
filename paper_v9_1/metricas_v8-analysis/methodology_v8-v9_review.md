# Methodology V8-V9 Review Matrix

## Audit scope

This audit compares the V8 Methodology with the current modular V9 Methodology
before further editorial edits. The preservation rule is strict: V9 changes are
allowed only for real methodological differences, factual corrections,
terminology alignment, V9 provenance, or interpretation limits.

## Structural findings

| V8 element | Current V9 state | Assessment | Decision |
|---|---|---|---|
| Methodology section | Present | Preserved | Keep. |
| Context, Course Design, and Rules of the Game | Condensed from V8 | Partial preservation | Restore V8 detail; update only factual terminology and provenance. |
| Project Scope and Real-World Complexity | Condensed; project table rewritten | Structural/content drift | Restore the V8 subsection and table unless a specific change is justified. |
| Data Sources and Collection Framework | Condensed to four paragraphs; survey table removed | Structural/content drift | Restore V8 detail and table; update contracts and limitations locally. |
| Advanced Metrics Operationalization | Three V8 RQ subsubsections removed | Unjustified structural drift | Restore all RQ1/RQ2/RQ3 subsubsections and update metric definitions locally. |
| V8 metric summary table | Removed | Unjustified removal | Restore or obtain explicit approval to remove. |
| LLM Usage subsection | Removed from current V9 Methodology | Content gap | Restore the subsection, adapting it to approved V9 M6b and internal provenance. |
| Existing subsection order | Compressed/reorganized | Unjustified structural drift | Preserve V8 order. |

## Tables and figures

- The V8 Methodology contains the project-scope table, survey-instrument table,
  metric-summary table, and LLM prompt-catalog table.
- The current V9 Methodology retains only a rewritten project table and removes
  the other methodological tables.
- No removal is justified merely because V9 has CSV/JSON artifacts. Tables that
  remain relevant must be restored or their removal explicitly approved.
- Figures are not present in the V8 Methodology block. Any first-version V9
  figure must have local LaTeX provenance comments and remain revisable during
  section review.

## Justified local V9 corrections

These changes should be applied without changing the V8 subsection structure:

- Describe M1-M9 as nine metric families with named components and artifact
  views; do not call every derived file an independent metric.
- Update M4 from raw repository activity to clean-change components under the
  current `code-churn-metrics-v2` policy.
- Update M5 from an opaque constant score to deterministic transcript evidence
  density, composition, coverage, and audit queue.
- Update M6a/M6b terminology: structural T1 evidence and approved structured
  declarative evidence, with no composite planning score.
- Update M7 terminology from planning omission to repository inactivity.
- Update M8 to baseline-conditioned clean rework components.
- Update M9 to stratified descriptive associations and leave-one-out diagnostics.
- State incompatible grains and unavailable states explicitly.
- Add local invisible LaTeX provenance comments beside claims, tables, and
  figures.

## Not justified without explicit approval

- Removing any V8 Methodology subsection or subsubsection.
- Removing the survey, metric, project, or LLM tables solely because V9 has
  machine-readable artifacts.
- Replacing the Methodology narrative with a shorter newly written narrative.
- Changing the order of existing subsections.
- Adding a methodological procedure not implemented by V9 contracts/producers.

## Required next edit

Restore the V8 Methodology structure and content into the modular V9 section,
then apply only the local corrections listed above. Compile after the edit and
review the resulting diff subsection by subsection before proceeding to Results.
