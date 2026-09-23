"""M5 -- Qualitative Coordination-Friction Trajectory (RQ2, qualitative side).

Definition
----------
For each temporal cut c in {T1, T2, T3}, the cohort-pooled coordination
friction score is an LLM-coded 1-10 rating of the transcript text for that
cut, already computed by `12_paper_signals_extractor.py` (prompt
"cohort_coordination_friction" in `paper_v4/advanced_metrics/llm_prompts.py`).
This script performs no re-scoring; it re-exposes the value with an explicit
label for use alongside M4 in the RQ2 "perception vs. reality" contrast.

Source artifact (read-only, paper_v4 signals pipeline, frozen; not part of
Phase 2's 00-09 chain but produced by the same LLM-gateway caching pattern)
---------------------------------------------------------------------------
    paper_v4/advanced_metrics/outputs/cohort_temporal_friction.csv
    (grain: Semestre x temporal_marker, Semestre pooled as "all";
    produced by `12_paper_signals_extractor.py`)

Output
------
    paper_v8/data/m5_coordination_friction_trajectory.csv
    columns: Semestre, temporal_marker, coordination_friction
"""

from __future__ import annotations

import pandas as pd
from _paths import PAPER_V4_OUTPUTS_DIR, ensure_output_dir

SOURCE_PATH = PAPER_V4_OUTPUTS_DIR / "cohort_temporal_friction.csv"
OUTPUT_PATH = ensure_output_dir() / "m5_coordination_friction_trajectory.csv"


def main() -> None:
    trajectory = pd.read_csv(SOURCE_PATH)
    trajectory.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(trajectory)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
