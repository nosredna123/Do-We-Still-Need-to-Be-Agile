"""Prepare the pinned, allowlisted snapshot using only the Python standard library."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import logging
import math
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import TypeAlias

sys.dont_write_bytecode = True

from snapshot_contracts import (  # noqa: E402
    ALIASES, BOOLEAN_FIELDS, CONTRACT_SHA256, INDEX_SHA256, INTEGER_FIELDS,
    JSON_SOURCES, NULLABLE_FIELDS, RENAMES, SUPPLEMENT, SUPPLEMENT_SHA256,
    TABLES, TEXT_FIELDS, VERIFICATION, Table,
)

Scalar: TypeAlias = str | int | float | bool | None
Row: TypeAlias = dict[str, Scalar]
RawRow: TypeAlias = dict[str, str]
Pair: TypeAlias = tuple[str, str]


class ContractError(ValueError):
    """An explicit preparation failure; no snapshot may be published."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def obj(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ContractError("Expected a JSON object")
    require(all(isinstance(k, str) for k in value), "Expected string object keys")
    return dict(value)


def array(value: object) -> list[object]:
    if not isinstance(value, list):
        raise ContractError("Expected a JSON array")
    return list(value)


def text(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError("Expected a nonempty string")
    return value


def strict_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ContractError(f"Nonfinite JSON constant: {value}")


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs,
                      parse_constant=reject_constant)


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def resolved(path: Path) -> Path:
    absolute = path.absolute()
    require(not any(p.is_symlink() for p in (absolute, *absolute.parents)),
            "Symlink paths are not accepted")
    return absolute.resolve()


def outside(path: Path, directory: Path) -> None:
    require(not path.is_relative_to(directory), "Private inputs/lineage must remain outside public output")


def approvals(approval_path: Path, registry_path: Path, excerpt_path: Path,
              site: Path) -> tuple[dict[str, str], dict[Pair, Pair]]:
    for path in (approval_path, registry_path, excerpt_path):
        outside(path, site)
    approval = obj(read_json(approval_path))
    require(approval.get("status") == "approved" and approval.get("task") == "T003",
            "T003 human publication approval is required")
    require(obj(approval.get("contract")).get("sha256") == CONTRACT_SHA256,
            "Approval contract fingerprint differs; renewed review required")
    require(obj(approval.get("results_index")).get("sha256") == INDEX_SHA256,
            "Approval index fingerprint differs; renewed review required")
    allowlist = obj(approval.get("proposed_allowlist"))
    require(allowlist.get("status") == "approved_by_explicit_contract_reference"
            and allowlist.get("publication_authority_confirmed") is True
            and allowlist.get("human_review_attested") is True,
            "Explicit contract, authority, and human-review attestations required")
    attestations = obj(obj(approval.get("approval")).get("attestations"))
    required = (
        "reviewed_every_proposed_field_and_actual_values_and_category_vocabularies",
        "authorized_and_applicable_permissions_confirmed",
        "exact_numeric_values_and_small_cells_approved_after_linkage_review",
        "original_cohort_labels_approved_after_linkage_review",
        "existing_TEAM_labels_scoped_by_cohort_approved_after_linkage_review",
    )
    require(all(attestations.get(k) is True for k in required), "Missing human attestation")
    require(approval.get("open_decisions") == []
            and obj(approval.get("approval")).get("additional_restrictions") == [],
            "Unresolved decisions or additional restrictions require implementation/review")
    excerpt = obj(read_json(excerpt_path))
    require(excerpt.get("status") == "completed_omit_excerpts"
            and excerpt.get("contract_sha256") == CONTRACT_SHA256
            and excerpt.get("results_index_sha256") == INDEX_SHA256,
            "Pinned T004 no-excerpt decision required")
    require(excerpt.get("approved_excerpts") == [] and excerpt.get("candidates_selected") == []
            and all(excerpt.get(k) is False for k in (
                "public_dataset_allowed", "public_view_allowed", "public_descriptor_allowed",
                "empty_placeholder_allowed", "private_source_text_copied")),
            "This tool only supports the approved no-excerpt release")
    registry = obj(read_json(registry_path))
    require(registry.get("status") == "approved"
            and registry.get("review_id") == approval.get("review_id"),
            "Registry must belong to the approved review")
    cohorts: dict[str, str] = {}
    for item in array(registry.get("cohorts")):
        item = obj(item)
        source, public = text(item.get("source")), text(item.get("public"))
        require(source == public and source not in cohorts, "Unapproved or duplicate cohort mapping")
        cohorts[source] = public
    teams: dict[Pair, Pair] = {}
    for item in array(registry.get("teams")):
        item = obj(item)
        source = (text(item.get("source_cohort")), text(item.get("source_team")))
        public = (text(item.get("public_cohort")), text(item.get("public_team")))
        require(source not in teams and source == public and source[0] in cohorts,
                "Unapproved or duplicate team mapping")
        teams[source] = public
    require(len(cohorts) == 2 and len(teams) == 14, "Incomplete approved identifier registry")
    return cohorts, teams


def csv_rows(content: bytes, expected_columns: list[object], expected_n: object) -> list[RawRow]:
    reader = csv.DictReader(io.StringIO(content.decode("utf-8"), newline=""))
    require(reader.fieldnames == expected_columns
            and len(set(reader.fieldnames or [])) == len(reader.fieldnames or []),
            "Source CSV schema differs from pinned index")
    rows: list[RawRow] = []
    for row in reader:
        require(None not in row and all(isinstance(v, str) for v in row.values()),
                "Ragged CSV row")
        rows.append({k: text(v) if v else "" for k, v in row.items() if k is not None})
    require(bool(rows) and len(rows) == expected_n, "Source CSV row count differs from pinned index")
    return rows


def load_sources(root: Path) -> tuple[dict[str, list[RawRow]], dict[str, object], dict[str, str]]:
    index_path = resolved(root / "data/results/results_summary.json")
    outside(index_path, Path(__file__).resolve().parent.parent)
    index_bytes = index_path.read_bytes()
    require(digest(index_bytes) == INDEX_SHA256, "Source index changed; renewed human review required")
    index = obj(json.loads(index_bytes))
    artifacts: dict[str, dict[str, object]] = {}
    families = [*obj(index.get("metrics")).values(),
                *obj(obj(index.get("robustness_artifacts")).get("families")).values()]
    for family in families:
        for item in array(obj(family).get("artifacts")):
            record = obj(item)
            name = Path(text(record.get("path"))).name
            require(name not in artifacts, "Ambiguous source basename in index")
            artifacts[name] = record
    names = {t.source for t in TABLES} | set(ALIASES) | set(VERIFICATION) | set(JSON_SOURCES)
    require(len(names) == 58, "Implementation does not cover the selected 58 source dispositions")
    csv_data: dict[str, list[RawRow]] = {}
    json_data: dict[str, object] = {}
    hashes: dict[str, str] = {}
    supplement_bytes = {name: resolved(root / "figures" / name).read_bytes() for name in SUPPLEMENT}
    supplement_fingerprint = "".join(
        name + "\0" + digest(content) + "\n" for name, content in sorted(supplement_bytes.items()))
    require(digest(supplement_fingerprint.encode("utf-8")) == SUPPLEMENT_SHA256,
            "Selected supplementary inputs changed; reconcile and renew review")
    for name, content in supplement_bytes.items():
        reader = csv.DictReader(io.StringIO(content.decode("utf-8"), newline=""))
        records = list(reader)
        require(name not in artifacts, "Supplement/index source overlap requires reconciliation")
        artifacts[name] = {
            "path": "figures/" + name, "sha256": digest(content), "bytes": len(content),
            "columns": reader.fieldnames, "rows": len(records),
        }
    for name in sorted(names):
        require(name in artifacts, f"Required source absent from frozen inventory: {name}")
        record = artifacts[name]
        path = resolved(root / text(record.get("path")))
        require(path.is_relative_to(root), "Source path escapes explicit root")
        content = supplement_bytes[name] if name in supplement_bytes else path.read_bytes()
        require(digest(content) == record.get("sha256") and len(content) == record.get("bytes"),
                f"Source changed: {name}; reconcile and renew approval before export")
        hashes[name] = digest(content)
        if name.endswith(".csv"):
            csv_data[name] = csv_rows(content, array(record.get("columns")), record.get("rows"))
        else:
            json_data[name] = json.loads(content, object_pairs_hook=strict_pairs,
                                         parse_constant=reject_constant)
    return csv_data, json_data, hashes


def scalar(raw: str, field: str, dataset_id: str) -> Scalar:
    if raw == "":
        require(field in NULLABLE_FIELDS, f"Undocumented null: {dataset_id}/{field}")
        return None
    if field in BOOLEAN_FIELDS:
        require(raw in ("True", "False"), f"Invalid boolean: {dataset_id}/{field}")
        return raw == "True"
    if field in TEXT_FIELDS and not (dataset_id == "m1-autonomy" and field == "category"):
        if field == "checkpoint":
            require(raw in ("T1", "T2", "T3"), "Invalid checkpoint")
        return raw
    if field in INTEGER_FIELDS or (dataset_id == "m1-autonomy" and field == "category"):
        require(re.fullmatch(r"-?\d+(?:\.0+)?", raw) is not None,
                f"Invalid integer: {dataset_id}/{field}")
        value = int(raw.split(".")[0])
        require(value >= 0 or field in ("window_end_day", "start_day_relative_to_t3", "end_day_relative_to_t3"),
                f"Negative count: {dataset_id}/{field}")
        if field == "score" or (dataset_id == "m1-autonomy" and field == "category"):
            require(1 <= value <= 5, "Invalid 1-5 category")
        return value
    try:
        value_float = float(raw)
    except ValueError as exc:
        raise ContractError(f"Invalid number: {dataset_id}/{field}") from exc
    require(math.isfinite(value_float), f"Nonfinite number: {dataset_id}/{field}")
    if "rho" in field:
        bound = 2 if "delta" in field else 1
        require(-bound <= value_float <= bound, f"Invalid coefficient: {dataset_id}/{field}")
    elif field in ("spearman_p_exploratory", "coverage", "share", "share_of_topic_assignments",
                   "clean_rework_ratio_t3") or field.endswith(("_share", "_component")) \
            or field in ("regularity_index", "author_gini", "median_author_gini", "median_max_author_share"):
        require(0 <= value_float <= 1, f"Invalid fraction: {dataset_id}/{field}")
    elif field.endswith("_pct"):
        require(0 <= value_float <= 100, f"Invalid percentage: {dataset_id}/{field}")
    return value_float


def keyed(rows: list[RawRow], keys: tuple[str, ...]) -> dict[tuple[str, ...], RawRow]:
    result: dict[tuple[str, ...], RawRow] = {}
    for row in rows:
        require(all(row.get(k) not in (None, "") for k in keys), "Missing/non-null key contract")
        key = tuple(row[k] for k in keys)
        require(key not in result, "Duplicate analytical key")
        result[key] = row
    return result


def equivalent(left: str, right: str) -> bool:
    if left == right:
        return True
    try:
        a, b = float(left), float(right)
    except ValueError:
        return False
    return math.isfinite(a) and math.isfinite(b) and math.isclose(a, b, rel_tol=0, abs_tol=1e-12)


def agree(left: list[RawRow], right: list[RawRow], keys: tuple[str, ...],
          fields: set[str]) -> None:
    a, b = keyed(left, keys), keyed(right, keys)
    require(a.keys() == b.keys(), "Join/alias coverage differs")
    for key in a:
        for field in fields:
            require(equivalent(a[key][field], b[key][field]), f"Join/alias values differ for {field}")


def map_identifiers(row: RawRow, projected: Row, cohorts: dict[str, str],
                    teams: dict[Pair, Pair]) -> None:
    for cohort_field, team_field, public_cohort, public_team in (
        ("Semestre", "ID_Equipe", "cohort", "team_id"),
        ("removed_Semestre", "removed_ID_Equipe", "omitted_cohort", "omitted_team_id"),
    ):
        if cohort_field in row:
            cohort = row[cohort_field]
            require(cohort in cohorts, "Unregistered cohort")
            if public_cohort in projected:
                projected[public_cohort] = cohorts[cohort]
            if team_field in row:
                require((cohort, row[team_field]) in teams, "Unregistered cohort/team pair")
                if public_team in projected:
                    projected[public_cohort], projected[public_team] = teams[cohort, row[team_field]]
    if "most_influential_case" in projected:
        lookup = {team + " \u00b7 " + cohort: public for (cohort, team), public in teams.items()}
        combined = row["most_influential_team_semester"]
        require(combined in lookup, "Unregistered encoded influential case")
        cohort, team = lookup[combined]
        projected["most_influential_case"] = cohort + " / " + team


def project(spec: Table, rows: list[RawRow], cohorts: dict[str, str],
            teams: dict[Pair, Pair]) -> list[Row]:
    require(len({target for _, target in spec.fields}) == len(spec.fields), "Duplicate public column")
    required = {source for source, _ in spec.fields}
    require(all(required <= row.keys() for row in rows), "Missing projected source column")
    keyed(rows, ("Semestre", "ID_Equipe", "week_bin") if spec.dataset_id == "weekly-bin-definitions"
          else spec.keys)
    output: list[Row] = []
    for row in rows:
        projected = {target: scalar(row[source], target, spec.dataset_id) for source, target in spec.fields}
        map_identifiers(row, projected, cohorts, teams)
        output.append(projected)
    if spec.definition:
        unique: dict[tuple[Scalar, ...], Row] = {}
        for row in output:
            identity = tuple(row[RENAMES.get(k, k)] for k in spec.keys)
            require(identity not in unique or unique[identity] == row, "Conflicting deduplicated definition")
            unique[identity] = row
        output = list(unique.values())
    public_keys = tuple(RENAMES.get(k, k) for k in spec.keys)
    require(all(all(row[k] is not None and row[k] != "" for k in public_keys) for row in output),
            "Null public key")
    require(len({tuple(row[k] for k in public_keys) for row in output}) == len(output),
            "Duplicate public key after mapping")
    return sorted(output, key=lambda row: json.dumps([row[k] for k in public_keys], ensure_ascii=True))


def ratio_policy(row: Row, reference: RawRow) -> None:
    eligible = scalar(reference["baseline_eligible_for_rework_t3"], "baseline_eligible_for_rework_t3", "m8")
    total = scalar(reference["clean_total_churn_t3"], "clean_total_churn_t3", "m8")
    require(isinstance(total, int), "Invalid M8 total")
    status = "baseline_not_observed" if not eligible else ("zero_clean_churn" if total == 0 else "available")
    row["baseline_eligible_for_rework_t3"] = eligible
    row["ratio_status"] = status
    if status != "available":
        row["clean_rework_ratio_t3"] = None
    else:
        require(row.get("clean_rework_ratio_t3") is not None, "Eligible ratio must be observed")


def json_projections(data: dict[str, object], cohorts: dict[str, str],
                     teams: dict[Pair, Pair]) -> dict[str, list[Row]]:
    lexicon = obj(data["m5_lexicon.json"])
    patterns = obj(lexicon.get("patterns"))
    require(len(patterns) == 5, "Lexicon coverage differs")
    definitions: list[Row] = [
        {"lexicon_version": text(lexicon.get("version")), "subtype": subtype,
         "pattern": text(pattern), "language": text(lexicon.get("language")),
         "counting_rule": text(lexicon.get("counting_rule"))}
        for subtype, pattern in sorted(patterns.items())
    ]
    planning: list[Row] = []
    seen: set[Pair] = set()
    lists = ("goals", "architecture_or_design", "task_decomposition", "risk_or_dependency", "evidence_quotes")
    for item in array(data["m6b_llm_planning_content.json"]):
        item = obj(item)
        cohort, team = text(item.get("Semestre")), text(item.get("ID_Equipe"))
        require(cohort in cohorts and (cohort, team) in teams and (cohort, team) not in seen,
                "M6b missing/duplicate registry key")
        seen.add((cohort, team))
        public_cohort, public_team = teams[cohort, team]
        status = text(item.get("status"))
        row: Row = {"cohort": public_cohort, "team_id": public_team, "measurement_status": status}
        if status == "success":
            parsed = obj(item.get("parsed_response"))
            present = parsed.get("planning_evidence_present")
            require(isinstance(present, bool), "M6b planning presence must be boolean")
            row["planning_evidence_present"] = present
            for field in lists:
                row[field + "_n"] = len(array(parsed.get(field)))
        else:
            require(status == "unavailable_not_measured" and item.get("parsed_response") is None,
                    "Invalid M6b unavailability contract")
            row.update({field: None for field in ("planning_evidence_present", *(k + "_n" for k in lists))})
        planning.append(row)
    require(seen == teams.keys() and sum(r["measurement_status"] == "success" for r in planning) == 9,
            "M6b coverage differs from approved snapshot")
    return {"m5-lexicon": definitions,
            "m6b-planning-content": sorted(planning, key=lambda row: (text(row["cohort"]), text(row["team_id"])))}


def verify_relationships(data: dict[str, list[RawRow]], teams: dict[Pair, Pair]) -> None:
    team_keys = ("Semestre", "ID_Equipe")
    for spec in TABLES:
        rows = data[spec.source]
        if spec.keys[:2] == team_keys:
            require({(r["Semestre"], r["ID_Equipe"]) for r in rows} == teams.keys(),
                    f"Team coverage differs: {spec.dataset_id}")
        if not spec.definition:
            keyed(rows, spec.keys)
    for alias, source in ALIASES.items():
        spec = next(t for t in TABLES if t.source == source)
        fields = set(data[alias][0]) & set(data[source][0])
        agree(data[alias], data[source], spec.keys, fields)
    for target, source, fields in (
        ("rq3_architecture_rework_profile_data.csv", "m6a_structural_planning.csv",
         "pi_file_count_t1 pi_line_delta_t1 planning_artifact_present_t1 planning_scope_log1p_t1 measurement_status"),
        ("rq3_architecture_rework_profile_data.csv", "m8_rework_magnitude.csv",
         "clean_rework_churn_t3 baseline_eligible_for_rework_t3"),
        ("rq3_complexity_profile_data.csv", "m8_rework_magnitude.csv",
         "clean_rework_churn_t3 clean_rework_ratio_t3 baseline_eligible_for_rework_t3"),
        ("rq3_technical_complexity_vs_rework_data.csv", "rq3_complexity_profile_data.csv",
         "technical_complexity_mean_t3 clean_rework_churn_t3 clean_rework_ratio_t3 planning_scope_tier "
         "planning_scope_log1p_t1 score_trajectory_group final7_commit_share_pct final7_clean_churn_share_pct"),
        ("m8_baseline_eligibility.csv", "m8_rework_magnitude.csv",
         "prior_clean_path_n baseline_eligible_for_rework_t3 measurement_status"),
    ):
        agree(data[target], data[source], team_keys, set(fields.split()))
    base = [dict(row, planning_artifact_present_t1=row["planning_present_t1"])
            for row in data["rq2_score_trajectory_base_data.csv"]]
    for spec in TABLES:
        if spec.keys == team_keys:
            common = set(base[0]) & set(data[spec.source][0])
            agree(data[spec.source], base, team_keys, common)
    cases = data["rq3_influence_map_data.csv"]
    matrix = keyed(data["rq3_influence_heatmap_matrix.csv"], ("removed_team_semester",))
    expected_cases = {team + " \u00b7 " + cohort for cohort, team in teams}
    require({key[0] for key in matrix} == expected_cases, "Influence pivot case coverage differs")
    for row in cases:
        label = row["removed_ID_Equipe"] + " \u00b7 " + row["removed_Semestre"]
        require(equivalent(matrix[label,][row["relationship_label"]], row["rho_delta_from_full"]),
                "Influence pivot does not represent rho deltas")
    for row in data["rq3_influence_relationship_contract.csv"]:
        available = [r for r in cases if r["relationship_id"] == row["relationship_id"]
                     and r["availability_status"] == "available"]
        require(len(available) == int(row["available_leave_one_out_rows"]), "Influence denominator differs")
        if available:
            share = sum(r["full_sample_sign"] == r["loo_sign"] for r in available) / len(available)
            require(equivalent(str(share), row["sign_preservation_share"]), "Influence sign share differs")
    for row in data["m8_rework_magnitude.csv"]:
        require((row["baseline_eligible_for_rework_t3"] == "True") == (int(row["prior_clean_path_n"]) > 0),
                "M8 eligibility differs from observed baseline")
    for name, field in (("rq3_architecture_rework_profile_data.csv", "eligibility_label"),
                        ("rq3_technical_complexity_vs_rework_data.csv", "baseline_eligibility_label")):
        rework = keyed(data["m8_rework_magnitude.csv"], team_keys)
        for row in data[name]:
            eligible = rework[row["Semestre"], row["ID_Equipe"]]["baseline_eligible_for_rework_t3"] == "True"
            require(row[field] == ("Baseline eligible" if eligible else "Baseline not observed"),
                    "Ambiguous figure eligibility label")


def prepare(source_root: Path, approval_path: Path, registry_path: Path,
            excerpt_path: Path) -> tuple[dict[str, list[Row]], dict[str, list[Row]], dict[str, object]]:
    site = Path(__file__).resolve().parent.parent
    require(digest((site / "dataset-contracts.md").read_bytes()) == CONTRACT_SHA256,
            "Public contract changed; reconcile implementation and renew approval")
    source_root, approval_path, registry_path, excerpt_path = (
        resolved(p) for p in (source_root, approval_path, registry_path, excerpt_path))
    outside(source_root, site)
    cohorts, teams = approvals(approval_path, registry_path, excerpt_path, site)
    data, json_data, hashes = load_sources(source_root)
    verify_relationships(data, teams)
    datasets: dict[str, list[Row]] = {}
    definitions: dict[str, list[Row]] = {}
    rework = keyed(data["m8_rework_magnitude.csv"], ("Semestre", "ID_Equipe"))
    lineage_ratios: list[dict[str, object]] = []
    for spec in TABLES:
        rows = project(spec, data[spec.source], cohorts, teams)
        if any("clean_rework_ratio_t3" in row for row in rows):
            by_public = {teams[k]: r for k, r in rework.items()}
            source_ratios = {
                teams[k]: r["clean_rework_ratio_t3"]
                for k, r in keyed(data[spec.source], ("Semestre", "ID_Equipe")).items()
            }
            for row in rows:
                pair = (text(row["cohort"]), text(row["team_id"]))
                reference = by_public[pair]
                lineage_ratios.append({"dataset": spec.dataset_id, "cohort": row["cohort"],
                                       "team_id": row["team_id"], "source_ratio": source_ratios[pair],
                                       "canonical_source_ratio": reference["clean_rework_ratio_t3"]})
                ratio_policy(row, reference)
        (definitions if spec.definition else datasets)[spec.dataset_id] = rows
    datasets.update(json_projections(json_data, cohorts, teams))
    require(len(definitions["weekly-bin-definitions"]) == 13
            and len(definitions["complexity-definitions"]) == 13, "Definition coverage differs")
    lineage: dict[str, object] = {
        "contract_sha256": CONTRACT_SHA256, "index_sha256": INDEX_SHA256,
        "source_sha256": hashes, "canonical_ratios_before_masking": lineage_ratios,
    }
    return datasets, definitions, lineage


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, allow_nan=False, indent=2) + "\n").encode("utf-8")


def csv_bytes(rows: list[Row]) -> bytes:
    require(bool(rows), "Cannot serialize an empty required dataset")
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    columns = list(rows[0])
    writer.writerow(columns)
    for row in rows:
        require(list(row) == columns, "Inconsistent output schema")
        cells = []
        for value in row.values():
            if isinstance(value, str):
                require(not value.lstrip(" ").startswith(("\t", "\r", "\n"))
                        and not value.lstrip().startswith(("=", "+", "-", "@")),
                        "Spreadsheet-unsafe text requires reviewed export handling")
            cells.append("" if value is None else ("true" if value is True else "false" if value is False else value))
        writer.writerow(cells)
    return stream.getvalue().encode("utf-8")


def write_snapshot(output: Path, lineage_path: Path, datasets: dict[str, list[Row]],
                   definitions: dict[str, list[Row]], lineage: dict[str, object]) -> None:
    output, lineage_path = resolved(output), resolved(lineage_path)
    site = Path(__file__).resolve().parent.parent
    outside(lineage_path, site)
    outside(lineage_path, output)
    require(not output.exists() and not lineage_path.exists(), "Output/lineage must be new paths; overwrite refused")
    require(output.parent.is_dir() and lineage_path.parent.is_dir(), "Destination parent directories must exist")
    payloads: dict[str, bytes] = {}
    for dataset_id, rows in sorted(datasets.items()):
        require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", dataset_id) is not None, "Invalid dataset ID")
        payloads[f"datasets/{dataset_id}.json"] = json_bytes(rows)
        payloads[f"downloads/{dataset_id}.csv"] = csv_bytes(rows)
    for name, rows in sorted(definitions.items()):
        payloads[f"definitions/{name}.json"] = json_bytes(rows)
    # Serialize and validate every byte before creating any final output.
    private_bytes = json_bytes(lineage)
    with tempfile.TemporaryDirectory(prefix=".snapshot-", dir=output.parent) as temporary:
        staging = Path(temporary) / "data"
        staging.mkdir()
        for name, content in payloads.items():
            path = staging / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(content)
        with lineage_path.open("xb") as handle:
            os.chmod(lineage_path, 0o600)
            handle.write(private_bytes)
        try:
            os.rename(staging, output)
        except OSError:
            lineage_path.unlink()
            raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--approval", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--excerpt-decision", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="New public data directory (not the site root)")
    parser.add_argument("--private-lineage", type=Path, help="New private JSON outside the site/output")
    parser.add_argument("--check", action="store_true", help="Validate all inputs without writing")
    args = parser.parse_args(argv)
    if args.check:
        if args.output or args.private_lineage:
            parser.error("--check does not accept output paths")
    elif not args.output or not args.private_lineage:
        parser.error("--output and --private-lineage are required unless --check is used")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        if args.output:
            output = resolved(args.output)
            for path in (args.source_root, args.approval, args.registry, args.excerpt_decision):
                outside(resolved(path), output)
        datasets, definitions, lineage = prepare(args.source_root, args.approval, args.registry, args.excerpt_decision)
        # Check mode also exercises serialization, including spreadsheet safety.
        for rows in datasets.values():
            json_bytes(rows)
            csv_bytes(rows)
        if not args.check:
            write_snapshot(args.output, args.private_lineage, datasets, definitions, lineage)
        logging.info("Validated %d datasets, %d definition sets, 58 sources; excerpts omitted.",
                     len(datasets), len(definitions))
    except (ContractError, OSError, ValueError, KeyError, TypeError) as exc:
        logging.error("Snapshot preparation failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
