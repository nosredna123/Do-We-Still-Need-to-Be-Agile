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
metadata are implemented. Whole-directory/actual-host approval remains pending.
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
for the CSV conventions and failure states. No neutral public URL or final
whole-directory/actual-host approval has been recorded yet.

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
anonymous-publication checklist. All 11 hosting/release boxes below remain
unchecked. These local acceptance results did not themselves complete T022-T026;
the subsequent T022 portability verification is recorded below. T023-T026
remain pending.

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

`NOT PASSED` is a blocking release result, not an implied approval or an
unreported test failure. These checks require later whole-directory or
actual-host evidence that local functional tests cannot supply.

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

**Remaining boundaries:** T023-T026 still require every-file privacy review
and neutralization of prohibited source references, human linkage-risk/release
approval, provider-neutral deployment documentation, neutral HTTPS-host
verification and the separate citation update. The T021 audit's five
publication checks remain NOT PASSED. No real public URL or anonymous-host
approval is implied. Firefox headless minimum width remains 500 px; the
360/320 px browser layout checks are Chrome results, not Firefox results.

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

**All checks below remain release gates.** Documentation and field approval are
not approval of the final directory or the actual host. Complete the
whole-directory review and obtain human release approval before public copying,
then verify the deployed result.

- [ ] Review all directory contents, including HTML/JavaScript source, comments,
  JSON/CSV, downloadable headers, filenames, chart metadata, docs, tools, license
  notices, hidden files, and error messages. Remove excluded material rather
  than merely hiding it in the UI.
- [ ] Confirm exported fields and actual values match the approved snapshot and
  contracts. Assess remaining searchable/category combinations and linkage
  risks through human review; automated string scans alone are not proof.
- [ ] Confirm that no excerpt payload, descriptor, request, or feature exists.
- [ ] Inspect the host/domain/account presentation and URL path for author or
  institution branding. Use a neutral HTTPS URL with no identifying redirects,
  public repository links, deployment badges, or provider-injected branding.
- [ ] Inspect actual redirect destinations, HTTP headers, TLS/browser-visible
  identity, generated error pages (including 404s), and directory responses for
  identifying account or server details.
- [ ] Disable directory listing. Ensure only the intended directory is served;
  private records, research inputs, and version-control history must not be
  reachable through aliases or parent paths.
- [ ] Confirm appropriate HTML, CSS, JavaScript, JSON, and CSV MIME types. Serve
  the directory over HTTP(S), not a `file://` URL.
- [ ] Verify an isolated copy at both domain root and a nested URL path, with
  relative links and no parent-directory or external network requests. No
  backend, database, account, package installation, build step, Python runtime,
  or research pipeline may be required on the destination host.
- [ ] On the actual host, repeat browse/filter/reset/compare/download checks,
  verify snapshot hashes and row counts, and check browser network requests and
  errors. Check that failed loads show errors rather than fabricated data.
- [ ] Confirm no telemetry or third-party runtime requests are introduced by the
  host or bundled code. Optional `noindex` is only a discovery hint, not privacy,
  anonymity, or access control.
- [ ] Record the verified neutral public URL and snapshot identifier only after
  approval and deployment verification; update the paper citation separately.

If a check fails, stop the affected release, identify the exposed content or
host behavior, correct it, and repeat the check. Changing the host is preferable
to accepting unavoidable identifying branding. If private material was already
served, remove it promptly and seek human reassessment; removal cannot guarantee
that public copies or caches disappear.

## Remaining operational documentation

The later deployment task will add the provider-neutral copy-and-serve procedure,
preview instructions, and release refresh procedure once the application exists.
No deployment URL is claimed here yet. A refresh must verify input fingerprints,
obtain renewed review for changed fields/values/vocabularies or identifier policy,
export only approved rows, and repeat whole-directory and actual-host checks.
Changed hashes must never silently inherit an earlier approval.

## Snapshot authoring (T006)

The preparation utility is implemented; no public observation snapshot has been
released yet. Authoring requires Python 3.10+ with only its standard library.
Python is **not** required to serve the resulting static files.
The tool and its [projection definitions](tools/snapshot_contracts.py) are local
to this directory and import nothing from the research pipeline.

From this directory, set the variables below to explicitly selected local
inputs, then validate without writing:

```sh
python3 -B tools/prepare_snapshot.py \
  --source-root "$SOURCE_ROOT" \
  --approval "$PUBLICATION_APPROVAL" \
  --registry "$IDENTIFIER_REGISTRY" \
  --excerpt-decision "$EXCERPT_DECISION" \
  --check
```

- `SOURCE_ROOT` is the selected research snapshot root containing its indexed
  metric and figure inputs, not a repository inferred from the current directory.
- The other three inputs are the private T003 publication record, private
  cohort/team registry, and private T004 omission decision. All must remain
  outside this directory and the public output. No example private locations
  or reviewer identities should be added here.
- The tool supports only the currently pinned contract/index and approved
  no-excerpt decision. It also pins the eight selected figure/support inputs
  absent from the results index as one supplementary set. Hash, schema, row
  count, key, alias, coverage, or required join failures block preparation.
  Changed inputs require reconciliation and renewed review, not a bypass flag.

After successful validation, prepare a candidate in a **new** output directory:

```sh
python3 -B tools/prepare_snapshot.py \
  --source-root "$SOURCE_ROOT" \
  --approval "$PUBLICATION_APPROVAL" \
  --registry "$IDENTIFIER_REGISTRY" \
  --excerpt-decision "$EXCERPT_DECISION" \
  --output "$PUBLIC_DATA_OUTPUT" \
  --private-lineage "$PRIVATE_LINEAGE_OUTPUT"
```

Both output paths must be new, with existing parent directories. Symlink paths
and overwrites are rejected. `PUBLIC_DATA_OUTPUT` is a data directory, not the
site root. It receives `datasets/<dataset-id>.json` and
`downloads/<dataset-id>.csv`: 49 matched dataset pairs in the current snapshot.
Two `definitions/<definition-id>.json` files hold reviewed definition-only rows,
not duplicate data-browser tabs. The catalog already embeds their 13 weekly-bin
and 13 complexity definitions; these preparation outputs can verify agreement.
The release manifest is generated separately as described under T009 below.

The T008 snapshot installs only the candidate's `datasets/` and `downloads/`
directories under `data/`, after catalog/schema and source-byte agreement checks.
The existing catalog is retained; do not pass the existing `data/` directory as
the preparation output or copy the private lineage. Do not install redundant
`definitions/` files: compare them with the embedded catalog definitions instead.
For future replacements, validate a separate candidate copy of the site and
repeat release review rather than overwriting the approved release in place.

`PRIVATE_LINEAGE_OUTPUT` must be outside this directory and the public output.
It records source fingerprints and exact original ratio cells before eligibility
masking, with private file permissions. Never copy it into a release.
Serialization and scientific checks run before public files are installed;
validation failures are logged explicitly and exit nonzero, without a partial
public snapshot. Existing releases are never modified in place.

JSON preserves typed scalar values; CSV uses the same rows/columns, lowercase
`true`/`false`, standard quoting, and empty cells for nulls. M8-ineligible or
zero-denominator ratios are null with explicit `ratio_status`; exact eligible
values remain unchanged. Text cells that could act as spreadsheet formulas are
rejected rather than silently altered. Any future need to export such text
requires a reviewed safety policy. No raw JSON records, quotes, or hidden source
columns are copied.

Run the synthetic and shipped-snapshot standard-library tests without generating
bytecode in this publishable directory:

```sh
python3 -B -m unittest discover -s tools -p 'test_*.py'
```

Preparation and successful tests do not replace whole-directory human release
approval or verification on the actual anonymous host.

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
