# Anonymous Research Data Explorer

An English-language companion for navigating the submitted paper's approved
research data. The intended implementation is plain static HTML, CSS, JavaScript,
and local JSON/CSV, contained entirely in this directory.

**Current status:** publication boundaries, the preparation tool, the
[public catalog](data/catalog.json), and 49 matched
[observation JSON](data/datasets/)/[download CSV](data/downloads/) pairs are
implemented, along with the [public data release manifest](data/release.json).
The [page shell](index.html) provides overview, research-question guides, and
methods with native in-page navigation and responsive local styling.
Catalog-based RQ/metric/source navigation, definitions, snapshot details,
observation tables, row filters, sorting, and compatible multi-cohort/team-semester
selection are implemented. All seven selected paper figures now render from
approved snapshots, with exact source tables and synchronized permitted
row selection. Full CSV/JSON links and displayed-row CSV with matching scope
metadata are implemented. T023 records human whole-directory approval of its
reviewed candidate; subsequent changes require affected review. Actual-host
approval remains pending.
The consolidated researcher guide covers dataset choice, snapshot recording,
units, download scope, typed import and scientific interpretation limits.
The [T021 acceptance audit](#acceptance-audit-t021) records local passes and
the publication checks that are not yet passed; an audit is not release approval.
The [independent-copy verification](#independent-copy-verification-t022)
confirms root/nested operation on a read-only static server without research
inputs or internet assets; publication approval is still pending.
This is not a ready-to-publish site.
T016 has selected and bundled one local chart dependency after a fidelity/size
check; T017 loads it locally. T018 links exact source-dataset filters to figures.
See the [implementation plan](plan.md) for task status and the
[dataset contracts](dataset-contracts.md) for scientific definitions and explicit
field projections.

## Researcher quick start (T020)

Use the on-page [data selection and reuse guide](index.html#reuse-guide) for
the same workflow while browsing. This guide explains reuse of the approved
snapshot; it does not grant publication approval or additional data access.

1. **Choose the evidence.** In Explore, narrow the research question, metric
   and evidence source, then select a dataset. Read its definition, grain,
   coverage, keys and limitations first. Navigation chooses datasets, not
   observation rows. Use **cohort plus team**, not the
   repeated team label alone, for a team-semester. Surveys and the global
   transcript corpus have no team attribution. Only permitted filters are
   offered: values within a group use OR, groups use AND, and none selected
   means all. Dataset changes reset incompatible filters. Use definition
   search for a field name, unit or metric rather than guessing its meaning.
2. **Check units and denominators.** Column headers and definitions distinguish
   counts, changed lines, score points, fractions, percentages and markers per
   1,000 tokens. A fraction (0-1) is not a percentage (0-100), and a score-point
   difference is not a difference in percentage points. Keep original Ns and
   denominators: selected rows are not a newly measured participant population.
   Null/Unavailable, observed zero, false, a zero-row selection and a failed
   load are distinct; preserve measurement/ratio status columns as well as values.
   Retry a failed load with its visible control rather than interpreting it
   as absent evidence.
3. **Record the snapshot.** Read [Snapshot and provenance](index.html#snapshot-details)
   and save the [release manifest](data/release.json). Record the manifest's
   snapshot ID, schema version and selected dataset ID, together with the full
   files or filtered CSV and matching metadata; do not mix snapshots. Record
   the dataset's coverage as well, not just an ID. The manifest hashes original
   public data files, not generated filtered CSVs or the whole application.
   A snapshot identifier is not a license or evidence of publication/anonymity
   approval. All release gates remain required for this development preview.
4. **Choose the download scope.** Full CSV/typed JSON contains every original
   row of the chosen dataset, independent of filters and sort. Displayed-row CSV
   contains exactly the observation table selection in its current sort order.
   Save its matching scope/column-definitions JSON: it records snapshot, dataset,
   counts, typed filter choices/field order and OR/AND rules, sort, units,
   denominator and interpretation limits. Empty selections are header-only CSV
   with zero selected rows in metadata. A chart's zoom or hidden legend traces
   do not affect exports. Other source panels are not joined or included;
   M4/M5 remain separate. Reset row filters and sort restores all original rows;
   Reset figure view keeps the selected rows and only resets the view.
5. **Import without changing values.** Use a CSV-aware importer configured for
   UTF-8, comma separators and a double-quote text qualifier. Quoted cells may
   contain commas/newlines; do not split CSV by lines or commas manually.
   Explicitly import cohort/team/category IDs as text and measures/booleans
   using the supplied column types. Map empty CSV cells to null, never zero,
   false or forward-filled values. Keep IDs/status fields and full precision.
   Avoid opening and resaving via automatic spreadsheet conversion, which can
   change identifiers and round numbers even when CSV text is quoted.
   Formula-leading text is rejected under the reviewed export policy, not
   prefixed or changed; quoting alone is not a safety guarantee. Preserve
   original downloads, and use typed JSON with a suitable data tool if the
   importer cannot preserve types/numeric precision. JSON is structured data,
   not literal spreadsheet cell text. Generated numeric decimal spelling can
   differ from authoring CSV while retaining the same numeric value.
6. **Preserve interpretation limits.** These are descriptive/exploratory
   observations and published associations, not causal evidence or team
   rankings. Filters choose existing rows, never new pooled/subset estimates.
   Original thresholds, medians, sample sizes and denominators stay fixed.
   SD bars are not confidence intervals; leave-one-out diagnostics are not
   confidence intervals either. No repository artifact observed does not mean
   no planning; rework is not a defect count. Ineligible ratios are unavailable
   even when magnitudes exist. Log axes omit zero magnitudes but retain them
   unchanged in source tables. Do not assign global transcript aggregates to
   teams, infer unmeasured-cohort evidence, calculate new subset correlations
   as if published, or attempt to re-identify participants. The transcript corpus
   covers 2025.2 only, not 2026.1. Evaluator scores are not repository structural
   complexity. No verbatim quotations are released here.

Before reusing a result, check that **dataset ID, snapshot, coverage,
column definitions/units, original denominator, selection/sort and missingness**
are all recorded. The [dataset contracts](dataset-contracts.md) and
[public catalog](data/catalog.json) are the dataset-specific reference, not a
license to join different grains. See [download operation and serialization](#dataset-and-displayed-row-downloads-t019)
for the CSV conventions and failure states. T025 records actual-host checks and
the accepted Netlify branding/icon exceptions below. T026 remains responsible
for recording the verified public URL and snapshot for the paper citation.

## Page shell (T010)

[The entry page](index.html) has three semantic sections: overview, explore,
and measures/methods. Main navigation and the three RQ cards use native fragment
links and work without JavaScript. A visible skip link moves keyboard focus to
the main content. The overview explains survey, team-semester, global transcript,
and fixed-estimate grains before the research-question guides.

The styled explorer now loads approved observation rows on dataset selection.
The page supports comparing existing compatible cases in the same table and
viewing the seven paper figures and downloading full datasets or displayed rows.
Local catalog, release-manifest, and documentation links work.
T011 provides layout/focus styling; T012 provides catalog loading and
dataset navigation; T013 provides row filters/tables/sorting; T014 adds multi-case
selection. T017 adds figures; T018 synchronizes permitted row selection; T019
provides full and filtered downloads.
No missing stylesheet/script references, external assets, router, or build step
have been added. Serve the directory over HTTP(S) to preview it; do not interpret
the working shell as whole-directory or host approval.

## Catalog navigation and definitions (T012)

The local [application script](assets/app.js) first loads `data/catalog.json`
and `data/release.json`, then the selected dataset on demand. It validates the supported schema, no-excerpt policy,
RQ/metric/source references, local paths, field definitions, and agreement of
the two public inventories/counts before enabling navigation. The validation
checks metadata consistency, not artifact bytes or publication permission;
use the release-authoring `--check` command for actual file-hash verification.

Choose a research question, metric, evidence source, and dataset. Choices are
restricted by the catalog's actual relationships; changing the RQ resets metric
and source, and changing metric resets source. Cross-RQ supporting datasets
retain all their catalog metric tags rather than being forced into one metric.
RQ cards select the appropriate catalog scope and move to Explore. Native
RQ guide links and `#rq1`/`#rq2`/`#rq3` fragments remain useful without a router;
full dataset/filter URL persistence is not implemented.

The selected descriptor shows grain, composite keys, denominator, coverage,
null/status meaning, fixed population, limitations, and expandable column
definitions/units. Measures and methods includes literal, case-insensitive
search over all dataset definitions (including RQ/metric tags, field names,
and units), the embedded weekly/complexity codebooks, and expandable frozen
policies. An unmatched search is explicitly empty, not a metadata-load failure.
Snapshot details come from the release manifest instead of a duplicated
hard-coded identifier. All metadata is inserted as text, never trusted HTML.

While metadata is loading, controls are disabled and the status is explicit.
HTTP errors, invalid JSON, unsupported/inconsistent metadata, and requests
exceeding 15 seconds display an alert, clear derived content, log the error,
and offer retry. No observation rows are synthesized.
Without JavaScript the static RQ guides and local documentation links remain
available, with a visible explanation that interactive catalog features need
JavaScript. The no-excerpt decision remains enforced; there is no excerpt
descriptor, view, request, or hidden payload.

Run all authoring/static tests with the Python command below, and JavaScript
tests with Node.js 18+ (authoring only, not required on the server):

```sh
node --check assets/app.js
node --test tools/test_app.cjs
```

There are no npm packages, package manifest, installation, bundling, or build
step. Twelve metadata/policy JavaScript tests use only Node's built-in runner and the public files:
metadata/schema errors, cross-RQ navigation, definition matching, HTTP/JSON
failure, request scope, and abort timeout.

## Excerpt omission (T015)

The approved-excerpt set for this release is empty by explicit human decision.
The application therefore implements the **no-excerpt branch**: no excerpt view,
navigation item, placeholder, text-search index, download, payload, or request.
This is not a claim that qualitative evidence does not exist. Approved lexical
aggregates, coding definitions, and structured planning counts remain available;
an evidence-quote count does not authorize publishing its source text.

No dormant renderer or feature switch was added. The existing metadata loader
requires the omission policy and fails explicitly before requesting observations
if that policy is missing or changed. Exact observation schemas reject added
quotation fields. These structural checks are not a classifier or guarantee
against arbitrary unapproved text disguised as an existing field: the frozen
allowlisted exports, release hashes, and final whole-directory human review
remain necessary.

Regression tests check the shipped descriptors/files/release inventory for
excerpt artifacts (including empty placeholders), absence of excerpt UI,
fail-closed policy loading, rejected extra quote fields, and continued availability
of approved aggregates/counts. Browser checks verify the runtime navigation,
definition search, and requests without an excerpt feature. Reopening this
decision requires individual human approval of exact text and context under
T004 before changing the export contracts or application.

## Observation tables and row filters (T013)

Selecting a dataset requests only its local JSON file, validates its exact
column order, scalar types/nullability, finite values, unique analytical keys,
and frozen row count, then renders all rows without rounding or pagination.
Metadata and observation loading/errors are separate. Changing datasets cancels
the previous request and invalidates stale responses, clears filters/sort, and
removes the old table while the new file loads. A failed, malformed, missing, or
timed-out file produces a logged error, no rows, disabled row controls, and retry;
it is never presented as a successful empty dataset.

Each catalog-approved filter uses observed typed values. Cohort, team-semester,
and omitted-case filters are native checkbox groups allowing multiple choices;
other filters are labeled single-value selectors with All. Team and omitted-case
choices always include cohort plus team, never a repeated team label alone.
Surveys and global transcript aggregates receive no unsupported team selector.
Selections are combined by intersection without changing values, estimators,
thresholds, denominators, or original pooled/association populations.

The active-filter summary, visible/total counts, and table caption show the
current scope. Zero matching rows is explicit and distinct from a load error.
Reset clears row filters and sort while keeping the chosen dataset. Filter
choices retain the full dataset vocabulary, so conflicting intersections are
visible as empty results rather than silently removing selections.

Column-header buttons toggle ascending/descending sort with `aria-sort` and keep
keyboard focus after rendering. Numbers and booleans use their types, text uses
English collation, ties keep source order, and nulls stay last in both directions.
Null cells read **Unavailable**, not zero; measurement/ratio-status columns and
dataset missingness notes retain their reasons. Headers include units, numeric
cells preserve full precision, and every value is inserted as literal text.
The named table region scrolls horizontally via keyboard at narrow widths.

Seventeen row tests using Node's built-in runner cover all 49 datasets, every approved
filter choice, composite keys, empty intersections/reset, stable numeric/text/
boolean/null sorting, exact display, fixed estimates, and fetch errors/cancellation/
timeout. Run both JavaScript test files with one command:

```sh
node --test tools/test_app.cjs tools/test_rows.cjs
```

## Compatible multi-case selection (T014)

Compare selected cohorts or team-semesters in the **same observation table**,
without a separate comparison view or joining different datasets. Cohort,
team-semester, omitted-cohort, and omitted-case filters use native checkbox
groups with explicit legends and clickable labels. Check any number of choices;
**none checked means all**, as the group hint explains. This avoids modifier-key
multiselect gestures. Long lists scroll locally; Tab and Space operate the
checkboxes. Other filters retain their one-value-or-All selector.

Choices within one group use **OR**; different filters use **AND**. Selecting
both cohorts and two team-semesters shows only those two cases, not every team
in either cohort. Team/omitted-case labels always include the cohort, and their
values encode the full composite identity. Repeated team labels never merge.
Conflicting selections produce an explicit empty result without deleting
choices. Uncheck the last choice to show all for that group; Reset clears every
group, single-value filter, and sort. Dataset/RQ navigation clears all old state.
Active-filter summaries list the selected cases, and counts update together
with the existing table.

The UI offers only filters declared in the catalog. Survey summaries can compare
cohorts, never teams. Global transcript aggregates cannot acquire team or
unmeasured-cohort selectors. Datasets without a team-semester observation filter
say so explicitly. Omitted-case diagnostic filters select existing fixed
leave-one-out results; they do not calculate new omissions or associations.
Original rows, denominators, estimator Ns, eligibility, missingness, and scientific
values stay fixed. The selection helper rejects unknown filters, unapproved or
wrongly typed choices, and duplicate tokens rather than silently returning a
misleading result.

Five T014 regression tests extend the twelve T013 row tests: cross-cohort repeated
team labels, OR/AND across every approved filter, invalid selections, fixed
omitted-case estimates, and absence of unsupported survey/transcript team filters.
Run them with the combined Node command above. No new package, server-side
requirement, or data artifact is introduced.

## Local chart dependency and fidelity gate (T016)

The sole chart dependency is the official **Plotly.js Cartesian distribution
4.1.2**, copied without modification as
[plotly-cartesian-4.1.2.min.js](assets/vendor/plotly-cartesian-4.1.2.min.js).
Its upstream [MIT license](assets/vendor/LICENSE-plotly-4.1.2.txt) and all notices
in the bundle are retained. The license's third-party copyright attribution is
not an author/project identity. No package manager or build is needed on the
hosting server. The entry page now loads this local dependency with deferred
scripts, before the figure and application scripts. T017 provides figures,
captions and source tables; T018 connects permitted filtering to table selection.

The Cartesian bundle supports scatter/line/bar traces, SD error bars, heatmaps,
color scales, variable marker diameters/symbols, logarithmic axes, and zoom.
It avoids the full bundle's unnecessary geospatial and 3D modules. A basic
scatter/bar-only bundle would not cover the requested heatmap capability.
Keeping this single maintained renderer is simpler than implementing error-bar
geometry, scales, hit testing, zoom, and heatmap behavior independently.

Size check: **1,507,990 bytes** raw (1.44 MiB), **499,721 bytes** with gzip level 9
(488.0 KiB). The full version's published package is about 6.17 MB unpacked,
versus 1.51 MB for this Cartesian package. The site remains usable on a plain
static server even without compression, at the larger raw transfer size. Gzip
is an optional hosting optimization, not a hosting-time build step or a shipped
second copy. No performance budget was previously specified; these measured
sizes are recorded transparently rather than claimed to meet an invented limit.

Pinned provenance and integrity:

- Package: `plotly.js-cartesian-dist-min@4.1.2`, from the
  [npm registry](https://registry.npmjs.org/plotly.js-cartesian-dist-min/4.1.2).
- Archive: `plotly.js-cartesian-dist-min-4.1.2.tgz`; verified against the registry's
  SHA-512 integrity before extracting only the bundle and license.
- Archive integrity:
  `sha512-3UkyAT7/U8f3sOLavLnUjA6mqFmnqEe246GZhxT0J3TT9oZ0mh6SgwsL1yo/3/4xfmRSDFdGOxe+EsvT2XiE0g==`.
- JavaScript SHA-256:
  `aaf12ff1d4671f7e93f6df4291651ab4ca6b76c0ea5f1576ec1030e3c2819a20`.
- License SHA-256:
  `8c45d9eaf50c2f72dd9c7ab9ef440788ba58a3538484b5c51c1f17d5128752e7`.

The [vendor tests](tools/test_vendor.cjs) pin the exact version, bundle/license
hashes, raw/compressed sizes, single-library inventory, retained notices, and
local script paths. Run all JavaScript tests together:

```sh
node --check assets/vendor/plotly-cartesian-4.1.2.min.js
node --check assets/charts.js
node --test tools/test_app.cjs tools/test_rows.cjs tools/test_vendor.cjs tools/test_charts.cjs tools/test_exports.cjs
```

A temporary authoring-only browser probe used approved data, not existing chart
HTML or private inputs. It verified all 36 M1 mean/SD points and rendered SD
endpoints, a correctly oriented 36-cell M2 role heatmap with the fixed 1-5 scale,
14 score-colored/size-encoded planning-concentration cases, and 11 positive
rework values on a log axis while retaining three zeros in the table. A synthetic
null heatmap cell remained a gap, not zero. Composite hover identity and
programmatic zoom/reset worked; all four plot specifications passed Plotly
validation without warnings. The M2 heatmap is a **capability probe**, not an
eighth manuscript figure or an extension of the approved seven-figure scope.

The probe is not shipped, and these semantic/geometry checks are not pixel-perfect
image matching or full keyboard/pointer accessibility sign-off. The shared hidden
browser made screenshot/stability waits unreliable. T017 checks final rendering,
responsive containment, and exact tables; T018 verifies synchronization. The full
accessibility audit remains a later gate. Do not enable cloud links, editable charts, external
fonts, maps, MathJax/CDN scripts, or telemetry. Browser requests for the tested
Cartesian plots stayed local. Preserve this property when wiring the library.
Vendor assets are outside the **data-only** release manifest; the vendor hash
tests and final whole-directory review cover them separately.

## Paper figures (T017)

Choose a figure in **Explore > Paper figures**. Selection opens its primary
source in the observation table and loads its one or two approved local
datasets, using the same type/key/count validation and
15-second request limit as observation tables. No new estimator, pooled subset,
cross-grain join, or browser-side threshold is calculated.
The [figure script](assets/charts.js) implements exactly the seven catalog
mappings; the M2 heatmap tested for T016 is not another selected figure.

| Figure | Preserved scientific meaning |
| --- | --- |
| RQ1 coded perceptions | Two cohort facets; 36 means, SD bars (not confidence intervals), original response Ns and 0-5 displayed axes. Coded families retain 0-4 units; autonomy/tool balance retains 1-5 units. |
| RQ2 pooled activity | 29 overlapping seven-day windows, numerically ordered relative days, original pooled Ns, T3 anchor and original day-one peak annotation. |
| RQ2 planning/concentration | 14 cases, original marker diameters for absolute score change, common T3 evaluator-score color limits, cohort symbols, and frozen median guides. |
| RQ2 churn/lexical density | Separate M4/M5 panels, axes, units and denominators. Global 2025.2 transcript evidence is never reassigned to individual teams or another cohort. |
| RQ3 artifact presence | Stacked raw counts and original cohort Ns (9/5), not percentages or quality scores. |
| RQ3 planning/rework | Logarithmic magnitude axis plots 11 positive cases; all three zeros remain unchanged in the source table and are listed as excluded, never replaced by one. Baseline eligibility stays separate from magnitude. |
| RQ3 complexity/rework | Linear magnitude axis retains all 14 cases and three zeros; eligibility, planning-tier colors, cohort symbols and original medians remain distinct. |

Every figure has a caption explaining units, coverage and limitations, plus
expandable exact source tables containing **every approved column and selected
original row** (all rows when filters are clear).
Tables preserve full numeric precision, composite cohort/team identity and
original denominators. `Unavailable` represents null, never zero. Source-table
Ns describe original populations, not the number of currently visible marks.
Hover is supplementary; exact values do not depend on pointer interaction.

Drag to zoom, use legends to toggle traces, and use **Reset figure view** to
restore zoom and trace visibility for the current row selection. Visibility changes
do not change source tables, values, denominators, or frozen guides. Narrow
screens use a labeled, focusable horizontal-scroll region instead of shrinking
multi-panel figures until their labels are illegible. Tables scroll locally too.

**Selection behavior (T018):** figures now follow the exact mapped dataset's
permitted observation filters and sorting. No filter is copied to a different
dataset. Fixed pooled/association summaries never become new selected-case
estimates. See the synchronization rules below.

Missing renderer files, HTTP/JSON/schema/count errors, and failed rendering have
explicit alerts, logged errors and retry/reload instructions. Old figures and
source tables are cleared, not displayed as a successful empty result. Changing
figures aborts superseded data loads and invalidates stale results. A figure
failure does not disable valid observation tables; a metadata failure clears
and disables both until metadata retry succeeds.

Browser checks matched all seven rendered scientific arrays and **1,378 exact
source-table cells across 117 rows**, including all 36 SD endpoint pairs within
0.011 px of their projected values. Marker diameters, common score limits,
composite hover identity, zoom/reset, trace visibility, errors/recovery and
stale-request handling were checked. All seven figures passed Plotly validation
and stayed contained at 1280/360/320 px; enlarged source-table text also stayed
locally scrollable. Requests remained local.

Two renderer-validation problems found during implementation were resolved,
not suppressed: the single-trace activity plot omits an unused legend
configuration, and the two score-colored traces use identical explicit
Viridis limits (1.5-2.5), with one visible colorbar, rather than shared color-axis
references rejected by this bundle's validator. The scientific color mapping is
unchanged. A duplicated percent suffix in concentration hover was also removed.
The dependency itself remains byte-identical to the pinned upstream release.
These checks are not pixel-perfect image matching or full real-keyboard/pointer
accessibility sign-off; those later gates and all publication approvals remain
pending.

## Synchronized figures and source tables (T018)

Use the existing observation controls; there is no second chart-filter system.
Selecting a mapped dataset selects its paper figure automatically. Selecting a
figure opens its primary source dataset, resets incompatible row filters/sort,
and clears navigation restrictions so that source is available. Other datasets
show an explicit "no mapped figure" message rather than an unrelated stale chart.

Only existing rows of the **exact mapped source dataset** are selected. The
figure, active-filter summary, observation table, and matching figure source
table use the same row selection. Sorting the observation table also orders its
source alternative; chart checkpoint/day ordering remains scientific rather
than alphabetical. Cohort and team choices retain the existing OR-within,
AND-between logic and composite cohort/team identity.

The M4/M5 figure has two independent source datasets. Filtering one changes only
that panel and its source table. The other retains its full approved snapshot,
explicitly identified in the caption. Use **Filter this source** in either
source-table disclosure to open that exact dataset in the existing observation
controls; changing sources resets the previous source's filters. A checkpoint
selection is not silently transferred between repository and transcript grains.

Captions identify each source's selected/original row counts and active filters.
Fixed published summaries are labeled as existing summary rows with original
populations and Ns, not recomputed estimates. Original Ns, denominators, score
color limits, planning thresholds, and median guides never change with filters.
Selecting one cohort in RQ1 shows that cohort's labeled facet with the original
0-5 displayed scale, original SDs and family colors/legends.

An empty filter intersection removes old marks and shows a clear empty-selection
message with a zero-row source table. Selected log-axis zeros remain unchanged
in source tables and explicit exclusion details; a selection containing only
such zeros shows "no plottable values", not a successful-looking fabricated plot.
Unavailable coordinates remain unavailable, not zero. Other panels, if any,
can still show their explicitly unfiltered data.
An unavailable SD has no error bar and is labeled Unavailable in hover/table;
known SDs and the original means remain visible. A missing SD is not drawn as
a zero-length error bar.

**Reset figure view** restores zoom/trace visibility without changing row
filters. **Reset row filters and sort** restores all original source rows.
Legend toggles change mark visibility only; they do not filter either table or
redefine scientific populations. Load/filter/source changes clear stale content
and cancel or invalidate older requests/renders. Errors remain explicit with
retry, and valid observation tables remain usable after figure-only failures.

## Dataset and displayed-row downloads (T019)

The download region below the observation table separates:

- **Full dataset (CSV)** and **Full dataset (typed JSON)**: native links to the
  selected dataset's original local snapshot files, unaffected by filters,
  sorting, figure legends, or another figure panel.
- **Download displayed rows (CSV)**: generated locally from the same typed
  rows, permitted filter predicates and stable sort order as the observation
  table. No hidden fields, display rounding, recalculation or chart-only
  visibility selection is applied.
- **Download matching export scope and column definitions (JSON)**: the CSV's
  companion record, identifying its filename, snapshot and dataset, selected
  and total row counts, typed filter choices and their field/OR/AND encoding, sort, column order, complete
  approved column definitions/units, grain, keys, denominator, missingness,
  coverage and fixed-population caveats.

Keep the companion JSON with its CSV. Both are regenerated together when the
dataset, filters or sort changes. Filenames use neutral approved dataset IDs;
no host, private source location, user identity or timestamp is inserted.
The visible status reports the current scope before downloading. Full files
are byte-identical snapshot artifacts; generated CSV uses equivalent typed
values rather than promising the author's Python decimal spelling.

Generated CSV is UTF-8 without a byte-order mark, with comma separators, LF
records, quoted string/header cells and doubled embedded double quotes.
Embedded commas, newlines and Unicode remain literal text. Finite numbers use
JavaScript's round-trip decimal representation, not chart/table formatting;
booleans are lowercase `true`/`false`. An empty unquoted cell means null
(`Unavailable`), not zero or false; use the supplied types and status fields.
The current snapshot has no empty strings or nullable text columns. A future
ambiguous empty nullable-text value is rejected rather than made indistinguishable
from null. Typed full JSON retains explicit nulls.

Formula-leading textual cells/headers are rejected under the preparation
tool's existing spreadsheet-safety policy, not prefixed or otherwise changed.
Negative numeric values remain numbers. Import with explicit column types:
even quoted CSV does not stop spreadsheets from auto-converting identifiers or
losing numeric precision. No spreadsheet application is a fidelity validator.

An empty filter intersection downloads a header-only CSV and companion record
with zero selected rows. Load failures expose no stale filtered download.
Full links still target the currently selected snapshot files, independently of
whether its observation JSON loaded. Export-generation failures show an alert,
log the error, clear partial links/Blob URLs, preserve valid observation tables,
and offer retry. Old Blob URLs are revoked on selection changes and page exit;
back/forward cache restoration rebuilds current links.

The [export tests](tools/test_exports.cjs) check all 49 datasets/17,046 scalar
cells, each permitted single-choice filter, exact sort/scope metadata, quoting,
empty results, null/zero/false distinction and explicit unsafe/invalid-data
rejection. Browser checks read the actual Blob payloads and all 49 original
JSON/CSV pairs, and verify scope/reset, errors/retry and URL cleanup.
The integrated hidden browser did not emit file-save download events for native
links despite click attempts; payload bytes, MIME types, relative targets and
download filenames were verified directly at T019. T021 now additionally verifies
completed native file saves in real Chrome and Firefox at root and nested paths.
Actual-host file-save behavior remains a release check.
T020 provides consolidated reuse guidance above. Later release/accessibility
gates remain pending.

## Responsive styling (T011)

The local [stylesheet](assets/styles.css) uses system fonts, a restrained light
palette, readable text widths, underlined links, and a bounded page layout.
Research-question cards use three columns on wide screens and stack below
52 rem. Navigation wraps instead of clipping. Text can enlarge and long values
can wrap without hiding content or forcing whole-page horizontal scrolling.
Keyboard focus uses an offset, high-contrast outline; no fixed header obscures
anchor targets. No external fonts, images, CSS imports, or build tools are used.

Shared native control styles cover labels, fieldsets, inputs, selects, and
buttons. Future controls must still have explicit labels and appropriate
semantics; CSS cannot supply those. Controls have a 44 px minimum height at
the default font size, except native checkboxes/radios, which must be paired
with clickable labels. Disabled controls retain legible colors and use a
dashed border and disabled cursor rather than reduced opacity.

Tables use a `.table-scroll` wrapper with `tabindex="0"`,
`role="region"`, and an accessible name, so narrow-screen users can scroll
with the keyboard. Use a caption and scoped headers; mark numeric data cells
with `.numeric` for right-aligned tabular numerals without splitting values.
Headers wrap, while long numeric values scroll within the wrapper. Sort
buttons retain native focus behavior. T013 applies these reusable rules to
the observation table.

Four [stylesheet tests](tools/test_styles.py) check local wiring, system-font
and no-network rules, palette contrast (4.5:1 text and 3:1 focus/borders), and
the control/table styling contract. Browser checks cover 320/360/768/1280 px
widths, 200% text at 360 px, keyboard focus, and a temporary control/wide-table
fixture. The fixture is not shipped. These checks do not replace the later
full application accessibility and actual-host review.

## Acceptance audit (T021)

**Audited 2026-10-22. Overall: NEEDS_SIGNOFF.** All 25 checks from
[plan Section 6](plan.md#6-acceptance-and-release-checklist) are assessed below:
**20 PASS locally; 5 NOT PASSED because whole-directory/human/actual-host
release gates remain open.** T021 completes the evidence audit, not the
anonymous-publication checklist. This is a dated, point-in-time T021 result; later
T022-T025 evidence and current hosting-gate status appear below. These local
acceptance results did not themselves complete T022-T026.

### Scientific fidelity

| ID | Check | Result | Evidence |
|---|---|---|---|
| S1 | Selected datasets/figures mapped or explicitly excluded | PASS | Pinned manuscript and seven included figure fingerprints still agree with the inventory. All 49 approved dataset mappings and seven figure mappings validate; inventory/contracts retain explicit exclusions and the human no-excerpt decision. |
| S2 | Exact source values, table/download precision, documented transformations | PASS | Fresh preparation from the approved frozen inputs reproduces all 98 JSON/CSV files byte-for-byte: 1,674 rows and 17,046 scalar cells per format. Public-safe projections and eligibility masking are documented; no new rounding, suppression or estimates. Both browsers independently compare every table and generated CSV cell with the typed snapshot. |
| S3 | Manuscript coverage | PASS | Source checks and public snapshot tests confirm 14 team-semesters (9/5 by cohort), 9 measured M6b cases and 12 baseline-eligible M8 cases. Row counts are not participant Ns. |
| S4 | M2 filename cannot imply team filtering | PASS | M2 summaries retain cohort/checkpoint/role grain. Both browsers offer no team-semester control; schema/filter tests cover all survey descriptors. |
| S5 | M5 measured corpus only, no team attribution | PASS | Only the global 2025.2 checkpoint corpus is measured; chunk coverage is 35/37/28. No 2026.1 observations or team keys/controls are fabricated. |
| S6 | Unavailable planning and ineligible ratios differ from zero | PASS | Null/status/boolean and eligibility tests pass. Both browsers retain literal Unavailable cells and null-to-empty CSV encoding; log figures explain excluded measured zeros rather than substituting a positive value. |
| S7 | SD versus CI; fixed M9/leave-one-out populations | PASS | Chart/caption tests and rendered captions say standard deviations, not confidence intervals. Original Ns, strata, denominators and diagnostic meanings stay fixed under selection. |
| S8 | Figure axes/scales/labels/zero policy | PASS | All seven figures render in both browsers with exact source-table alternatives; the chart tests check original coordinates, SDs, scales, fixed medians, cohort/score encodings and separate M4/M5 units. The log profile plots 11 positive cases while retaining 14 source rows; the linear complexity view retains three zeros. |

### Researcher journeys

| ID | Check | Result | Evidence |
|---|---|---|---|
| R1 | Landing page to each RQ's measures/definitions | PASS | Native keyboard activation of all three RQ cards selects the corresponding evidence. Dataset definitions, denominators and labeled definition search remain available. Without scripts, native RQ/methods/catalog links and the static guide remain available. |
| R2 | Cohort/checkpoint, numeric sort, exact values and reset | PASS | Keyboard selection of one cohort and T3 yields six exact M1 rows; ascending mean order is numeric. Reset restores 36 original rows with no active filters or stale sort. |
| R3 | Two eligible cases and unsupported comparison | PASS | Keyboard selection compares TEAM_01 from each cohort as two distinct team-semesters. M2 survey and M5 transcript datasets expose no team-semester comparison control. |
| R4 | Full/filtered download fidelity and missingness | PASS | Chrome and Firefox each save full CSV, full typed JSON, displayed-row CSV and scope JSON to disk at both URL prefixes (16 completed saves overall). Full files match original bytes; the filtered two-row CSV matches the table/order and its metadata. All 49 generated CSVs also match exact typed rows/null encoding in each browser; quoting, empty output and unsafe-text policies pass the export tests. |
| R5 | No misleading excerpt feature | PASS | The approved branch omits excerpts. Catalog, application and file-inventory regressions find no excerpt payload, descriptor, request or empty feature. Counts do not authorize quotation text. |
| R6 | Missing/malformed data fail explicitly | PASS | In isolated copies, missing observation JSON (HTTP 404), malformed observations and malformed metadata show explicit errors, remove stale tables/generated links and recover through the native retry controls. No success-shaped empty default is used. Expected injected errors are separate from clean happy-path logs. |

### Accessibility and portability

| ID | Check | Result | Evidence |
|---|---|---|---|
| A1 | Keyboard journeys, visible focus, labels and table alternatives | PASS | Both browsers use native Tab/Shift+Tab, Space, arrows and Enter for RQ selection, dataset choice, cohort/checkpoint filters, sorting, composite comparison, reset and downloads. Focus-visible outlines are present; inputs/selects have labels. Arrow keys scroll the focused observation region. All seven figures have exact source tables. This is not a screen-reader or comprehensive WCAG certification. |
| A2 | 360 px navigation/controls and contained tables | PASS | Actual Chrome inner widths of 360 and 320 px preserve all seven charts and controls without whole-page horizontal overflow. Wide tables scroll locally; enlarged 32 px text also stays contained. Firefox's headless window clamps at 500 px: its desktop/500 px checks pass, but no 360 px Firefox result is claimed. |
| A3 | Current Firefox and Chromium-based browser | PASS | Real headless Firefox 158.0 and Chrome 155.0.8059.84 each pass the same three multi-step runtime flows. These are browser-engine/native-input checks, not a claim of testing every operating system or assistive technology. |
| A4 | Isolated root/nested URLs, local requests and clean console | PASS | Independent copies serve byte-identical assets, metadata and all 49 JSON/CSV pairs at `/` and `/review/explorer/`. Both browsers complete journeys and native downloads at both prefixes. No parent-prefix/external asset requests, happy-path console errors or JavaScript exceptions remain after the favicon correction below. No host-time build/backend is required. |
| A5 | On-demand data and measured payload | PASS | Initial loading requests only the chosen M1 dataset, not all 49. Local metadata and chart code load first; later requests follow the selected dataset or its explicitly mapped figure sources. Actual decoded file sizes and the duplicate-source observation are recorded below; no infrastructure was added. |

### Anonymous publication

**Historical T021 status:** each `NOT PASSED` result below records the release
state on 2026-10-22, before T023 whole-directory approval and T025 live-host
verification. The local T021 `PASS` for P4 did not evaluate host-injected
behavior. These entries are retained as audit history; current host findings
and the explicitly accepted Netlify exceptions are recorded in T025 below.

| ID | Check | Result | Evidence and required action |
|---|---|---|---|
| P1 | Inspect all shipped content/source/metadata/licenses/URLs/error pages | NOT PASSED | Runtime content, paths and data projections were checked, but this is not a completed every-file publication review or actual-host inspection. T023 must review the entire directory, including planning/authoring material and retained vendor notices; T025 must inspect deployed URLs, redirects, headers and generated pages. |
| P2 | Exclude identities/private fields/source paths/restricted evidence | NOT PASSED | Fresh preparation and public snapshot tests verify approved fields and no raw transcript/private observation payload. Planning/authoring documentation and tools still contain source-filename/relative research-location references. T023 must remove or neutralize prohibited source references and assess every shipped file; field approval cannot certify the entire directory. Keep confidential lineage and reviewer records outside the served directory. |
| P3 | Searchable combinations/linkage risk, human approval | NOT PASSED | The prior exact field/value scope decision does not approve the final directory or host. Human reviewers must assess combinations, small cells and residual linkage risk for the actual release; automated scans cannot close this gate. No quotations are enabled. |
| P4 | No telemetry/widgets/source links; retain third-party notices | PASS | Local application and browser network checks show no analytics, tracking, external assets or deployment badges. Vendor integrity/license tests pass and required notices remain unchanged. Repeat network checks after hosting; provider-injected behavior is not covered locally. |
| P5 | Neutral host/domain/account presentation and HTTPS | NOT PASSED | No public host has been selected or approved. T024 must document deployment requirements; T025 must verify neutrality, HTTPS, redirects, headers and error/directory responses on the actual host. `noindex` would not replace this review. |
| P6 | Whole-directory approval and actual hosted files before citation | NOT PASSED | T023/T025 human release and deployed-snapshot verification remain mandatory. Only T026 may record a verified neutral URL and snapshot for the separate paper citation update. No public URL or final approval is claimed here. |

### Measurements, corrected issue and remaining limitations

- The first real Chrome audit found an implicit `/favicon.ico` request outside
  the nested site prefix and a 404. With explicit human authorization, a neutral
  [local SVG icon](assets/favicon.svg) and relative HTML reference were added.
  The new page regression failed before this fix. Both browsers now request
  only the local icon and pass the clean-prefix/console checks.
- Initial decoded resource bodies total **1,979,090 bytes**, plus the
  **21,866-byte HTML** at this audit. Major components: vendor renderer
  1,507,990; catalog 322,214; manifest 45,542; application 40,836; chart logic
  29,454; stylesheet 5,386; icon 196 bytes. The default observation file is
  13,736 bytes and is fetched twice by the independent table/figure loaders.
  This is duplicate retrieval of the same chosen dataset, not preloading the
  collection. Observation files range from 483 to 115,834 decoded bytes.
  The preview uses no compression or shared cache; transfer headers add overhead.
  Host compression of unchanged static bytes is the simplest later delivery
  improvement. If duplicate reads become material, use an explicitly tested
  shared in-flight request/cache rather than a backend; no cache/lifecycle change
  is justified solely by this 13,736-byte duplicate.
- The test-only browser drivers ran outside the publishable directory; no
  package manifest, browser framework or host dependency was added to the site.
  A Firefox driver download needed a direct upstream retry. The browser harness
  was corrected to use reverse Tab instead of wrapping through browser chrome,
  and to wait for finished downloads rather than empty temporary placeholders.
  These were test-harness problems, not silently waived application failures.
- The earlier integrated hidden-browser file-save limitation is resolved for
  this local acceptance audit by real WebDriver/native-key activation and
  completed disk-save checks in both browsers. Actual-host downloads still
  require verification. No private screenshots, machine paths, reviewer
  identity or runtime logs are included here.

### Reproduction and verdict

From this directory, the dependency-free public regression commands are:

```sh
python3 -B -m unittest discover -s tools -p 'test_*.py' -q
node --test tools/test_*.cjs
python3 -B tools/build_release.py --output data/release.json --check
```

Results: **59 Python + 58 JavaScript regressions pass** (117 total,
zero failed/skipped; exit code 0). Three additional native-browser runtime
flows pass in each browser (six total, both runner exit codes 0).
Source reproduction and independent root/nested HTTP/hash checks also exit 0.
For browser repetition, follow R1-R6/A1-A5 on isolated copies, use the table
and typed snapshot as the oracle, verify completed saved files, and inject
failures only into disposable copies. No private fixtures or authoring inputs
are required on a publication server.

```text
environment: static HTML/CSS/JS; Node and real Chrome/Firefox available;
             no database, authentication or persistent application state
startup: PASS — isolated local static servers respond at both URL prefixes
integration: PASS — exit_code: 0; 117 regressions, exact source/hash/HTTP checks
e2e: PASS — exit_code: 0 per browser; 3 flows each; native keys/files verified
overall: NEEDS_SIGNOFF — five publication checks and T023-T026 remain open
```

## Independent-copy verification (T022)

**Verified 2026-10-22. Portability: PASS; not publication approval.**
Only this directory was copied to a new temporary location outside the
repository. All **125 shipped files** were inventoried and compared by hash.
The destination was a bare Nginx static server with **no Python, Node, npm or Git**,
no research inputs, pipeline, parent-repository mount, symlinks, authoring
environment or build service. Only the copied public directory and a neutral
static-server configuration were mounted, both read-only. Temporary server
working storage was separate from the site.

The same unchanged copy was served independently at `/` and
`/review/explorer/`. Browser test clients and their drivers were outside the
destination and are not site or hosting dependencies. This verifies
copy-and-serve behavior, not a requirement to use Nginx, containers or a
particular provider.

| Check | Result | Evidence |
|---|---|---|
| Exact independent directory | PASS | All 125 copied file hashes agree before/after; the served tree is read-only and unchanged. No parent research tree or pipeline is available to the static server. |
| Entire HTTP inventory at both prefixes | PASS | Every shipped file returns HTTP 200 with identical bytes at both URLs, including all 49 JSON/CSV pairs, catalog, manifest, application/vendor/license, documentation and tools. The 99-artifact scientific manifest still validates. Publicly reachable does not mean publication-approved. |
| Views and scientific values | PASS | Real Chrome 155.0.8059.84 and Firefox 158.0 each exercise all 49 exact observation tables/generated CSVs and all seven figures with exact source alternatives at both prefixes: 17,046 observation cells per browser/prefix. RQ navigation, definition search, cohort/checkpoint filters, numeric sort, reset and composite team-semester comparison work. |
| Native full and generated downloads | PASS | **808 completed file saves** are checked: all four download kinds for every dataset, plus header-only empty results, in both browsers at both prefixes (792 files), and the additional keyboard-operated comparison downloads (16 files). Full files match original bytes; generated CSVs match the selected exact values/columns/null encoding; companion metadata matches snapshot, scope and definitions. Conflicting filters produce zero rows and reset restores all 14 original cases. |
| No internet asset dependency | PASS | Both browsers use a local **deny-only proxy**, with only loopback site traffic exempt. Reserved-domain negative controls demonstrably fail in each browser; the proxy never forwards requests. All application asset/data requests remain within the active site prefix, with no external or parent-prefix requests and no happy-path console/JavaScript errors. Browser background-service requests are also rejected; they are not reported as site asset requests. |
| Server behavior | PASS | HTML, CSS, JavaScript, JSON, CSV and SVG have appropriate MIME types. Missing/private paths return 404, raw parent-traversal requests are rejected, and dataset-directory listing returns 403. This is local server evidence, not proof of a future host's headers/error pages. |
| Standalone authoring regressions | PASS | Public tests execute from a separate copy with no repository/pipeline input or user-site Python imports; JavaScript syntax and reproducible release hashes pass. These developer-side checks use Python/Node on the test client, not on the static destination. |

The test host's default MIME map did not assign CSV correctly. Adding the
explicit `text/csv` mapping fixed delivery; the complete HTTP/browser checks
were rerun. The later T024 deployment procedure must require MIME verification
rather than assume a server's defaults. This is a server configuration issue,
not a reason to modify approved CSV bytes or add application infrastructure.

The first developer-side test run also inherited read-only fixture permissions
when copying the immutable site, preventing tests that intentionally mutate
their own temporary data. Verification now runs those tests in a separate
writable disposable copy, while the served tree remains read-only throughout.
No test writes into the approved source or served directory. Raw parent paths
can be rejected with HTTP 400/403 as well as 404; no parent content is returned.

All final runtime runners exit 0 (three flows per browser), and all
**60 Python + 58 JavaScript tests pass** (118 regressions, zero failed/skipped).
The new page regression requires this portability evidence and keeps the
11 publication checklist gates unchecked. The final updated documentation
and tests were also copied and rechecked independently. Application/chart
logic, data/catalog/release and vendor/license bytes remain unchanged.
All task browser sessions, test servers, proxy, container and disposable
copies/downloads were cleaned up after verification.

**Historical boundary note:** At the T022 audit point, T023-T026 and actual-host
checks remained open. See the subsequent T023 whole-directory approval and T025
live-host audit below. The T021 audit's five publication checks remain a
point-in-time record, not current deployment status. Firefox headless minimum
width remains 500 px; the 360/320 px browser layout checks are Chrome results,
not Firefox results.

## Whole-directory publication review (T023)

**Sanitized candidate reviewed and explicitly approved by an authorized human
for the later hosting gate, including status-only completion updates.** This review
does not approve an actual public host or a manuscript citation.

The review covers every shipped file, whether linked or not: all 100 data and
manifest files, five browser assets/page files, two vendor/license files, three
documents, and 15 public validation/test files. No hidden files, symlinks,
source maps, private approval records, or authoring inputs are shipped.

Prohibited private-input filenames, research locations, original column mappings,
and private input fingerprints were removed from the public plan, contracts,
and source-specific tools. Their original bytes and originally approved contract
were preserved outside this directory. The public contract now documents only
the unchanged public catalog. Public catalog and release generation still verify
the exact reviewed metadata, not just a weaker structural substitute.

All 49 JSON/CSV pairs, catalog and release bytes, page/browser assets, favicon,
and vendor/license bytes remain unchanged. Private preparation with the original
approved contract reproduces all 98 observation/download files exactly.
The 45 public Python tests, 17 private source-preparation tests, and 58 JavaScript
tests pass. The new privacy regression detected original source references before
sanitation and passes after it. Public schema and serialization helpers also
pass Python syntax validation.

A fresh isolated copy returned all 125 files byte-identically at both `/` and
`/review/explorer/` (250 HTTP checks); all 134 local documentation links resolve.
Chrome and Firefox each rechecked all 49 exact tables/CSV representations and
seven figures at both prefixes, with local-only page resources. Chrome also
passed actual 320/360 px layouts; the Firefox headless minimum was 500 px, so
no narrower Firefox viewport is claimed.

Vendor URLs, contributor notices and copyright names belong to the upstream
chart library, not the paper authors. Required license attribution is retained.
Their presence is not permission to introduce external browser requests.
Upstream namespace/documentation and license URLs are inert here; defaults for
online chart publishing and geographic resources are unused by these Cartesian
figures. The site disables the chart logo and mode bar. Do not enable new vendor
features without repeating dependency, privacy and network review.
Public hashes identify only public artifacts; prohibition strings in test code
are synthetic policy assertions, not private records. Approved lexical patterns
are definitions, not transcript excerpts.

Exact cohort/team labels, small cells, categories, and cross-dataset combinations
retain residual linkage risk. Existing field/value approval is not automatically
extended to revised documentation or another directory. The authorized human
confirmed review of this complete candidate, accepted the stated residual
linkage/anonymity risks, and approved only completion/status-record updates.
T023 is complete; any substantive change requires renewed review. Hosting
branding, HTTPS, redirects, headers and error pages were evaluated during T025.
See the live-host audit and current checklist below; T023 approval alone did
not approve a host or paper citation.

The T021 and T022 sections above are historical candidate evidence. Their
previous directory-reference blockers have been remediated locally; neither
record certifies this changed candidate or a future deployment.

## Live-host verification (T025)

**Actual-host functional and transport checks passed on 2026-10-23.** The
authorized human approved the deployed candidate and explicitly accepted the
generic Netlify badge as a host-branding exception. This exception is not an
author/institution identity finding and does not eliminate residual anonymity
or linkage risk.

The selected static host serves a randomly named HTTPS subdomain without an
identifying author, institution, repository or username in the observed page,
URL, certificate or response headers. HTTP redirects directly to the same HTTPS
host; the verified TLS certificate covers the hostname and HSTS is enabled.
The 404 response is the provider's generic “Page not found” page with a generic
Netlify support link; it revealed no account or author identity. Netlify's
default server and request-ID headers identify the hosting provider, not the
author. No `robots.txt` or `noindex` response is configured; this optional
discovery hint is not access control.

The host injects a `Powered by Netlify` badge/toolbar in an isolated iframe and
modifies the delivered `index.html` with generic Netlify hosting text, a public
project identifier, and a same-origin HUD script. The badge offers a link to
Netlify's public product page that carries that project identifier if clicked.
The human explicitly approved retaining this provider branding as an exception.
Netlify's [badge documentation](https://docs.netlify.com/manage/projects/powered-by-netlify-badge/)
states the badge makes no network requests, sets no cookies, collects no
analytics, and does not identify the owner or team. Browser network checks found
no third-party resource requests during site journeys; the injected HUD script
itself is an additional same-origin request and visible provider branding.

The provider also serves an unlisted `/favicon.ico` containing its own icon.
The page explicitly links and browsers load the approved neutral local
[SVG favicon](assets/favicon.svg); no browser journey requested the provider
icon. The authorized human accepted the unlisted provider icon as a recorded
caveat. Exact comparison found 124 of the 125 candidate paths byte-identical;
the only differing candidate path was `index.html`, modified by the edge
injection. All 99 public data-manifest artifacts, including the catalog, all 49
JSON datasets and all 49 CSV downloads, remain byte-identical to the approved
candidate. This host-generated behavior is not in the site's static source.
This T025 audit was added to the local README after that deployment check; the
live copy still contains the earlier T024 deployment documentation. T026 must
publish and recheck the final documentation before recording the paper citation.

The host returned correct HTML, CSS, JavaScript, JSON, CSV and SVG content types.
Static Markdown and Python/JavaScript authoring files are served as text, not
executed. Data, asset and tools directories, private archive paths and hidden
version-control paths did not expose listings or parent content. Missing paths
returned 404; parent traversal was rejected. No unexpected data or author
identifiers were found in deployed static files.

Chrome 155 and Firefox 158 each passed the complete live-site journey: all 49
exact dataset tables and generated CSVs (17,046 scalar cells), all seven figures
with their source-table alternatives, RQ navigation, definition search, keyboard
filter/sort/reset, cohort-scoped team comparison, full CSV/JSON downloads and
filtered CSV plus scope metadata. Deliberately malformed dataset JSON produced
a visible error with no fabricated rows; restoring the resource and retrying
recovered the full table. Neither browser reported application console or
JavaScript errors on happy paths. Chrome verified 320/360 px layouts without
page overflow; Firefox headless limits its test viewport to 500 px, so no
narrower Firefox claim is made. All application resources stayed on the site
origin; Netlify's host-injected script is the exception to byte-pure source
delivery, explicitly accepted above.

Ten hosting checks below are verified, subject to the documented platform
branding/icon exceptions and their explicit human acceptance. The eleventh
check—recording the public URL and snapshot for the separate paper citation—is
reserved for T026. These results do not claim that a public anonymous host
removes linkage risk, that `noindex` is enabled, or that the hosting provider
does not retain its ordinary infrastructure logs.

## Public-safe naming

- Use neutral English titles, dataset identifiers, filenames, labels, and
  snapshot identifiers. RQ1-RQ3 and M1-M9 are paper-aligned navigation labels,
  not permission to include additional evidence.
- Original cohort labels and existing TEAM labels are explicitly approved for
  this snapshot. A team-semester is identified by `(cohort, team_id)`; TEAM labels
  repeat between cohorts and must never be treated as global identifiers.
- Use evidence-source labels such as "Survey summaries", "Repository activity",
  and "Transcript lexical aggregates", rather than source repository URLs,
  personal names, institution names, or internal source locations.
- Map source names/categories only through approved dictionaries. Do not infer
  identities, apply ad hoc text replacement, or rename scientific categories in
  ways that change their meaning. Unlisted fields are denied by default.
- Use relative asset, data, and download URLs. Public provenance will describe
  the exported snapshot with its neutral identifier, schema version, public
  artifact hashes, row counts, and coverage, not research-repository commits or
  confidential lineage.

Naming is not anonymization: exact values, small cells, cohort labels, and
project profiles may still be linkable. The authorized human review accepted
that residual risk for the pinned field/value scope; it did not certify
non-identifiability or approve new values automatically.

## What may be included

Only the submitted-paper inventory and explicitly approved projections may be
exported. JSON and CSV must come from the same approved rows, with the original
scientific precision, denominators, coverage, eligibility, and missingness.
Definitions and metadata are selected fields, not wholesale source-file copies.

Keep surveys at cohort/checkpoint or cohort/checkpoint/role grain. Repository
profiles use cohort-plus-team keys. Transcript lexical aggregates belong only to
the measured corpus/checkpoint, not to individual teams or unmeasured cohorts.
Published pooled summaries and association estimates keep their original
populations and sample sizes when rows are filtered. Missing or ineligible
measurements are not zero.

Exact approved values, including small positive cells, may be released without
introducing an unapproved suppression threshold. If a value must be withheld,
explain the limitation; never silently perturb it or fabricate a substitute.

## Exclusions: never ship these

- Author, institution, participant, respondent, or repository-author identities;
  respondent hashes, personal contacts, credentials, or secrets.
- Source repository links, commit hashes, exact commit subjects, identifying
  source filenames, absolute timestamps, or private source locations.
- Full transcripts, transcript audit trails, raw free-text responses, raw
  evaluation votes, prompts, model output, or extraction/audit records.
- Internal input inventories, metadata files, source manifests, list-valued
  provenance, private identity crosswalks, or approval/reviewer records.
- Unapproved datasets, fields, category vocabularies, hidden payloads, or
  verification-only inputs used to derive an approved public projection.
- Analytics, trackers, social widgets, author-attributed deployment badges,
  external fonts, CDN dependencies, or public source-repository links.
- Version-control history, local environment files, logs, backups, symlinks,
  parent-directory imports, or source maps containing private paths.

Keep private review records and confidential lineage outside this directory.
Do not publish this README with a filled-in private location or reviewer name.
Every shipped file is public, including documentation, tools, comments, hidden
files, and unlinked assets. Removing a navigation link is not access control.
Retain required third-party license notices; review their content without
stripping attribution obligations.

## Excerpt policy for this release

The human decision is to **omit all verbatim excerpts**. The approved-excerpt set
is empty by choice, not because extraction failed or qualitative evidence is
absent.

- Do not create an excerpt dataset, even as an empty JSON placeholder.
- Do not provide an excerpt descriptor, navigation item, view, search index,
  download, dataset request, or hidden quote text in application assets.
- Approved lexical aggregates, coding definitions, and structured planning
  evidence counts remain in scope. A quote count does not authorize its text.
- To add excerpts later, reopen the individual approval process for each exact
  text and its public context. Review searchable text, linkage, coverage, and any
  translation; review and label translations explicitly. Renew affected
  field/snapshot approval as needed before enabling an excerpt feature.

The later application and release checks must enforce the no-excerpt branch;
recording this policy alone does not complete those checks.

## Anonymous-hosting checklist

- [x] Review all directory contents, including HTML/JavaScript source, comments,
  JSON/CSV, downloadable headers, filenames, chart metadata, docs, tools, license
  notices, hidden files, and error messages. T023 reviewed the candidate; T025
  compared all hosted paths and inspected the only edge-modified HTML. No
  excluded private content was found.
- [x] Confirm exported fields and actual values match the approved snapshot and
  contracts. The authorized review accepted remaining searchable/category
  combinations and linkage risks; all 99 manifest artifacts match byte-for-byte.
- [x] Confirm that no excerpt payload, descriptor, request, or feature exists.
- [x] Inspect the host/domain/account presentation and URL path for author or
  institution branding. No author, institution, repository or username identity
  was found. Explicit exception: the authorized human accepted the generic
  Netlify badge/edge injection and unlisted provider favicon; see T025 above.
  The host is not provider-brand-free; this is a documented waiver, not a claim
  that the requirement was met without exception. Count this gate as waived,
  not passed.
- [x] Inspect actual redirect destinations, HTTP headers, TLS/browser-visible
  identity, generated error pages (including 404s), and directory responses for
  identifying account or server details. Only generic provider branding and
  request IDs were observed; no author/account identifiers were found.
- [x] Disable directory listing. Ensure only the intended directory is served;
  private records, research inputs, and version-control history must not be
  reachable through aliases or parent paths. Directory indexes, private paths
  and parent traversal were tested; `/favicon.ico` is an unlisted provider icon.
- [x] Confirm appropriate HTML, CSS, JavaScript, JSON, and CSV MIME types. Serve
  the directory over HTTP(S), not a `file://` URL. Valid HTTPS/TLS and direct
  HTTP-to-HTTPS redirection were verified.
- [x] Verify an isolated copy at both domain root and a nested URL path, with
  relative links and no parent-directory or external network requests. No
  backend, database, account, package installation, build step, Python runtime,
  or research pipeline is required on the destination host. Root/nested checks
  are recorded under T022; actual-host runtime requests remained same-origin.
- [x] On the actual host, repeat browse/filter/reset/compare/download checks,
  verify snapshot hashes and row counts, and check browser network requests and
  errors. Chrome and Firefox passed all core journeys; malformed-data errors and
  recovery were verified in Chrome.
- [x] Confirm no telemetry or third-party runtime requests are introduced by the
  host or bundled code. Netlify's HUD was accepted as an explicit provider
  branding exception; its official documentation says it performs no tracking
  or network calls. Normal site journeys made no third-party resource requests.
  Optional `noindex` is only a discovery hint, not privacy, anonymity, or access
  control. No `robots.txt`/`noindex` is configured.
- [ ] Record the verified public URL and snapshot identifier only after approval
  and deployment verification; update the paper citation separately (T026).

**Status: 9 checks passed, 1 branding gate explicitly waived, and 1 remains
pending for T026.** The T025 reviewer explicitly accepted the stated generic
Netlify branding and default-icon exceptions; if that waiver is withdrawn, turn
off the badge or move the site to a host that meets the no-provider-branding
requirement and repeat the review.
If private material is ever served, remove it promptly and seek human
reassessment; removal cannot guarantee that public copies or caches disappear.

## Copy, serve, and refresh (T024)

This is a provider-neutral procedure, not a deployment record. T025 has verified
the actual host after human release approval; see the live-host findings above.
T026 records the verified public URL and snapshot identifier and supplies the
URL for the separate paper citation change. The exact URL is intentionally
reserved for that task. The authorized T025 exception is limited to this
generic host branding and icon; no author/account identity was found.

The copy and catalog/release check commands below were verified in a disposable
copy: all 45 public Python tests passed, all 125 file bytes matched over HTTP at
both root and nested prefixes (250 checks), and local documentation links
resolved. The copied site was not modified by validation; preview processes and
temporary copies were removed. This verifies the local procedure, not HTTPS,
production server configuration, human approval of this update, or an actual host.

### 1. Prepare an isolated deployment candidate

On a local authoring/test machine, set `SITE` to the absolute path of this
directory and `STAGING` to a **new, non-existent directory outside the repository
and outside every currently served tree**. Its parent must already exist.
Do not use either variable for a repository root, private archive, or existing
release. Check the chosen paths before running:

```sh
mkdir "$STAGING" &&
cp -R "$SITE/." "$STAGING/"
```

Stop on any command failure; do not continue with a partial copy. This copies the
directory's contents, including otherwise hidden/unlinked files: **all shipped
files are public**. Inspect the complete candidate, not just the landing page.
Never copy the parent repository, private authoring archive, version-control
history, approvals, lineage, environment files, logs, backups, or research inputs.
Do not rely on a host's hidden-file block or disabled directory listing to
protect material that should not have been uploaded.

Compare the full candidate inventory and bytes with the reviewed site using
local file-comparison/hash tools; include documentation, tools, assets and vendor
notices. The data manifest alone does not cover these files. Keep the approved
whole-directory inventory and review evidence privately, outside the candidate.
Retain mandatory upstream licenses. Reject symlinks and unexpected files.

From the candidate, check the frozen catalog and data manifest:

```sh
cd "$STAGING" &&
python3 -B tools/build_catalog.py --output data/catalog.json --check &&
python3 -B tools/build_release.py --output data/release.json --check
```

Use the existing public tests under [Public validation tooling](#public-validation-tooling)
on this local machine. A failure is a release blocker, not a reason to regenerate
hashes until the check turns green. Python and Node are test/authoring tools;
neither is required on the destination server.

### 2. Preview locally over HTTP

For a loopback-only development preview, from the candidate directory run:

```sh
python3 -B -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/` and stop the preview with Ctrl+C when finished.
If the port is occupied, choose an unused local port; do not stop unrelated
processes. This development server is **not a public hosting configuration**:
it can list directories, uses HTTP, and has not been approved for public exposure.
Do not use `file://`, whose fetch behavior is not the supported serving model.

For a nested-prefix preview, place a second copy of the candidate at
`review/explorer/` inside a new otherwise empty preview root, serve that root
with the same loopback command, and open
`http://127.0.0.1:8000/review/explorer/`. Keep private material outside both
preview roots. All app links remain relative; do not rewrite them with a domain
name, leading slash, or parent-directory URL. Check browser Network and Console,
then stop the server and remove only the explicitly created disposable copies.

### 3. Configure an ordinary static host

Use a neutral HTTPS domain/account presentation and neutral URL prefix with no
author, institution, repository, username, identifying redirect, badge, injected
branding, tracking script, or external asset requirement. Review browser-visible
certificate information and provider-generated pages as well as the URL.
Optional `noindex` is a discovery hint, not anonymity or access control.

Configure the host using its normal static-document-root or subdirectory mapping:

- Serve **only the candidate's contents**, at `/` or a prefix such as
  `/review/explorer/`, with `index.html` as the directory index.
- Disable directory listing. Missing files must return an actual 404, not the
  landing page with a successful 200 response; do not enable SPA fallback.
- Expose no parent aliases or adjacent directories. A missing directory index
  should yield a neutral rejection rather than a file inventory.
- Serve HTML/CSS/JavaScript/JSON/CSV/SVG as the MIME types below. Configure CSV
  explicitly if the server defaults to binary data. `nosniff` is useful only
  with correct content types.
- Require valid HTTPS for the public URL. If HTTP redirects to HTTPS, inspect
  the exact destination and intervening responses for identifying hostnames.
  Do not bypass certificate errors or accept mixed-content requests.
- Disable provider telemetry/injection and identifying custom error pages.
  Inspect response headers, redirects, TLS presentation and errors; remove
  identifying account details. Change host if these cannot be neutralized.
- During submission, prefer revalidation (for example `Cache-Control: no-cache`)
  for HTML, scripts, catalog and release metadata to avoid mixing revisions.
  Do not mark mutable paths immutable; if a CDN/cache is present, verify its
  invalidation behavior before a refresh.

| File extension | Expected Content-Type |
|---|---|
| `.html` | `text/html; charset=utf-8` |
| `.css` | `text/css; charset=utf-8` |
| `.js` | `text/javascript` or `application/javascript` |
| `.json` | `application/json` |
| `.csv` | `text/csv; charset=utf-8` |
| `.svg` | `image/svg+xml` |
| `.md`, `.txt` | `text/plain; charset=utf-8` (not executable content) |
| `.py`, `.cjs` | Static text/download only; never server-side execution |

A download disposition is acceptable for static documentation/tools. Markdown
rendering, if offered by the provider, must not add account branding or scripts.
No backend, database, account system, build service, package installation,
research pipeline, Python or Node runtime is needed on the destination.

### 4. Copy and verify on the actual host (T025)

After human approval of the exact candidate, upload only its contents through
the host's ordinary file-copy/upload mechanism. Transfer as bytes: disable
newline conversion, minification, data reformatting, template processing and
provider script injection. Keep credentials and upload logs outside this
directory. Prefer a complete replacement/switch of a separately uploaded
candidate, not a merge that can retain stale or private files.

Before announcing the URL, compare remotely retrieved files against the approved
local whole-directory inventory, including all public assets and tools, and
recheck the 99 data-artifact hashes/counts against the local approved manifest.
Retrieve bytes with a local HTTP client or browser; no verifier is installed on
the destination. A matching remote manifest alone is insufficient: compare it
to the trusted local one and verify the artifacts it names.

T025 verified the published candidate with one accepted host transformation:
Netlify modifies `index.html` and serves its own unlisted `/favicon.ico`.
The authorized human explicitly accepted these exceptions for this deployment;
they do not satisfy a strict provider-brand-free copy requirement. Any later
change of host, badge setting, deployment copy, or exception requires a new
actual-host check before T026 records the URL for citation.

Check the landing page, stylesheet, scripts, favicon, catalog, release manifest,
a JSON dataset and CSV download for status and MIME type. Inspect HTTPS and HTTP
redirect chains manually, including non-trailing-slash URLs; inspect headers,
neutral 404 responses and directory responses. A directory with an index may
return that index, but a directory without one must not list its contents.
Check that parent/adjacent private paths are unreachable without publishing or
guessing actual private names in this README.

In current Chromium and Firefox, repeat RQ navigation, definitions, exact table
values, cohort/checkpoint selection, composite team comparison, numeric sorting,
reset, seven figures/source alternatives, full downloads, and filtered CSV plus
scope metadata. Confirm no unsupported survey/transcript team filters appear.
Check keyboard use and narrow layouts. Inspect Network/Console for missing
assets, out-of-prefix or third-party requests, mixed content and errors.
Use a disposable private preview for missing/malformed-data recovery tests;
do not corrupt the public approved snapshot to test error handling.

Stop publication on any failed check, correct the copy/configuration or choose
another host, and repeat verification. Do not cite an unverified deployment.
T025 has verified this deployment with the explicitly accepted exceptions
recorded above. T026 may record the URL and snapshot only after the final
published copy is checked. This procedure does not change the data manifest's
release status or imply the hosting provider retains no infrastructure logs.

### 5. Refresh or roll back without changing evidence silently

Keep the last approved directory and private review/inventory outside the served
tree. Prepare every refresh in a new candidate, never edit the live snapshot:

1. Reconcile privately pinned inputs and reproduce the approved projection.
   Renew human review for changed fields, values, vocabulary, identifiers,
   excerpt policy, documentation/tools or linkage risk. Changed hashes never
   silently inherit approval. Verbatim excerpts remain omitted.
2. For changed scientific data, assign a new neutral snapshot identifier and
   update the authoring contract/tests deliberately; do not reuse
   `research-data-001` to conceal changed observations. A documentation-only
   update does not require changing unchanged data or its snapshot identifier.
3. Preserve exact numeric precision, JSON/CSV parity, null/eligibility states,
   units, denominators and fixed populations. Generate any changed catalog or
   release manifest to a new path, review the differences, and run the existing
   catalog/release `--check` commands and tests on the complete candidate.
4. Repeat whole-directory human review, isolated root/nested checks and the
   actual-host procedure above. Review all new/removed files, not only manifest
   entries. Switch the entire reviewed directory consistently and invalidate or
   revalidate caches; do not leave old files in a merged deployment.
5. If verification fails, stop announcing/serving the affected candidate and
   restore the entire last approved directory only if it remains safe; repeat
   deployed hash, cache and browser checks. Never restore a candidate known to
   contain private material. Seek renewed human assessment for an exposure;
   removal cannot guarantee deletion from caches or third-party copies.

Keep operational evidence private. Update the public release record and paper
citation only after the replacement is verified, without exposing source paths,
reviewer identities, credentials or private lineage.

## Public validation tooling

Only source-free public validation tools are shipped. The source preparation
utility, original pinned contract, private input mappings and authoring history
are retained outside this directory and must never be deployed. Runtime files,
data, public catalog generation and release validation do not import them.

Run public tests with Python 3.10+ and Node 18+ on an authoring/test machine:

```sh
python3 -B -m unittest discover -s tools -p 'test_*.py'
node --test tools/test_*.cjs
```

Neither interpreter is required by the static hosting server. The
[serialization helpers](tools/snapshot_io.py) preserve the original JSON/CSV
bytes. [Public schemas](tools/public_schema.py) specify only public keys and
ordered columns; catalog generation still compares every reviewed metadata value.
Public tests cannot prove agreement with private originals or authorize release.
Private source reproduction and renewed human review remain necessary for
changed fields, values, category vocabularies, or identifier policies.

## Catalog metadata (T007)

[The catalog](data/catalog.json) has schema version `1.0`, 49 dataset
descriptors, and seven paper-figure mappings. It describes public columns,
types, units, null states, original denominators, coverage, valid filters, frozen
thresholds, and permitted relationships. Definition-only rows are embedded under
`methods.definition_sets`; they are not extra observation datasets. Source labels
are neutral and no confidential source paths, hashes, approvals, or observations
are embedded. English display labels do not rewrite source category values.

All catalog data/download paths are relative to the **site root**, not relative
to the catalog file. For example, `data/datasets/<dataset-id>.json` is resolved
from the page alongside this README, including at a nested hosting path.
All 49 JSON paths and 49 CSV paths now resolve to the approved T008 snapshot:
1,674 observation rows and 17,046 scalar cells per format. JSON/CSV pairs preserve
identical row order, column order, and values. The catalog is marked
`snapshot_prepared_release_pending`; this is not full-site publication approval.
Do not present missing files as empty datasets.

Use the local, standard-library [catalog authoring tool](tools/build_catalog.py)
to verify saved bytes:

```sh
python3 -B tools/build_catalog.py --output data/catalog.json --check
```

To regenerate a candidate after an intentional metadata change, set
`NEW_CATALOG_OUTPUT` to a new file with an existing parent directory:

```sh
python3 -B tools/build_catalog.py --output "$NEW_CATALOG_OUTPUT"
```

The tool refuses overwrites and needs no research inputs at runtime or authoring
time: its descriptors use only explicit public contract definitions. Compare and
review the candidate before replacing the saved catalog. For changes to the
underlying approved scope or values, reconcile source fingerprints and obtain
renewed approval first; catalog generation is not a publication authorization.
Catalog and shipped-snapshot tests run with the same test command above, using
only local public files. They check exact inventory, deterministic serialization,
JSON/CSV parity, column types, nullability, keys, coverage, and scientific
missingness. Authoring verification must also reproduce every exported byte
from the pinned approved inputs; public-file tests alone cannot prove provenance.
Distinct profile/figure inputs retain their own original numeric precision;
cross-table ratio comparisons use the preparation contract's `1e-12` absolute
tolerance without rounding or rewriting exported values.

## Public release metadata (T009)

[The release manifest](data/release.json) identifies the frozen public snapshot
as `research-data-001`, with manifest schema version `1.0`. Its
`snapshot_prepared_release_pending` status is not publication approval.
It contains only public metadata:

- SHA-256 and byte length for the catalog and every approved observation JSON
  and CSV download: 99 artifacts, with paths relative to the site root.
- Per-file and per-dataset row counts; per-dataset column counts; 49 datasets,
  1,674 observation rows, and 17,046 scalar cells counted once across JSON,
  not doubled by CSV. These are exported rows, not independent participant Ns.
- Catalog-declared coverage plus observed cohort/checkpoint lists where those
  columns exist, distinct team-semester counts only for team-keyed datasets,
  measurement/ratio-status counts, baseline eligibility, and transcript chunks.
  Pooled datasets retain original denominator fields; transcript coverage is
  restricted to the measured corpus and is never attributed to teams.

The hash scope is the **data snapshot**, not every site file. The manifest
excludes its own hash to avoid circularity and excludes documentation, tools,
and application assets. Future application/host review still covers those files.
Hash equality detects byte changes; it does not establish anonymity, scientific
approval, or authenticity against malicious replacement of both data and manifest.
No Git identifiers, private source hashes/locations, approval records, reviewer
identities, confidential lineage, or authoring timestamps are included.

Check all saved metadata from this directory with the local, standard-library
[release authoring tool](tools/build_release.py):

```sh
python3 -B tools/build_release.py --output data/release.json --check
```

It needs only this directory's public files. It validates the reviewed catalog,
exact data inventory, columns/types/nulls/keys, canonical JSON, and JSON/CSV
agreement before computing hashes and counts. Missing or malformed inputs,
symlinks, extra files under `data/`, and stale manifest bytes fail explicitly.
Existing output files are never overwritten.

For an intentionally reviewed refresh, prepare a separate candidate site and
set `CANDIDATE_SITE` and `NEW_RELEASE_OUTPUT` to that site and a new output path:

```sh
python3 -B tools/build_release.py \
  --site-root "$CANDIDATE_SITE" --output "$NEW_RELEASE_OUTPUT"
```

Investigate a stale check before regenerating: restore accidentally modified
public bytes from the approved snapshot, or reconcile intentional input changes,
renew affected approval, and prepare a new snapshot. A genuinely new data
snapshot must receive a new neutral identifier in the authoring tool and its
tests; do not reuse `research-data-001` to hide changed data. Review the new
manifest before installing it, then rerun `--check` and the full local test
command above. Do not copy confidential lineage into the candidate or release.
