# Do We Still Need to Be Agile?

Reproducible research pipeline for the article **Do We Still Need to Be Agile? An Empirical Analysis of Planning Debt and Rework in Software Engineering**.

The project studies planning debt, code churn, technical degradation, integration friction, and contextual exhaustion signals while preserving the observed unit of each source.

## Requirements

- Python 3.11
- A project virtual environment at `.venv/`
- `ffmpeg` for audio preparation
- OpenAI credentials only for remote transcription, NER, or NLP stages

Install the pinned Python dependencies with:

```bash
.venv/bin/pip install -r requirements.txt
```

The statistical visualization layer uses Plotly and Kaleido to generate interactive HTML and publication-ready PNG, SVG, and PDF files.

## Configuration

Create `.env` at the repository root when remote services are required:

```dotenv
OPENAI_API_KEY=your_key
ANONYMIZATION_SALT=your_random_secret
```

Never commit `.env`, the anonymization salt, raw data, processed text, private NLP outputs, or private reports.

Versioned methodological decisions live in `pipeline_config.py`. Versioned prompts live in `pipeline_prompts.py`. Neither file may contain credentials, PII, or raw research text.

## Pipeline Entry Point

The main entry point is `run_pipeline.py`. The default sequence is:

```text
prepare -> transcribe -> ner -> anonymize -> git -> lake
-> repo-snapshots -> nlp -> metrics -> stats
```

`cleanup` is intentionally excluded from the default sequence because it is destructive and must be selected explicitly.

Run a non-destructive structural preview:

```bash
.venv/bin/python run_pipeline.py --dry-run
```

Run the complete pipeline when all required inputs and credentials are available:

```bash
.venv/bin/python run_pipeline.py
```

Use a batch limit only for incremental item-processing stages:

```bash
.venv/bin/python run_pipeline.py --stages prepare transcribe --limite 10
.venv/bin/python run_pipeline.py --stages ner anonymize --limite 10
```

## Stage Selection and Resume

Stages can be selected independently. A selected stage does not automatically run upstream dependencies; it consumes the persisted contracts already present on disk.

```bash
# Phase 2 NLP with the deterministic offline backend
.venv/bin/python run_pipeline.py --stages nlp --nlp-backend mock

# Phase 2 NLP with the remote OpenAI backend
.venv/bin/python run_pipeline.py --stages nlp --nlp-backend openai

# Metrics only
.venv/bin/python run_pipeline.py --stages metrics

# Statistical manifest, correlations, hypotheses, and figures only
.venv/bin/python run_pipeline.py --stages stats

# Continuous range of stages
.venv/bin/python run_pipeline.py --from-stage lake --to-stage stats
```

The `mock` NLP backend is deterministic and is intended for offline tests and structural validation. It does not produce scientific LLM evidence. The `openai` backend requires `OPENAI_API_KEY` and performs the configured remote analysis.

`--force` affects only the selected stages:

```bash
.venv/bin/python run_pipeline.py --stages stats --force
```

Each producer owns its artifacts and validates checksums before resuming. A failed stage stops the pipeline immediately. Every execution writes a human-readable log and a structured JSON execution manifest in the configured log directory.

## Phase 2 Artifacts

Phase 2 artifacts are written to `data/analysis/`:

- `phase2_contract_report.json`: validated input schemas, keys, types, coverage, and Git reconciliation status.
- `student_nlp.parquet`: private individual-response NLP output.
- `transcript_nlp.parquet`: private transcript-session NLP output.
- `textual_cut_signals.parquet`: persisted textual aggregates by semester and temporal cut.
- `planning_metrics.parquet`: planning metrics at `team_semester` level.
- `code_churn_metrics.parquet`: normalized and absolute code-churn metrics.
- `technical_degradation_metrics.parquet`: longitudinal technical-degradation metrics.
- `integration_friction_metrics.parquet`: author concentration and integration-pressure metrics.
- `cut_context_metrics.parquet`: IE and textual context at `cut_context` level.
- `team_metrics.parquet`: PI, CC, Delta DT, and AI at `team_semester` level. IE is never broadcast into this file.
- `team_metrics_exclusions.json`: private team-metric availability report.
- `statistical_dataset_manifest.json`: variable catalog, units, availability, definitions, and statistical protocol.
- `statistical_dataset_manifest_exclusions.json`: private exclusion report with true observation keys.
- `correlation_results.csv`: declared Spearman analyses and diagnostics.
- `hypothesis_results.csv`: declared Mann-Whitney U analyses and diagnostics.
- `figure_manifest.json`: figure sources, transformations, units, limitations, paths, and checksums.

Each Parquet and analytical CSV has a `.metadata.json` sidecar with status, checksum, contract version, and effective options.

## Units of Analysis

The pipeline never fabricates a team key:

- `team_semester`: one row per `ID_Equipe + Semestre`; used by PI, CC, Delta DT, and AI.
- `cut_context`: one row per `Semestre + temporal_marker`; canonical unit for IE and transcript context.
- `student_response`: individual NLP response, keyed by persisted response/question fields.
- `transcript_session`: persisted transcript session, keyed by `transcript_file`.

`team_metrics.parquet` must not contain replicated `ie_*` columns. Analyses combining team metrics and IE must align the units explicitly in the statistical layer.

## Visualizations

The statistical stage generates 12 Plotly visualizations from shared persisted data specifications:

```text
assets/figures/prioritarias/
assets/figures/exploratorias/
assets/figures/dashboard_interativo/
data/analysis/figure_data/
```

Each figure has an interactive HTML version and static PNG/SVG exports. The five prioritized figures also have PDF exports:

- `pi_vs_cc`
- `cc_by_temporal_cut`
- `delta_dt_by_team_semester`
- `ai_before_t3`
- `ie_by_cut_or_corpus`

The static and interactive versions share the same filters, transformations, units, missingness policy, and figure-data CSV. Visible labels are English for international publication. Canonical source column names remain unchanged in the CSV data for lineage.

The figures preserve missingness as gaps or explicit availability information and never interpolate missing observations. Team IDs are not displayed in images. Absolute `cc_total` visualizations use a declared logarithmic scale; normalized `cc_per_source_loc` is the primary churn measure.

## Privacy and Publication Policy

The following artifacts remain private and must not be published without a semantic PII audit:

- `data/raw/`
- `data/processed/`
- `data/lake/`
- `student_responses.parquet`
- `transcript_sessions.parquet`
- `student_nlp.parquet`
- `transcript_nlp.parquet`
- private exclusion reports containing true observation keys
- `evidence_summary_private`
- relational mappings and anonymization secrets

Reports and manifests must not contain raw student answers, transcript text, summaries of identifiable content, credentials, or the anonymization salt. The `ANONYMIZATION_SALT` is never sent to OpenAI.

A replication package may contain only audited, privacy-safe artifacts. Publication/export is not authorized merely because an artifact was generated successfully.

## Statistical Interpretation Limits

- Results are observational associations, not causal claims.
- `team_semester` and `cut_context` are separate populations.
- IE is not evidence about an individual team unless a future analysis defines an explicit valid alignment.
- Small-sample results are exploratory and retain their `n_valid`, missingness, and availability diagnostics.
- The primary PI/CC association uses `cc_per_source_loc`; absolute churn is size-sensitive.
- Missing activity is not silently converted to zero unless the metric contract explicitly identifies observed no-activity.
- Spearman confidence intervals are not calculated in the current protocol.
- Hypothesis tests use median-defined groups, a minimum of three observations per group, bilateral Mann-Whitney U, and uncorrected exploratory p-values.

## Validation

Run the complete test and lint suite with the project interpreter:

```bash
.venv/bin/pytest -q
.venv/bin/ruff check .
```

The current validated snapshot contains:

```text
4 persisted statistical datasets
4 Spearman analyses
3 hypothesis analyses
12 Plotly figures
158 tests passed
6 tests skipped
```

Regenerate all statistical outputs and figures with:

```bash
.venv/bin/python run_pipeline.py --stages stats --force
```

The numeric snapshot above describes one validated data state and must be regenerated after input contracts or configuration change.

## Phase 1 Data Lake Contracts

The first pipeline stages generate these independent contracts under `data/lake/`:

- `student_responses.parquet`
- `evaluator_team_cuts.parquet`
- `git_team_cuts.parquet`
- `git_commits.parquet`
- `git_files.parquet`
- `git_repository_snapshots.parquet`
- `transcript_sessions.parquet`

The project does not build or require a `master_dataset.parquet`.
