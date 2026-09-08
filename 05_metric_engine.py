"""Quantitative Phase 2 metric computations with explicit unavailable values."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


KEYS = ["ID_Equipe", "Semestre"]
CUTS = ("T1", "T2", "T3")


def _pivot_cut(frame: pd.DataFrame, value: str, prefix: str) -> pd.DataFrame:
    pivot = frame.pivot_table(index=KEYS, columns="temporal_marker", values=value, aggfunc="first")
    pivot.columns = [f"{prefix}_{column.lower()}" for column in pivot.columns]
    return pivot.reset_index()


def build_cut_context_metrics(students: pd.DataFrame, transcripts: pd.DataFrame) -> pd.DataFrame:
    """Build IE context metrics without assigning observations to teams."""
    keys = ["Semestre", "temporal_marker"]
    student = students.groupby(keys).agg(ie_student_cognitive_load_mean=("cognitive_load_score", "mean"), ie_student_sentiment_mean=("sentiment_score", "mean"), ie_student_ai_dependency_mean=("ai_dependency_score", "mean"), ie_student_n=("cognitive_load_score", "count")).reset_index()
    transcript = transcripts.groupby(keys).agg(ie_transcript_coordination_friction_mean=("coordination_friction_score", "mean"), ie_transcript_rework_signal_mean=("rework_signal_score", "mean"), ie_transcript_session_n=("coordination_friction_score", "count")).reset_index()
    result = student.merge(transcript, on=keys, how="outer", validate="one_to_one")
    result["unit_of_analysis"] = "cut_context"
    result["ie_definition_version"] = "ie-v1"
    return result


def compute_code_churn(commits: pd.DataFrame, files: pd.DataFrame, snapshots: pd.DataFrame) -> pd.DataFrame:
    """Compute longitudinal churn normalized by observed source LOC."""
    commits = commits.copy()
    commits["commit_churn"] = commits["lines_added"] + commits["lines_deleted"]
    grouped = commits.groupby(KEYS + ["temporal_marker"]).agg(cc_total=("commit_churn", "sum"), cc_commit_n=("commit_hash", "nunique")).reset_index()
    file_counts = files.groupby(KEYS + ["temporal_marker"]).agg(cc_unique_changed_files=("file_path", "nunique")).reset_index()
    snapshot_values = snapshots[KEYS + ["temporal_marker", "repo_source_loc"]]
    grouped = grouped.merge(file_counts, on=KEYS + ["temporal_marker"], how="left", validate="one_to_one").merge(snapshot_values, on=KEYS + ["temporal_marker"], how="left", validate="one_to_one")
    grouped["cc_per_source_loc"] = grouped["cc_total"].where(grouped["repo_source_loc"] > 0) / grouped["repo_source_loc"].where(grouped["repo_source_loc"] > 0)
    grouped["cc_per_changed_file"] = grouped["cc_total"].where(grouped["cc_unique_changed_files"] > 0) / grouped["cc_unique_changed_files"].where(grouped["cc_unique_changed_files"] > 0)
    grouped["cc_mean_per_commit"] = grouped["cc_total"].where(grouped["cc_commit_n"] > 0) / grouped["cc_commit_n"].where(grouped["cc_commit_n"] > 0)
    pieces = []
    for key, subset in grouped.groupby(KEYS):
        row: dict[str, Any] = dict(zip(KEYS, key))
        for cut in CUTS:
            current = subset[subset["temporal_marker"] == cut]
            values = current.iloc[0] if not current.empty else pd.Series(dtype=object)
            for metric in ("cc_total", "cc_commit_n", "repo_source_loc", "cc_unique_changed_files", "cc_per_source_loc", "cc_per_changed_file", "cc_mean_per_commit"):
                row[f"{metric}_{cut.lower()}"] = values.get(metric, np.nan)
        row["cc_denominator_kind"] = "observed_source_loc"
        row["repo_size_definition_version"] = "source-loc-v1"
        pieces.append(row)
    return pd.DataFrame(pieces)


def compute_delta_dt(evaluator: pd.DataFrame) -> pd.DataFrame:
    """Compute technical complexity trajectory and T1-to-T3 deltas."""
    result = _pivot_cut(evaluator, "technical_complexity_mean", "technical_complexity")
    for left, right, name in (("t1", "t2", "delta_dt_t1_t2"), ("t2", "t3", "delta_dt_t2_t3"), ("t1", "t3", "delta_dt_t1_t3")):
        result[name] = result[f"technical_complexity_{right}"] - result[f"technical_complexity_{left}"]
    return result


def compute_integration_friction(commits: pd.DataFrame, cut_starts: dict[str, pd.Timestamp]) -> pd.DataFrame:
    """Compute author concentration and churn for cuts and the T3 final window."""
    required = {"timestamp", "ID_Autor_Local", "branch_or_ref", "branch_or_ref_source"}
    if not required.issubset(commits.columns):
        raise ValueError(f"git_commits missing AI fields: {sorted(required - set(commits.columns))}")
    rows = []
    for key, subset in commits.groupby(KEYS):
        row = dict(zip(KEYS, key))
        for cut in CUTS:
            current = subset[subset["temporal_marker"] == cut]
            counts = current["ID_Autor_Local"].value_counts()
            row[f"ai_commit_n_{cut.lower()}"] = int(len(current))
            row[f"ai_churn_{cut.lower()}"] = int((current["lines_added"] + current["lines_deleted"]).sum())
            row[f"ai_author_n_{cut.lower()}"] = int(current["ID_Autor_Local"].nunique())
            row[f"ai_max_author_share_{cut.lower()}"] = float(counts.iloc[0] / len(current)) if len(current) else np.nan
        start = cut_starts["T3"]
        window = subset[(subset["timestamp"] >= start - pd.Timedelta(hours=48)) & (subset["timestamp"] < start)]
        counts = window["ID_Autor_Local"].value_counts()
        row["ai_commit_n_48h_before_t3"] = int(len(window))
        row["ai_churn_48h_before_t3"] = int((window["lines_added"] + window["lines_deleted"]).sum())
        row["ai_author_n_48h_before_t3"] = int(window["ID_Autor_Local"].nunique())
        row["ai_max_author_share_48h_before_t3"] = float(counts.iloc[0] / len(window)) if len(window) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def build_team_metrics(*partials: pd.DataFrame) -> pd.DataFrame:
    """Merge team-level metric partials with declared one-to-one cardinality."""
    if not partials:
        raise ValueError("At least one metric partial is required")
    result = partials[0].copy()
    for partial in partials[1:]:
        if partial.duplicated(KEYS).any():
            raise ValueError("Metric partial has duplicate team_semester keys")
        result = result.merge(partial, on=KEYS, how="outer", validate="one_to_one")
    result["unit_of_analysis"] = "team_semester"
    return result