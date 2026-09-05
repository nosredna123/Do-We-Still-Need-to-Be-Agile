from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import shutil
import statistics
import subprocess
from html import escape
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

IDENTIFIER_HINTS = (
    "name",
    "nome",
    "email",
    "mail",
    "matricula",
    "student",
    "aluno",
    "reviewer",
    "avaliador",
    "participant",
    "person",
    "author",
)

PLANNING_KEYWORDS = {
    "spec",
    "specification",
    "planejamento",
    "planning",
    "design",
    "arquitetura",
    "architecture",
    "requisito",
    "requirement",
    "bdud",
    "bduf",
    "structured",
    "estrutura",
}
VIBE_KEYWORDS = {"vibe", "tentativa", "erro", "trial", "guess", "improviso", "ad hoc"}
EXHAUSTION_KEYWORDS = {"cansado", "exausto", "overload", "burnout", "stress", "frustrado", "frustrating"}
POSITIVE_KEYWORDS = {"bom", "good", "great", "clear", "confident", "sustainable", "stable"}
NEGATIVE_KEYWORDS = {"ruim", "bad", "chaos", "confusing", "difficult", "hard", "late", "broken"}
TOPIC_KEYWORDS = {
    "planning_debt": {"planning debt", "dívida", "debt", "rework", "retrabalho", "scope"},
    "code_churn": {"rewrite", "refactor", "rollback", "churn", "rework", "merge"},
    "cognitive_load": {"overload", "stress", "exausto", "cansado", "confusing", "cognitive"},
    "spec_driven": {"spec", "specification", "requirements", "sdd", "design upfront"},
}


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def require_pyarrow():
    try:
        import pyarrow as pa  # type: ignore
        import pyarrow.parquet as pq  # type: ignore
    except ImportError as exc:  # pragma: no cover - exercised by manual usage
        raise RuntimeError(
            "Parquet support requires pyarrow. Install dependencies with `pip install -r requirements.txt`."
        ) from exc
    return pa, pq


def is_identifier_column(name: str) -> bool:
    lowered = name.strip().lower()
    return any(token in lowered for token in IDENTIFIER_HINTS)


def hash_identifier(value: Any, salt: str = "") -> str:
    normalized = f"{salt}:{str(value).strip().lower()}"
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
    return f"anon_{digest}"


def replace_text(text: str, mapping: dict[str, str]) -> str:
    result = text
    for original in sorted((key for key in mapping if key), key=len, reverse=True):
        result = re.sub(re.escape(original), mapping[original], result, flags=re.IGNORECASE)
    return result


def redact_payload(payload: Any, mapping: dict[str, str]) -> Any:
    if isinstance(payload, dict):
        return {key: redact_payload(value, mapping) for key, value in payload.items()}
    if isinstance(payload, list):
        return [redact_payload(item, mapping) for item in payload]
    if isinstance(payload, str):
        return replace_text(payload, mapping)
    return payload


def load_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    if suffix == ".json":
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            return [item if isinstance(item, dict) else {"value": item} for item in payload]
        if isinstance(payload, dict):
            return [payload]
        return [{"value": payload}]
    if suffix == ".jsonl":
        rows: list[dict[str, Any]] = []
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows
    if suffix == ".txt":
        return [{"text": path.read_text(encoding="utf-8"), "source_file": path.name}]
    if suffix == ".parquet":
        _, pq = require_pyarrow()
        table = pq.read_table(path)
        return table.to_pylist()
    raise ValueError(f"Unsupported input format: {path}")


def write_records(path: Path, records: Sequence[dict[str, Any]]) -> None:
    ensure_parent(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        fieldnames = sorted({key for row in records for key in row.keys()})
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        return
    if suffix == ".json":
        with path.open("w", encoding="utf-8") as handle:
            json.dump(list(records), handle, indent=2, ensure_ascii=False)
        return
    if suffix == ".jsonl":
        with path.open("w", encoding="utf-8") as handle:
            for row in records:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        return
    if suffix == ".txt":
        text = "\n".join(str(row.get("text", "")) for row in records)
        path.write_text(text, encoding="utf-8")
        return
    if suffix == ".parquet":
        pa, pq = require_pyarrow()
        table = pa.Table.from_pylist(list(records))
        pq.write_table(table, path)
        return
    raise ValueError(f"Unsupported output format: {path}")


def to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def mean(values: Iterable[float]) -> float:
    seq = list(values)
    return sum(seq) / len(seq) if seq else 0.0


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def load_mapping(mapping_path: Path | None) -> dict[str, str]:
    if not mapping_path or not mapping_path.exists():
        return {}
    with mapping_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return {key: value for key, value in payload.get("mapping", {}).items()}


def build_anonymization_mapping(csv_paths: Sequence[Path], transcript_paths: Sequence[Path], salt: str = "") -> dict[str, str]:
    mapping: dict[str, str] = {}
    for csv_path in csv_paths:
        for row in load_records(csv_path):
            for key, value in row.items():
                if not value:
                    continue
                if is_identifier_column(key):
                    mapping[str(value)] = hash_identifier(value, salt=salt)
    for transcript_path in transcript_paths:
        if transcript_path.suffix.lower() == ".txt":
            continue
        for row in load_records(transcript_path):
            speaker = row.get("speaker") or row.get("author")
            if speaker:
                mapping[str(speaker)] = hash_identifier(speaker, salt=salt)
    return mapping


def anonymize_csv_file(csv_path: Path, output_path: Path, mapping: dict[str, str], salt: str = "") -> None:
    rows = load_records(csv_path)
    anonymized: list[dict[str, Any]] = []
    for row in rows:
        new_row: dict[str, Any] = {}
        for key, value in row.items():
            if isinstance(value, str):
                if is_identifier_column(key):
                    new_row[key] = mapping.get(value, hash_identifier(value, salt=salt)) if value else value
                else:
                    new_row[key] = replace_text(value, mapping)
            else:
                new_row[key] = value
        anonymized.append(new_row)
    write_records(output_path, anonymized)


def anonymize_transcript_file(transcript_path: Path, output_path: Path, mapping: dict[str, str]) -> None:
    if transcript_path.suffix.lower() == ".txt":
        redacted = replace_text(transcript_path.read_text(encoding="utf-8"), mapping)
        ensure_parent(output_path)
        output_path.write_text(redacted, encoding="utf-8")
        return
    payload = load_records(transcript_path)
    write_records(output_path, [redact_payload(item, mapping) for item in payload])


def run_git(*args: str, cwd: Path) -> str:
    completed = subprocess.run(["git", *args], cwd=cwd, check=True, text=True, capture_output=True)
    return completed.stdout


def mirror_repository(repo_path: Path, output_dir: Path) -> Path:
    target = output_dir / repo_path.name
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(repo_path, target, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
    git_dir = target / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir)
    return target


def extract_git_history(repo_path: Path, mapping: dict[str, str], salt: str = "") -> list[dict[str, Any]]:
    raw_output = run_git(
        "log",
        "--numstat",
        "--date=iso-strict",
        "--format=%x1e%H%x1f%an%x1f%ae%x1f%ad%x1f%s",
        cwd=repo_path,
    )
    records: list[dict[str, Any]] = []
    for chunk in raw_output.split("\x1e"):
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.splitlines()
        header = lines[0].split("\x1f")
        commit_hash, author_name, author_email, authored_at, subject = header
        added = 0
        deleted = 0
        files_changed = 0
        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            plus, minus, _ = parts
            if plus.isdigit():
                added += int(plus)
            if minus.isdigit():
                deleted += int(minus)
            files_changed += 1
        alias = mapping.get(author_email) or mapping.get(author_name) or hash_identifier(author_email or author_name, salt=salt)
        records.append(
            {
                "repository": repo_path.name,
                "commit_hash": commit_hash,
                "author_alias": alias,
                "author_name": alias,
                "author_email": alias,
                "authored_at": authored_at,
                "subject": subject,
                "files_changed": files_changed,
                "lines_added": added,
                "lines_deleted": deleted,
                "code_churn": added + deleted,
            }
        )
    return records


def build_master_dataset(csv_paths: Sequence[Path], git_log_path: Path) -> list[dict[str, Any]]:
    master_rows: list[dict[str, Any]] = []
    for csv_path in csv_paths:
        for row in load_records(csv_path):
            row = dict(row)
            row.setdefault("source_type", "tabular")
            row["source_file"] = csv_path.name
            master_rows.append(row)
    for row in load_records(git_log_path):
        row = dict(row)
        row.setdefault("source_type", "git")
        row["source_file"] = git_log_path.name
        master_rows.append(row)
    return master_rows


def select_text_fields(record: dict[str, Any], explicit_fields: Sequence[str] | None = None) -> list[str]:
    if explicit_fields:
        return [field for field in explicit_fields if isinstance(record.get(field), str)]
    return [key for key, value in record.items() if isinstance(value, str) and len(value.split()) >= 2]


def heuristic_nlp(text: str) -> dict[str, Any]:
    normalized = text.lower()
    tokens = re.findall(r"[\w-]+", normalized)
    word_count = len(tokens)
    planning_score = sum(keyword in normalized for keyword in PLANNING_KEYWORDS)
    vibe_score = sum(keyword in normalized for keyword in VIBE_KEYWORDS)
    exhaustion_score = sum(keyword in normalized for keyword in EXHAUSTION_KEYWORDS)
    positive_score = sum(keyword in normalized for keyword in POSITIVE_KEYWORDS)
    negative_score = sum(keyword in normalized for keyword in NEGATIVE_KEYWORDS)
    sentiment = 0.0
    if positive_score or negative_score:
        sentiment = (positive_score - negative_score) / max(positive_score + negative_score, 1)
    topics = sorted(topic for topic, keywords in TOPIC_KEYWORDS.items() if any(keyword in normalized for keyword in keywords))
    if planning_score > vibe_score:
        work_style = "structured"
    elif vibe_score > planning_score:
        work_style = "vibe_coding"
    else:
        work_style = "mixed"
    return {
        "nlp_text_length": word_count,
        "nlp_planning_signal": planning_score,
        "nlp_vibe_signal": vibe_score,
        "nlp_sentiment_score": round(sentiment, 4),
        "nlp_exhaustion_score": round(clamp(exhaustion_score / 3, 0.0, 1.0), 4),
        "nlp_topics": ",".join(topics),
        "nlp_work_style": work_style,
    }


OPENAI_RESPONSE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "qualitative_mining",
        "schema": {
            "type": "object",
            "properties": {
                "nlp_sentiment_score": {"type": "number"},
                "nlp_exhaustion_score": {"type": "number"},
                "nlp_work_style": {"type": "string"},
                "nlp_topics": {"type": "array", "items": {"type": "string"}},
                "nlp_planning_signal": {"type": "number"},
                "nlp_vibe_signal": {"type": "number"},
            },
            "required": [
                "nlp_sentiment_score",
                "nlp_exhaustion_score",
                "nlp_work_style",
                "nlp_topics",
                "nlp_planning_signal",
                "nlp_vibe_signal",
            ],
            "additionalProperties": False,
        },
    },
}


def openai_nlp(text: str, model: str) -> dict[str, Any]:  # pragma: no cover - depends on external API
    try:
        from openai import OpenAI  # type: ignore
    except ImportError as exc:
        raise RuntimeError("OpenAI backend requires the `openai` package.") from exc
    client = OpenAI()
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": (
                    "Extract sentiment, exhaustion, planning-vs-vibe signals and topic tags from software-project feedback."
                ),
            },
            {"role": "user", "content": text},
        ],
        text={"format": OPENAI_RESPONSE_SCHEMA},
    )
    payload = json.loads(response.output_text)
    payload["nlp_topics"] = ",".join(payload.get("nlp_topics", []))
    return payload


def enrich_records(records: Sequence[dict[str, Any]], backend: str = "heuristic", text_fields: Sequence[str] | None = None, model: str = "gpt-4o-mini") -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for record in records:
        updated = dict(record)
        fields = select_text_fields(record, explicit_fields=text_fields)
        combined_text = " ".join(str(record[field]) for field in fields if record.get(field))
        if combined_text:
            analysis = heuristic_nlp(combined_text) if backend == "heuristic" else openai_nlp(combined_text, model=model)
            updated.update(analysis)
        else:
            updated.update(
                {
                    "nlp_text_length": 0,
                    "nlp_planning_signal": 0,
                    "nlp_vibe_signal": 0,
                    "nlp_sentiment_score": 0.0,
                    "nlp_exhaustion_score": 0.0,
                    "nlp_topics": "",
                    "nlp_work_style": "unknown",
                }
            )
        enriched.append(updated)
    return enriched


def compute_record_metrics(record: dict[str, Any]) -> dict[str, Any]:
    updated = dict(record)
    planning_inputs = [
        to_float(record.get("planning_score")),
        to_float(record.get("pi")),
        to_float(record.get("nlp_planning_signal")),
    ]
    if record.get("nlp_work_style") == "structured":
        planning_inputs.append(1.0)
    elif record.get("nlp_work_style") == "vibe_coding":
        planning_inputs.append(0.0)
    planning_values = [value for value in planning_inputs if value is not None]
    planning_index = clamp(mean(value / 3 if value > 1 else value for value in planning_values)) if planning_values else 0.0

    additions = to_float(record.get("lines_added")) or 0.0
    deletions = to_float(record.get("lines_deleted")) or 0.0
    code_churn = to_float(record.get("code_churn"))
    if code_churn is None:
        code_churn = additions + deletions

    t1 = to_float(record.get("technical_complexity_t1"))
    t3 = to_float(record.get("technical_complexity_t3"))
    debt_t1 = to_float(record.get("technical_debt_t1"))
    debt_t3 = to_float(record.get("technical_debt_t3"))
    delta_dt = 0.0
    if t1 is not None and t3 is not None:
        delta_dt = t3 - t1
    elif debt_t1 is not None and debt_t3 is not None:
        delta_dt = debt_t3 - debt_t1
    else:
        delta_dt = round(code_churn / max((to_float(record.get("files_changed")) or 1.0), 1.0), 4)

    integration_inputs = [
        to_float(record.get("integration_friction")),
        to_float(record.get("merge_conflicts")),
        to_float(record.get("files_changed")),
    ]
    integration_values = [value for value in integration_inputs if value is not None]
    integration_attrition = mean(value / 5 if value > 1 else value for value in integration_values) if integration_values else 0.0

    exhaustion_inputs = [
        to_float(record.get("nlp_exhaustion_score")),
        0.0 if (to_float(record.get("nlp_sentiment_score")) or 0.0) >= 0 else abs(to_float(record.get("nlp_sentiment_score")) or 0.0),
        to_float(record.get("burnout_score")),
    ]
    exhaustion_values = [value for value in exhaustion_inputs if value is not None]
    exhaustion_index = clamp(mean(exhaustion_values)) if exhaustion_values else 0.0

    updated.update(
        {
            "planning_index": round(planning_index, 4),
            "code_churn": round(code_churn, 4),
            "delta_technical_degradation": round(delta_dt, 4),
            "integration_attrition": round(integration_attrition, 4),
            "exhaustion_index": round(exhaustion_index, 4),
        }
    )
    return updated


def compute_metrics(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    return [compute_record_metrics(record) for record in records]


def rank_values(values: Sequence[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    position = 0
    while position < len(indexed):
        end = position
        while end < len(indexed) and indexed[end][1] == indexed[position][1]:
            end += 1
        average_rank = (position + 1 + end) / 2
        for index, _ in indexed[position:end]:
            ranks[index] = average_rank
        position = end
    return ranks


def pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = math.sqrt(sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys))
    return numerator / denominator if denominator else 0.0


def spearman(xs: Sequence[float], ys: Sequence[float]) -> float:
    return pearson(rank_values(xs), rank_values(ys))


def normal_cdf(value: float) -> float:
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def correlation_rows(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    numeric_columns: dict[str, list[float]] = {}
    for key in sorted({column for record in records for column in record.keys()}):
        values = [to_float(record.get(key)) for record in records]
        usable = [value for value in values if value is not None]
        if len(usable) >= 2:
            numeric_columns[key] = usable
    rows: list[dict[str, Any]] = []
    keys = sorted(numeric_columns)
    for left in keys:
        for right in keys:
            pairs = [
                (to_float(record.get(left)), to_float(record.get(right)))
                for record in records
                if to_float(record.get(left)) is not None and to_float(record.get(right)) is not None
            ]
            if len(pairs) < 2:
                continue
            xs = [pair[0] for pair in pairs if pair[0] is not None]
            ys = [pair[1] for pair in pairs if pair[1] is not None]
            coefficient = spearman(xs, ys)
            statistic = coefficient * math.sqrt((len(xs) - 2) / max(1e-9, 1 - coefficient**2)) if abs(coefficient) < 1 else math.inf
            p_value = 0.0 if math.isinf(statistic) else 2 * (1 - normal_cdf(abs(statistic)))
            rows.append(
                {
                    "feature_x": left,
                    "feature_y": right,
                    "spearman_r": round(coefficient, 6),
                    "p_value": round(p_value, 6),
                    "sample_size": len(xs),
                }
            )
    return rows


def mann_whitney_u(left: Sequence[float], right: Sequence[float]) -> tuple[float, float]:
    combined = [(value, 0) for value in left] + [(value, 1) for value in right]
    combined.sort(key=lambda item: item[0])
    ranks: list[float] = [0.0] * len(combined)
    position = 0
    while position < len(combined):
        end = position
        while end < len(combined) and combined[end][0] == combined[position][0]:
            end += 1
        average_rank = (position + 1 + end) / 2
        for index in range(position, end):
            ranks[index] = average_rank
        position = end
    rank_sum_left = sum(rank for rank, (_, group) in zip(ranks, combined) if group == 0)
    n1 = len(left)
    n2 = len(right)
    u1 = rank_sum_left - n1 * (n1 + 1) / 2
    mean_u = n1 * n2 / 2
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    z_score = (u1 - mean_u) / sigma if sigma else 0.0
    p_value = 2 * (1 - normal_cdf(abs(z_score)))
    return round(u1, 6), round(p_value, 6)


def hypothesis_rows(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    structured = [to_float(record.get("code_churn")) for record in records if record.get("nlp_work_style") == "structured"]
    vibe = [to_float(record.get("code_churn")) for record in records if record.get("nlp_work_style") == "vibe_coding"]
    left = [value for value in structured if value is not None]
    right = [value for value in vibe if value is not None]
    if not left or not right:
        return []
    u_statistic, p_value = mann_whitney_u(left, right)
    return [
        {
            "test": "mann_whitney_u",
            "group_a": "structured",
            "group_b": "vibe_coding",
            "metric": "code_churn",
            "u_statistic": u_statistic,
            "p_value": p_value,
            "n_group_a": len(left),
            "n_group_b": len(right),
        }
    ]


def svg_rect(x: float, y: float, width: float, height: float, fill: str, label: str = "") -> str:
    title = f"<title>{escape(label)}</title>" if label else ""
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}">{title}</rect>'


def svg_text(x: float, y: float, text: str, size: int = 12, anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-family="Arial">{escape(text)}</text>'


def write_heatmap_svg(correlation_data: Sequence[dict[str, Any]], output_path: Path) -> None:
    features = sorted({row["feature_x"] for row in correlation_data})
    matrix = {(row["feature_x"], row["feature_y"]): float(row["spearman_r"]) for row in correlation_data}
    cell = 48
    size = 220 + cell * len(features)
    elements = ['<svg xmlns="http://www.w3.org/2000/svg" width="{0}" height="{0}">'.format(size)]
    for index, feature in enumerate(features):
        x = 180 + index * cell + cell / 2
        y = 170 + index * cell + cell / 2
        elements.append(svg_text(x, 120, feature, size=11, anchor="middle"))
        elements.append(svg_text(170, y + 4, feature, size=11, anchor="end"))
    for row_index, left in enumerate(features):
        for col_index, right in enumerate(features):
            value = matrix.get((left, right), 0.0)
            red = int(255 * (1 - max(value, 0)))
            blue = int(255 * (1 - max(-value, 0)))
            fill = f"rgb({red},235,{blue})"
            x = 180 + col_index * cell
            y = 140 + row_index * cell
            elements.append(svg_rect(x, y, cell - 2, cell - 2, fill, label=f"{left}/{right}: {value:.2f}"))
            elements.append(svg_text(x + cell / 2, y + cell / 2 + 4, f"{value:.2f}", size=10, anchor="middle"))
    elements.append("</svg>")
    ensure_parent(output_path)
    output_path.write_text("".join(elements), encoding="utf-8")


def write_scatter_svg(records: Sequence[dict[str, Any]], output_path: Path) -> None:
    points = [
        (to_float(record.get("planning_index")), to_float(record.get("code_churn")), str(record.get("nlp_work_style", "unknown")))
        for record in records
    ]
    clean_points = [(x, y, style) for x, y, style in points if x is not None and y is not None]
    width = 720
    height = 480
    max_x = max((point[0] for point in clean_points), default=1.0) or 1.0
    max_y = max((point[1] for point in clean_points), default=1.0) or 1.0
    colors = {"structured": "#2a9d8f", "vibe_coding": "#e76f51", "mixed": "#e9c46a", "unknown": "#6c757d"}
    elements = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    elements.append(svg_text(360, 28, "Planning Index vs Code Churn", size=18, anchor="middle"))
    elements.append('<line x1="60" y1="420" x2="680" y2="420" stroke="#444" />')
    elements.append('<line x1="60" y1="60" x2="60" y2="420" stroke="#444" />')
    for x, y, style in clean_points:
        cx = 60 + (x / max_x) * 620 if max_x else 60
        cy = 420 - (y / max_y) * 340 if max_y else 420
        color = colors.get(style, colors["unknown"])
        tooltip = escape(f"{style}: PI={x:.2f}, CC={y:.2f}")
        elements.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="6" fill="{color}"><title>{tooltip}</title></circle>')
    elements.append(svg_text(370, 455, "planning_index", size=12, anchor="middle"))
    elements.append(svg_text(20, 240, "code_churn", size=12, anchor="middle"))
    elements.append("</svg>")
    ensure_parent(output_path)
    output_path.write_text("".join(elements), encoding="utf-8")


def write_work_style_svg(records: Sequence[dict[str, Any]], output_path: Path) -> None:
    counts = Counter(str(record.get("nlp_work_style", "unknown")) for record in records)
    width = 720
    height = 480
    bar_width = 120
    max_count = max(counts.values(), default=1)
    colors = ["#2a9d8f", "#e9c46a", "#e76f51", "#6c757d"]
    elements = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    elements.append(svg_text(360, 28, "Work-style distribution", size=18, anchor="middle"))
    elements.append('<line x1="60" y1="420" x2="680" y2="420" stroke="#444" />')
    for index, (label, count) in enumerate(sorted(counts.items())):
        x = 110 + index * 150
        bar_height = 300 * (count / max_count)
        y = 420 - bar_height
        elements.append(svg_rect(x, y, bar_width, bar_height, colors[index % len(colors)], label=f"{label}: {count}"))
        elements.append(svg_text(x + bar_width / 2, 440, label, size=12, anchor="middle"))
        elements.append(svg_text(x + bar_width / 2, y - 8, str(count), size=12, anchor="middle"))
    elements.append("</svg>")
    ensure_parent(output_path)
    output_path.write_text("".join(elements), encoding="utf-8")


def write_hypothesis_csv(rows: Sequence[dict[str, Any]], output_path: Path) -> None:
    if rows:
        write_records(output_path, rows)


def run_txt_sidecar_transcription(audio_path: Path) -> tuple[str, dict[str, Any]]:
    sidecar = audio_path.with_suffix(".txt")
    if not sidecar.exists():
        raise FileNotFoundError(f"Missing sidecar transcript for {audio_path.name}: expected {sidecar.name}")
    text = sidecar.read_text(encoding="utf-8")
    return text, {"backend": "txt-sidecar", "segments": [{"start": 0.0, "end": 0.0, "text": text}]}


def run_whisper_transcription(audio_path: Path, model_name: str) -> tuple[str, dict[str, Any]]:  # pragma: no cover - external dependency
    try:
        import whisper  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Whisper backend requires the `openai-whisper` package.") from exc
    model = whisper.load_model(model_name)
    payload = model.transcribe(str(audio_path))
    return payload["text"], payload


def run_openai_transcription(audio_path: Path, model_name: str) -> tuple[str, dict[str, Any]]:  # pragma: no cover - external dependency
    try:
        from openai import OpenAI  # type: ignore
    except ImportError as exc:
        raise RuntimeError("OpenAI transcription backend requires the `openai` package.") from exc
    client = OpenAI()
    with audio_path.open("rb") as handle:
        response = client.audio.transcriptions.create(model=model_name, file=handle, response_format="verbose_json")
    payload = response.model_dump() if hasattr(response, "model_dump") else dict(response)
    return payload.get("text", ""), payload


AUDIO_SUFFIXES = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="*")
    return parser.parse_args(argv)
