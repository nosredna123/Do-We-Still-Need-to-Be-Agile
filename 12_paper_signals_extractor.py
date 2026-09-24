from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from pipeline_config import is_measurement_code_path

PROJECT_ROOT = Path(__file__).resolve().parent
PROMPT_DIR = PROJECT_ROOT / "paper_v4" / "advanced_metrics"
if str(PROMPT_DIR) not in sys.path:
    sys.path.insert(0, str(PROMPT_DIR))
from llm_prompts import get_prompt


ADVANCED_METRICS_DIR = PROJECT_ROOT / "paper_v4" / "advanced_metrics"
LOGS_DIR = ADVANCED_METRICS_DIR / "logs"
CACHE_DIR = ADVANCED_METRICS_DIR / "llm_cache"
OUTPUTS_DIR = ADVANCED_METRICS_DIR / "outputs"
CACHE_PATH = CACHE_DIR / "llm_results_cache.json"
HISTORY_PATH = CACHE_DIR / "llm_call_history.csv"


def configure_logging() -> logging.Logger:
    """Configure a console and file logger for the extractor."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("paper_signals_extractor")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    file_handler = logging.FileHandler(LOGS_DIR / f"{timestamp}_12_paper_signals_extractor.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = configure_logging()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_cache(path: Path) -> dict[str, Any]:
    """Load the JSON cache dictionary, creating it if missing."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
        raise ValueError("Cache root must be a JSON object")
    except json.JSONDecodeError:
        logger.warning("Cache file %s is invalid JSON; recreating empty cache.", path)
        return {}


def save_cache(path: Path, cache: dict[str, Any]) -> None:
    """Persist the cache atomically."""
    ensure_dir(path.parent)
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    temp_path.replace(path)


def append_history_row(history_path: Path, record: dict[str, Any]) -> None:
    """Append a new row to the CSV call ledger."""
    ensure_dir(history_path.parent)
    if history_path.exists():
        dataframe = pd.read_csv(history_path)
        dataframe = pd.concat([dataframe, pd.DataFrame([record])], ignore_index=True)
        dataframe.to_csv(history_path, index=False)
        return

    pd.DataFrame([record]).to_csv(history_path, index=False)


def parse_llm_score(raw_response: str, expected_key: str) -> int:
    """Parse an integer score from a raw LLM JSON response."""
    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM response is not valid JSON: {raw_response!r}") from exc

    if not isinstance(result, dict):
        raise ValueError(f"LLM response is not a JSON object: {raw_response!r}")
    if expected_key not in result:
        raise ValueError(f"Expected key {expected_key!r} in response: {result!r}")

    value = result[expected_key]
    if isinstance(value, bool):
        raise ValueError(f"Expected numeric score for {expected_key!r}, got boolean: {value!r}")
    if not isinstance(value, (int, float)):
        raise ValueError(f"Expected numeric score for {expected_key!r}, got {type(value).__name__}: {value!r}")
    return int(value)


def load_dotenv_file(dotenv_path: Path) -> None:
    """Inject key/value pairs from a .env file into os.environ without overriding existing values."""
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def call_llm_task(
    *,
    task_type: str,
    payload_text: str,
    team_id: str | None,
    semester: str | None,
    cache: dict[str, Any],
    history_path: Path,
    cache_key: str | None = None,
    skip_llm: bool = False,
) -> dict[str, Any]:
    """Invoke the LLM using the project gateway, reusing cache when available."""
    if cache_key is None:
        cache_key = f"{semester}_{team_id}_{task_type}" if semester and team_id else f"{task_type}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    if cache_key in cache:
        logger.info("Using cached LLM result for key=%s", cache_key)
        return dict(cache[cache_key])

    if skip_llm:
        raise RuntimeError(f"LLM execution skipped for {cache_key!r}")

    prompt_text = get_prompt(task_type)
    raw_prompt = f"{prompt_text}\n\nContext:\n{payload_text[:12000]}"

    load_dotenv_file(PROJECT_ROOT / ".env")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Configure it in the project root .env file before running the extractor.")

    try:
        from llm_gateway import LLMCallGateway  # type: ignore
        from openai import OpenAI  # type: ignore
    except ImportError as exc:  # pragma: no cover - runtime guard
        raise RuntimeError("llm_gateway or openai module is unavailable; ensure the project dependencies are installed.") from exc

    client = OpenAI(api_key=api_key)
    gateway = LLMCallGateway(client)
    raw_response = gateway.chat_json(
        observation_id=cache_key,
        model="gpt-4o-mini",
        system_prompt="You are a careful evaluator.",
        user_prompt=raw_prompt,
        request_options={"temperature": 0.0},
    )

    expected_key = "t1_planning_score" if "planning" in task_type.lower() else "coordination_friction"
    parsed_score = parse_llm_score(raw_response, expected_key)
    result = {expected_key: parsed_score}
    cache[cache_key] = result
    save_cache(CACHE_PATH, cache)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_type": task_type,
        "ID_Equipe": team_id,
        "Semestre": semester,
        "prompt_key": cache_key,
        "prompt_text": raw_prompt,
        "raw_response": raw_response,
        "parsed_score": parsed_score,
        "status": "success",
        "notes": "",
    }
    append_history_row(history_path, record)
    return result


def call_cohort_llm_task(
    *,
    task_type: str,
    payload_text: str,
    semester: str | None,
    cache: dict[str, Any],
    history_path: Path,
    cache_key: str | None = None,
    skip_llm: bool = False,
) -> dict[str, Any]:
    """Task wrapper for cohort-level coordination friction scoring."""
    if cache_key is None:
        cache_key = f"{semester or 'all'}_cohort_{task_type}"
    return call_llm_task(
        task_type=task_type,
        payload_text=payload_text,
        team_id=None,
        semester=semester,
        cache=cache,
        history_path=history_path,
        cache_key=cache_key,
        skip_llm=skip_llm,
    )


def _is_boilerplate_path(file_path: str) -> bool:
    """Return True when a path is outside the shared code-measurement policy."""
    return not is_measurement_code_path(file_path)


def _team_semester_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row["ID_Equipe"]), str(row["Semestre"])


def _team_label_from_repo_name(repo_name: str) -> str | None:
    match = re.search(r"team[_-]?0*(\d+)", repo_name, flags=re.IGNORECASE)
    if match:
        return f"TEAM_{int(match.group(1)):02d}"
    return None


def load_commit_messages_from_repos(git_commits: pd.DataFrame, repos_root: Path) -> dict[str, str]:
    """Resolve T1 commit subjects from the persisted raw Git histories by hash."""
    required = {"repository", "commit_hash", "temporal_marker"}
    missing = sorted(required.difference(git_commits.columns))
    if missing:
        raise ValueError(f"git_commits missing fields needed to recover commit messages: {missing}")
    if not repos_root.exists():
        raise FileNotFoundError(f"Raw repository cache not found: {repos_root}")

    t1_commits = git_commits.loc[git_commits["temporal_marker"].eq("T1")].copy()
    messages_by_hash: dict[str, str] = {}
    for repository, rows in t1_commits.groupby("repository", dropna=False):
        repo_dir = repos_root / str(repository)
        if not (repo_dir / ".git").exists():
            raise FileNotFoundError(f"Git history not found for repository {repository!r}: {repo_dir}")

        commit_hashes = rows["commit_hash"].dropna().astype(str).drop_duplicates().tolist()
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_dir), "log", "--no-walk", "--format=%H%x09%s", *commit_hashes],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise RuntimeError(f"Could not recover T1 commit subjects from {repo_dir}") from exc

        for line in result.stdout.splitlines():
            commit_hash, separator, subject = line.partition("\t")
            if separator and subject.strip():
                messages_by_hash[commit_hash] = subject.strip()

        unresolved = sorted(set(commit_hashes).difference(messages_by_hash))
        if unresolved:
            raise RuntimeError(f"Could not resolve {len(unresolved)} T1 commit subjects in {repository!r}")

    return messages_by_hash


def get_commit_text_by_team_semester(git_commits: pd.DataFrame, repos_root: Path) -> dict[tuple[str, str], str]:
    """Create the text payload for each team-semester planning prompt."""
    commit_text: dict[tuple[str, str], str] = {}

    if "message" in git_commits.columns:
        grouped = git_commits.loc[git_commits["temporal_marker"].eq("T1")].groupby(["ID_Equipe", "Semestre"], dropna=False)["message"]
        for (team_id, semester), series in grouped:
            text = "\n".join(str(value).strip() for value in series if str(value).strip())
            if text:
                commit_text[(str(team_id), str(semester))] = text
        return commit_text

    messages_by_hash = load_commit_messages_from_repos(git_commits, repos_root)
    t1_commits = git_commits.loc[git_commits["temporal_marker"].eq("T1")].sort_values("timestamp")
    grouped = t1_commits.groupby(["ID_Equipe", "Semestre"], dropna=False)
    for (team_id, semester), rows in grouped:
        text = "\n".join(messages_by_hash[str(commit_hash)] for commit_hash in rows["commit_hash"])
        if not text:
            raise RuntimeError(f"No T1 commit subjects found for {team_id!r}, {semester!r}")
        commit_text[(str(team_id), str(semester))] = text
    return commit_text


def build_rework_dataset(git_files: pd.DataFrame, git_commits: pd.DataFrame) -> pd.DataFrame:
    """Compute T3 rework and deferred churn by team-semester."""
    required = {"ID_Equipe", "Semestre", "temporal_marker", "file_path", "lines_added", "lines_deleted"}
    missing = sorted(required.difference(git_files.columns))
    if missing:
        raise ValueError(f"git_files missing required columns: {missing}")

    if "commit_hash" not in git_files.columns:
        raise ValueError("git_files table must contain commit_hash for provenance mapping")

    ordered_markers = {"T1": 1, "T2": 2, "T3": 3}
    git_files = git_files.copy()
    git_files["marker_rank"] = git_files["temporal_marker"].map(ordered_markers)
    earliest = (
        git_files.loc[~git_files["file_path"].apply(_is_boilerplate_path)]
        .groupby(["ID_Equipe", "Semestre", "file_path"], dropna=False)["marker_rank"]
        .min()
        .reset_index()
        .rename(columns={"marker_rank": "earliest_marker_rank"})
    )

    with_origin = git_files.merge(earliest, on=["ID_Equipe", "Semestre", "file_path"], how="left")
    t3_rows = with_origin.loc[
        with_origin["temporal_marker"].eq("T3") & ~with_origin["file_path"].apply(_is_boilerplate_path)
    ].copy()
    t3_rows["origin_type"] = t3_rows["earliest_marker_rank"].map(lambda rank: "rework" if rank in {1, 2} else "deferred")

    totals = (
        t3_rows.assign(churn=t3_rows["lines_added"].fillna(0) + t3_rows["lines_deleted"].fillna(0))
        .groupby(["ID_Equipe", "Semestre", "origin_type"], dropna=False)["churn"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )

    totals = totals.rename(columns={"rework": "rework_churn_t3", "deferred": "deferred_churn_t3"})
    rework = totals[["ID_Equipe", "Semestre", "rework_churn_t3", "deferred_churn_t3"]]
    return rework.fillna(0)


def build_team_level_dataset(
    *,
    git_files: pd.DataFrame,
    git_commits: pd.DataFrame,
    evaluator_team_cuts: pd.DataFrame,
    transcript_sessions: pd.DataFrame,
    output_dir: str | Path,
    llm_cache_path: str | Path = CACHE_PATH,
    llm_history_path: str | Path = HISTORY_PATH,
    skip_llm: bool = False,
) -> pd.DataFrame:
    """Build the final team-semester dataset for the paper signals extractor."""
    output_dir = Path(output_dir)
    ensure_dir(output_dir)
    llm_cache_path = Path(llm_cache_path)
    llm_history_path = Path(llm_history_path)
    cache = load_cache(llm_cache_path)

    churn = build_rework_dataset(git_files, git_commits)

    evaluator = evaluator_team_cuts.copy()
    required_eval = {"ID_Equipe", "Semestre", "scope_applicability_mean", "technical_complexity_mean"}
    missing_eval = sorted(required_eval.difference(evaluator.columns))
    if missing_eval:
        raise ValueError(f"evaluator_team_cuts missing required columns: {missing_eval}")

    evaluator_agg = (
        evaluator.groupby(["ID_Equipe", "Semestre"], dropna=False)[["scope_applicability_mean", "technical_complexity_mean"]]
        .mean()
        .reset_index()
    )

    planning_rows: list[dict[str, Any]] = []
    repo_root = PROJECT_ROOT / "data" / "raw" / "repos_cache"
    commit_texts = get_commit_text_by_team_semester(git_commits, repo_root)

    for (team_id, semester), text in commit_texts.items():
        cache_key = f"{semester}_{team_id}_Planning"
        result = call_llm_task(
            task_type="planning",
            payload_text=text,
            team_id=str(team_id),
            semester=str(semester),
            cache=cache,
            history_path=llm_history_path,
            cache_key=cache_key,
            skip_llm=skip_llm,
        )
        planning_rows.append({"ID_Equipe": str(team_id), "Semestre": str(semester), "t1_planning_score": result.get("t1_planning_score")})

    planning_df = pd.DataFrame(planning_rows)
    if not planning_df.empty:
        planning_df = planning_df[["ID_Equipe", "Semestre", "t1_planning_score"]]

    merged = churn.merge(evaluator_agg, on=["ID_Equipe", "Semestre"], how="outer")
    if not planning_df.empty:
        merged = merged.merge(planning_df, on=["ID_Equipe", "Semestre"], how="outer")

    ordered = [
        "ID_Equipe",
        "Semestre",
        "rework_churn_t3",
        "deferred_churn_t3",
        "t1_planning_score",
        "scope_applicability_mean",
        "technical_complexity_mean",
    ]
    final = merged.reindex(columns=[col for col in ordered if col in merged.columns])
    save_cache(llm_cache_path, cache)
    team_signals_path = output_dir / "team_level_signals.csv"
    final.to_csv(team_signals_path, index=False)
    logger.info("Saved team-level signals to %s with %d rows", team_signals_path, len(final))
    return final


def build_cohort_friction_dataset(
    *,
    transcript_sessions: pd.DataFrame,
    output_dir: str | Path,
    llm_cache_path: str | Path = CACHE_PATH,
    llm_history_path: str | Path = HISTORY_PATH,
    skip_llm: bool = False,
) -> pd.DataFrame:
    """Compute the descriptive cohort-level coordination friction by temporal marker."""
    transcript_sessions = transcript_sessions.copy()
    required = {"Semestre", "temporal_marker", "transcript_text"}
    missing = sorted(required.difference(transcript_sessions.columns))
    if missing:
        raise ValueError(f"transcript_sessions missing required columns: {missing}")

    output_dir = Path(output_dir)
    ensure_dir(output_dir)
    llm_cache_path = Path(llm_cache_path)
    llm_history_path = Path(llm_history_path)
    cache = load_cache(llm_cache_path)

    groups: list[dict[str, Any]] = []
    for marker in ["T1", "T2", "T3"]:
        text = "\n".join(
            str(value).strip()
            for value in transcript_sessions.loc[transcript_sessions["temporal_marker"].eq(marker), "transcript_text"].dropna()
            if str(value).strip()
        )
        if not text:
            logger.warning("No transcript text available for temporal marker %s; storing NaN score.", marker)
            groups.append({"Semestre": "all", "temporal_marker": marker, "coordination_friction": None})
            continue
        cache_key = f"all_cohort_{marker}_CoordinationFriction"
        result = call_cohort_llm_task(
            task_type="cohort_coordination_friction",
            payload_text=text,
            semester="all",
            cache=cache,
            history_path=llm_history_path,
            cache_key=cache_key,
            skip_llm=skip_llm,
        )
        groups.append({"Semestre": "all", "temporal_marker": marker, "coordination_friction": result.get("coordination_friction")})

    cohort_df = pd.DataFrame(groups)
    save_cache(llm_cache_path, cache)
    cohort_path = output_dir / "cohort_temporal_friction.csv"
    cohort_df.to_csv(cohort_path, index=False)
    logger.info("Saved cohort friction output to %s with %d rows", cohort_path, len(cohort_df))
    return cohort_df


def run_pipeline() -> None:
    """Execute the full paper signal extraction pipeline."""
    ensure_dir(CACHE_DIR)
    ensure_dir(OUTPUTS_DIR)

    logger.info("Step 1: Loading lake inputs")
    git_files = pd.read_parquet(PROJECT_ROOT / "data" / "lake" / "git_files.parquet")
    git_commits = pd.read_parquet(PROJECT_ROOT / "data" / "lake" / "git_commits.parquet")
    evaluator_team_cuts = pd.read_parquet(PROJECT_ROOT / "data" / "lake" / "evaluator_team_cuts.parquet")
    transcript_sessions = pd.read_parquet(PROJECT_ROOT / "data" / "lake" / "transcript_sessions.parquet")

    logger.info("Step 2: Building team-level signals")
    team_signals = build_team_level_dataset(
        git_files=git_files,
        git_commits=git_commits,
        evaluator_team_cuts=evaluator_team_cuts,
        transcript_sessions=transcript_sessions,
        output_dir=OUTPUTS_DIR,
        llm_cache_path=CACHE_PATH,
        llm_history_path=HISTORY_PATH,
        skip_llm=False,
    )

    logger.info("Step 3: Building cohort-level friction artifact")
    build_cohort_friction_dataset(
        transcript_sessions=transcript_sessions,
        output_dir=OUTPUTS_DIR,
        llm_cache_path=CACHE_PATH,
        llm_history_path=HISTORY_PATH,
        skip_llm=False,
    )

    logger.info("Pipeline complete. Team-level rows: %d", len(team_signals))


if __name__ == "__main__":
    run_pipeline()
