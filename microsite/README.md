# Anonymous Research Data Explorer

An English-language companion for navigating the submitted paper's approved
research data. The intended implementation is plain static HTML, CSS, JavaScript,
and local JSON/CSV, contained entirely in this directory.

**Current status:** publication boundaries, the preparation tool, and the
[public catalog](data/catalog.json) are implemented. The application and public
observation/download snapshot are not implemented. This is not a ready-to-publish site.
See the [implementation plan](plan.md) for task status and the
[dataset contracts](dataset-contracts.md) for scientific definitions and explicit
field projections.

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
Release metadata remains a separate task.

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

Run the synthetic standard-library tests without generating bytecode in this
publishable directory:

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
These paths describe future T008 files; they do not claim those files exist yet.
The catalog is marked `metadata_only_datasets_pending` until that stage is
reconciled. Do not present missing files as empty datasets.

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
Catalog tests run with the same synthetic test command above. Before observation
exports, also verify column types, nullability, keys, and filters against the
approved prepared rows.
