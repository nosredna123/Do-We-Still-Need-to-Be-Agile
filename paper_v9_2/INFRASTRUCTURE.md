# Paper V9 — Infrastructure (Task 1.1)

Common utilities shared by every Paper V9 metric/results/LaTeX script. All
modules follow the repository-wide **DRY / KISS / Fail Fast** principles
declared in `V9_CONVERSION_PLAN.md`.

## Modules (`paper_v9/scripts/common/`)

| Module | Responsibility | Reuses |
|---|---|---|
| `paths.py` | Resolve `paper_v9/` subdirectories relative to the repo root. Raises `FileNotFoundError` immediately if a required directory is missing. | — |
| `provenance.py` | SHA-256 checksums and `.metadata.json` sidecars. | `pipeline_core.file_checksum`, `pipeline_core.input_checksum` |
| `resume.py` | `ArtifactCache` decides whether an artifact must be regenerated based on a combined input+config checksum. | `pipeline_core.is_current_artifact`, `write_artifact_metadata`, `invalidate_artifacts` |
| `statistics.py` | Exploratory descriptive summaries only (mean/median/std/min/max/quartiles). No causal inference. | Python `statistics` stdlib |
| `artifact_policy.py` | Adapts the single central artifact whitelist/blacklist (`pipeline_config.is_measurement_code_path`) with explicit policy-version validation. | `pipeline_config.is_measurement_code_path` |

None of these modules duplicate hashing, resume, or artifact-classification
logic that already exists in `pipeline_core.py` / `pipeline_config.py` — they
wrap the canonical implementations so v8 and v9 always share one contract.

## Orchestrator (`paper_v9/scripts/orchestrate_v9.py`)

CLI with stages `metrics`, `results`, `figures`, `latex-check`, `all`.

```bash
python paper_v9/scripts/orchestrate_v9.py <stage> [--force] [--verbose]
```

Stages are registered explicitly in `STAGE_REGISTRY` as later tasks (2.1+)
implement each metric/results/figure/LaTeX step. Running an unregistered
stage fails fast with a clear error and the list of currently available
stages — it never silently no-ops.

## Tests (`paper_v9/tests/test_contracts.py`)

13 tests covering: module imports, path resolution (including fail-fast on a
missing directory), checksum determinism/verification, resume
should-regenerate/mark-complete/clear-cache behavior, artifact-policy
classification and version rejection, and descriptive-statistics
correctness/fail-fast behavior.

Run with:

```bash
python -m pytest paper_v9/tests/test_contracts.py -v
```

`pytest.ini` now discovers both `tests/` (root pipeline) and `paper_v9/tests/`
(v9 conversion) via `testpaths = tests paper_v9/tests`.

## Conventions

- Namespace: `paper_v9.scripts.common` (import as `from paper_v9.scripts.common import paths, provenance, resume, statistics, artifact_policy`).
- No absolute paths anywhere in source files; all resolution goes through `paths.py`.
- Every public function has a docstring and full type hints.
- All log/error messages are in English.
