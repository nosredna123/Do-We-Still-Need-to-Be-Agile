# Editorial Plan: Consolidating Threats to Validity

## Purpose

Remove repetitive methodological and causal caveats from paper-facing sections while preserving the precise qualifier needed where a result could otherwise be misunderstood. `Threats to Validity` becomes the main location for the complete limitations argument; other sections retain only local interpretation boundaries. Changes must alter the text and structure as little as possible.

This is an editorial consolidation, not a change to the study design, metrics, results, or claims. No substantive information may be removed: only genuinely redundant wording may be shortened or consolidated, and every non-redundant qualification, result, definition, and scope boundary must remain available to the reader.

## Governing Rules

1. State each general threat fully in `Threats to Validity`.
2. In `Methodology`, define measurement boundaries once, where they are necessary to understand an operationalization.
3. In `Results`, report the result and its local unit, scale, denominator, and unavailable state. Do not repeat the full limitation rationale.
4. In `Discussion`, interpret the evidence and refer back to `Threats to Validity` when discussing generalization, causality, proxy validity, or missingness.
5. In `Conclusion`, avoid reopening limitations already consolidated in `Threats to Validity`; retain only the final scope of the contribution.
6. Keep invisible provenance comments unchanged or improve them only when needed for traceability. Internal identifiers may remain in comments but not in reader-facing prose.
7. Never remove a qualifier that prevents a materially misleading interpretation of a nearby number. Short local qualifiers are allowed when they are inseparable from the result.
8. Do not use transition history, internal version history, conversion history, or pipeline-development language in article prose.
9. Make the smallest possible textual and structural change needed to remove duplication. Preserve paragraph order, headings, argument flow, references, examples, quantitative details, and reader-facing qualifications unless a change is strictly necessary for consolidation.
10. Do not remove information merely because it is a limitation. Information may be relocated or lightly condensed only when its complete meaning remains represented in the canonical section and its local context remains accurate.
11. Treat each section as a separate editing session. After editing a section, perform a final coherence review of that section in context, record the changes and the coherence check in a report, and stop for user authorization before proceeding to the next section.

## Canonical Threat Inventory

These topics should receive their complete treatment in `Threats to Validity`:

- Construct validity of self-reported M1/M2 measures and lack of behavioral AI telemetry.
- Construct validity of M6a structural artifact measures and M6b textual extraction.
- M8 path provenance as a rework proxy rather than semantic defect or intent detection.
- M5 lexical markers as candidate textual evidence rather than direct friction measurement.
- Observational design and the non-causal interpretation of M9.
- Small sample size, influential team-semesters, and leave-one-out sensitivity.
- Incompatible analytical grains and denominators.
- Missing T1 subjects, repository absence, and off-repository planning/collaboration.
- Transcript coverage limited to 2025.2.
- Overlapping rolling windows.
- Educational setting and external-validity boundaries.
- Exploratory status of M6b and use of human review.

## Section-by-Section Review Queue

### Methodology

**Keep locally:**

- Exact unit of analysis, scale, transformation, and missingness rule needed to reproduce each metric.
- A concise statement that a metric is descriptive when that is part of its definition.
- The M8 statement that path provenance is not semantic defect validation.
- The M5 statement that chunks are provenance units, not independent observations.
- The M6b statement that structured categories are exploratory and non-composite.

**Consolidate into Threats:**

- Repeated general warnings about causal interpretation.
- Repeated explanations that Git cannot observe off-repository planning.
- Repeated broad discussions of self-report limitations.
- Repeated descriptions of small sample and influence limitations.
- Repeated prose explaining all missingness consequences beyond the local operational rule.

**Check:**

- Each M1-M9 definition remains understandable after deleting duplicated caveats.
- Methodology still states the exact transformation and analytical grain.

### Results

**Keep locally:**

- Denominators, scales, `mean +/- SD`, medians/IQRs, ranges, and checkpoint/stratum labels.
- The minimal qualifier needed to distinguish a proxy from a direct measure in the same sentence as the result.
- Explicit statements that a missing case was not measured when necessary to interpret a reported count.

**Consolidate into Threats:**

- Full explanations of why a proxy is imperfect.
- Repeated declarations that a result is not causal or not confirmatory after every paragraph.
- Repeated generalization warnings already stated in the dedicated section.
- Repeated explanations of overlapping windows and transcript coverage.

**Check:**

- Every quantitative claim remains interpretable without importing a misleading meaning.
- Results remain focused on what was observed rather than why every inference is limited.

### Discussion

**Keep locally:**

- Interpretation of the specific evidence pattern.
- A concise reminder when moving from observed association to broader implication.
- The explicit statement that SDD is a proposed, testable intervention rather than a tested effect.

**Consolidate into Threats:**

- Repeated inventory of all data limitations.
- Repeated descriptions of every M1-M9 measurement boundary.
- Repeated discussion of all missingness and coverage gaps.

**Check:**

- Discussion advances interpretation instead of repeating Results or Threats.
- SDD claims remain clearly bounded without making the section defensive or repetitive.

### Threats to Validity

This section is the canonical home for the complete limitations argument. Keep it concise but comprehensive. It should explain how the threats affect interpretation, not merely list them.

**Check:**

- Every major threat from the inventory appears here.
- No threat is introduced here for the first time in a way that changes a prior result.
- The section does not mention internal conversion/version history.

### Conclusion

**Keep locally:**

- The positive contribution and the bounded SDD proposition.
- One concise sentence distinguishing a testable implication from an established causal result.

**Remove or avoid:**

- Repetition of the full Threats inventory.
- Repetition of sample size, coverage, proxy, and missingness details unless essential to the final claim.

**Check:**

- Conclusion ends with contribution and future testability, not a second limitations section.

### Introduction

**Keep locally:**

- The motivation and research gap.
- A concise framing that the study is observational if needed to prevent an overclaim in the opening argument.

**Remove or avoid:**

- Detailed limitations before the reader has seen the design and results.
- Repetition of M1-M9 caveats.

**Check:**

- Introduction creates curiosity and accurately previews the study without becoming defensive.

### Background and Related Work

**Keep locally:**

- Literature-based qualifications that define the research gap.
- The distinction between SDD as a process proposition and SDD efficacy as an open empirical question.

**Remove or avoid:**

- Study-specific limitations that belong in Threats to Validity.
- Repeated caveats about this dataset or these team-semesters.

**Check:**

- Background motivates the study and does not read like a second limitations section.

### Abstract

Review as a dedicated section, after the substantive sections are stable. The Abstract currently contains several validity alerts that are unnecessary and redundant at that level; consolidate them with the smallest possible wording change while preserving the study design, scope, contribution, and any qualifier needed to prevent an overclaim.

**Keep locally:**

- A compact design qualifier such as `descriptive and exploratory study` if needed.
- The contribution, principal findings, scope, and essential design boundary.

**Remove or consolidate:**

- Repeated validity alerts that duplicate the detailed `Threats to Validity` discussion.
- Detailed threat inventory, proxy explanations, missingness consequences, or generalization caveats that cannot be understood or acted on at Abstract length.

**Check:**

- The abstract reports the contribution and scope without repeating caveats from Threats.
- No substantive information has been lost; only redundant validity wording has been shortened or consolidated.
- The Abstract remains coherent on its own and does not imply stronger validity, causality, or generalization than the paper supports.

## Editing Procedure

For each section, in the order approved by the user:

1. Mark every sentence that describes a limitation, causal boundary, missingness condition, proxy boundary, or generalization threat.
2. Classify it as `operational definition`, `local qualifier`, or `general threat`.
3. Keep operational definitions in Methodology.
4. Keep only the shortest local qualifier needed beside a result in Results/Discussion.
5. Move general threats to `Threats to Validity` or delete duplicate wording if already covered there.
6. Apply the smallest possible edit, preserving the section's existing structure and all non-redundant information.
7. Recompile the PDF and inspect the affected pages.
8. Run a terminology search for duplicated threat phrases.
9. Perform a final section-level coherence review, checking transitions, references, claims, qualifiers, and consistency with the unchanged sections.
10. Report the exact changes made, information preserved, validation performed, and confirmation that the section remained coherent.
11. Wait for the user's authorization before beginning the next section.

### Session-by-Session Approval Protocol

No multi-section batch edit is allowed. Each editing session must end with:

- the section edited;
- the minimal changes made, with locations identified;
- duplicated wording consolidated or removed;
- information and qualifications explicitly confirmed as preserved;
- PDF, terminology, and section-level coherence checks performed;
- a short report delivered to the user;
- an explicit request for authorization to continue.

The next section may be edited only after the user's authorization. If the coherence review finds an ambiguity, contradiction, broken transition, altered scope, or possible information loss, repair that same section and repeat the coherence review before requesting authorization.

## Review Log

| Section | Reviewed | Duplicates removed/consolidated | Local qualifiers retained | Validation | Approval |
|---|---:|---|---|---|---|
| Methodology | [x] | Removed the repeated general causal/observability caveat from the statistical overview; softened the repository "single source of truth" wording without changing the collection protocol. | Metric grains, scales, transformations, missingness rules, proxy boundaries, and quantitative details retained. | PDF rebuilt; no undefined references or overfull boxes; final coherence review completed. | Pending user authorization |
| Results | [x] | Consolidated repeated causal, population-level, generalization, and proxy-validity caveats while retaining local evidence-stream, sensitivity-summary, scale, denominator, coverage, and proxy qualifiers. | Quantitative results, units, denominators, cohort/checkpoint labels, missingness states, and local interpretation boundaries retained. | PDF rebuilt after clearing stale generated auxiliaries; no fatal errors, undefined references, or overfull boxes; final coherence review completed. | Pending user authorization |
| Discussion | [ ] |  |  |  |  |
| Threats to Validity | [ ] |  |  |  |  |
| Conclusion | [ ] |  |  |  |  |
| Introduction | [ ] |  |  |  |  |
| Background and Related Work | [ ] |  |  |  |  |
| Abstract | [ ] |  |  |  |  |

## Validation Checklist

- [ ] No general threat is repeated verbatim across multiple paper sections.
- [ ] Results retain denominators, units, scales, and local missingness information.
- [ ] Methodology retains operational definitions and exact measurement boundaries.
- [ ] Discussion contains interpretation rather than a second threat inventory.
- [ ] Conclusion remains contribution-focused.
- [ ] Abstract remains concise and does not duplicate Threats to Validity.
- [ ] Changes are minimal and preserve the existing text structure wherever possible.
- [ ] No substantive information, result, definition, qualifier, or scope boundary was removed.
- [ ] Each section received its own final coherence review after editing.
- [ ] A change report and coherence confirmation were delivered before requesting authorization for the next section.
- [ ] No subsequent section was edited without the user's authorization.
- [ ] All reader-facing text remains in technical English.
- [ ] PDF compiles without overfull boxes or undefined citations.
- [ ] Full test suite remains green where executable validation is applicable.
