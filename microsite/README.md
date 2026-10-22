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
observation tables, row filters, and sorting are implemented. Multi-case comparisons,
figures, and export controls remain pending, and
whole-directory/actual-host approval remains pending.
This is not a ready-to-publish site.
See the [implementation plan](plan.md) for task status and the
[dataset contracts](dataset-contracts.md) for scientific definitions and explicit
field projections.

## Page shell (T010)

[The entry page](index.html) has three semantic sections: overview, explore,
and measures/methods. Main navigation and the three RQ cards use native fragment
links and work without JavaScript. A visible skip link moves keyboard focus to
the main content. The overview explains survey, team-semester, global transcript,
and fixed-estimate grains before the research-question guides.

The styled explorer now loads approved observation rows on dataset selection.
The page states that multi-case comparisons, figures, and export controls are pending.
Local catalog, release-manifest, and documentation links work.
T011 provides layout/focus styling; T012 provides catalog loading and
dataset navigation; T013 provides row filters/tables/sorting. Charts and export actions remain later tasks.
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
step. Nine JavaScript tests use only Node's built-in runner and the public files:
metadata/schema errors, cross-RQ navigation, definition matching, HTTP/JSON
failure, request scope, and abort timeout.

## Observation tables and row filters (T013)

Selecting a dataset requests only its local JSON file, validates its exact
column order, scalar types/nullability, finite values, unique analytical keys,
and frozen row count, then renders all rows without rounding or pagination.
Metadata and observation loading/errors are separate. Changing datasets cancels
the previous request and invalidates stale responses, clears filters/sort, and
removes the old table while the new file loads. A failed, malformed, missing, or
timed-out file produces a logged error, no rows, disabled row controls, and retry;
it is never presented as a successful empty dataset.

Each catalog-approved filter is a labeled native selector with All plus observed
typed values. At this stage choose **one value per filter**; T014 will extend
cohort/team-semester selection for multi-case comparisons. Team and omitted-case
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

Twelve additional built-in Node tests cover all 49 datasets, every approved
filter choice, composite keys, empty intersections/reset, stable numeric/text/
boolean/null sorting, exact display, fixed estimates, and fetch errors/cancellation/
timeout. Run both JavaScript test files with one command:

```sh
node --test tools/test_app.cjs tools/test_rows.cjs
```

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
