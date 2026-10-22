"""Build deterministic release metadata from public catalog and dataset files only."""

from __future__ import annotations

import argparse
import logging
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True

from build_catalog import build_catalog, validate_catalog
from snapshot_io import (
    ContractError, Row, array, csv_bytes, digest, json_bytes, obj, read_json,
    require, resolved, text,
)


def public_rows(path: Path, descriptor: dict[str, object]) -> list[Row]:
    columns = [obj(column) for column in array(descriptor["columns"])]
    names = [text(column["id"]) for column in columns]
    keys = [text(key) for key in array(descriptor["key"])]
    rows: list[Row] = []
    identities = set()
    for value in array(read_json(path)):
        raw = obj(value)
        require(list(raw) == names, f"Dataset columns differ: {descriptor['id']}")
        row: Row = {}
        for column in columns:
            name = text(column["id"])
            cell = raw[name]
            if cell is None:
                require(column["nullable"] is True, f"Unexpected null: {descriptor['id']}/{name}")
            elif isinstance(cell, bool):
                require(column["type"] == "boolean", f"Invalid type: {descriptor['id']}/{name}")
            elif isinstance(cell, int):
                require(column["type"] in ("integer", "number"), f"Invalid type: {descriptor['id']}/{name}")
            elif isinstance(cell, float):
                require(column["type"] == "number" and math.isfinite(cell),
                        f"Invalid type: {descriptor['id']}/{name}")
            elif isinstance(cell, str):
                require(column["type"] == "string", f"Invalid type: {descriptor['id']}/{name}")
            else:
                raise ContractError(f"Invalid scalar type: {descriptor['id']}/{name}")
            row[name] = cell
        identity = tuple(row[key] for key in keys)
        require(all(v is not None and v != "" for v in identity) and identity not in identities,
                f"Invalid or duplicate key: {descriptor['id']}")
        identities.add(identity)
        rows.append(row)
    require(bool(rows), f"Empty required dataset: {descriptor['id']}")
    return rows


def coverage(rows: list[Row], descriptor: dict[str, object]) -> dict[str, object]:
    result: dict[str, object] = {"declared": obj(descriptor["coverage"])}
    for field, label in (("cohort", "observed_cohorts"), ("checkpoint", "observed_checkpoints")):
        if field in rows[0]:
            result[label] = sorted({text(row[field]) for row in rows})
    if "team_id" in array(descriptor["key"]):
        pairs = {(text(row["cohort"]), text(row["team_id"])) for row in rows}
        result["team_semesters_by_cohort"] = {
            cohort: sum(pair[0] == cohort for pair in pairs)
            for cohort in sorted({pair[0] for pair in pairs})
        }
    for field in ("measurement_status", "ratio_status"):
        if field in rows[0]:
            values = [text(row[field]) for row in rows]
            result[field + "_counts"] = {value: values.count(value) for value in sorted(set(values))}
    if "baseline_eligible_for_rework_t3" in rows[0]:
        result["baseline_eligible"] = sum(row["baseline_eligible_for_rework_t3"] is True for row in rows)
        result["baseline_ineligible"] = sum(row["baseline_eligible_for_rework_t3"] is False for row in rows)
    if descriptor["id"] == "m5-corpus-coverage":
        result["chunks_by_checkpoint"] = {text(row["checkpoint"]): row["transcript_chunk_n"] for row in rows}
    return result


def build_release(site_root: Path) -> dict[str, object]:
    site = resolved(site_root)
    catalog_path = resolved(site / "data/catalog.json")
    catalog = obj(read_json(catalog_path))
    validate_catalog(catalog)
    require(catalog == build_catalog(), "Catalog differs from reviewed public metadata")
    descriptors = [obj(value) for value in array(catalog["datasets"])]
    expected = {"data/catalog.json"}
    for descriptor in descriptors:
        expected.update(text(path) for path in obj(descriptor["paths"]).values())
    actual = set()
    for path in (site / "data").rglob("*"):
        require(not path.is_symlink(), "Symlink artifacts are not accepted")
        if path.is_file():
            actual.add(path.relative_to(site).as_posix())
        else:
            require(path.is_dir() and path.relative_to(site).as_posix() in
                    ("data/datasets", "data/downloads"),
                    "Unexpected public data inventory entry")
    require(actual - {"data/release.json"} == expected, "Public data inventory differs from catalog")
    datasets = []
    artifact_rows = {}
    scalar_count = 0
    for descriptor in sorted(descriptors, key=lambda d: text(d["id"])):
        paths = obj(descriptor["paths"])
        json_path, csv_path = (site / text(paths[k]) for k in ("json", "csv"))
        rows = public_rows(json_path, descriptor)
        require(json_path.read_bytes() == json_bytes(rows), f"Noncanonical JSON: {descriptor['id']}")
        require(csv_path.read_bytes() == csv_bytes(rows), f"CSV differs from JSON: {descriptor['id']}")
        datasets.append({
            "id": descriptor["id"], "row_count": len(rows),
            "column_count": len(rows[0]), "coverage": coverage(rows, descriptor),
        })
        for path in paths.values():
            artifact_rows[text(path)] = len(rows)
        scalar_count += sum(len(row) for row in rows)
    artifacts = []
    for name in sorted(expected):
        content = (site / name).read_bytes()
        artifact: dict[str, object] = {"path": name, "sha256": digest(content), "bytes": len(content)}
        if name in artifact_rows:
            artifact["row_count"] = artifact_rows[name]
        artifacts.append(artifact)
    return {
        "schema_version": "1.0", "snapshot_id": "research-data-001",
        "status": "snapshot_prepared_release_pending", "path_base": "site_root",
        "hash_algorithm": "sha256",
        "artifact_scope": "Public catalog and all observation JSON/CSV files only. Excludes this manifest "
                          "(no self-hash), documentation, tools, and application assets; not a whole-site approval.",
        "coverage_note": "Counts describe exported rows, not independent participants or pooled sample sizes. "
                         "Dataset grains, original denominators, and declared coverage remain in the catalog. "
                         "Observed cohort/checkpoint lists are included only when present in the rows; "
                         "global transcript measurements are not attributed to teams or unmeasured cohorts.",
        "summary": {
            "dataset_count": len(datasets), "artifact_count": len(artifacts),
            "observation_row_count": sum(artifact_rows[text(obj(d["paths"])["json"])] for d in descriptors),
            "scalar_cell_count": scalar_count,
        },
        "artifacts": artifacts, "datasets": datasets,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="Check existing manifest bytes without writing")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        content = json_bytes(build_release(args.site_root))
        output = resolved(args.output)
        if args.check:
            require(output.read_bytes() == content, "Saved release metadata differs; investigate before regenerating")
        else:
            require(not output.exists(), "Refusing to overwrite existing release metadata")
            require(output.parent.is_dir(), "Release metadata parent directory must exist")
            with output.open("xb") as handle:
                handle.write(content)
        logging.info("Validated public data manifest: 49 datasets, 99 artifact hashes; publication remains pending.")
    except (ContractError, OSError, ValueError, KeyError, TypeError) as exc:
        logging.error("Release metadata preparation failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
