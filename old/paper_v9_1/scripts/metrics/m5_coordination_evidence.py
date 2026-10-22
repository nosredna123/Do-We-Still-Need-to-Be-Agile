"""Generate deterministic M5 coordination-friction evidence from transcripts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_metrics_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "m5-coordination-evidence-v1"
LEXICON_VERSION = "m5-friction-lexicon-pt-v1"
TEMPORAL_MARKERS = ("T1", "T2", "T3")
REQUIRED_COLUMNS = {
    "session_id", "transcript_file", "Semestre", "temporal_marker",
    "temporal_marker_source", "transcript_text", "status", "source_type",
}
FRICTION_LEXICON = {
    "alignment": r"coordena[çc][aã]o|comunica[çc][aã]o|alinh|sincron|divis[aã]o de taref|distribui[çc][aã]o de taref|depend[eê]ncia",
    "handoff": r"repasse|handoff|deleg[aã]|passar.{0,30}para",
    "integration": r"integra[çc][aã]o|merge|conflit|incompatibil|acopl",
    "blocker": r"bloque|imped|trava|gargalo",
    "rework": r"retrabalh|refaz|refazer|revis[aã]o",
}


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    frame.to_csv(temporary, index=False)
    os.replace(temporary, path)


def _atomic_json(payload: dict[str, Any], path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, path)


def _load_transcripts(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"M5 transcript contract not found: {path}")
    frame = pd.read_parquet(path)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"M5 transcript contract is missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("M5 transcript contract is empty")
    if frame[list(REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("M5 transcript contract contains null required values")
    if not frame["status"].eq("success").all():
        raise ValueError("M5 transcript contract contains non-success records")
    if frame["transcript_text"].astype(str).str.strip().eq("").any():
        raise ValueError("M5 transcript contract contains empty transcript text")
    invalid_markers = set(frame["temporal_marker"]) - set(TEMPORAL_MARKERS)
    if invalid_markers:
        raise ValueError(f"M5 transcript contract has invalid temporal markers: {sorted(invalid_markers)}")
    return frame.copy()


def _code_chunks(transcripts: pd.DataFrame) -> pd.DataFrame:
    chunks = transcripts[["session_id", "transcript_file", "Semestre", "temporal_marker", "transcript_text"]].copy()
    chunks["normalized_text"] = chunks["transcript_text"].astype(str).str.lower()
    chunks["token_n"] = chunks["normalized_text"].map(lambda text: len(re.findall(r"\b\w+\b", text)))
    for subtype, pattern in FRICTION_LEXICON.items():
        compiled = re.compile(pattern)
        chunks[subtype] = chunks["normalized_text"].map(lambda text, expression=compiled: len(expression.findall(text)))
    chunks["friction_marker_n"] = chunks[list(FRICTION_LEXICON)].sum(axis=1)
    if chunks["token_n"].le(0).any():
        raise ValueError("M5 cannot compute density for a transcript chunk without tokens")
    return chunks


def _build_outputs(chunks: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    subtype_columns = list(FRICTION_LEXICON)
    observed_markers = set(chunks["temporal_marker"])
    missing_markers = set(TEMPORAL_MARKERS).difference(observed_markers)
    if missing_markers:
        raise ValueError(f"M5 transcript contract has no observations for temporal markers: {sorted(missing_markers)}")
    grouped = chunks.groupby("temporal_marker", sort=False, observed=True)
    density = grouped.agg(
        transcript_chunk_n=("transcript_text", "size"),
        source_session_n=("session_id", "nunique"),
        character_n=("transcript_text", lambda values: int(values.str.len().sum())),
        token_n=("token_n", "sum"),
        friction_marker_n=("friction_marker_n", "sum"),
        **{subtype: (subtype, "sum") for subtype in subtype_columns},
    ).reindex(list(TEMPORAL_MARKERS)).reset_index()
    density["friction_marker_density_per_1k_tokens"] = 1_000 * density["friction_marker_n"] / density["token_n"]
    density["analysis_level"] = "global_transcript_corpus_by_temporal_marker"
    density["measurement_status"] = "available"

    composition = density[["temporal_marker", "friction_marker_n", *subtype_columns]].melt(
        id_vars=["temporal_marker", "friction_marker_n"],
        value_vars=subtype_columns,
        var_name="friction_subtype",
        value_name="marker_n",
    )
    composition["marker_share"] = composition["marker_n"] / composition["friction_marker_n"].replace(0, pd.NA)
    composition["analysis_level"] = "global_transcript_corpus_by_temporal_marker"

    coverage = density[[
        "temporal_marker", "transcript_chunk_n", "source_session_n", "character_n", "token_n",
    ]].copy()
    coverage["friction_marker_n"] = density["friction_marker_n"]
    coverage["observed_semester_n"] = chunks.groupby("temporal_marker")["Semestre"].nunique().reindex(list(TEMPORAL_MARKERS)).to_numpy()
    coverage["observed_semesters"] = chunks.groupby("temporal_marker")["Semestre"].agg(lambda values: ", ".join(sorted(values.unique()))).reindex(list(TEMPORAL_MARKERS)).to_numpy()
    coverage["analysis_level"] = "global_transcript_corpus_by_temporal_marker"

    audit = chunks.loc[chunks["friction_marker_n"].gt(0), [
        "Semestre", "temporal_marker", "session_id", "transcript_file", "token_n", "friction_marker_n",
        *subtype_columns, "transcript_text",
    ]].sort_values(["temporal_marker", "friction_marker_n", "token_n"], ascending=[True, False, False]).reset_index(drop=True)
    audit["lexicon_version"] = LEXICON_VERSION
    return density, composition, coverage, audit


def generate(force: bool = False, verbose: bool = False) -> dict[str, Any]:
    root = resolve_paper_v9_dir()
    metrics_dir = resolve_metrics_dir()
    transcripts_path = root.parent / "data" / "lake" / "transcript_sessions.parquet"
    input_hash = compute_sha256(transcripts_path)
    config = {"contract_version": CONTRACT_VERSION, "lexicon_version": LEXICON_VERSION, "temporal_markers": list(TEMPORAL_MARKERS)}
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    names = [
        "m5_marker_density.csv", "m5_marker_composition.csv", "m5_corpus_coverage.csv",
        "m5_evidence_audit_trail.csv", "m5_lexicon.json", "m5_coordination_evidence.metadata.json",
    ]
    paths = [metrics_dir / name for name in names]
    if not force and all(path.is_file() for path in paths):
        metadata = json.loads(paths[-1].read_text(encoding="utf-8"))
        if metadata.get("input_sha256") == input_hash and metadata.get("config_sha256") == config_hash:
            return {"status": "resumed", "artifacts": [str(path) for path in paths]}

    chunks = _code_chunks(_load_transcripts(transcripts_path))
    density, composition, coverage, audit = _build_outputs(chunks)
    lexicon = {"version": LEXICON_VERSION, "language": "Portuguese", "patterns": FRICTION_LEXICON, "counting_rule": "regex match count per transcript chunk; chunks are provenance units, not independent observations"}
    metadata = {
        "status": "success", "gate_status": "pending", "contract_version": CONTRACT_VERSION,
        "metric_definition_version": CONTRACT_VERSION, "input_sha256": input_hash, "config_sha256": config_hash,
        "rq": "RQ2", "unit_of_analysis": "global transcript corpus by temporal marker",
        "source_contract": "data/lake/transcript_sessions.parquet", "legacy_source": "paper_v8/data/m5_coordination_friction_trajectory.csv",
        "lexicon_version": LEXICON_VERSION, "llm_calls_required": False, "inference": "descriptive_only",
        "observed_semesters": sorted(chunks["Semestre"].unique()), "observed_temporal_markers": list(TEMPORAL_MARKERS),
        "coverage": {"transcript_chunks": int(len(chunks)), "source_sessions": int(chunks["session_id"].nunique()), "tokens": int(chunks["token_n"].sum()), "audit_rows": int(len(audit))},
        "limitations": ["lexical markers are candidate textual evidence, not diagnoses of coordination failure", "transcript data has no team identifier", "chunks and source sessions are not independent replicates", "no hypothesis tests, confidence intervals, correlations, or causal claims are produced"],
        "artifacts": names,
    }
    _atomic_csv(density, paths[0]); _atomic_csv(composition, paths[1]); _atomic_csv(coverage, paths[2]); _atomic_csv(audit, paths[3]); _atomic_json(lexicon, paths[4]); _atomic_json(metadata, paths[5])
    if verbose:
        print(json.dumps(metadata, indent=2, sort_keys=True))
    return {"status": "generated", "artifacts": [str(path) for path in paths]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the v9 M5 coordination evidence metric")
    parser.add_argument("--force", action="store_true", help="Regenerate existing artifacts")
    parser.add_argument("--verbose", action="store_true", help="Print generated metadata")
    args = parser.parse_args()
    print(json.dumps(generate(force=args.force, verbose=args.verbose), indent=2))


if __name__ == "__main__":
    main()