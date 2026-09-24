"""Versioned research-protocol configuration for the data pipeline.

This module contains non-secret, version-controlled decisions that determine
how raw research inputs are interpreted. It must not contain PII, credentials,
or raw data values.
"""

from __future__ import annotations

from datetime import date
from pathlib import PurePosixPath


# Models and request parameters are version-controlled protocol decisions.
# Secrets and local overrides belong in the environment, not here.
MODEL_CONFIG: dict[str, dict[str, object]] = {
    "transcription": {
        "provider": "openai",
        "model": "whisper-1",
        "language": "pt",
    },
    "ner": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0,
        "response_format": "json_object",
    },
    "qualitative_mining": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0,
        "response_format": "json_object",
        "service_tier": "standard",
    },
}

LLM_PRICING_VERSION = "openai-pricing-2026-09-attached-v1"
LLM_PRICING_REGISTRY: dict[str, dict[str, object]] = {
    "gpt-4o-mini": {
        "pricing_mode": "token",
        "input_usd_per_1m_tokens": 0.15,
        "cached_input_usd_per_1m_tokens": 0.075,
        "output_usd_per_1m_tokens": 0.60,
    },
    "whisper-1": {
        "pricing_mode": "minute",
        "usd_per_minute": 0.006,
    },
}
LLM_MAX_RETRIES = 0

REPOSITORY_SNAPSHOT_CONTRACT_VERSION = "git-repository-snapshots-v1"
SOURCE_LOC_DEFINITION_VERSION = "source-loc-v1"
EXCLUDED_PATH_PATTERNS_VERSION = "source-exclusions-v4"
SOURCE_CODE_EXTENSION_ALLOWLIST = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".dart",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}
SOURCE_CODE_EXCLUDED_PATH_PATTERNS = {
    ".git/",
    ".history/",
    ".next/",
    ".env/",
    ".tox/",
    ".venv/",
    "backup/",
    "backups/",
    "build/",
    "coverage/",
    "dist/",
    "env/",
    "node_modules/",
    "site-packages/",
    "target/",
    "venv/",
    "vendor/",
}


def is_measurement_code_path(file_path: str | None) -> bool:
    """Return whether a repository path is eligible for code-change measurement.

    The predicate is the shared whitelist/blacklist contract for LOC, clean
    churn, and file-provenance rework. A directory exclusion matches at any
    path segment, so nested editor history or dependencies cannot enter a
    measurement merely because their filename has a source extension.
    """
    normalized = str(file_path or "").replace("\\", "/").strip().lower()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if not normalized:
        return False
    for pattern in SOURCE_CODE_EXCLUDED_PATH_PATTERNS:
        if pattern.endswith("/") and (
            normalized.startswith(pattern) or f"/{pattern}" in normalized
        ):
            return False
    return PurePosixPath(normalized).suffix.lower() in SOURCE_CODE_EXTENSION_ALLOWLIST

NLP_SCORE_SCALES = {
    "sentiment_score": {"version": "v1", "minimum": -2, "maximum": 2, "integer": True},
    "cognitive_load_score": {"version": "v1", "minimum": 0, "maximum": 4, "integer": True},
    "ai_dependency_score": {"version": "v1", "minimum": 0, "maximum": 4, "integer": True},
    "coordination_friction_score": {"version": "v1", "minimum": 0, "maximum": 4, "integer": True},
    "rework_signal_score": {"version": "v1", "minimum": 0, "maximum": 4, "integer": True},
    "planning_clarity_score": {"version": "v1", "minimum": 0, "maximum": 4, "integer": True},
}
NLP_ENUMS = {
    "methodological_orientation": {"structured", "mixed", "vibe_coding", "insufficient_evidence"},
    "planning_debt_signal": {"present", "absent", "insufficient_evidence"},
    "integration_risk_signal": {"absent", "low", "moderate", "high", "critical"},
    "dominant_topic": {
        "planning_debt", "coordination", "rework", "integration", "technical_quality",
        "ai_dependency", "cognitive_load", "deadline_pressure", "communication",
        "testing", "architecture", "other",
    },
}
TRANSCRIPT_CHUNK_TOKENS = 8_000
TRANSCRIPT_CHUNK_OVERLAP_TOKENS = 500
TRANSCRIPT_EVIDENCE_MAX_CHARS = 1_000
_ALL_STUDENT_CUT_SCOPES = [
    {"Semestre": semester, "temporal_marker": marker, "requirement": "required"}
    for semester in ("2025.2", "2026.1")
    for marker in ("T1", "T2", "T3")
]
STUDENT_TEXT_QUESTION_REGISTRY = {
    "ai_benefit": {
        "question_id": "ai_benefit",
        "construct": "ai_dependency",
        "aliases": [
            "Qual foi o maior benefício que você obteve (ou imagina) ao usar ferramentas de IA generativa em projetos de Engenharia de Software?",
            "Qual foi o maior benefício que você obteve (ou imagina) ao usar ferramentas de IA generativa em projetos de Engenharia de Software?.1",
        ],
        "required_scopes": _ALL_STUDENT_CUT_SCOPES,
        "duplicate_strategy": "coalesce_without_conflict",
        "conflict_strategy": "reject_on_conflict",
        "registry_version": "student-text-v1",
    },
    "ai_career_impact_5y": {
        "question_id": "ai_career_impact_5y",
        "construct": "career_expectation",
        "aliases": [
            "Em 5 anos, como você enxerga o impacto das ferramentas de IA generativa em sua carreira de engenharia de software?",
            "Em 5 anos, como você enxerga o impacto das ferramentas de IA generativa em sua carreira de engenharia de software?.1",
        ],
        "required_scopes": _ALL_STUDENT_CUT_SCOPES,
        "duplicate_strategy": "coalesce_without_conflict",
        "conflict_strategy": "reject_on_conflict",
        "registry_version": "student-text-v1",
    },
    "project_feeling": {
        "question_id": "project_feeling",
        "construct": "cognitive_load",
        "aliases": [
            "Descreva brevemente como você se sente em relação ao projeto que irá desenvolver nesta disciplina.",
            "Descreva brevemente como você se sente em relação ao projeto que você está desenvolvendo nesta disciplina.",
        ],
        "required_scopes": _ALL_STUDENT_CUT_SCOPES,
        "duplicate_strategy": "coalesce_without_conflict",
        "conflict_strategy": "reject_on_conflict",
        "registry_version": "student-text-v1",
    },
    "project_challenges": {
        "question_id": "project_challenges",
        "construct": "planning_debt",
        "aliases": [
            "Quais aspectos do projeto você acredita que serão mais desafiadores? (marque todos que se aplicam)",
            "Quais aspectos do projeto você acredita que foram/são mais desafiadores? (marque todos que se aplicam)",
        ],
        "required_scopes": _ALL_STUDENT_CUT_SCOPES,
        "duplicate_strategy": "coalesce_without_conflict",
        "conflict_strategy": "reject_on_conflict",
        "registry_version": "student-text-v1",
    },
    "autonomy_tool_dependency": {
        "question_id": "autonomy_tool_dependency",
        "construct": "ai_dependency",
        "aliases": [
            "Para você, qual deve ser o equilíbrio ideal entre a autonomia de cada integrante e a dependência de ferramentas de suporte no desenvolvimento do projeto?",
        ],
        "required_scopes": _ALL_STUDENT_CUT_SCOPES,
        "duplicate_strategy": "coalesce_without_conflict",
        "conflict_strategy": "reject_on_conflict",
        "registry_version": "student-text-v1",
    },
    "career_expectation": {
        "question_id": "career_expectation",
        "construct": "career_expectation",
        "aliases": [
            "Quais expectativas você tem sobre sua própria evolução profissional ao participar deste projeto?",
        ],
        "required_scopes": _ALL_STUDENT_CUT_SCOPES,
        "duplicate_strategy": "coalesce_without_conflict",
        "conflict_strategy": "reject_on_conflict",
        "registry_version": "student-text-v1",
    },
}
PLANNING_FILE_EXTENSIONS = {".md", ".txt", ".rst", ".adoc", ".pdf", ".doc", ".docx", ".odt", ".yaml", ".yml", ".json", ".toml", ".drawio", ".puml", ".mmd", ".mermaid", ".uml", ".bpmn"}
PLANNING_PATH_PATTERNS = {"docs/", "doc/", "documentation/", "requirements/", "spec/", "specs/", "architecture/", "design/", "planning/", "planejamento/", "requisitos/", "arquitetura/", "prototipo/", "prototype/"}
PLANNING_DEFINITION_VERSION = "pi-v1"
FILE_CATEGORY_DEFINITION_VERSION = "file-category-rules-v4"
FILE_CATEGORY_RULES: dict[str, object] = {
    "version": FILE_CATEGORY_DEFINITION_VERSION,
    "default_category": "unknown",
    "path_precedence": "path_context_over_extension",
    "category_order": [
        "generated",
        "planning",
        "test",
        "source",
        "localization",
        "config",
        "asset",
        "unknown",
    ],
    "path_patterns": {
        "generated": SOURCE_CODE_EXCLUDED_PATH_PATTERNS | {"__pycache__/"},
        "planning": PLANNING_PATH_PATTERNS,
        "test": {
            "__tests__/", "test/", "tests/", "spec/", "specs/",
        },
    },
    "filename_suffixes": {
        "generated": {".bundle.js", ".min.css", ".min.js"},
        "config": {".d.ts"},
        "test": {".spec.js", ".spec.jsx", ".spec.ts", ".spec.tsx", ".test.js", ".test.jsx", ".test.ts", ".test.tsx", "_test.py"},
    },
    "extensions": {
        "source": SOURCE_CODE_EXTENSION_ALLOWLIST | {".m", ".mm", ".proto"},
        "planning": PLANNING_FILE_EXTENSIONS,
        "config": {
            ".cfg", ".conf", ".csv", ".env", ".ini", ".json", ".lock",
            ".properties", ".pyi", ".toml", ".typed", ".xml", ".yaml", ".yml",
        },
        "generated": {
            ".class", ".dll", ".map", ".mo", ".o", ".obj", ".pyc", ".so",
        },
        "localization": {".arb", ".po", ".pot", ".xliff", ".xlf"},
        "asset": {
            ".avi", ".bin", ".bmp", ".doc", ".docx", ".eot", ".gif", ".gz",
            ".ico", ".jpeg", ".jpg", ".mp3", ".mp4", ".odt", ".otf", ".pdf",
            ".png", ".svg", ".tar", ".tgz", ".ttf", ".wav", ".webp", ".woff",
            ".woff2", ".zip",
        },
    },
    "contextual_extensions": {
        "planning_when_path_matches_planning": {".json", ".toml", ".yaml", ".yml"},
    },
    "warnings": {
        "empty_extension": "classify_by_path_or_unknown",
        "generated_source_like_path": "generated_path_takes_precedence",
        "planning_config_extension": "planning_path_takes_precedence_over_config_extension",
    },
}
AI_DEFINITION_VERSION = "ai-v1"
AI_T3_WINDOW_HOURS = 72
AI_T3_WINDOW_BOUNDS = "[t3_start - hours, t3_start)"
AI_REF_REQUIRED_FIELDS = ["branch_or_ref", "branch_or_ref_source"]
AI_GINI_METHOD = "author_commit_count_standard_gini"
AI_AUTHOR_SHARE_DISTRIBUTION = "per_author_commit_share"
STATISTICAL_ANALYSIS_REGISTRY = {
    "pi_vs_cc_primary": {"unit_of_analysis": "team_semester", "x": "pi_file_count_t1", "y": "cc_per_source_loc_t3", "test": "spearman", "priority": "primary", "figure": "pi_vs_cc.png"},
    "pi_vs_delta_dt_primary": {"unit_of_analysis": "team_semester", "x": "pi_file_count_t1", "y": "delta_dt_t1_t3", "test": "spearman", "priority": "primary", "figure": None},
    "ai_vs_cc_primary": {"unit_of_analysis": "team_semester", "x": "ai_max_author_share_before_t3_window", "y": "cc_total_t3", "test": "spearman", "priority": "primary", "figure": "ai_before_t3.png"},
    "context_ie_temporal_primary": {"unit_of_analysis": "cut_context", "x": "ie_transcript_coordination_friction_score_mean", "y": "ie_transcript_rework_signal_score_mean", "test": "spearman", "priority": "primary", "figure": None},
}
HYPOTHESIS_TEST_REGISTRY = {
    "pi_high_vs_low_cc_primary": {
        "unit_of_analysis": "team_semester",
        "group_variable": "pi_file_count_t1",
        "outcome_variable": "cc_per_source_loc_t3",
        "test": "mann_whitney_u",
        "priority": "primary",
        "split_rule": "median_low_le_high_gt",
    },
    "ai_high_vs_low_cc_primary": {
        "unit_of_analysis": "team_semester",
        "group_variable": "ai_max_author_share_before_t3_window",
        "outcome_variable": "cc_total_t3",
        "test": "mann_whitney_u",
        "priority": "primary",
        "split_rule": "median_low_le_high_gt",
    },
    "context_ie_high_vs_low_rework_primary": {
        "unit_of_analysis": "cut_context",
        "group_variable": "ie_transcript_coordination_friction_score_mean",
        "outcome_variable": "ie_transcript_rework_signal_score_mean",
        "test": "mann_whitney_u",
        "priority": "primary",
        "split_rule": "median_low_le_high_gt",
    },
}

# Each range identifies one evaluation moment. The two-day ranges in 2025.2 are
# deliberate: teams were distributed between presentation days because all teams
# could not be evaluated in one session. Each range is therefore one observation
# window, not two independent longitudinal observations.
EVALUATOR_TEMPORAL_CUTS: dict[str, dict[str, tuple[str, str]]] = {
    "2025.2": {
        "T1": ("2025-10-17", "2025-10-24"),
        "T2": ("2025-11-14", "2025-11-21"),
        "T3": ("2025-12-05", "2025-12-12"),
    },
    "2026.1": {
        "T1": ("2026-04-24", "2026-04-24"),
        "T2": ("2026-05-22", "2026-05-22"),
        "T3": ("2026-06-19", "2026-06-19"),
    },
}


def temporal_marker_for(semester: str, evaluation_date: str) -> str:
    """Return the configured temporal marker for an evaluator response date.

    Args:
        semester: Semester identifier, such as ``2025.2``.
        evaluation_date: Evaluation date in ISO-8601 ``YYYY-MM-DD`` format.

    Returns:
        The configured ``T1``, ``T2``, or ``T3`` marker.

    Raises:
        ValueError: If the semester or date is not covered by the protocol.
    """
    cuts = EVALUATOR_TEMPORAL_CUTS.get(semester)
    if cuts is None:
        raise ValueError(f"Semester {semester} has no configured evaluator cuts")

    parsed_date = date.fromisoformat(evaluation_date)
    for marker, (start_date, end_date) in cuts.items():
        if date.fromisoformat(start_date) <= parsed_date <= date.fromisoformat(end_date):
            return marker

    raise ValueError(
        f"Date {evaluation_date} is not in a configured evaluator cut for {semester}"
    )


def git_temporal_marker_for(semester: str, event_date: str) -> str:
    """Assign a Git event to a semester phase using ordered cut boundaries.

    Git history is continuous, unlike evaluator submissions. Events before the
    T1 boundary belong to T1, events before T2 belong to T2, and events from
    T2 onward belong to T3.
    """
    cuts = EVALUATOR_TEMPORAL_CUTS.get(semester)
    if cuts is None:
        raise ValueError(f"Semester {semester} has no configured evaluator cuts")

    parsed_date = date.fromisoformat(event_date)
    t1_start = date.fromisoformat(cuts["T1"][0])
    t2_start = date.fromisoformat(cuts["T2"][0])
    if parsed_date < t1_start:
        return "T1"
    if parsed_date < t2_start:
        return "T2"
    return "T3"


# --- Intermediary Phase 2.5: Artifact Narrative Audit (docs/02a) ---
#
# This registry declares, for every Phase 2 analytical artifact, what kind of
# file it is, which narrative acts of docs/00b.narrative-arc.md it serves, and
# (when applicable) which primary correlation/hypothesis analysis_ids from
# STATISTICAL_ANALYSIS_REGISTRY / HYPOTHESIS_TEST_REGISTRY determine whether it
# currently supports the thesis. Only artifacts directly examined by a
# statistical test use "aggregate_from_tests"; every other artifact is
# "descriptive_infrastructure" (it feeds a tested artifact but is not itself a
# test outcome).
NARRATIVE_REPORT_CONTRACT_VERSION = "artifact-narrative-report-v1"
NARRATIVE_AUDIT_MIN_SUFFICIENT_TEAM_N = 30

ARTIFACT_NARRATIVE_REGISTRY: dict[str, dict[str, object]] = {
    "phase2_contract_report": {
        "kind": "json",
        "path": "phase2_contract_report.json",
        "producer_script": "phase2_contracts.py",
        "acts": [1, 2, 3],
        "verdict_mode": "descriptive_infrastructure",
    },
    "student_nlp": {
        "kind": "parquet",
        "path": "student_nlp.parquet",
        "producer_script": "04_nlp_qualitative_miner.py",
        "acts": [2, 3],
        "verdict_mode": "descriptive_infrastructure",
    },
    "transcript_nlp": {
        "kind": "parquet",
        "path": "transcript_nlp.parquet",
        "producer_script": "04_nlp_qualitative_miner.py",
        "acts": [3],
        "verdict_mode": "descriptive_infrastructure",
    },
    "textual_cut_signals": {
        "kind": "parquet",
        "path": "textual_cut_signals.parquet",
        "producer_script": "04_nlp_qualitative_miner.py",
        "acts": [3],
        "verdict_mode": "descriptive_infrastructure",
    },
    "planning_metrics": {
        "kind": "parquet",
        "path": "planning_metrics.parquet",
        "producer_script": "05_metric_engine.py",
        "acts": [2],
        "verdict_mode": "descriptive_infrastructure",
    },
    "code_churn_metrics": {
        "kind": "parquet",
        "path": "code_churn_metrics.parquet",
        "producer_script": "05_metric_engine.py",
        "acts": [2],
        "verdict_mode": "descriptive_infrastructure",
    },
    "technical_degradation_metrics": {
        "kind": "parquet",
        "path": "technical_degradation_metrics.parquet",
        "producer_script": "05_metric_engine.py",
        "acts": [2, 3],
        "verdict_mode": "descriptive_infrastructure",
    },
    "integration_friction_metrics": {
        "kind": "parquet",
        "path": "integration_friction_metrics.parquet",
        "producer_script": "05_metric_engine.py",
        "acts": [3],
        "verdict_mode": "descriptive_infrastructure",
    },
    "cut_context_metrics": {
        "kind": "parquet",
        "path": "cut_context_metrics.parquet",
        "producer_script": "05_metric_engine.py",
        "acts": [3],
        "verdict_mode": "aggregate_from_tests",
        "related_correlations": ["context_ie_temporal_primary"],
        "related_hypotheses": ["context_ie_high_vs_low_rework_primary"],
    },
    "team_metrics": {
        "kind": "parquet",
        "path": "team_metrics.parquet",
        "producer_script": "05_metric_engine.py",
        "acts": [2, 3],
        "verdict_mode": "aggregate_from_tests",
        "related_correlations": ["pi_vs_cc_primary", "pi_vs_delta_dt_primary", "ai_vs_cc_primary"],
        "related_hypotheses": ["pi_high_vs_low_cc_primary", "ai_high_vs_low_cc_primary"],
        "exclusions_path": "team_metrics_exclusions.json",
    },
    "statistical_dataset_manifest": {
        "kind": "json",
        "path": "statistical_dataset_manifest.json",
        "producer_script": "06_statistical_analyzer.py",
        "acts": [2, 3, 4],
        "verdict_mode": "descriptive_infrastructure",
        "exclusions_path": "statistical_dataset_manifest_exclusions.json",
    },
    "correlation_results": {
        "kind": "csv",
        "path": "correlation_results.csv",
        "producer_script": "06_statistical_analyzer.py",
        "acts": [2, 3],
        "verdict_mode": "aggregate_from_tests",
        "related_correlations": list(STATISTICAL_ANALYSIS_REGISTRY),
        "related_hypotheses": [],
    },
    "hypothesis_results": {
        "kind": "csv",
        "path": "hypothesis_results.csv",
        "producer_script": "06_statistical_analyzer.py",
        "acts": [2, 3],
        "verdict_mode": "aggregate_from_tests",
        "related_correlations": [],
        "related_hypotheses": list(HYPOTHESIS_TEST_REGISTRY),
    },
    "figure_pi_vs_cc": {
        "kind": "figure",
        "figure_id": "pi_vs_cc",
        "producer_script": "06_statistical_analyzer.py",
        "acts": [2],
        "verdict_mode": "aggregate_from_tests",
        "related_correlations": ["pi_vs_cc_primary"],
        "related_hypotheses": ["pi_high_vs_low_cc_primary"],
    },
    "figure_cc_by_temporal_cut": {
        "kind": "figure",
        "figure_id": "cc_by_temporal_cut",
        "producer_script": "06_statistical_analyzer.py",
        "acts": [2],
        "verdict_mode": "descriptive_infrastructure",
    },
    "figure_delta_dt_by_team_semester": {
        "kind": "figure",
        "figure_id": "delta_dt_by_team_semester",
        "producer_script": "06_statistical_analyzer.py",
        "acts": [2, 3],
        "verdict_mode": "aggregate_from_tests",
        "related_correlations": ["pi_vs_delta_dt_primary"],
        "related_hypotheses": [],
    },
    "figure_ai_before_t3": {
        "kind": "figure",
        "figure_id": "ai_before_t3",
        "producer_script": "06_statistical_analyzer.py",
        "acts": [3],
        "verdict_mode": "aggregate_from_tests",
        "related_correlations": ["ai_vs_cc_primary"],
        "related_hypotheses": ["ai_high_vs_low_cc_primary"],
    },
    "figure_ie_by_cut_or_corpus": {
        "kind": "figure",
        "figure_id": "ie_by_cut_or_corpus",
        "producer_script": "06_statistical_analyzer.py",
        "acts": [3],
        "verdict_mode": "aggregate_from_tests",
        "related_correlations": ["context_ie_temporal_primary"],
        "related_hypotheses": ["context_ie_high_vs_low_rework_primary"],
    },
}

# One synthesis report per act of docs/00b.narrative-arc.md.
NARRATIVE_ACT_REGISTRY: dict[int, dict[str, str]] = {
    1: {
        "slug": "evolutionary_ceiling",
        "title": "Ato 1 - O Teto Evolutivo do Agile (Context)",
    },
    2: {
        "slug": "planning_debt",
        "title": "Ato 2 - A Anatomia da Divida de Planejamento (Diagnosis)",
    },
    3: {
        "slug": "human_factor",
        "title": "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)",
    },
    4: {
        "slug": "value_inversion",
        "title": "Ato 4 - A Inversao de Valores na Era da IA (Conclusion)",
    },
}


# --- Cross-evidence extension (docs/02c, CE-0.1) ---
#
# This block declares the scope, versions, stable relative output layout, and
# central artifact registry for the independent cross-evidence extension.
# Metric, statistical-analysis, figure, and narrative prompt registries are
# intentionally separate later tasks so each layer can evolve without changing
# the artifact inventory contract.
CROSS_EVIDENCE_CONTRACT_VERSION = "cross-evidence-v1"
CROSS_EVIDENCE_MANIFEST_VERSION = "cross-evidence-manifest-v1"
CROSS_EVIDENCE_OUTPUT_LAYOUT_VERSION = "cross-evidence-layout-v1"
CROSS_EVIDENCE_SCOPE = "secondary_exploratory_evidence"
CROSS_EVIDENCE_COMPATIBILITY_POLICY_VERSION = "cross-evidence-compatibility-v1"
CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY = "read_legacy_only"
CROSS_EVIDENCE_ROOT = "data/analysis/cross_evidence"
CROSS_EVIDENCE_DATASETS_DIR = f"{CROSS_EVIDENCE_ROOT}/datasets"
CROSS_EVIDENCE_RESULTS_DIR = f"{CROSS_EVIDENCE_ROOT}/results"
CROSS_EVIDENCE_FIGURE_DATA_DIR = f"{CROSS_EVIDENCE_ROOT}/figure_data"
CROSS_EVIDENCE_REPORTS_DIR = f"{CROSS_EVIDENCE_ROOT}/reports"
CROSS_EVIDENCE_ARTIFACT_REPORTS_DIR = f"{CROSS_EVIDENCE_REPORTS_DIR}/artifact_reports"
CROSS_EVIDENCE_GROUP_REPORTS_DIR = f"{CROSS_EVIDENCE_REPORTS_DIR}/group_reports"
CROSS_EVIDENCE_ACT_REPORTS_DIR = f"{CROSS_EVIDENCE_REPORTS_DIR}/act_reports"
CROSS_EVIDENCE_MANIFEST_PATH = f"{CROSS_EVIDENCE_ROOT}/cross_evidence_manifest.json"
CROSS_EVIDENCE_EXCLUSIONS_PATH = f"{CROSS_EVIDENCE_ROOT}/cross_evidence_manifest_exclusions.json"
CROSS_EVIDENCE_FIGURES_ROOT = "assets/figures/cross_evidence"
CROSS_EVIDENCE_PRIORITY_FIGURES_DIR = f"{CROSS_EVIDENCE_FIGURES_ROOT}/prioritarias"
CROSS_EVIDENCE_EXPLORATORY_FIGURES_DIR = f"{CROSS_EVIDENCE_FIGURES_ROOT}/exploratorias"
CROSS_EVIDENCE_DASHBOARD_FIGURES_DIR = f"{CROSS_EVIDENCE_FIGURES_ROOT}/dashboard_interativo"
CROSS_EVIDENCE_OUTPUT_DIRECTORIES = {
    "root": CROSS_EVIDENCE_ROOT,
    "datasets": CROSS_EVIDENCE_DATASETS_DIR,
    "results": CROSS_EVIDENCE_RESULTS_DIR,
    "figure_data": CROSS_EVIDENCE_FIGURE_DATA_DIR,
    "reports": CROSS_EVIDENCE_REPORTS_DIR,
    "artifact_reports": CROSS_EVIDENCE_ARTIFACT_REPORTS_DIR,
    "group_reports": CROSS_EVIDENCE_GROUP_REPORTS_DIR,
    "act_reports": CROSS_EVIDENCE_ACT_REPORTS_DIR,
    "figures_root": CROSS_EVIDENCE_FIGURES_ROOT,
    "priority_figures": CROSS_EVIDENCE_PRIORITY_FIGURES_DIR,
    "exploratory_figures": CROSS_EVIDENCE_EXPLORATORY_FIGURES_DIR,
    "dashboard_figures": CROSS_EVIDENCE_DASHBOARD_FIGURES_DIR,
}

CROSS_EVIDENCE_ARTIFACT_REGISTRY: dict[str, dict[str, object]] = {
    "evaluator_outcome_metrics": {
        "kind": "dataset",
        "path": f"{CROSS_EVIDENCE_DATASETS_DIR}/evaluator_outcome_metrics.parquet",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "descriptive_context",
        "acts": [3],
        "privacy": "public_aggregate_with_anonymized_team_ids",
        "inputs": ["lake.evaluator_team_cuts"],
    },
    "file_category_churn_metrics": {
        "kind": "dataset",
        "path": f"{CROSS_EVIDENCE_DATASETS_DIR}/file_category_churn_metrics.parquet",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester_cut_category",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [2, 3, 4],
        "privacy": "public_aggregate_with_anonymized_team_ids",
        "inputs": ["lake.git_files"],
    },
    "author_pressure_metrics": {
        "kind": "dataset",
        "path": f"{CROSS_EVIDENCE_DATASETS_DIR}/author_pressure_metrics.parquet",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester_cut",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [3],
        "privacy": "public_aggregate_with_anonymized_team_ids",
        "inputs": ["lake.git_commits"],
    },
    "temporal_escalation_metrics": {
        "kind": "dataset",
        "path": f"{CROSS_EVIDENCE_DATASETS_DIR}/temporal_escalation_metrics.parquet",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "metric_family",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [2, 3, 4],
        "privacy": "public_aggregate",
        "inputs": [
            "analysis.planning_metrics",
            "analysis.code_churn_metrics",
            "analysis.technical_degradation_metrics",
        ],
    },
    "late_instability_metrics": {
        "kind": "dataset",
        "path": f"{CROSS_EVIDENCE_DATASETS_DIR}/late_instability_metrics.parquet",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [2, 3, 4],
        "privacy": "public_aggregate_with_anonymized_team_ids",
        "inputs": [
            "analysis.team_metrics",
            "cross_evidence.file_category_churn_metrics",
            "cross_evidence.author_pressure_metrics",
        ],
    },
    "cross_evidence_panel": {
        "kind": "dataset",
        "path": f"{CROSS_EVIDENCE_DATASETS_DIR}/cross_evidence_panel.parquet",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "descriptive_context",
        "acts": [2, 3, 4],
        "privacy": "public_aggregate_with_anonymized_team_ids",
        "inputs": [
            "cross_evidence.evaluator_outcome_metrics",
            "cross_evidence.late_instability_metrics",
            "cross_evidence.author_pressure_metrics",
            "cross_evidence.file_category_churn_metrics",
        ],
    },
    "cross_evidence_correlations": {
        "kind": "result",
        "path": f"{CROSS_EVIDENCE_RESULTS_DIR}/cross_evidence_correlations.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "analysis_result",
        "contract_version": "cross-evidence-correlations-v1",
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [2, 3, 4],
        "privacy": "public_aggregate",
        "inputs": ["cross_evidence.cross_evidence_panel"],
    },
    "best_worst_project_contrasts": {
        "kind": "result",
        "path": f"{CROSS_EVIDENCE_RESULTS_DIR}/best_worst_project_contrasts.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "analysis_result",
        "contract_version": "cross-evidence-best-worst-contrasts-v1",
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "secondary_support",
        "acts": [3],
        "privacy": "public_aggregate",
        "inputs": ["cross_evidence.cross_evidence_panel"],
    },
    "leave_one_out_sensitivity": {
        "kind": "result",
        "path": f"{CROSS_EVIDENCE_RESULTS_DIR}/leave_one_out_sensitivity.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "analysis_result",
        "contract_version": "cross-evidence-leave-one-out-v1",
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [2, 3],
        "privacy": "public_aggregate",
        "inputs": ["cross_evidence.cross_evidence_panel", "cross_evidence.cross_evidence_correlations"],
    },
    "extreme_case_overlap": {
        "kind": "result",
        "path": f"{CROSS_EVIDENCE_RESULTS_DIR}/extreme_case_overlap.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "analysis_result",
        "contract_version": "cross-evidence-extreme-overlap-v1",
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "secondary_support",
        "acts": [2, 3],
        "privacy": "public_ranked_anonymized_team_ids",
        "inputs": ["cross_evidence.cross_evidence_panel"],
    },
    "semester_stratified_results": {
        "kind": "result",
        "path": f"{CROSS_EVIDENCE_RESULTS_DIR}/semester_stratified_results.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "analysis_result",
        "contract_version": "cross-evidence-semester-stratified-v1",
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "methodological_warning",
        "acts": [2, 3],
        "privacy": "public_aggregate",
        "inputs": ["cross_evidence.cross_evidence_panel"],
    },
    "evidence_priority_matrix": {
        "kind": "result",
        "path": f"{CROSS_EVIDENCE_RESULTS_DIR}/evidence_priority_matrix.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "evidence_item",
        "contract_version": "cross-evidence-priority-matrix-v1",
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "descriptive_context",
        "acts": [1, 2, 3, 4],
        "privacy": "public_aggregate",
        "inputs": [
            "cross_evidence.cross_evidence_correlations",
            "cross_evidence.best_worst_project_contrasts",
            "cross_evidence.leave_one_out_sensitivity",
            "cross_evidence.extreme_case_overlap",
            "cross_evidence.semester_stratified_results",
        ],
    },
    "scope_vs_late_instability_data": {
        "kind": "figure_data",
        "path": f"{CROSS_EVIDENCE_FIGURE_DATA_DIR}/scope_vs_late_instability.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [3],
        "privacy": "private_figure_data_with_anonymized_team_ids",
        "inputs": ["cross_evidence.cross_evidence_panel"],
    },
    "source_churn_vs_planning_rework_data": {
        "kind": "figure_data",
        "path": f"{CROSS_EVIDENCE_FIGURE_DATA_DIR}/source_churn_vs_planning_rework.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [2],
        "privacy": "private_figure_data_with_anonymized_team_ids",
        "inputs": ["cross_evidence.late_instability_metrics"],
    },
    "temporal_escalation_panel_data": {
        "kind": "figure_data",
        "path": f"{CROSS_EVIDENCE_FIGURE_DATA_DIR}/temporal_escalation_panel.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "metric_family_cut",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [2, 3],
        "privacy": "public_aggregate",
        "inputs": ["cross_evidence.temporal_escalation_metrics", "cross_evidence.evaluator_outcome_metrics"],
    },
    "file_category_churn_by_cut_data": {
        "kind": "figure_data",
        "path": f"{CROSS_EVIDENCE_FIGURE_DATA_DIR}/file_category_churn_by_cut.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester_cut_category",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "methodological_warning",
        "acts": [2, 3],
        "privacy": "private_figure_data_with_anonymized_team_ids",
        "inputs": ["cross_evidence.file_category_churn_metrics"],
    },
    "author_pressure_vs_churn_data": {
        "kind": "figure_data",
        "path": f"{CROSS_EVIDENCE_FIGURE_DATA_DIR}/author_pressure_vs_churn.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [3],
        "privacy": "private_figure_data_with_anonymized_team_ids",
        "inputs": ["cross_evidence.cross_evidence_panel"],
    },
    "pareto_extreme_cases_data": {
        "kind": "figure_data",
        "path": f"{CROSS_EVIDENCE_FIGURE_DATA_DIR}/pareto_extreme_cases.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "ranked_team_semester",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "secondary_support",
        "acts": [2, 3],
        "privacy": "public_ranked_anonymized_team_ids",
        "inputs": ["cross_evidence.cross_evidence_panel", "cross_evidence.extreme_case_overlap"],
    },
    "leave_one_out_robustness_data": {
        "kind": "figure_data",
        "path": f"{CROSS_EVIDENCE_FIGURE_DATA_DIR}/leave_one_out_robustness.csv",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "analysis_result",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [2, 3],
        "privacy": "public_aggregate",
        "inputs": ["cross_evidence.leave_one_out_sensitivity"],
    },
    "scope_vs_late_instability_figure": {
        "kind": "figure",
        "path": f"{CROSS_EVIDENCE_PRIORITY_FIGURES_DIR}/scope_vs_late_instability.png",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [3],
        "privacy": "public_visual_ranked_or_aggregate",
        "inputs": ["cross_evidence.scope_vs_late_instability_data"],
        "figure_category": "prioritarias",
        "export_formats": ["html", "png", "svg", "pdf"],
    },
    "source_churn_vs_planning_rework_figure": {
        "kind": "figure",
        "path": f"{CROSS_EVIDENCE_PRIORITY_FIGURES_DIR}/source_churn_vs_planning_rework.png",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [2],
        "privacy": "public_visual_ranked_or_aggregate",
        "inputs": ["cross_evidence.source_churn_vs_planning_rework_data"],
        "figure_category": "prioritarias",
        "export_formats": ["html", "png", "svg", "pdf"],
    },
    "temporal_escalation_panel_figure": {
        "kind": "figure",
        "path": f"{CROSS_EVIDENCE_PRIORITY_FIGURES_DIR}/temporal_escalation_panel.png",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "metric_family_cut",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [2, 3],
        "privacy": "public_visual_aggregate",
        "inputs": ["cross_evidence.temporal_escalation_panel_data"],
        "figure_category": "prioritarias",
        "export_formats": ["html", "png", "svg", "pdf"],
    },
    "file_category_churn_by_cut_figure": {
        "kind": "figure",
        "path": f"{CROSS_EVIDENCE_PRIORITY_FIGURES_DIR}/file_category_churn_by_cut.png",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester_cut_category",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "methodological_warning",
        "acts": [2, 3],
        "privacy": "public_visual_aggregate",
        "inputs": ["cross_evidence.file_category_churn_by_cut_data"],
        "figure_category": "prioritarias",
        "export_formats": ["html", "png", "svg", "pdf"],
    },
    "author_pressure_vs_churn_figure": {
        "kind": "figure",
        "path": f"{CROSS_EVIDENCE_PRIORITY_FIGURES_DIR}/author_pressure_vs_churn.png",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "team_semester",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [3],
        "privacy": "public_visual_ranked_or_aggregate",
        "inputs": ["cross_evidence.author_pressure_vs_churn_data"],
        "figure_category": "prioritarias",
        "export_formats": ["html", "png", "svg", "pdf"],
    },
    "pareto_extreme_cases_figure": {
        "kind": "figure",
        "path": f"{CROSS_EVIDENCE_PRIORITY_FIGURES_DIR}/pareto_extreme_cases.png",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "ranked_team_semester",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "secondary_support",
        "acts": [2, 3],
        "privacy": "public_visual_ranked_or_aggregate",
        "inputs": ["cross_evidence.pareto_extreme_cases_data"],
        "figure_category": "prioritarias",
        "export_formats": ["html", "png", "svg", "pdf"],
    },
    "leave_one_out_robustness_figure": {
        "kind": "figure",
        "path": f"{CROSS_EVIDENCE_PRIORITY_FIGURES_DIR}/leave_one_out_robustness.png",
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "analysis_result",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "primary_candidate",
        "acts": [2, 3],
        "privacy": "public_visual_aggregate",
        "inputs": ["cross_evidence.leave_one_out_robustness_data"],
        "figure_category": "prioritarias",
        "export_formats": ["html", "png", "svg", "pdf"],
    },
    "cross_evidence_manifest": {
        "kind": "manifest",
        "path": CROSS_EVIDENCE_MANIFEST_PATH,
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "artifact_inventory",
        "contract_version": CROSS_EVIDENCE_MANIFEST_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "descriptive_context",
        "acts": [1, 2, 3, 4],
        "privacy": "public_aggregate",
        "inputs": ["cross_evidence.all_engine_outputs"],
    },
    "cross_evidence_manifest_exclusions": {
        "kind": "manifest",
        "path": CROSS_EVIDENCE_EXCLUSIONS_PATH,
        "producer_script": "08_cross_evidence_engine.py",
        "unit_of_analysis": "artifact_inventory",
        "contract_version": CROSS_EVIDENCE_MANIFEST_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "methodological_warning",
        "acts": [1, 2, 3, 4],
        "privacy": "private_no_raw_text",
        "inputs": ["cross_evidence.all_engine_outputs"],
    },
    "artifact_reports": {
        "kind": "report_collection",
        "path": CROSS_EVIDENCE_ARTIFACT_REPORTS_DIR,
        "producer_script": "09_cross_evidence_narrative_reporter.py",
        "unit_of_analysis": "artifact_report",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "descriptive_context",
        "acts": [1, 2, 3, 4],
        "privacy": "public_aggregate_no_raw_text",
        "inputs": ["cross_evidence.cross_evidence_manifest", "cross_evidence.engine_artifacts"],
    },
    "group_reports": {
        "kind": "report_collection",
        "path": CROSS_EVIDENCE_GROUP_REPORTS_DIR,
        "producer_script": "09_cross_evidence_narrative_reporter.py",
        "unit_of_analysis": "evidence_group_report",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "descriptive_context",
        "acts": [1, 2, 3, 4],
        "privacy": "public_aggregate_no_raw_text",
        "inputs": ["cross_evidence.artifact_reports", "cross_evidence.evidence_priority_matrix"],
    },
    "act_reports": {
        "kind": "report_collection",
        "path": CROSS_EVIDENCE_ACT_REPORTS_DIR,
        "producer_script": "09_cross_evidence_narrative_reporter.py",
        "unit_of_analysis": "narrative_act_report",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "descriptive_context",
        "acts": [1, 2, 3, 4],
        "privacy": "public_aggregate_no_raw_text",
        "inputs": ["cross_evidence.artifact_reports", "cross_evidence.group_reports"],
    },
    "cross_evidence_consolidated_report": {
        "kind": "report",
        "path": f"{CROSS_EVIDENCE_REPORTS_DIR}/00_cross_evidence_consolidated_report.md",
        "producer_script": "09_cross_evidence_narrative_reporter.py",
        "unit_of_analysis": "cross_evidence_audit",
        "contract_version": CROSS_EVIDENCE_CONTRACT_VERSION,
        "evidence_scope": CROSS_EVIDENCE_SCOPE,
        "evidence_type": "descriptive_context",
        "acts": [1, 2, 3, 4],
        "privacy": "public_aggregate_no_raw_text",
        "inputs": [
            "cross_evidence.cross_evidence_manifest",
            "cross_evidence.evidence_priority_matrix",
            "cross_evidence.artifact_reports",
            "cross_evidence.group_reports",
            "cross_evidence.act_reports",
        ],
    },
}

CROSS_EVIDENCE_LEGACY_INPUT_REGISTRY: dict[str, dict[str, object]] = {
    "lake.evaluator_team_cuts": {
        "path": "data/lake/evaluator_team_cuts.parquet",
        "metadata_path": "data/lake/evaluator_team_cuts.parquet.metadata.json",
        "kind": "parquet",
        "source_layer": "lake",
        "required": True,
        "status_required": "success",
        "compatibility_policy": CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY,
    },
    "lake.git_commits": {
        "path": "data/lake/git_commits.parquet",
        "metadata_path": "data/lake/git_commits.parquet.metadata.json",
        "kind": "parquet",
        "source_layer": "lake",
        "required": True,
        "status_required": "success",
        "compatibility_policy": CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY,
    },
    "lake.git_files": {
        "path": "data/lake/git_files.parquet",
        "metadata_path": "data/lake/git_files.parquet.metadata.json",
        "kind": "parquet",
        "source_layer": "lake",
        "required": True,
        "status_required": "success",
        "compatibility_policy": CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY,
    },
    "lake.git_repository_snapshots": {
        "path": "data/lake/git_repository_snapshots.parquet",
        "metadata_path": "data/lake/git_repository_snapshots.parquet.metadata.json",
        "kind": "parquet",
        "source_layer": "lake",
        "required": True,
        "status_required": "success",
        "compatibility_policy": CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY,
    },
    "lake.git_team_cuts": {
        "path": "data/lake/git_team_cuts.parquet",
        "metadata_path": "data/lake/git_team_cuts.parquet.metadata.json",
        "kind": "parquet",
        "source_layer": "lake",
        "required": False,
        "status_required": "success",
        "compatibility_policy": CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY,
    },
    "analysis.planning_metrics": {
        "path": "data/analysis/planning_metrics.parquet",
        "metadata_path": "data/analysis/planning_metrics.parquet.metadata.json",
        "kind": "parquet",
        "source_layer": "analysis",
        "required": True,
        "status_required": "success",
        "compatibility_policy": CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY,
    },
    "analysis.code_churn_metrics": {
        "path": "data/analysis/code_churn_metrics.parquet",
        "metadata_path": "data/analysis/code_churn_metrics.parquet.metadata.json",
        "kind": "parquet",
        "source_layer": "analysis",
        "required": True,
        "status_required": "success",
        "compatibility_policy": CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY,
    },
    "analysis.technical_degradation_metrics": {
        "path": "data/analysis/technical_degradation_metrics.parquet",
        "metadata_path": "data/analysis/technical_degradation_metrics.parquet.metadata.json",
        "kind": "parquet",
        "source_layer": "analysis",
        "required": True,
        "status_required": "success",
        "compatibility_policy": CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY,
    },
    "analysis.integration_friction_metrics": {
        "path": "data/analysis/integration_friction_metrics.parquet",
        "metadata_path": "data/analysis/integration_friction_metrics.parquet.metadata.json",
        "kind": "parquet",
        "source_layer": "analysis",
        "required": False,
        "status_required": "success",
        "compatibility_policy": CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY,
    },
    "analysis.team_metrics": {
        "path": "data/analysis/team_metrics.parquet",
        "metadata_path": "data/analysis/team_metrics.parquet.metadata.json",
        "kind": "parquet",
        "source_layer": "analysis",
        "required": True,
        "status_required": "success",
        "compatibility_policy": CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY,
    },
    "analysis.correlation_results": {
        "path": "data/analysis/correlation_results.csv",
        "metadata_path": "data/analysis/correlation_results.csv.metadata.json",
        "kind": "csv",
        "source_layer": "analysis",
        "required": False,
        "status_required": "success",
        "compatibility_policy": CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY,
    },
    "analysis.hypothesis_results": {
        "path": "data/analysis/hypothesis_results.csv",
        "metadata_path": "data/analysis/hypothesis_results.csv.metadata.json",
        "kind": "csv",
        "source_layer": "analysis",
        "required": False,
        "status_required": "success",
        "compatibility_policy": CROSS_EVIDENCE_CURRENT_ARTIFACT_POLICY,
    },
}

ANALYSIS_ARTIFACT_PATH_REGISTRY_VERSION = "analysis-artifact-paths-v1"
ANALYSIS_ARTIFACT_MIGRATION_POLICY = "read_current_else_legacy"
ANALYSIS_ARTIFACT_MIGRATION_STATUS = "planned_not_active"
ANALYSIS_ARTIFACT_PATH_REGISTRY: dict[str, dict[str, object]] = {
    "analysis.planning_metrics": {
        "current_path": "data/analysis/phase2/datasets/planning_metrics.parquet",
        "current_metadata_path": "data/analysis/phase2/datasets/planning_metrics.parquet.metadata.json",
        "current_required": False,
        "legacy_path": "data/analysis/planning_metrics.parquet",
        "legacy_metadata_path": "data/analysis/planning_metrics.parquet.metadata.json",
        "legacy_required": True,
        "kind": "parquet",
        "artifact_group": "datasets",
        "migration_policy": ANALYSIS_ARTIFACT_MIGRATION_POLICY,
        "migration_status": ANALYSIS_ARTIFACT_MIGRATION_STATUS,
        "consumers": ["cross-evidence"],
    },
    "analysis.code_churn_metrics": {
        "current_path": "data/analysis/phase2/datasets/code_churn_metrics.parquet",
        "current_metadata_path": "data/analysis/phase2/datasets/code_churn_metrics.parquet.metadata.json",
        "current_required": False,
        "legacy_path": "data/analysis/code_churn_metrics.parquet",
        "legacy_metadata_path": "data/analysis/code_churn_metrics.parquet.metadata.json",
        "legacy_required": True,
        "kind": "parquet",
        "artifact_group": "datasets",
        "migration_policy": ANALYSIS_ARTIFACT_MIGRATION_POLICY,
        "migration_status": ANALYSIS_ARTIFACT_MIGRATION_STATUS,
        "consumers": ["cross-evidence"],
    },
    "analysis.technical_degradation_metrics": {
        "current_path": "data/analysis/phase2/datasets/technical_degradation_metrics.parquet",
        "current_metadata_path": "data/analysis/phase2/datasets/technical_degradation_metrics.parquet.metadata.json",
        "current_required": False,
        "legacy_path": "data/analysis/technical_degradation_metrics.parquet",
        "legacy_metadata_path": "data/analysis/technical_degradation_metrics.parquet.metadata.json",
        "legacy_required": True,
        "kind": "parquet",
        "artifact_group": "datasets",
        "migration_policy": ANALYSIS_ARTIFACT_MIGRATION_POLICY,
        "migration_status": ANALYSIS_ARTIFACT_MIGRATION_STATUS,
        "consumers": ["cross-evidence"],
    },
    "analysis.integration_friction_metrics": {
        "current_path": "data/analysis/phase2/datasets/integration_friction_metrics.parquet",
        "current_metadata_path": "data/analysis/phase2/datasets/integration_friction_metrics.parquet.metadata.json",
        "current_required": False,
        "legacy_path": "data/analysis/integration_friction_metrics.parquet",
        "legacy_metadata_path": "data/analysis/integration_friction_metrics.parquet.metadata.json",
        "legacy_required": True,
        "kind": "parquet",
        "artifact_group": "datasets",
        "migration_policy": ANALYSIS_ARTIFACT_MIGRATION_POLICY,
        "migration_status": ANALYSIS_ARTIFACT_MIGRATION_STATUS,
        "consumers": ["cross-evidence"],
    },
    "analysis.team_metrics": {
        "current_path": "data/analysis/phase2/datasets/team_metrics.parquet",
        "current_metadata_path": "data/analysis/phase2/datasets/team_metrics.parquet.metadata.json",
        "current_required": False,
        "legacy_path": "data/analysis/team_metrics.parquet",
        "legacy_metadata_path": "data/analysis/team_metrics.parquet.metadata.json",
        "legacy_required": True,
        "kind": "parquet",
        "artifact_group": "datasets",
        "migration_policy": ANALYSIS_ARTIFACT_MIGRATION_POLICY,
        "migration_status": ANALYSIS_ARTIFACT_MIGRATION_STATUS,
        "consumers": ["cross-evidence"],
    },
    "analysis.correlation_results": {
        "current_path": "data/analysis/phase2/results/correlation_results.csv",
        "current_metadata_path": "data/analysis/phase2/results/correlation_results.csv.metadata.json",
        "current_required": False,
        "legacy_path": "data/analysis/correlation_results.csv",
        "legacy_metadata_path": "data/analysis/correlation_results.csv.metadata.json",
        "legacy_required": True,
        "kind": "csv",
        "artifact_group": "results",
        "migration_policy": ANALYSIS_ARTIFACT_MIGRATION_POLICY,
        "migration_status": ANALYSIS_ARTIFACT_MIGRATION_STATUS,
        "consumers": ["cross-evidence"],
    },
    "analysis.hypothesis_results": {
        "current_path": "data/analysis/phase2/results/hypothesis_results.csv",
        "current_metadata_path": "data/analysis/phase2/results/hypothesis_results.csv.metadata.json",
        "current_required": False,
        "legacy_path": "data/analysis/hypothesis_results.csv",
        "legacy_metadata_path": "data/analysis/hypothesis_results.csv.metadata.json",
        "legacy_required": True,
        "kind": "csv",
        "artifact_group": "results",
        "migration_policy": ANALYSIS_ARTIFACT_MIGRATION_POLICY,
        "migration_status": ANALYSIS_ARTIFACT_MIGRATION_STATUS,
        "consumers": ["cross-evidence"],
    },
}
