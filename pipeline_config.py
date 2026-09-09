"""Versioned research-protocol configuration for the data pipeline.

This module contains non-secret, version-controlled decisions that determine
how raw research inputs are interpreted. It must not contain PII, credentials,
or raw data values.
"""

from __future__ import annotations

from datetime import date


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
EXCLUDED_PATH_PATTERNS_VERSION = "source-exclusions-v1"
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
    ".next/",
    ".venv/",
    "build/",
    "coverage/",
    "dist/",
    "node_modules/",
    "target/",
    "vendor/",
}

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
STATISTICAL_ANALYSIS_REGISTRY = {
    "pi_vs_cc_primary": {"unit_of_analysis": "team_semester", "x": "pi_file_count_t1", "y": "cc_per_source_loc_t3", "test": "spearman", "priority": "primary", "figure": "pi_vs_cc.png"},
    "pi_vs_delta_dt_primary": {"unit_of_analysis": "team_semester", "x": "pi_file_count_t1", "y": "delta_dt_t1_t3", "test": "spearman", "priority": "primary", "figure": None},
    "ai_vs_cc_primary": {"unit_of_analysis": "team_semester", "x": "ai_max_author_share_48h_before_t3", "y": "cc_total_t3", "test": "spearman", "priority": "primary", "figure": "ai_before_t3.png"},
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
