# Anonymous Research Data Explorer: Implementation Plan

## 1. Purpose and agreed scope

Build a small, English-language companion to the submitted paper. Researchers
should be able to find the evidence behind a research question, inspect its
measures, compare compatible observations, and download approved data without
working directly with the research pipeline.

This document tracks implementation work; it does not approve any dataset for
release. Completed tasks are checked only after their stated scope is verified.

### Decisions agreed during clarification

- Use a fully static site: HTML, CSS, JavaScript, and bundled data.
- Keep this plan and every browser-site source file inside `microsite/`; private authoring is outside it.
- Make the entire directory independently deployable by copying it to an ordinary
  static web server, at either a domain root or a subdirectory.
- Require no backend, database, account, package installation, build step, or
  research pipeline at serving time.
- Cover the submitted paper's measures and supporting datasets, not every
  pipeline output or every exploratory artifact in the repository.
- Provide research-question navigation, evidence-source browsing, filtering,
  sorting, metric explanations, interactive paper figures, valid comparisons,
  and approved dataset/filtered-result downloads.
- Include qualitative excerpts only after individual human review. Omit that
  view if no excerpts are approved; retain approved aggregate qualitative data.
- Preserve strict double-blind author anonymity and participant confidentiality.
- Allow one locally bundled chart library if needed, with its license retained.
- Keep the interface simple and user-friendly rather than building an analysis
  workbench.

### Explicit non-goals

No live pipeline connection, user uploads, user accounts, server-side search,
arbitrary joins, new statistical analyses, AI assistant, telemetry, external
fonts, CDN requests, automated updates, or hosting-provider-specific deployment
machinery. No requirement to work through a `file://` URL: preview and deployment
use HTTP(S). No frontend framework, router, or package manager unless a later
requirement genuinely demands one.

## 2. Requirements

| ID | Requirement |
|---|---|
| REQ-001 | One self-contained, copyable directory with relative asset/data links and no runtime dependency outside it. |
| REQ-002 | Plain static implementation and a small, English, accessible interface. |
| REQ-003 | Browse the submitted paper by RQ1-RQ3, evidence source, and metric families M1-M9. |
| REQ-004 | Filter, sort, inspect, and compare data only at its documented analytical grain. |
| REQ-005 | Explain definitions, units, denominators, coverage, missingness, provenance, and interpretation limits. |
| REQ-006 | Offer interactive counterparts of the submitted paper's figures without changing their statistical meaning. |
| REQ-007 | Download approved full datasets and the currently filtered rows. |
| REQ-008 | Publish only explicitly approved fields and individually approved excerpts; protect participants and double-blind anonymity. |
| REQ-009 | Freeze a paper-aligned snapshot with reproducible public provenance and explicit release gates. |

## 3. Frozen public scope and verification boundaries

The neutral snapshot is `research-data-001`, schema `1.0`, with status
`snapshot_prepared_release_pending`. Its [catalog](data/catalog.json) describes
49 datasets, 510 columns, seven figures, and embedded definition-only rows.
The 49 JSON/CSV pairs preserve 1,674 rows and 17,046 scalar cells per format.
The [release manifest](data/release.json) checks 99 public artifacts.
Public dataset IDs, units, grain, valid keys and filters are documented in
[public dataset contracts](dataset-contracts.md).

T001-T009 reconciled the paper-aligned inventory, obtained explicit private
field/value approval and an all-excerpts-omitted decision, and verified exact
source reproduction and public serialization. Original source paths, filenames,
column mappings, private input fingerprints, and approval records are not public
provenance and are retained outside this directory.

T010-T020 verified the semantic, responsive interface, all dataset tables,
grain-aware selection, seven exact figures, faithful downloads, and researcher
reuse guidance. T021 audited all 25 acceptance checks: 20 local passes and five
publication checks not passed. T022 verified an unchanged 125-file candidate on
a read-only independent static server at root and nested prefixes in two browsers,
including 808 completed disk downloads. These are historical candidate results,
not approval of a subsequently changed directory or actual public host.

T023 reviewed and sanitized every shipped file, including unlinked tools,
documentation and vendor notices. The exact approved observations, catalog,
release manifest, runtime assets and required upstream license remain unchanged.
Source preparation is retained outside the publication directory; public
validation tooling imports only public definitions and local public files.
An authorized human explicitly approved the complete sanitized candidate,
accepted the stated residual linkage/anonymity risks, and permitted status-only
completion updates. Automated checks cannot prove anonymity; substantive changes
require renewed review. T024 and T025 are complete; the host was accepted
with the explicit Netlify branding/icon exceptions recorded in T025. T026
remains required to record the verified URL and snapshot before paper citation.

## 4. Smallest useful design

### Three views in one page

1. **Overview:** short orientation, RQ1-RQ3 cards, evidence coverage, and a visible
   explanation that these are descriptive/exploratory observations.
2. **Explore:** choose a research question and metric/evidence dataset; see a short
   explanation, applicable filters, an interactive figure where relevant, a
   sortable table, and download actions.
3. **Measures and methods:** searchable definitions, scales, eligibility,
   provenance, limitations, snapshot identifier, and download guidance.

Use native navigation links and HTML sections, not a client-side router. A small
URL fragment may preserve the selected research question and metric; complex
shareable query state is not required.

### Interaction rules

- Show only filters valid for the selected dataset. Reset incompatible filters
  when changing datasets and display the active filters and visible row count.
- Use native select boxes or checkbox-based multiselects for cohort, checkpoint, role/category, and
  team-semester where applicable. Avoid a general-purpose query builder.
- Provide a clear reset action, understandable empty states, and visible data-load
  errors. Distinguish load failure, unavailable measurement, ineligible observation,
  and an empty filter result.
- Keep exact values in tables and downloads; round only presentation labels.
- Display units and denominators beside the relevant numbers, not only in a
  separate glossary. Missing values must not sort or render as numeric zero.
- Allow side-by-side comparison through the same table/chart with selected
  compatible cohorts or team-semesters, not a separate comparison subsystem.
- Apply filters to underlying observation charts and tables together. Published
  pooled summaries and association estimates retain their original population:
  do not make them appear recalculated for a selected subset.
- Show original Portuguese excerpts only when approved, with an English
  explanation. Any translation must be reviewed and labeled as a translation.
- Use semantic headings, labeled controls, keyboard navigation, visible focus,
  sufficient contrast, and a table alternative for every chart. Do not rely on
  hover or color alone to communicate values.
- Use a restrained layout with system fonts, a readable content width, and
  horizontally scrollable tables on narrow screens. No dashboard decoration.

### Technical approach

- One `index.html`, one stylesheet, and a small set of plain JavaScript files.
- Fetch only local, approved JSON; load the selected dataset on demand.
- Keep a small catalog describing available datasets, columns, filter dimensions,
  chart type, grain, and limitations. It is metadata, not a generic plugin system.
- Keep CSV downloads alongside JSON. Prepare both from the same approved rows
  before release. Generate filtered CSV in the browser from those same public rows.
- Use the locally bundled Plotly.js Cartesian 4.1.2 distribution selected by
  T016's fidelity/size check, because existing figures already use Plotly and
  require error bars, heatmaps, and scatterplots. Use only one library and retain
  its license. Do not load it from a CDN or embed unreviewed existing chart HTML.
- Render dataset text as text, never as trusted HTML. Use robust CSV quoting and
  a documented spreadsheet-safety policy for textual export cells.
- Do not compute new statistical estimates in the browser. Reuse the paper's
  vetted summaries, eligibility flags, and figure-data tables.
- Private standard-library authoring may prepare snapshots outside the
  publishable directory, using explicit input and approval paths. Neither it
  nor its private mappings are shipped or required to serve or test the site.

### Planned directory layout

```text
microsite/
  plan.md                       # This plan; itself safe to publish
  README.md                     # Preview, copy/deploy, refresh, and release checks
  index.html
  assets/
    styles.css
    app.js                      # Navigation, filters, tables, and downloads
    charts.js                   # Paper-aligned chart rendering
    vendor/
      plotly.min.js             # Only if required by the fidelity check
      plotly-LICENSE.txt
  data/
    catalog.json                # Public definitions and dataset descriptors
    release.json                # Snapshot version, public hashes and row counts
    datasets/
      <dataset-id>.json         # Approved public rows only
    downloads/
      <dataset-id>.csv          # The same approved public rows
  tools/
    snapshot_io.py              # Public serialization/validation helpers
    public_schema.py            # Only public field definitions
    build_catalog.py            # Public metadata validation
    build_release.py            # Public artifact validation
```

Create only files needed by the implementation; this is not a request to scaffold
empty files now. Do not add a second application source tree or a `dist/` directory.
All URLs use relative paths. No symlinks, parent-directory imports, external
assets, private approval files, hidden backups, or source maps with private paths.
Everything in the copied directory, including documentation and tools, must be
safe to publish.

## 5. Phases and tasks

Dependencies are sequential unless explicitly stated otherwise. Publication
approval is a blocking prerequisite for producing public data, not a final
cosmetic review.

### Phase 1 - Freeze scope and approve publication

**Plan 1.1:** Identify the submitted-paper snapshot and the exact supporting
datasets/figures. **Requirements:** REQ-003, REQ-006, REQ-009.

- [x] T001 [Plan:1.1] Record the paper/snapshot version and a concise RQ-to-dataset/figure inventory in `microsite/plan.md`, reconciling the manuscript, metric index, and artifact usage catalog. Verified in Section 3, "T001 - Paper snapshot and bounded inventory".
- [x] T002 [Plan:1.1] Specify each selected dataset's grain, key, units, filters, denominators, eligibility rules, and source-to-public field mapping for `microsite/data/catalog.json`; keep identifying source mappings in the private approval record instead. The original approved mapping contract is retained privately; the source-free `microsite/dataset-contracts.md` describes the unchanged public schema. See Section 3 and T003.

**Plan 1.2:** Approve fields and anonymity boundaries.
**Requirements:** REQ-005, REQ-008, REQ-009.

- [x] T003 [Plan:1.2] Obtain an explicit human-reviewed allowlist for every field destined for `microsite/data/datasets/`, assessing direct identifiers, searchable values, small cells, linkage, and free text. Keep the signed/private review record outside `microsite/`. Explicit authorized human approval is recorded privately; pinned field scope, identifier policy, and remaining gates are summarized in Section 3.
- [x] T004 [Plan:1.2] Individually approve any excerpts intended for publication; omit this dataset/view if none are approved. Do not reuse the full transcript audit trail. Human decision: empty approved-excerpt set; omit all excerpt payloads and UI for this release, as recorded in Section 3.
- [x] T005 [Plan:1.2] Document public-safe naming, exclusions, excerpt policy, and the hosting anonymity checklist in `microsite/README.md`, without including private source locations or reviewer identities. Verified README scope, links, exclusions, unchanged contracts, and 11 unchecked future hosting gates; see Section 3.

**Exit:** A bounded dataset/figure inventory and explicit publication approval.
Unresolved privacy questions block the affected dataset, not an implicit release.

### Phase 2 - Prepare the self-contained public snapshot

**Plan 2.1:** Export approved data and public metadata.
**Requirements:** REQ-001, REQ-004, REQ-005, REQ-007, REQ-008, REQ-009.

- [x] T006 [Plan:2.1] Implement private snapshot preparation with explicit source/approval inputs, schema/key validation, deterministic JSON/CSV output, and explicit rejection of unapproved fields or broken required contracts. Never copy source files wholesale. Verified 17 unit tests, all 58 source dispositions, isolated deterministic exports, JSON/CSV parity, and fail-closed rejection paths; see Section 3.
- [x] T007 [Plan:2.1] Produce `microsite/data/catalog.json` with English labels, source-grain definitions, valid filters, approved relationships, missingness states, figure mappings, and interpretation notes. Use neutral source labels rather than identifying URLs. Verified 49 descriptors, 510 columns, seven figure mappings, embedded definitions, all 17,046 prepared scalar cells, 27 passing tests, and isolated deterministic generation; see Section 3.
- [x] T008 [Plan:2.1] Write approved rows to `microsite/data/datasets/<dataset-id>.json` and matching `microsite/data/downloads/<dataset-id>.csv`; preserve scientific values and explicit unavailable/ineligible states. Verified all 49 pairs, 1,674 rows, 17,046 scalar cells, exact approved-source byte reproduction, 34 passing tests, standalone-copy checks, and corruption rejection; see Section 3.
- [x] T009 [Plan:2.1] Write `microsite/data/release.json` with a neutral snapshot identifier, schema version, public artifact hashes, row counts, and coverage. Retain confidential source lineage only outside the directory. Verified all 99 public artifact hashes, 49 dataset counts/coverage, isolated byte-identical regeneration, 43 passing tests, and explicit failure paths; see Section 3.

**Exit:** Frozen public JSON/CSV that agrees with the paper and contains no private
fields. Preparation can depend on explicitly supplied research inputs; the
resulting directory cannot depend on them at runtime.

### Phase 3 - Implement navigation and the table explorer

**Plan 3.1:** Build the three-view shell.
**Requirements:** REQ-001, REQ-002, REQ-003, REQ-005.

- [x] T010 [US1] [Plan:3.1] Build semantic overview, explore, and methods sections in `microsite/index.html`, with RQ cards and a visible evidence-grain explanation. Verified semantic structure, RQ/metric scope, local links, keyboard skip-link focus, browser fragment navigation, isolated HTTP root/nested hosting, and all 48 tests; see Section 3.
- [x] T011 [US1] [Plan:3.1] Implement the responsive layout, system-font styling, accessible controls, focus states, and readable tables in `microsite/assets/styles.css`. Verified 52 tests, measured contrast, browser widths 320-1280 px, 200% text, keyboard focus and local table scrolling, and standalone HTTP CSS delivery; see Section 3.
- [x] T012 [US1] [Plan:3.1] Load the local catalog and implement RQ/metric navigation, definitions, snapshot details, and explicit loading/error states in `microsite/assets/app.js`. Verified all 49 descriptors, cross-RQ metrics, definition search, snapshot metadata, loading/errors/retry, 52 Python plus nine JavaScript tests, and isolated root/nested delivery; see Section 3.

**Plan 3.2:** Add compatible filtering, sorting, and comparisons.
**Requirements:** REQ-002, REQ-004, REQ-005.

- [x] T013 [US2] [Plan:3.2] Implement dataset-specific filters, reset, active-filter summaries, visible counts, numeric/text sorting, missing-value display, and empty states in `microsite/assets/app.js`. Verified all 49 tables/17,046 cells, every approved filter and column, explicit errors/retry/cancellation, 73 tests, and independent root/nested hosting; see Section 3.
- [x] T014 [US2] [Plan:3.2] Implement compatible multi-cohort/team-semester selections in `microsite/assets/app.js`, using cohort-plus-team keys and disabling unsupported team filters for surveys/transcripts. Verified all 49 datasets/51 checkbox groups, exact values, OR/AND/reset and evidence-grain limits, 78 tests, and independent root/nested delivery; see Section 3.
- [x] T015 [US2] [Plan:3.2] Render approved excerpts, if any, in `microsite/index.html` through `microsite/assets/app.js`, with checkpoint/source context and no fabricated team attribution. Completed the no-excerpt branch required by T004: no view/payload/placeholder/request; 82 tests, all 49 runtime datasets, fail-closed policy/retry and independent root/nested delivery verified; see Section 3.

**Exit:** A researcher can navigate from an RQ to exact values and understand what
is measured, what is missing, and which comparisons are valid.

### Phase 4 - Add paper figures and downloads

**Plan 4.1:** Recreate only the selected paper visualizations.
**Requirements:** REQ-002, REQ-004, REQ-005, REQ-006.

- [x] T016 [US3] [Plan:4.1] Check representative error-bar, heatmap, and scatterplot fidelity; if needed, bundle the pinned chart library and license under `microsite/assets/vendor/`. Do not add a chart framework or second library. Verified Plotly.js Cartesian 4.1.2, upstream integrity/MIT notices, 1.51 MB raw/0.50 MB gzip, representative rendered geometry/data, local-only requests, 85 tests and independent root/nested delivery; see Section 3.
- [x] T017 [US3] [Plan:4.1] Implement selected RQ1-RQ3 figures in `microsite/assets/charts.js` from approved figure-data mappings, preserving units, uncertainty semantics, axes, zero handling, eligibility, and sample sizes.
- [x] T018 [US3] [Plan:4.1] Connect permitted chart filtering to table selection in `microsite/assets/app.js`; label fixed pooled/association summaries and ensure unavailable values are not plotted as zero. Provide captions and table alternatives in `microsite/index.html`.

**Plan 4.2:** Make approved data easy to reuse.
**Requirements:** REQ-005, REQ-007, REQ-008, REQ-009.

- [x] T019 [US4] [Plan:4.2] Add full-dataset links and filtered CSV export in `microsite/assets/app.js`, preserving public column definitions, filter scope, exact numeric values, and unambiguous missingness.
- [x] T020 [US4] [Plan:4.2] Explain dataset selection, snapshot identity, units, download scope, spreadsheet handling, and scientific caveats in `microsite/index.html` and `microsite/README.md`.

**Exit:** Paper figures are inspectable without becoming a new statistical tool;
downloads faithfully represent the approved snapshot and the displayed filters.

### Phase 5 - Verify, approve, and publish anonymously

**Plan 5.1:** Verify scientific fidelity, usability, and directory independence.
**Requirements:** REQ-001 through REQ-009.

- [x] T021 [Plan:5.1] Complete the acceptance checklist below and record pass/fail evidence in `microsite/README.md`, using neutral descriptions and no private screenshots or machine paths. Audit complete: 20 local passes, five publication checks not passed; release remains NEEDS_SIGNOFF.
- [x] T022 [Plan:5.1] Copy only `microsite/` to a separate location and serve it over HTTP at both `/` and a non-root prefix such as `/review/explorer/`; confirm all views/downloads work without the repository, pipeline, or internet asset requests.
- [x] T023 [Plan:5.1] Review every file to be published, including `microsite/plan.md`, `microsite/README.md`, assets, downloads, metadata, and tools, against the privacy allowlist and double-blind requirements. Verified all 125 files, removed private-input mappings/references while preserving approved scientific/runtime bytes, passed 120 regressions and two-browser root/nested checks, and obtained explicit authorized human whole-directory approval accepting residual risk. See README T023; the actual-host check is recorded separately in T025.

**Plan 5.2:** Release the frozen snapshot on a neutral host.
**Requirements:** REQ-001, REQ-008, REQ-009.

- [x] T024 [Plan:5.2] Document a provider-neutral copy-and-serve procedure in `microsite/README.md`, including MIME types, disabled directory listing, HTTPS, neutral URL requirements, refresh procedure, and the fact that all shipped files are public. Verified documented isolated copy/check/loopback preview commands, all 45 public Python tests and 250 root/nested file-byte checks; no deployment performed.
- [x] T025 [Plan:5.2] After human release approval, inspect the deployed URL/redirects/headers/error pages and repeat the core browse/filter/download checks against the deployed snapshot. Chrome 155/Firefox 158 passed all 49 datasets (17,046 scalar cells), seven figures and required interactions; all 99 manifest artifacts match. HTTPS/TLS/headers/MIME/404/private-path checks passed. Netlify's edge-injected `index.html` and unlisted `/favicon.ico` are documented exceptions explicitly accepted by the authorized human; this is not a provider-brand-free claim. See README T025 and the private live-audit evidence.
- [ ] T026 [Plan:5.2] Record the neutral public URL and snapshot identifier in `microsite/README.md`; supply the verified explorer URL for the paper citation through a separate manuscript change.

**Exit:** A frozen, approved directory has been proven portable and the actual
deployment works with the accepted host-branding/icon exceptions. This does not
claim provider-free delivery or eliminate anonymity/linkage risk. A local preview
alone is not publication verification.

## 6. Acceptance and release checklist

These are release checks, not a request to introduce a heavyweight testing stack.
Use existing tooling where appropriate and a browser for the interaction checks.

### Scientific fidelity

- Every selected paper dataset/figure is mapped or has an explicit, approved
  exclusion reason.
- Public numeric fields agree with the frozen source values; tables and downloads
  preserve precision. Display rounding and any privacy redactions are documented.
- Coverage agrees with the selected manuscript version, including its 14
  team-semesters, 9 M6b-observed cases, and 12 M8-eligible cases where applicable.
- M2's misleading source filename does not result in a team filter.
- M5 has no fabricated 2026.1 values or team attribution.
- Unavailable M6b values and baseline-ineligible M8 ratios remain visibly distinct
  from measured zero.
- M1 standard-deviation bars are not labeled confidence intervals. M9 and
  leave-one-out summaries retain their original populations and meaning.
- Figure axes, log-scale zero handling, scales, and labels agree with the approved
  paper figures/contracts.

### Researcher journeys

- From the landing page, reach each RQ's supporting measures and definitions.
- Select a cohort/checkpoint, sort a numeric column, inspect exact values, and
  reset without stale filters.
- Compare two eligible team-semesters; attempt an unsupported survey/transcript
  team comparison and confirm that no such control is offered.
- Download a full dataset and filtered results; verify exported row counts,
  columns, values, quoting, and missingness against the displayed scope.
- If approved excerpts exist, inspect them with correct coverage/context; if
  none exist, confirm there is no empty or misleading excerpt feature.
- Simulate a missing/malformed required dataset and confirm a clear error rather
  than an empty-success table or fabricated default.

### Accessibility and portability

- Complete core journeys using the keyboard; check visible focus and labeled
  controls. Every chart's information is also available in a table.
- At a 360 px viewport, navigation and controls remain usable; wide tables scroll
  within their own container rather than forcing the whole page sideways.
- Check current Firefox and a Chromium-based browser.
- With the isolated directory served at both root and nested paths, all local
  asset/data/download requests succeed. There are no parent-directory requests,
  external asset requests, console errors, or dependencies on a build service.
- After initial page load, the browser fetches only the chosen datasets rather
  than the entire collection. Record actual payload sizes; if a view is slow,
  reduce unnecessary data/dependencies before adding infrastructure.

### Anonymous publication

- Inspect visible content, source, strings, JSON/CSV, filenames, chart metadata,
  license notices, URLs, redirects, and server-generated error pages.
- Exclude author/institution identifiers, source repository links, commit hashes,
  respondent hashes, raw transcripts, hidden private fields, secrets, source
  paths, prompts, and restricted extraction/audit records.
- Check searchable excerpts and combinations of public attributes for linkage
  risk. Human approval is required; automated string scanning is not proof.
- Do not add analytics, trackers, social widgets, public source-repository links,
  or author-attributed deployment badges. Preserve third-party license notices.
- Use a neutral host/domain/account presentation and HTTPS. `noindex` may reduce
  discovery but is not an anonymity or access-control mechanism.
- Approve the whole directory and verify the actual hosted files before updating
  the paper's explorer citation.

## 7. Requirement mapping

| Requirement | Plan items | Planned implementation evidence |
|---|---|---|
| REQ-001 | 2.1, 3.1, 5.1, 5.2 | Relative links in `index.html` and assets; isolated root/subdirectory deployment checks; `README.md`. |
| REQ-002 | 3.1, 3.2, 4.1, 5.1 | `index.html`, `assets/styles.css`, plain JavaScript, keyboard/mobile checks. |
| REQ-003 | 1.1, 3.1, 5.1 | Paper inventory, `data/catalog.json`, RQ/metric navigation. |
| REQ-004 | 2.1, 3.2, 4.1, 5.1 | Grain-aware catalog, compatible filters/comparisons, fixed-summary labels. |
| REQ-005 | 1.2, 2.1, 3.1, 3.2, 4.1, 4.2, 5.1 | Catalog definitions, captions, eligibility/missingness states, methods section. |
| REQ-006 | 1.1, 4.1, 5.1 | Selected figure mappings, `assets/charts.js`, paper-value/figure checks. |
| REQ-007 | 2.1, 4.2, 5.1 | Approved JSON/CSV pairs, full links and filtered exports. |
| REQ-008 | 1.2, 2.1, 4.2, 5.1, 5.2 | Private approval gate; allowlisted exports; whole-directory and host review. |
| REQ-009 | 1.1, 1.2, 2.1, 4.2, 5.1, 5.2 | Frozen inventory, `data/release.json`, reproducible snapshot preparation and release record. |

## 8. Simplicity and conventions check

- **KISS/DRY:** one static application and one approved snapshot; no backend,
  duplicated application tree, custom query language, or framework.
- **Fail explicitly:** reject invalid preparation inputs and display runtime data
  errors. Missing evidence never receives a silent numeric substitute.
- **Preserve evidence:** reuse vetted paper artifacts rather than introducing new
  estimators, composites, causal claims, or inferred identifiers.
- **Independent deployment:** authoring inputs may be external; serving inputs
  must all be contained here.
- **Related project conventions:** if Python is used for snapshot preparation,
  follow the project's typed/pathlib/logging conventions and use its virtual
  environment during development. Python is not required on the destination host.
- **Migration guidelines:** no framework migration or rewrite is involved; no
  migration-specific transformation rules are needed.
- **Scope control:** create the site only after this plan is accepted. Do not
  modify research outputs or the manuscript as part of the microsite implementation
  without a separate explicit need.
