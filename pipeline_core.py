"""Core pipeline functions for anonymization, data processing, and analysis.

This module provides reusable functions for the UECE research pipeline:
- Anonymization of PII with salted hashing
- Git history extraction with dynamic author mapping
- Record loading/writing in multiple formats
- NLP enrichment for work style classification
- Metric computation (code churn, planning index, etc.)
- Statistical analysis (correlations, hypothesis tests)
"""

from __future__ import annotations

import csv
import hashlib
import logging
import re
from pathlib import Path
from typing import Any
import subprocess

import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)
IDENTIFIER_FIELD_TOKENS = {"email", "mail", "nome", "name", "aluno", "avaliador"}


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
) -> dict[str, str]:
    """Build a mapping of identifiers to anonymized versions.

    Args:
        name_lists: Lists of names/emails to anonymize
        transcript_paths: Paths to transcript files to extract identifiers from
        salt: Salt for hashing

    Returns:
        A dictionary mapping original identifiers to anonymized versions
    """
    identifiers: set[str] = set()

    # Collect from name lists
    for name_list in name_lists:
        identifiers.update(
            name.strip() for name in name_list if isinstance(name, str) and name.strip()
        )

    # Extract from transcripts
    for transcript_path in transcript_paths:
        try:
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
        except Exception as e:
            logger.warning(f"Failed to read transcript {transcript_path}: {e}")

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
    text = _replace_identifiers_in_text(text, mapping)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")

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


def extract_git_history(
    repo_path: Path,
    mapping: dict[str, str],
    salt: str = "",
) -> list[dict[str, Any]]:
    """Extract anonymized Git history from a repository.

    Args:
        repo_path: Path to Git repository
        mapping: Dictionary of identifier -> anonymized mappings
        salt: Salt for hashing new author emails

    Returns:
        List of commit records with anonymized authors
    """
    rows = []
    repo_name = repo_path.name

    try:
        # Get list of all commits with stats
        result = subprocess.run(
            [
                "git",
                "log",
                "--pretty=format:%ae|%ai|%H",
                "--numstat",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )

        lines = result.stdout.strip().split("\n")
        current_commit = None
        files_changed = 0
        lines_added = 0
        lines_deleted = 0

        for line in lines:
            if "|" in line and "@" in line:
                # This is a commit header
                if current_commit:
                    # Store previous commit
                    author_email = current_commit["author_email"]
                    if author_email in mapping:
                        author_alias = mapping[author_email]
                    else:
                        author_alias = _hash_identifier(author_email, salt)

                    rows.append(
                        {
                            "repository": repo_name,
                            "author_alias": author_alias,
                            "commit_hash": current_commit["commit_hash"],
                            "timestamp": current_commit["timestamp"],
                            "files_changed": files_changed,
                            "lines_added": lines_added,
                            "lines_deleted": lines_deleted,
                        }
                    )

                parts = line.split("|")
                current_commit = {
                    "author_email": parts[0],
                    "timestamp": parts[1],
                    "commit_hash": parts[2],
                }
                files_changed = 0
                lines_added = 0
                lines_deleted = 0

            elif current_commit and line.strip():
                # This is a file stat line
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        added = int(parts[0])
                        deleted = int(parts[1])
                        files_changed += 1
                        lines_added += added
                        lines_deleted += deleted
                    except ValueError:
                        pass

        # Store last commit
        if current_commit:
            author_email = current_commit["author_email"]
            if author_email in mapping:
                author_alias = mapping[author_email]
            else:
                author_alias = _hash_identifier(author_email, salt)

            rows.append(
                {
                    "repository": repo_name,
                    "author_alias": author_alias,
                    "commit_hash": current_commit["commit_hash"],
                    "timestamp": current_commit["timestamp"],
                    "files_changed": files_changed,
                    "lines_added": lines_added,
                    "lines_deleted": lines_deleted,
                }
            )

    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to extract Git history from {repo_path}: {e}")

    return rows


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


def compute_metrics(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute research metrics from enriched records.

    Metrics:
    - code_churn: lines_added + lines_deleted (total code changes)
    - planning_index: 1.0 if structured, 0.5 if mixed, 0.1 if vibe_coding
    - exhaustion_index: (technical_complexity_t3 - technical_complexity_t1) / 10
    - delta_technical_degradation: technical_complexity_t3 - technical_complexity_t1

    Args:
        records: List of enriched records

    Returns:
        Records with computed metrics
    """
    metrics_records = []

    def _coerce_float(value: Any) -> float:
        if value is None or pd.isna(value):
            return 0.0
        try:
            if isinstance(value, str):
                value = value.strip().replace(",", ".")
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    for record in records:
        metric_record = record.copy()

        # Code Churn: Total lines changed (added + deleted)
        lines_added = _coerce_float(record.get("lines_added", 0))
        lines_deleted = _coerce_float(record.get("lines_deleted", 0))
        metric_record["code_churn"] = lines_added + lines_deleted

        # Planning Index
        work_style = record.get("nlp_work_style", "mixed")
        planning_map = {
            "structured": 1.0,
            "mixed": 0.5,
            "vibe_coding": 0.1,
        }
        metric_record["planning_index"] = planning_map.get(work_style, 0.5)

        # Exhaustion Index
        t1 = _coerce_float(record.get("technical_complexity_t1", 0))
        t3 = _coerce_float(record.get("technical_complexity_t3", 0))
        delta = t3 - t1
        metric_record["exhaustion_index"] = max(0.0, delta / 10.0)
        metric_record["delta_technical_degradation"] = delta

        metrics_records.append(metric_record)

    return metrics_records


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
                try:
                    corr, p_value = stats.spearmanr(df[col_x], df[col_y])
                    results.append(
                        {
                            "feature_x": col_x,
                            "feature_y": col_y,
                            "correlation": corr,
                            "p_value": p_value,
                        }
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to compute correlation for {col_x}, {col_y}: {e}"
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
        return results

    work_styles = df["nlp_work_style"].dropna().unique()
    if len(work_styles) < 2:
        return results

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    for metric in numeric_cols:
        # Compare structured vs vibe_coding
        structured = df[df["nlp_work_style"] == "structured"][metric].dropna()
        vibe = df[df["nlp_work_style"] == "vibe_coding"][metric].dropna()

        if len(structured) > 0 and len(vibe) > 0:
            try:
                statistic, p_value = stats.mannwhitneyu(
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
            except Exception as e:
                logger.warning(f"Failed to run Mann-Whitney U test for {metric}: {e}")

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
