"""Core pipeline functions for anonymization, data processing, and analysis.

This module provides reusable functions for the UECE research pipeline:
- Anonymization of PII with salted hashing
- Git history extraction with dynamic author mapping
- Record loading/writing in multiple formats
- NLP enrichment for work style classification
- Statistical analysis (correlations, hypothesis tests)
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Any, Mapping
import subprocess

import pandas as pd
from dotenv import load_dotenv
from scipy import stats as scipy_stats

logger = logging.getLogger(__name__)
DOTENV_PATH = Path(__file__).resolve().with_name(".env")
IDENTIFIER_FIELD_TOKENS = {"email", "mail", "nome", "name", "aluno", "avaliador"}


def load_project_environment() -> bool:
    """Load the project dotenv file without overriding process variables."""
    return load_dotenv(dotenv_path=DOTENV_PATH, override=False)


def file_checksum(path: Path) -> str:
    """Calculate the SHA-256 checksum of a file.

    Args:
        path: Path to the file to fingerprint.

    Returns:
        Hexadecimal SHA-256 checksum.
    """
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def input_checksum(paths: list[Path], options: Mapping[str, str]) -> str:
    """Calculate a deterministic checksum for files and processing options.

    Args:
        paths: Input files that affect the generated artifact.
        options: Processing options that affect the generated artifact.

    Returns:
        Hexadecimal SHA-256 checksum of the effective inputs.
    """
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.name.encode("utf-8"))
        digest.update(file_checksum(path).encode("ascii"))
    digest.update(json.dumps(dict(options), sort_keys=True).encode("utf-8"))
    return digest.hexdigest()


def artifact_metadata_path(artifact_path: Path) -> Path:
    """Return the sidecar metadata path for a generated artifact."""
    return artifact_path.with_name(f"{artifact_path.name}.metadata.json")


def is_current_artifact(artifact_path: Path, source_checksum: str) -> bool:
    """Return whether an artifact completed successfully for an input checksum."""
    metadata_path = artifact_metadata_path(artifact_path)
    if not artifact_path.exists() or not metadata_path.exists():
        return False

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError, OSError):
        return False

    return (
        metadata.get("status") == "success"
        and metadata.get("input_checksum") == source_checksum
    )

def write_artifact_metadata(artifact_path: Path, source_checksum: str) -> None:
    """Record successful processing metadata for an artifact.

    Args:
        artifact_path: Generated artifact associated with the metadata.
        source_checksum: SHA-256 checksum of the artifact's effective input.
    """
    metadata_path = artifact_metadata_path(artifact_path)
    metadata_path.write_text(
        json.dumps({"input_checksum": source_checksum, "status": "success"}, indent=2),
        encoding="utf-8",
    )


def _resolve_project_root(path: Path) -> Path:
    """Resolve a nested cleanup path to the repository root for this project."""
    resolved = path.resolve()
    if not resolved.exists():
        raise ValueError(f"Cleanup path {path} is outside the project root")

    for candidate in (resolved, *resolved.parents):
        data_dir = candidate / "data"
        if data_dir.exists() and (data_dir / "processed").exists():
            return candidate

    raise ValueError(f"Cleanup path {path} is outside the project root")


def cleanup_phase_one_artifacts(project_root: Path) -> None:
    """Remove the Phase 1 derived artifacts while preserving raw inputs.

    Args:
        project_root: Root directory of the project being cleaned.

    Raises:
        ValueError: If the requested path is not a valid project root.
    """
    resolved_root = _resolve_project_root(project_root)

    targets = [
        resolved_root / "data" / "processed" / "forms",
        resolved_root / "data" / "processed" / "transcripts_anon",
        resolved_root / "data" / "processed" / "chave_relacional.json",
        resolved_root / "data" / "lake" / "master_dataset.parquet",
        resolved_root / "data" / "lake" / "student_responses.parquet",
        resolved_root / "data" / "lake" / "evaluator_team_cuts.parquet",
        resolved_root / "data" / "lake" / "git_team_cuts.parquet",
        resolved_root / "data" / "lake" / "git_commits.parquet",
        resolved_root / "data" / "lake" / "git_files.parquet",
        resolved_root / "data" / "lake" / "transcript_sessions.parquet",
        resolved_root / "data" / "lake" / "lake_validation_report.json",
        resolved_root / "data" / "processed" / "git_logs_anon.csv",
        resolved_root / "data" / "processed" / "git_commits_anon.csv",
        resolved_root / "data" / "processed" / "git_files_anon.csv",
        resolved_root / "data" / "processed" / "clean_repos",
    ]

    for target in targets:
        if target.is_dir():
            for child in sorted(target.iterdir(), reverse=True):
                if child.is_dir():
                    for nested_child in sorted(child.rglob("*"), reverse=True):
                        if nested_child.is_file() or nested_child.is_symlink():
                            nested_child.unlink()
                        elif nested_child.is_dir():
                            nested_child.rmdir()
                    child.rmdir()
                else:
                    child.unlink()
            target.rmdir()
        elif target.exists():
            target.unlink()
        sidecar = artifact_metadata_path(target)
        if sidecar.exists():
            sidecar.unlink()

    protected_paths = [
        resolved_root / "data" / "raw",
        resolved_root / "data" / "processed" / "audio_chunks",
        resolved_root / "data" / "processed" / "transcripts",
        resolved_root / "data" / "processed" / "ner_candidates",
    ]
    for protected in protected_paths:
        if protected.exists():
            logger.info("Preserving Phase 1 raw artifact directory: %s", protected)


def _hash_identifier(identifier: str, salt: str = "") -> str:
    """Generate a salted hash for an identifier.

    Args:
        identifier: The text to hash (name, email, etc.)
        salt: Salt to mix with the hash for additional security

    Returns:
        A deterministic anonymized identifier starting with 'anon_'
    """
    combined = f"{identifier}_{salt}".encode("utf-8")
    digest = hashlib.sha256(combined).hexdigest()[:12]
    return f"anon_{digest}"


def is_identifier_field(field_name: str) -> bool:
    """Return whether a CSV column name should be treated as an identifier field."""
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", field_name)
    normalized = re.sub(r"[^0-9A-Za-zÀ-ÿ]+", " ", normalized).lower()
    tokens = {token for token in normalized.split() if token}
    return bool(tokens & IDENTIFIER_FIELD_TOKENS)


def build_anonymization_mapping(
    name_lists: list[list[str]],
    transcript_paths: list[Path],
    salt: str = "",
    person_names: list[str] | None = None,
) -> dict[str, str]:
    """Build a mapping of identifiers to anonymized versions.

    Args:
        name_lists: Lists of names/emails to anonymize
        transcript_paths: Paths to transcript files to extract identifiers from
        salt: Salt for hashing
        person_names: Person names identified by the NER stage

    Returns:
        A dictionary mapping original identifiers to anonymized versions
    """
    identifiers: set[str] = set()
    identifiers.update(person_names or [])

    # Collect from name lists
    for name_list in name_lists:
        identifiers.update(
            name.strip() for name in name_list if isinstance(name, str) and name.strip()
        )

    # Extract from transcripts
    for transcript_path in transcript_paths:
        text = transcript_path.read_text(encoding="utf-8")
        # Extract emails
        for email in re.findall(r"\b[\w.\-+%]+@[\w.\-]+\.\w+\b", text):
            identifiers.add(email)

        # Extract explicit speaker labels (e.g., "Carol:")
        for line in text.splitlines():
            match = re.match(
                r"^\s*([A-ZÀ-Ý][\wÀ-ÿ'’-]*(?:\s+[A-ZÀ-Ý][\wÀ-ÿ'’-]*){0,3})\s*:\s*(.+)$",
                line,
            )
            if match and "@" not in match.group(2):
                identifiers.add(match.group(1).strip())

    return {ident: _hash_identifier(ident, salt) for ident in identifiers}


def anonymize_csv_file(
    csv_path: Path,
    output_path: Path,
    mapping: dict[str, str],
    salt: str = "",
) -> None:
    """Anonymize a CSV file by replacing identifiers with hashes.

    Args:
        csv_path: Path to input CSV
        output_path: Path to output CSV
        mapping: Dictionary of identifier -> anonymized mappings
        salt: Salt for hashing new identifiers not in mapping
    """
    rows = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        
        for row in reader:
            anon_row = {}
            for key, value in row.items():
                if not isinstance(value, str):
                    anon_row[key] = value
                    continue

                if is_identifier_field(key):
                    anon_row[key] = mapping.get(value, _hash_identifier(value, salt))
                else:
                    anon_row[key] = _replace_identifiers_in_text(value, mapping, salt)
            rows.append(anon_row)

    # Write anonymized CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if rows:
            writer.writerows(rows)


def anonymize_transcript(
    transcript_path: Path,
    output_path: Path,
    mapping: dict[str, str],
) -> None:
    """Redact identifiers from a transcript file.

    Args:
        transcript_path: Path to input transcript
        output_path: Path to output transcript
        mapping: Dictionary of identifier -> anonymized mappings
    """
    text = transcript_path.read_text(encoding="utf-8")
    if transcript_path.suffix.lower() == ".json":
        data = json.loads(text)
        text = json.dumps(_anonymize_json_value(data, mapping), indent=2)
    else:
        text = _replace_identifiers_in_text(text, mapping)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def _anonymize_json_value(value: Any, mapping: dict[str, str]) -> Any:
    """Recursively redact strings contained in a JSON-compatible value."""
    if isinstance(value, dict):
        return {key: _anonymize_json_value(item, mapping) for key, item in value.items()}
    if isinstance(value, list):
        return [_anonymize_json_value(item, mapping) for item in value]
    if isinstance(value, str):
        return _replace_identifiers_in_text(value, mapping)
    return value

def _replace_identifiers_in_text(
    text: str,
    mapping: dict[str, str],
    salt: str = "",
) -> str:
    """Replace mapped identifiers within free text while preserving other content."""
    replaced_text = text
    for original in sorted(mapping, key=len, reverse=True):
        replaced_text = re.sub(
            rf"\b{re.escape(original)}\b",
            mapping[original],
            replaced_text,
            flags=re.IGNORECASE,
        )

    for email in re.findall(r"\b[\w.\-+%]+@[\w.\-]+\.\w+\b", replaced_text):
        replaced_text = replaced_text.replace(email, mapping.get(email, _hash_identifier(email, salt)))

    return replaced_text


def infer_temporal_marker_from_timestamp(value: Any, semester: str | None = None) -> str:
    """Infer the Phase 1 temporal marker from a commit timestamp.

    Git events use phase boundaries rather than evaluator submission windows:
    dates before T1 are T1, dates from T1 until T2 are T2, and dates from T2
    onward are T3.
    """
    from datetime import date

    from pipeline_config import EVALUATOR_TEMPORAL_CUTS, git_temporal_marker_for

    if value is None or pd.isna(value):
        raise ValueError("Git commit timestamp is missing")

    parsed = pd.to_datetime(value, errors="raise")
    date_value = parsed.strftime("%Y-%m-%d")
    current_date = date.fromisoformat(date_value)

    if semester:
        return git_temporal_marker_for(str(semester), date_value)

    for cuts in EVALUATOR_TEMPORAL_CUTS.values():
        semester_dates = [
            d
            for _marker, (start_date, end_date) in cuts.items()
            for d in (date.fromisoformat(start_date), date.fromisoformat(end_date))
        ]
        if min(semester_dates) <= current_date <= max(semester_dates):
            for marker, (start_date, end_date) in cuts.items():
                if date.fromisoformat(start_date) <= current_date <= date.fromisoformat(end_date):
                    return marker
            raise ValueError(
                f"Commit timestamp {value!r} does not fall inside any configured T1/T2/T3 cut"
            )

    raise ValueError(
        f"Commit timestamp {value!r} does not fall inside any configured T1/T2/T3 cut"
    )


def _git_branch_for_commit(repo_path: Path, commit_hash: str) -> tuple[str | None, str]:
    """Return an observed branch/ref for a commit, without fabricating one."""
    result = subprocess.run(
        ["git", "branch", "--contains", commit_hash, "--format=%(refname:short)"],
        cwd=repo_path, capture_output=True, text=True, check=True,
    )
    refs = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return (refs[0], "git_branch_contains") if refs else (None, "unavailable")


def _git_diff_paths(repo_path: Path, commit_hash: str) -> list[dict[str, Any]]:
    """Read NUL-delimited numstat and name-status records for one commit."""
    numstat = subprocess.run(
        ["git", "diff-tree", "--root", "--no-commit-id", "--numstat", "-z", "-r", "--find-renames", commit_hash],
        cwd=repo_path, capture_output=True, check=True,
    ).stdout.split(b"\0")
    status_tokens = subprocess.run(
        ["git", "diff-tree", "--root", "--no-commit-id", "--name-status", "-z", "-r", "--find-renames", commit_hash],
        cwd=repo_path, capture_output=True, check=True,
    ).stdout.split(b"\0")
    statuses: list[tuple[str, str, str | None]] = []
    index = 0
    while index < len(status_tokens):
        token = status_tokens[index].decode("utf-8", errors="strict")
        index += 1
        if not token:
            continue
        status = token
        if index >= len(status_tokens) or not status:
            raise ValueError(f"Malformed Git name-status record for {commit_hash}")
        old_path = status_tokens[index].decode("utf-8", errors="strict")
        index += 1
        new_path: str | None = None
        if status.startswith(("R", "C")):
            if index >= len(status_tokens):
                raise ValueError(f"Incomplete Git rename record for {commit_hash}")
            new_path = status_tokens[index].decode("utf-8", errors="strict")
            index += 1
        statuses.append((status[0].lower() if status[0] not in "RC" else status[0].lower(), old_path, new_path))

    file_stats: list[tuple[int | None, int | None, str]] = []
    index = 0
    while index < len(numstat):
        token = numstat[index].decode("utf-8", errors="strict")
        index += 1
        if not token:
            continue
        parts = token.split("\t", 2)
        if len(parts) != 3:
            raise ValueError(f"Malformed Git numstat record for {commit_hash}")
        added = None if parts[0] == "-" else int(parts[0])
        deleted = None if parts[1] == "-" else int(parts[1])
        path = parts[2]
        if not path and statuses[len(file_stats)][0] in {"r", "c"}:
            if index + 1 >= len(numstat):
                raise ValueError(f"Incomplete Git rename statistics for {commit_hash}")
            index += 1
            path = numstat[index].decode("utf-8", errors="strict")
            index += 1
        file_stats.append((added, deleted, path))

    if len(file_stats) != len(statuses):
        raise ValueError(f"Git file statistics do not align for {commit_hash}")
    rows: list[dict[str, Any]] = []
    for (added, deleted, path), (status, old_path, new_path) in zip(file_stats, statuses):
        rows.append({
            "file_path": path, "file_path_old": old_path if status == "r" else None,
            "change_status": {"a": "added", "m": "modified", "d": "deleted", "r": "renamed", "c": "copied"}[status],
            "lines_added": added, "lines_deleted": deleted,
            "is_binary": added is None or deleted is None,
        })
        if new_path is not None:
            rows[-1]["file_path"] = new_path
    return rows


def extract_git_events(repo_path: Path, semester: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Extract commit and file events using unambiguous NUL-delimited Git output."""
    result = subprocess.run(
        ["git", "log", "--reverse", "--format=%H%x00%ae%x00%aI%x00"],
        cwd=repo_path, capture_output=True, text=True, check=True,
    )
    fields = [field.strip() for field in result.stdout.split("\0") if field.strip()]
    if len(fields) % 3:
        raise ValueError(f"Malformed Git commit output for {repo_path}")
    commits: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    for offset in range(0, len(fields), 3):
        commit_hash, author_email, timestamp = fields[offset:offset + 3]
        marker = infer_temporal_marker_from_timestamp(timestamp, semester)
        branch, branch_source = _git_branch_for_commit(repo_path, commit_hash)
        file_rows = _git_diff_paths(repo_path, commit_hash)
        commits.append({
            "repository": repo_path.name, "author_alias": author_email,
            "commit_hash": commit_hash, "timestamp": timestamp,
            "temporal_marker": marker, "files_changed": len(file_rows),
            "lines_added": sum(row["lines_added"] or 0 for row in file_rows),
            "lines_deleted": sum(row["lines_deleted"] or 0 for row in file_rows),
            "branch_or_ref": branch, "branch_or_ref_source": branch_source,
        })
        for row in file_rows:
            files.append({**row, "repository": repo_path.name, "author_alias": author_email,
                          "commit_hash": commit_hash, "timestamp": timestamp,
                          "temporal_marker": marker, "branch_or_ref": branch,
                          "branch_or_ref_source": branch_source})
    return commits, files


def load_records(path: Path) -> list[dict[str, Any]]:
    """Load records from CSV or Parquet file.

    Args:
        path: Path to CSV or Parquet file

    Returns:
        List of dictionaries representing records
    """
    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
        return df.to_dict(orient="records")
    elif path.suffix == ".csv":
        df = pd.read_csv(path, keep_default_na=False, dtype=str)
        return df.to_dict(orient="records")
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")


def write_records(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write records to Parquet file.

    Args:
        path: Path to output Parquet file
        rows: List of dictionaries to write
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_parquet(path, index=False)


def enrich_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Enrich records with NLP-based work style classification.

    Args:
        records: List of records to enrich

    Returns:
        Enhanced records with nlp_work_style field
    """
    enriched = []

    for record in records:
        enriched_record = record.copy()
        feedback = str(record.get("feedback", "")).lower()

        # Simple keyword-based classification
        if any(
            keyword in feedback
            for keyword in [
                "specification",
                "planning",
                "architecture",
                "structured",
                "design",
                "clear",
            ]
        ):
            enriched_record["nlp_work_style"] = "structured"
        elif any(
            keyword in feedback
            for keyword in ["vibe", "chaos", "rework", "stress", "unclear"]
        ):
            enriched_record["nlp_work_style"] = "vibe_coding"
        else:
            enriched_record["nlp_work_style"] = "mixed"

        enriched.append(enriched_record)

    return enriched


def correlation_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute pairwise Spearman correlations between numeric features.

    Args:
        records: List of records with numeric fields

    Returns:
        List of correlation results
    """
    df = pd.DataFrame(records)
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    results = []

    for i, col_x in enumerate(numeric_cols):
        for col_y in numeric_cols[i + 1 :]:
            # Avoid self-correlations
            if col_x != col_y:
                corr, p_value = scipy_stats.spearmanr(df[col_x], df[col_y])
                results.append(
                    {
                        "feature_x": col_x,
                        "feature_y": col_y,
                        "correlation": corr,
                        "p_value": p_value,
                    }
                )

    return results


def hypothesis_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run Mann-Whitney U tests comparing groups (e.g., structured vs vibe_coding).

    Args:
        records: List of records with nlp_work_style and numeric metrics

    Returns:
        List of hypothesis test results
    """
    df = pd.DataFrame(records)
    results = []

    if "nlp_work_style" not in df.columns:
        raise ValueError("records are missing required nlp_work_style column")

    work_styles = df["nlp_work_style"].dropna().unique()
    if len(work_styles) < 2:
        return results

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    for metric in numeric_cols:
        # Compare structured vs vibe_coding
        structured = df[df["nlp_work_style"] == "structured"][metric].dropna()
        vibe = df[df["nlp_work_style"] == "vibe_coding"][metric].dropna()

        if len(structured) > 0 and len(vibe) > 0:
            statistic, p_value = scipy_stats.mannwhitneyu(
                structured, vibe, alternative="two-sided"
            )
            results.append(
                {
                    "test": "mann_whitney_u",
                    "group_a": "structured",
                    "group_b": "vibe_coding",
                    "metric": metric,
                    "u_statistic": float(statistic),
                    "p_value": float(p_value),
                    "n_group_a": len(structured),
                    "n_group_b": len(vibe),
                }
            )

    return results


def write_hypothesis_csv(
    rows: list[dict[str, Any]], output_path: Path
) -> None:
    """Write hypothesis test results to CSV.

    Args:
        rows: List of hypothesis test results
        output_path: Path to output CSV file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "test",
        "group_a",
        "group_b",
        "metric",
        "u_statistic",
        "p_value",
        "n_group_a",
        "n_group_b",
    ]

    with output_path.open("w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
