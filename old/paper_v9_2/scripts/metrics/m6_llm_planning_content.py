"""Generate gated M6b structured planning-content evidence from T1 subjects."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from llm_gateway import LLMCallGateway
from paper_v9.scripts.common.paths import resolve_metrics_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "m6b-structured-planning-v1.1"
MODEL = "gpt-4o-mini"
TEMPERATURE = 0.0
TEAM_KEY = ["ID_Equipe", "Semestre"]
REQUIRED_RESPONSE_FIELDS = {
    "planning_evidence_present", "goals", "architecture_or_design", "task_decomposition",
    "risk_or_dependency", "evidence_quotes", "insufficient_evidence",
}
ALLOWED_CATEGORIES = {"goals", "architecture_or_design", "task_decomposition", "risk_or_dependency"}


def _atomic_json(payload: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.partial")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True, default=str), encoding="utf-8")
    os.replace(temporary, path)


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _subject_rows(root: Path) -> dict[tuple[str, str], list[dict[str, str]]]:
    commits = pd.read_parquet(root / "data" / "lake" / "git_commits.parquet")
    required = {"ID_Equipe", "Semestre", "temporal_marker", "repository", "commit_hash"}
    missing = required.difference(commits.columns)
    if missing:
        raise ValueError(f"M6b commit contract is missing columns: {sorted(missing)}")
    t1 = commits.loc[commits["temporal_marker"].eq("T1")].copy()
    result: dict[tuple[str, str], list[dict[str, str]]] = {}
    for key, group in t1.groupby(TEAM_KEY, sort=False):
        repository = str(group["repository"].iloc[0])
        mirrors = sorted((root / "data" / "raw" / "repos_parent_cache").glob(f"{repository}*.git"))
        if len(mirrors) != 1:
            raise FileNotFoundError(f"Expected one parent mirror for {repository}, found {len(mirrors)}")
        rows: list[dict[str, str]] = []
        for commit in group.sort_values("timestamp").itertuples(index=False):
            completed = subprocess.run(
                ["git", f"--git-dir={mirrors[0]}", "show", "-s", "--format=%cI%x09%s", str(commit.commit_hash)],
                check=True, capture_output=True, text=True,
            ).stdout.rstrip("\n")
            timestamp, subject = completed.split("\t", 1)
            rows.append({"commit_hash": str(commit.commit_hash), "timestamp": timestamp, "subject": subject})
        result[(str(key[0]), str(key[1]))] = rows
    return result


def _prompt(team: str, semester: str, subjects: list[dict[str, str]]) -> str:
    payload = json.dumps(subjects, ensure_ascii=False, separators=(",", ":"))
    return f"""You are extracting structured planning evidence from software-project commit subjects.

Judge only the supplied T1 commit subjects. Do not infer intent, quality, architecture,
effort, success, or missing information. Do not assign a numeric quality score.
Use only literal evidence from the input. Every non-empty category must include one or
more exact evidence_quotes copied from the supplied subjects. If the text does not
support a category, return an empty list and explain the absence in insufficient_evidence.

Return only valid JSON matching this schema:
{{
  "planning_evidence_present": boolean,
  "goals": [{{"text": string, "evidence_quote_ids": [string]}}],
  "architecture_or_design": [{{"text": string, "evidence_quote_ids": [string]}}],
  "task_decomposition": [{{"text": string, "evidence_quote_ids": [string]}}],
  "risk_or_dependency": [{{"text": string, "evidence_quote_ids": [string]}}],
  "evidence_quotes": [{{"quote_id": string, "quote": string, "category": string, "commit_hash": string}}],
  "insufficient_evidence": [{{"category": string, "reason": string}}]
}}

The allowed categories are: goals, architecture_or_design, task_decomposition,
risk_or_dependency. A quote must be copied exactly from one supplied subject.
For each evidence quote, copy commit_hash exactly from the object whose subject
contains the quote; never invent, hash, truncate, or reuse a quote as a hash.

Team-semester: {team}|{semester}
T1 commit subjects, in timestamp order:
{payload}"""


def _validate_response(raw: str, subjects: list[dict[str, str]]) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("M6b response is not valid JSON") from error
    if not isinstance(parsed, dict) or set(parsed) != REQUIRED_RESPONSE_FIELDS:
        raise ValueError("M6b response has an invalid top-level schema")
    if not isinstance(parsed["planning_evidence_present"], bool):
        raise ValueError("M6b planning_evidence_present must be boolean")
    for field in REQUIRED_RESPONSE_FIELDS - {"planning_evidence_present"}:
        if not isinstance(parsed[field], list):
            raise ValueError(f"M6b response field {field} must be a list")
    subject_by_hash = {item["commit_hash"]: item["subject"] for item in subjects}
    quote_ids: set[str] = set()
    for quote in parsed["evidence_quotes"]:
        if set(quote) != {"quote_id", "quote", "category", "commit_hash"}:
            raise ValueError("M6b evidence quote has an invalid schema")
        if quote["quote_id"] in quote_ids or not isinstance(quote["quote_id"], str):
            raise ValueError("M6b evidence quote IDs must be unique")
        quote_ids.add(quote["quote_id"])
        if quote["category"] not in ALLOWED_CATEGORIES or quote["commit_hash"] not in subject_by_hash:
            raise ValueError("M6b evidence quote references an invalid category or commit")
        if quote["quote"] not in subject_by_hash[quote["commit_hash"]]:
            raise ValueError("M6b evidence quote is not an exact input substring")
    for field in ALLOWED_CATEGORIES:
        for item in parsed[field]:
            if set(item) != {"text", "evidence_quote_ids"} or not isinstance(item["evidence_quote_ids"], list):
                raise ValueError(f"M6b category {field} has an invalid item")
            if not set(item["evidence_quote_ids"]).issubset(quote_ids):
                raise ValueError(f"M6b category {field} references an unknown quote")
    for item in parsed["insufficient_evidence"]:
        if set(item) != {"category", "reason"} or not item["reason"]:
            raise ValueError("M6b insufficient_evidence entries require category and reason")
    return parsed


def generate(force: bool = False, verbose: bool = False) -> dict[str, Any]:
    root = resolve_paper_v9_dir().parent
    metrics = resolve_metrics_dir()
    source_path = root / "data" / "lake" / "git_commits.parquet"
    planning_path = root / "data" / "analysis" / "planning_metrics.parquet"
    output_path = metrics / "m6b_llm_planning_content.json"
    metadata_path = metrics / "m6_llm_planning_content.metadata.json"
    cache_path = root / "paper_v9" / "data" / "llm" / "m6b_cache.json"
    input_hash = hashlib.sha256((compute_sha256(source_path) + compute_sha256(planning_path)).encode()).hexdigest()
    config = {"contract_version": CONTRACT_VERSION, "model": MODEL, "temperature": TEMPERATURE, "prompt_version": "m6b-structured-planning-v1.1"}
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    if not force and output_path.is_file() and metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("input_sha256") == input_hash and metadata.get("config_sha256") == config_hash:
            return {"status": "resumed", "artifacts": [str(output_path), str(metadata_path)]}

    planning = pd.read_parquet(planning_path)[TEAM_KEY].drop_duplicates().sort_values(TEAM_KEY)
    subjects_by_key = _subject_rows(root)
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.is_file() else {}
    records: list[dict[str, Any]] = []
    client_gateway: LLMCallGateway | None = None
    _load_dotenv(root / ".env")
    for key in planning.itertuples(index=False, name=None):
        team, semester = str(key[0]), str(key[1])
        subjects = subjects_by_key.get((team, semester), [])
        cache_key = f"m6b:{team}:{semester}:{input_hash}:{config_hash}"
        if not subjects:
            records.append({"ID_Equipe": team, "Semestre": semester, "status": "unavailable_not_measured", "insufficient_evidence": [{"category": "all", "reason": "no_t1_commit_subjects"}], "input_subjects": []})
            continue
        if cache_key in cache:
            cached = cache[cache_key]
            parsed = _validate_response(cached["raw_response"], subjects)
            records.append({**cached, "parsed_response": parsed})
            continue
        if client_gateway is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY is missing; M6b cannot execute")
            from openai import OpenAI
            client_gateway = LLMCallGateway(OpenAI(api_key=api_key))
        user_prompt = _prompt(team, semester, subjects)
        raw_response = client_gateway.chat_json(
            observation_id=cache_key,
            model=MODEL,
            system_prompt="You are a careful, evidence-constrained research data extractor.",
            user_prompt=user_prompt,
            request_options={"temperature": TEMPERATURE, "response_format": {"type": "json_object"}},
        )
        parsed = _validate_response(raw_response, subjects)
        record = {"ID_Equipe": team, "Semestre": semester, "status": "success", "input_subjects": subjects, "prompt_sha256": hashlib.sha256(user_prompt.encode()).hexdigest(), "raw_response": raw_response, "parsed_response": parsed, "model": MODEL, "temperature": TEMPERATURE, "completed_at": datetime.now(timezone.utc).isoformat()}
        cache[cache_key] = record
        _atomic_json(cache, cache_path)
        records.append(record)

    metadata = {"status": "success", "gate_status": "approved_human_review", "contract_version": CONTRACT_VERSION, "metric_definition_version": CONTRACT_VERSION, "input_sha256": input_hash, "config_sha256": config_hash, "rq": "RQ3", "unit_of_analysis": "team_semester", "model": MODEL, "temperature": TEMPERATURE, "llm_calls_required": True, "coverage": {"team_semester_n": len(records), "success_n": sum(r["status"] == "success" for r in records), "unavailable_not_measured_n": sum(r["status"] == "unavailable_not_measured" for r in records)}, "limitations": ["LLM extraction is exploratory and was approved after human review", "literal quote validation does not establish semantic correctness", "M6b structured fields feed M9 separately; no composite score is produced"], "artifacts": [output_path.name, metadata_path.name]}
    ledger_path = root / "data" / "analysis" / ".private" / "llm_call_ledger.parquet"
    if ledger_path.is_file():
        ledger = pd.read_parquet(ledger_path)
        calls = ledger.loc[ledger["observation_id"].astype(str).str.startswith("m6b:")]
        metadata["ledger"] = {
            "path": "data/analysis/.private/llm_call_ledger.parquet",
            "attempt_n": int(len(calls)),
            "success_n": int(calls["status"].eq("success").sum()),
            "total_tokens": int(calls["total_tokens"].fillna(0).sum()),
            "estimated_cost_usd": float(calls["estimated_cost_usd"].fillna(0).sum()),
        }
    _atomic_json(records, output_path)
    _atomic_json(metadata, metadata_path)
    if verbose:
        print(json.dumps(metadata, indent=2, sort_keys=True))
    return {"status": "generated", "artifacts": [str(output_path), str(metadata_path)]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate gated v9 M6b structured planning content")
    parser.add_argument("--force", action="store_true", help="Regenerate existing M6b outputs")
    parser.add_argument("--verbose", action="store_true", help="Print generated metadata")
    args = parser.parse_args()
    print(json.dumps(generate(force=args.force, verbose=args.verbose), indent=2))


if __name__ == "__main__":
    main()