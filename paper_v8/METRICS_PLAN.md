# Plan — "Advanced Metrics Operationalization" subsection (paper_v8)

Status: IMPLEMENTED (2026-09-23, corrected 2026-09-23). All 9 scripts under
`paper_v8/scripts/metrics/` run successfully and write to `paper_v8/data/`.
The LaTeX subsection is drafted in `paper_v8/latex_code/main.tex`
(`\subsection{Advanced Metrics Operationalization}`), formalizing M1-M9 with
`% PROVENANCE:` comment blocks per metric. Tables/figures are deferred to the
future Results section per decision in §4.

**Correction (2026-09-23):** the original M1 ("AI-Authorship Density") was
factually wrong — the underlying `ai_*` columns in
`integration_friction_metrics.parquet` have no AI-tool detection logic; they
are generic commit-authorship concentration in a 72h pre-T3 window. This
metric was renamed to "Pre-Deadline Author-Concentration Density" and moved
from RQ1 (AI-adoption) to RQ2 (integration-pressure proxy). All metrics were
renumbered accordingly: M1/M2 = RQ1 (self-report only), M3/M4/M5 = RQ2,
M6-M9 = RQ3 (unchanged). Scripts renamed to match. The visible LaTeX text was
also rewritten to describe raw-to-metric transformation logic in plain
methodological terms, without repo/pipeline jargon ("Phase 2", script names,
"already computed upstream") — that jargon is now confined to the invisible
`% PROVENANCE` comments only. See `/memories/repo/paper-v8-advanced-metrics.md`
for full details.

## 0. Ground rules carried over from repo memory
- Phase 2 (00–09 pipeline) is frozen (2026-09-21): consume `data/lake/*.parquet` and
  `data/analysis/*.parquet` as-is, read-only. Do not rerun `run_pipeline.py`.
- `paper_v4/advanced_metrics/` (built by `12_paper_signals_extractor.py`) is a separate,
  already-executed signals pipeline. Its cached LLM outputs are the direct source of the
  abstract's headline numbers (55% omission, 8/10 friction, 100,000+ line rework). Reuse
  its outputs as-is; do not re-issue LLM calls unless explicitly approved (cost/reproducibility).
- All new work for this subsection is genuinely new, small, deterministic derivations on
  top of already-computed artifacts — no new LLM calls, no re-running Phase 2.
- Every new script: one metric per script, reuses `phase2_contracts.load_phase2_inputs`,
  `pipeline_statistics.summarize_numeric_distribution`, and `pipeline_core` path/checksum
  helpers where applicable. Scripts live in `paper_v8/scripts/metrics/`. Outputs (CSV/JSON)
  live in `paper_v8/data/`. Each script is self-documented (module docstring: inputs,
  transformation, output, formula).

## 1. Data inventory recap (already verified against the repo)

| Artifact | Grain | Key columns | Status |
|---|---|---|---|
| `paper_v4/advanced_metrics/outputs/team_level_signals.csv` | team-semester (14 rows, 2 missing planning score is expected — no T1 commits) | `t1_planning_score` (LLM 1–10 over T1 commit messages), `rework_churn_t3`, `deferred_churn_t3` (file-provenance split), `scope_applicability_mean`, `technical_complexity_mean` | **Exists, frozen, matches abstract exactly** |
| `paper_v4/advanced_metrics/outputs/cohort_temporal_friction.csv` | cohort × cut (3 rows, T1/T2/T3, all semesters pooled) | `coordination_friction` (LLM 1–10 over transcript blocks) | **Exists** (constant 8/8/8 — matches abstract) |
| `data/analysis/code_churn_metrics.parquet` / `team_metrics.parquet` | team-semester | `cc_total_t1/t2/t3`, `cc_commit_n_t1/t2/t3` | Exists (Phase 2) |
| `data/analysis/integration_friction_metrics.parquet` | team-semester | `ai_author_share_median_t{1,2,3}`, `ai_commit_n_t{1,2,3}`, `ai_churn_t{1,2,3}`, `ai_gini_t{1,2,3}` | Exists (Phase 2) |
| `data/lake/evaluator_team_cuts.parquet` / `cross_evidence/datasets/evaluator_outcome_metrics.parquet` | team-semester × cut | `project_progress_mean`, `scope_applicability_mean`, `technical_complexity_mean`, `engagement_participation_mean` (+ deltas) | Exists (Phase 2), matches the 4 rubric criteria described in Methodology |
| `data/analysis/textual_cut_signals.parquet` | **cohort × cut only** (no `ID_Equipe`) | `student_*_ai_dependency_score_*` (6 question families) | Exists, but not team-attributable |
| `data/analysis/student_nlp.parquet` | student-response (anonymous, no team id) | `ai_dependency_score`, `sentiment_score`, `cognitive_load_score` | Exists, cohort-level only |
| `data/lake/student_responses.parquet` | student response, raw (187 rows) | Likert items on perceived role-risk (Backend/Frontend/QA/PM/PO/SM) — **raw structured Likert, not LLM-coded**; grain confirmed as `Semestre` + `temporal_marker` only, **no `ID_Equipe`** (cohort-level, same asymmetry as `textual_cut_signals.parquet`) | Verified — exact column names captured in §2 (M3) |

Constraint discovered: **AI-role-perception and AI-dependency survey signals cannot be
attributed to individual teams** (student responses are anonymized at cohort×cut grain
only). RQ1 metrics must therefore be reported at the **cohort level** (both semesters
pooled, or per-semester if `Semestre` is present — confirmed present in
`textual_cut_signals.parquet`), triangulated against the **team-level** AI-authorship
behavioral proxy from `integration_friction_metrics.parquet`. This asymmetry must be
stated explicitly in the subsection (construct-validity note), not hidden.

## 2. Proposed metric set (mapped to RQs)

### RQ1 — AI adoption & longitudinal perception
- **M1 — AI Authorship Density (behavioral proxy).** Reuse `integration_friction_metrics.parquet`
  as-is (team-semester grain). No new script strictly required; a thin "table builder"
  script formats the T1→T3 trajectory for the LaTeX table/figure.
  → `paper_v8/scripts/metrics/m1_ai_authorship_density.py`
- **M2 — Self-Reported AI-Dependency Trajectory (perception proxy).** Derived from
  `textual_cut_signals.parquet`'s six `*_ai_dependency_score_mean` families, averaged into
  one composite per Semestre × temporal_marker. **New metric** (simple mean-of-means
  aggregation across already-scored constructs; no new LLM calls).
  → `paper_v8/scripts/metrics/m2_ai_dependency_trajectory.py`
- **M3 — Perceived Role-Disruption Risk.** **Confirmed in scope.** Direct descriptive
  stats (mean/median, 5-point Likert, no LLM involved) per role, per `Semestre` ×
  `temporal_marker`, from `data/lake/student_responses.parquet`. Exact source columns
  (verbatim, Portuguese, verified against the parquet schema):
  - Backend: `A função de backend será extinta ou severamente afetada pelo uso de ferramentas de IA generativa na engenharia de software. Indique seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente).`
  - Frontend: `A função de frontend será extinta ou severamente afetada pelo uso de ferramentas de IA generativa na engenharia de software. Indique seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente).`
  - QA: `A função de QA (Garantia de Qualidade) será extinta ou severamente afetada pelo uso de ferramentas de IA generativa na engenharia de software. Indique seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente).`
  - Project Manager: `A função de gerente de projeto será extinta ou severamente afetada pelo uso de ferramentas de IA generativa na engenharia de software. Indique seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente).`
  - Product Manager: `A função de Product Manager será extinta ou severamente afetada pelo uso de ferramentas de IA generativa na engenharia de software. Indique seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente).`
  - Scrum Master: `A função de Scrum Master será extinta ou severamente afetada pelo uso de ferramentas de IA generativa na engenharia de software. Indique seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente).`
  Same cohort-level grain constraint as M2 (`Semestre` + `temporal_marker`, no `ID_Equipe`).
  → `paper_v8/scripts/metrics/m3_role_disruption_risk.py`

### RQ2 — repository temporal density vs. coordination friction
- **M4 — Repository Activity Density Trajectory.** Cohort-level aggregation (mean/median
  across teams) of `cc_total_t{1,2,3}` and `cc_commit_n_t{1,2,3}` from
  `code_churn_metrics.parquet`, to be plotted against M5 on a shared T1/T2/T3 axis.
  **New metric** (existing table is team-level; this cohort aggregation doesn't exist yet).
  → `paper_v8/scripts/metrics/m4_repo_activity_density.py`
- **M5 — Qualitative Coordination-Friction Trajectory.** Reuse
  `cohort_temporal_friction.csv` as-is (T1=8, T2=8, T3=8). Thin formatting script only.
  → `paper_v8/scripts/metrics/m5_coordination_friction_trajectory.py`
- The RQ2 narrative point is precisely the **divergence** between M4 (which spikes at T3)
  and M5 (which is already chronically high at T1 and stays flat) — i.e., friction is not
  an emergent property of late crunch, it is a standing condition since day one, while
  repository evidence of it only appears late. This is the "perception vs. reality" arc.

### RQ3 — planning quality vs. destructive rework vs. evaluator outcomes (primary)
- **M6 — T1 Planning-Quality Score.** Reuse `t1_planning_score` from
  `team_level_signals.csv` as-is. Thin formatting/labeling script.
  → `paper_v8/scripts/metrics/m6_t1_planning_quality.py`
- **M7 — T1 Planning-Omission Rate.** **New metric.** Formalizes the abstract's "55%"
  claim: proportion of teams per cohort with no T1 planning score (i.e., zero T1 commits
  to evaluate — `t1_planning_score` is `NaN`). Deterministic count/percentage, grouped by
  `Semestre`.
  → `paper_v8/scripts/metrics/m7_planning_omission_rate.py`
- **M8 — Rework Severity Ratio.** **New metric.** From `rework_churn_t3` and
  `deferred_churn_t3` (already-split file-provenance churn), computes
  `rework_ratio_t3 = rework_churn_t3 / (rework_churn_t3 + deferred_churn_t3)` and
  `total_churn_t3 = rework_churn_t3 + deferred_churn_t3` per team-semester.
  → `paper_v8/scripts/metrics/m8_rework_severity_ratio.py`
- **M9 — Planning Quality vs. Rework/Outcome Association.** **New metric.** Joins M6 + M8 +
  evaluator outcome scores (`project_progress_mean`, `scope_applicability_mean`,
  `technical_complexity_mean`, `engagement_participation_mean` at T3, from
  `evaluator_outcome_metrics.parquet`). Computes: (a) Spearman correlation(s) between
  `t1_planning_score` and `rework_churn_t3` / `rework_ratio_t3`; (b) a low-vs-high planning
  tertile/median-split group contrast on rework and evaluator outcomes, reusing
  `pipeline_statistics.summarize_numeric_distribution` per group. This produces the exact
  contrast the abstract claims ("low-planning teams penalized with catastrophic rework;
  high-planning teams contained rework to nominal levels").
  → `paper_v8/scripts/metrics/m9_planning_vs_rework_association.py`
- All RQ3 stats explicitly labeled exploratory/descriptive given n=14 (per repo's own
  "conditional-go" verdict in `data/analysis/artifact_reports/00_consolidated_audit.md`
  and `docs/02a.artifact-narrative-audit.md`) — no causal language.

## 3. Output convention

Each script writes one artifact to `paper_v8/data/`:
- `m1_ai_authorship_density.csv`, `m2_ai_dependency_trajectory.csv`,
  `m3_role_disruption_risk.csv`, `m4_repo_activity_density.csv`,
  `m5_coordination_friction_trajectory.csv`, `m6_t1_planning_quality.csv`,
  `m7_planning_omission_rate.csv`, `m8_rework_severity_ratio.csv`,
  `m9_planning_vs_rework_association.csv` (+ a small `_group_contrast.csv` sidecar).

Every script has a module docstring stating: source artifact path(s) (with a one-line
provenance note on how that source was produced upstream, e.g. "produced by
`12_paper_signals_extractor.py`, Phase 2-adjacent, LLM-scored"), the exact transformation/
formula, and the output path — so the paper repo remains auditable end-to-end.

## 4. Resolved decisions

1. **M3 (role-disruption risk) is in scope.** Exact source columns verified above; script
   will be fully documented and persisted like every other metric script.
2. **LaTeX provenance**: each metric's paragraph in the subsection will be preceded by a
   `% PROVENANCE:` LaTeX comment block naming the source artifact path(s), the upstream
   producer (pipeline stage or `12_paper_signals_extractor.py`), and the generating
   `paper_v8/scripts/metrics/*.py` script.
3. **No tables in the Methodology subsection.** All metrics will only be formally defined
   and referenced here; concrete tables/figures are deferred to the future
   `sec:results` section (`\label{sec:results}` already referenced in the Introduction but
   not yet written).
4. **`scipy` dependency confirmed available** (`scipy==1.11.4` already pinned in
   `requirements.txt`) — M9 will use `scipy.stats.spearmanr` directly, no new dependency
   needed.

Implementation order: M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8 → M9, verifying each
script's output against the source numbers already spot-checked above, then draft the
LaTeX subsection referencing the generated artifacts and formalizing each metric with
notation consistent with Section 3 (Methodology) already in `main.tex`.
