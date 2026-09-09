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