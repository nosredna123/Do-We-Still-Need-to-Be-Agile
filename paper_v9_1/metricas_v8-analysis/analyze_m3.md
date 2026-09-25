# M3 V8 Analysis and V9 Decision

## V8 findings

M3 belongs to RQ2 and does not measure AI use or coordination friction directly.
The v8 review recommends a final-phase commit-share measure anchored at the
last T3 evaluator vote for each team-semester, using seven days before and
seven days after the anchor. Author concentration and rolling activity remain
contextual outputs. The legacy CSV is arithmetically reproducible but its
pre-T3 aggregation does not implement the reviewed final-vote window.

## V9 outputs

- `m3_author_activity_participation.csv`: M3a, with total denominator commits,
  pre/post counts and shares, final-window share, and small-denominator flag.
- `m3_author_concentration.csv`: M3b, with phase-specific commit counts,
  active days, author counts, maximum author share, and Gini. Missing activity
  is `no_observed_activity`, not a concentration of zero.
- `m3_activity_rolling_7day.csv`: M3c, 29 overlapping seven-day windows from
  day -21 through +7 relative to the last T3 vote.
- `m3_activity_rolling_7day_pooled.csv`: secondary M3c view aggregated across
  semesters by relative window end, without a `Semestre` dimension.

All authors are represented by short hashes in private processing and no author
identity is exported. The source is the default branch of read-only parent
mirrors and temporal inclusion uses committer timestamps.

## V8-to-V9 traceability

| V8 recommendation | V9 decision | Status | Evidence | Limitation |
|---|---|---|---|---|
| Link M3 to RQ2 | Validate the current paper section before processing | `applied` | Producer anchor contract and notebook | RQ linkage changes require rerun |
| Use the last T3 evaluator vote as anchor | Derive one latest T3 vote per team-semester | `applied` | M3 metadata and participation CSV | Vote is an operational proxy for presentation end |
| Use symmetric seven-day pre/post phases | Persist `pre` and `post` separately around the anchor | `applied` | Concentration CSV | Post activity is not automatically authorized |
| Make final commit share the primary result | Persist numerator, denominator, shares, and small denominators | `applied` | Participation CSV | Low denominators remain sensitive |
| Keep authorship concentration separate | Persist M3b phase context, without a composite score | `applied` | Concentration CSV | Authorship does not measure effort or coordination |
| Add rolling seven-day dynamics | Persist 29 overlapping windows from -21 to +7 | `applied` | Rolling CSV and notebook figures | Windows are autocorrelated |
| Use parent default-branch mirrors and committer date | Read mirrors without pushing or mutating them | `applied` | Producer and metadata | Mirror history cannot identify the person who pushed a remote update |
| Report no activity separately | Use `no_observed_activity` for phase/rolling concentration | `applied` | M3b and M3c outputs | No activity is not evidence of planning quality |
| Remove misleading AI naming | Use M3-neutral artifact names | `applied` | v9 artifact filenames | Legacy v8 names remain frozen |
| Preserve legacy for sensitivity | Compare v8 rows to v9 only where grains are compatible | `partially_applied` | Analysis and notebook | Legacy pre-T3 window is retained as context, not the primary M3 |

## Preliminary RQ2 interpretation

M3 describes when repository activity concentrates and whether final activity is
dominated by a small number of authors. It supplies temporal and authorship
context for the RQ2 contrast with M4 clean-change magnitude and M5 qualitative
coordination evidence. It does not establish friction, effort, productivity,
planning quality, or causality.

## Gate status

M3a--M3c is **APPROVED for the descriptive v9 scope** on 2026-09-24. The
approval includes the semester-stratified rolling series and the secondary
pooled-by-relative-window M3c view. M3 remains contextual RQ2 evidence: it does
not measure coordination friction, effort, productivity, planning quality, or
causality.
