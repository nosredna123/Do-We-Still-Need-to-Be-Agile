"""Centralized prompts for the paper signal extraction tasks."""

from __future__ import annotations


PROMPTS = {
    "planning": """Evaluate the planning quality reflected in these T1 commit messages.
Score the evidence from 1 (no meaningful planning) to 10 (clear, specific, and coherent planning).
Judge only the supplied text. Do not infer missing evidence.
Return only valid JSON in exactly this form:
{"t1_planning_score": <integer from 1 to 10>}""",
    "cohort_coordination_friction": """Evaluate the level of coordination friction reflected in this cohort transcript block.
Score the evidence from 1 (little or no coordination friction) to 10 (severe, repeated coordination friction).
Consider blockers, misunderstandings, handoff problems, merge or integration conflicts, and repeated coordination overhead.
Judge only the supplied text. Do not infer missing evidence.
Return only valid JSON in exactly this form:
{"coordination_friction": <integer from 1 to 10>}""",
}


def get_prompt(task_type: str) -> str:
    """Return the prompt for a supported LLM task."""
    try:
        return PROMPTS[task_type]
    except KeyError as exc:
        supported = ", ".join(sorted(PROMPTS))
        raise ValueError(f"Unsupported LLM task {task_type!r}; expected one of: {supported}") from exc
