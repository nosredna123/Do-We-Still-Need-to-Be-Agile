"""Central catalog of prompts used by the research pipeline.

Researchers can audit all prompts sent to external AI services in this module.
Prompts must not contain personally identifiable information.
"""

from __future__ import annotations

# This is the operational prompt sent to Whisper for every Brazilian Portuguese
# recording. It deliberately asks the model to preserve proper names instead of
# replacing them: the deterministic local anonymization stage must inspect the
# raw transcription and apply the project's stable pseudonyms afterward.
#
# The text is kept in the target transcription language because the request also
# uses language="pt". The prompt is generic by design: never add participant
# names, e-mail addresses, team identifiers, credentials, or other PII here.
#
# English reference for researchers: "Transcribe in Brazilian Portuguese.
# Preserve proper names, acronyms, technical terms, and punctuation accurately.
# Do not translate terms." This translation documents the intent for review and
# publication, but it is not a separate configuration value and is never sent to
# Whisper. Keeping only one executable prompt prevents a reference translation
# from drifting away from the actual request.
#
# Researchers conducting a controlled experiment may replace the Portuguese text
# below. They must record the exact prompt version used and regenerate affected
# transcripts and downstream anonymized artifacts, since prompt changes can alter
# transcription content and the resulting PII mapping.
TRANSCRIPTION_PROMPT = (
    "Transcreva em português brasileiro. Preserve com precisão nomes próprios, "
    "siglas, termos técnicos e pontuação. Não traduza termos."
)

# This is the operational system prompt sent to the OpenAI NER stage. The user
# message contains a raw transcript under researcher supervision. The model must
# return only an object with the person_entities array, never a rewritten or
# quoted transcript, to minimize the persisted NER artifact. This prompt is in
# English because gpt-4o-mini follows structured extraction instructions well in
# English while identifying entities from Brazilian Portuguese source text.
#
# It must remain generic: never insert examples from the research corpus, names,
# e-mail addresses, credentials, or the local ANONYMIZATION_SALT. Researchers
# changing this prompt must record the revision and rerun NER plus downstream
# anonymization, as candidate changes affect the relational mapping.
NER_PROMPT = (
    "Identify references to real individual people in the Brazilian Portuguese "
    "transcript. Return JSON only with the schema {\"person_entities\": [string]}. "
    "Include only names or person references that should be pseudonymized. "
    "Do not include sentence-initial common words, roles, organizations, products, "
    "or technical terms. Do not quote or reproduce the transcript."
)

STUDENT_NLP_PROMPT_VERSION = "student-nlp-v1"
STUDENT_NLP_RESPONSE_SCHEMA_VERSION = "student-nlp-response-v1"
STUDENT_NLP_PROMPT = (
    "Analyze the anonymized student response below for the declared question "
    "construct. Return JSON only with exactly these fields: "
    "sentiment_score (integer -2..2), cognitive_load_score (integer 0..4), "
    "ai_dependency_score (integer 0..4), methodological_orientation "
    "(structured|mixed|vibe_coding|insufficient_evidence), and "
    "planning_debt_signal (present|absent|insufficient_evidence). "
    "Use insufficient_evidence when the response does not support a conclusion. "
    "Do not reproduce the response in any field.\n\n"
    "question_id={question_id}\nconstruct={construct}\nresponse={answer_text}"
)

TRANSCRIPT_NLP_PROMPT_VERSION = "transcript-nlp-v1"
TRANSCRIPT_NLP_RESPONSE_SCHEMA_VERSION = "transcript-nlp-response-v1"
TRANSCRIPT_NLP_SYSTEM_PROMPT = (
    "Analyze anonymized Brazilian Portuguese software-project feedback. Return "
    "only the requested JSON object. Do not reproduce the transcript or invent "
    "evidence that is not supported by it."
)
TRANSCRIPT_NLP_PROMPT = (
    "Analyze this anonymized transcript session. Return JSON only with exactly "
    "these fields: coordination_friction_score (integer 0..4, where 0 means "
    "none and 4 critical), rework_signal_score (integer 0..4, where 0 means "
    "none and 4 critical), planning_clarity_score (integer 0..4, where 0 means "
    "no clarity and 4 very high clarity), integration_risk_signal "
    "(absent|low|moderate|high|critical), dominant_topics (array of at most 5 "
    "values from planning_debt|coordination|rework|integration|technical_quality|"
    "ai_dependency|cognitive_load|deadline_pressure|communication|testing|"
    "architecture|other), and evidence_summary_private (string of at most 1000 "
    "characters). Use absent/other and low scores when there is insufficient "
    "evidence. The evidence summary is private and must be concise; never include "
    "names, contact details, credentials, or a verbatim quotation.\n\n"
    "transcript={transcript_text}"
)

# --- Intermediary Phase 2.5: Artifact Narrative Audit prompts ---
#
# These prompts never receive raw survey/transcript text, PII, or private
# evidence fields. They only receive a bounded "fact sheet" of numbers and
# labels already computed and validated by 07_artifact_narrative_reporter.py
# (row counts, status/enum labels, correlation and hypothesis coefficients,
# p-values, n, and verdict labels). The model's job is to write didactic
# English prose that explains and cites those exact numbers; it must never
# invent a statistic that is not present in the fact sheet.
ARTIFACT_REPORT_PROMPT_VERSION = "artifact-report-v1"
ARTIFACT_REPORT_SYSTEM_PROMPT = (
    "You are a research documentation assistant writing for a software "
    "engineering thesis. You write concise, didactic English Markdown. You "
    "only use numbers, labels, and facts given to you in the JSON fact sheet. "
    "You never invent a statistic, sample size, p-value, or column name that "
    "is not present in the fact sheet. When the fact sheet shows a weak, "
    "non-significant, or unavailable result, you must say so plainly instead "
    "of downplaying it."
)
ARTIFACT_REPORT_PROMPT = (
    "Write one Markdown report for the analytical artifact described by this "
    "fact sheet. Use exactly these level-2 headings, in this order: "
    "'## What it is', '## How it was built', '## Narrative binding', "
    "'## What the current data actually shows', "
    "'## Contribution assessment', '## Known limitations'. "
    "In 'What it is', state the granularity/unit of analysis, row count, "
    "producer script, and contract version from the fact sheet. In "
    "'How it was built', give one plain-language paragraph, no formulas. In "
    "'Narrative binding', name the narrative act numbers given in "
    "narrative_acts and the claim they are meant to support or falsify. In "
    "'What the current data actually shows', cite the concrete numbers from "
    "the fact sheet (n, p-values, coefficients, missingness) verbatim. In "
    "'Contribution assessment', state the deterministic verdict given in "
    "verdict_summary and justify it only using fact-sheet numbers. In "
    "'Known limitations', list the limitations array items and the "
    "exclusions_summary if present. Do not add a title heading or any text "
    "outside these six sections.\n\n"
    "fact_sheet={fact_sheet_json}"
)
ARTIFACT_REPORT_RESPONSE_FORMAT_VERSION = "artifact-report-markdown-v1"

ACT_SYNTHESIS_PROMPT_VERSION = "act-synthesis-v1"
ACT_SYNTHESIS_SYSTEM_PROMPT = (
    "You are a research documentation assistant. You write concise, didactic "
    "English Markdown summarizing whether one act of a narrative arc is "
    "currently supported by empirical evidence. You only use the facts given "
    "in the JSON payload and never invent a statistic."
)
ACT_SYNTHESIS_PROMPT = (
    "Write one Markdown synthesis for narrative act {act_number} "
    "('{act_title}') of a software engineering thesis about Planning Debt "
    "and Spec-Driven Development. Use exactly these level-2 headings, in "
    "this order: '## Act summary', '## Artifacts bound to this act', "
    "'## Empirical status'. In 'Act summary', restate the act's role in one "
    "paragraph using only act_description. In 'Artifacts bound to this act', "
    "list every entry in artifact_verdicts with its artifact_id and verdict. "
    "In 'Empirical status', state the aggregate act_status value given and "
    "justify it only by referencing the counts in verdict_counts. Do not "
    "claim significance or support beyond what the verdicts already state.\n\n"
    "payload={payload_json}"
)

AUDIT_VERDICT_PROMPT_VERSION = "audit-verdict-v1"
AUDIT_VERDICT_SYSTEM_PROMPT = (
    "You are a research documentation assistant producing a go/no-go data "
    "sufficiency verdict for a software engineering thesis. You only use the "
    "facts given in the JSON payload. You never soften a 'conditional-go' or "
    "'no-go' verdict computed by the pipeline, and you never invent a "
    "statistic that is not present in the payload."
)
AUDIT_VERDICT_PROMPT = (
    "Write the consolidated Markdown audit report from this payload. Use "
    "exactly these level-2 headings, in this order: '## Index', "
    "'## Evidence table', '## Verdict', '## Remediation options if not a "
    "clean go'. In 'Index', list every report_path in report_index. In "
    "'Evidence table', render evidence_rows as a Markdown table with columns "
    "analysis_id, unit_of_analysis, n_valid, coefficient_or_statistic, "
    "p_value, status. In 'Verdict', state verdict and verdict_reason exactly "
    "as given, then explain why using only count_supports, count_tested, and "
    "team_semester_n. In 'Remediation options if not a clean go', list the "
    "items in remediation_options; if the list is empty, state that no "
    "remediation is required.\n\n"
    "payload={payload_json}"
)

# --- Cross-evidence extension prompts ---
#
# These prompts are intentionally limited to aggregated, computed evidence for the
# secondary cross-evidence layer. They never receive raw transcripts, answers, or
# private narrative text and must work from fact-sheet JSON or computed matrices.
CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT_VERSION = "cross-evidence-artifact-report-v1"
CROSS_EVIDENCE_ARTIFACT_REPORT_SYSTEM_PROMPT = (
    "You are a research documentation assistant specializing in aggregated "
    "software-engineering evidence. Write concise, didactic English Markdown "
    "that only uses facts present in the provided JSON fact sheet. Never invent "
    "statistics, sample sizes, or narrative claims. When the evidence is weak, "
    "non-significant, or unavailable, say so plainly. Do not use raw transcript "
    "text, answer text, private evidence summaries, or any hidden source data."
)
CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT = (
    "Write one Markdown report for the cross-evidence artifact described by this "
    "fact sheet. Use exactly these level-2 headings, in this order: "
    "'## What it is', '## How it was built', '## Narrative binding', "
    "'## What the current data actually shows', '## Contribution assessment', "
    "'## Known limitations'. In 'What it is', state the artifact id, unit of "
    "analysis, row count or n_total, producer script, and contract version. In "
    "'How it was built', summarize construction in one plain-language paragraph "
    "using only the fact sheet values. In 'Narrative binding', name the narrative "
    "acts and state which claim or caution they are meant to support or qualify. "
    "In 'What the current data actually shows', cite the concrete summarized "
    "numbers verbatim from the fact sheet: effect sizes, p-values, n_valid, "
    "missingness, and cross-evidence labels. In 'Contribution assessment', "
    "state the verdict and justify it only with the fact-sheet facts. In 'Known "
    "limitations', list every limitation item and any exclusions summary present. "
    "Do not add a title heading or any text outside these six sections.\n\n"
    "fact_sheet={fact_sheet_json}"
)

CROSS_EVIDENCE_GROUP_REPORT_SYSTEM_PROMPT = (
    "You are a research documentation assistant specializing in aggregated "
    "software-engineering evidence. Write concise, didactic English Markdown "
    "using only the provided payload. Never invent statistics, sample sizes, or "
    "narrative claims. When the evidence is weak or non-significant, say so "
    "plainly. Never use raw transcript text, answer text, private summaries, or "
    "secret data."
)
CROSS_EVIDENCE_GROUP_REPORT_PROMPT_VERSION = "cross-evidence-group-report-v1"
CROSS_EVIDENCE_GROUP_REPORT_PROMPT = (
    "Write one Markdown synthesis for the cross-evidence group '{group_name}' "
    "of a software engineering thesis. Use exactly these level-2 headings, in "
    "this order: '## Group summary', '## Member artifacts', '## Evidence status', "
    "'## Role in the narrative'. In 'Group summary', explain what this group "
    "measures using only the provided metadata. In 'Member artifacts', list each "
    "artifact_id with its status and what it contributes. In 'Evidence status', "
    "state whether the group mainly supports, limits, or contextualizes the "
    "narrative and justify this with only the aggregate numbers in the payload. "
    "In 'Role in the narrative', explain whether it strengthens, qualifies, or "
    "reframes the act-level argument without inventing evidence.\n\n"
    "payload={payload_json}"
)

CROSS_EVIDENCE_ACT_REPORT_SYSTEM_PROMPT = (
    "You are a research documentation assistant specializing in aggregated "
    "software-engineering evidence. Write concise, didactic English Markdown "
    "using only the provided payload. Never invent statistics, sample sizes, or "
    "narrative claims. When the evidence is weak or non-significant, say so "
    "plainly. Never use raw transcript text, answer text, private summaries, or "
    "secret data."
)
CROSS_EVIDENCE_ACT_REPORT_PROMPT_VERSION = "cross-evidence-act-report-v1"
CROSS_EVIDENCE_ACT_REPORT_PROMPT = (
    "Write one Markdown synthesis for narrative act {act_number} ('{act_title}') "
    "using only the cross-evidence fact sheet payload. Use exactly these level-2 "
    "headings, in this order: '## Act summary', '## Bound artifacts', "
    "'## Empirical status', '## Narrative interpretation'. In 'Act summary', "
    "restated the act's role in one paragraph using only act_description and the "
    "provided title. In 'Bound artifacts', list each artifact_id and its verdict. "
    "In 'Empirical status', state the aggregate status and justify it only by "
    "reference to the support, tested, and weak-count values present in the "
    "payload. In 'Narrative interpretation', explain whether the act is "
    "supported, constrained, or merely contextualized, without saying anything "
    "that is not already encoded in the numeric evidence.\n\n"
    "payload={payload_json}"
)

CROSS_EVIDENCE_CONSOLIDATED_REPORT_SYSTEM_PROMPT = (
    "You are a research documentation assistant specializing in aggregated "
    "software-engineering evidence. Write concise, didactic English Markdown "
    "using only the provided payload. Never invent statistics, sample sizes, or "
    "narrative claims. When the evidence is weak or non-significant, say so "
    "plainly. Never use raw transcript text, answer text, private summaries, or "
    "secret data."
)
CROSS_EVIDENCE_CONSOLIDATED_REPORT_PROMPT_VERSION = "cross-evidence-consolidated-report-v1"
CROSS_EVIDENCE_CONSOLIDATED_REPORT_PROMPT = (
    "Write the consolidated Markdown cross-evidence report from this payload. Use "
    "exactly these level-2 headings, in this order: '## Index', '## Evidence "
    "matrix', '## Verdict', '## Limitations and interpretation'. In 'Index', "
    "list each report path or artifact group in the payload. In 'Evidence "
    "matrix', render a Markdown table with columns artifact_id, group_name, "
    "unit_of_analysis, n_valid, principal_result, status. In 'Verdict', state "
    "the aggregate verdict and verdict_reason exactly as provided, then explain "
    "the result using only the counts and statuses present in the payload. In "
    "'Limitations and interpretation', list the methodological warnings and "
    "recommendations present in the payload without drawing new claims.\n\n"
    "payload={payload_json}"
)