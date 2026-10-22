# Anonymous Research Data Explorer

An English-language companion for navigating the submitted paper's approved
research data. The intended implementation is plain static HTML, CSS, JavaScript,
and local JSON/CSV, contained entirely in this directory.

**Current status:** publication boundaries are documented, but the application
and public snapshot are not implemented. This is not a ready-to-publish site.
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
preview instructions, and refresh commands once the application and snapshot
preparation utility exist. No runnable commands or deployment URL are claimed
here yet. A refresh must verify input fingerprints, obtain renewed review for
changed fields/values/vocabularies or identifier policy, export only approved
rows, and repeat whole-directory and actual-host checks. Changed hashes must
never silently inherit an earlier approval.
