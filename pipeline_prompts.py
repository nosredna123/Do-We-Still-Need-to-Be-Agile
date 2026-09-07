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