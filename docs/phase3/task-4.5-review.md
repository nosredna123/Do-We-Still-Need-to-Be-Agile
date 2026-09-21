# Task 4.5: Consistency and page-budget review

**Review date:** 2026-09-21

**Status:** pre-submission preflight complete; venue-template pagination and authoritative bibliography verification remain pending.

## Automated checks

| check | result | evidence |
| --- | --- | --- |
| manuscript draft sections present | pass | `manuscript-introduction.md`, `manuscript-method.md`, `manuscript-results.md`, `manuscript-discussion.md` |
| local Markdown links | pass | 0 missing links across the five manuscript/outline drafts |
| citation keys used by drafts | pass | all cited keys resolve in `references.bib` |
| reference matrix keys | pass | all 14 reference-matrix rows resolve in `references.bib` |
| claim control | pass | seven claims (`CLAIM-01` through `CLAIM-07`) remain represented in the package |
| null/unavailable visibility | pass | all five manuscript drafts contain null or unavailable evidence language |
| figure captions | pass | six plot-book caption drafts, all with an `n`/denominator mention |
| evidence boundary | pass | introduction, results, discussion, and outline retain the `conditional-go` boundary; Method records the same boundary through its statistical and availability contracts |
| Phase 2 immutability | pass | no tracked Phase 2 files changed during Phase 3/4 drafting |
| identifying metadata preflight | pass | no repository URLs, email addresses, or author-name metadata found in paper-facing drafts |

## Draft package size

The five manuscript/outline drafts contain approximately 8,258 words before IEEE formatting, references, figures, tables, and captions. This is a drafting estimate, not a page count.

The workspace contains no IEEE conference template or SEET-specific `.tex`, `.cls`, or `.docx` template. Files with those extensions are embedded raw/repository artifacts and were not used for pagination. The 10-page paper plus reference-page budget must therefore be checked after obtaining the current venue template.

## Manual gates still required

- Verify each bibliography entry against an authoritative publication record. In particular, confirm title, authors, venue, year, DOI, and whether recent contextual references are real and appropriate for the target venue.
- Format the four section drafts in the current IEEE/SEET template and measure the actual page count.
- Check figure legibility at final two-column size, including axis labels, legends, caption text, and the unit/`n` statement.
- Run the final privacy and double-anonymous review across the formatted manuscript, figure metadata, repository history, supplementary files, and external artifact links.
- Confirm the current SEET call, page limit, reference limit, data-availability wording, and submission deadline immediately before submission.

## Consistency decisions

- The original four acts remain an organizing device, not four empirically proven stages.
- The primary boundary remains team-semester `n = 14`, five primary analyses, no significant primary result, and `conditional-go`.
- Cross-evidence remains secondary exploratory triangulation; `supports` labels do not override the primary audit.
- SDD/BDUF remains a proposed methodological direction, not a demonstrated superior or unique solution.
- Results, unavailable analyses, exclusions, and robustness checks remain visible in the manuscript rather than being moved exclusively to limitations.

## Candidate manuscript inputs

- [Introduction](manuscript-introduction.md)
- [Method](manuscript-method.md)
- [Results](manuscript-results.md)
- [Discussion, Threats, Conclusion, and Data Availability](manuscript-discussion.md)
- [Full manuscript outline](manuscript-outline.md)
- [References](references.bib)
- [Threats to validity](threats_to_validity.md)
