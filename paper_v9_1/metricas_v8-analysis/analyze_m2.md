# M2 V8 Analysis and V9 Decision

## V8 computation

V8 reads six structured role-disruption Likert questions from
`data/lake/student_responses.parquet`. The roles are Backend, Frontend, QA,
Project Manager, Product Manager, and Scrum Master. Responses use a 1--5
agreement scale for the combined statement that a role will be eliminated or
severely affected by generative AI. V8 summarizes each role by
`Semestre × temporal_marker × role` with n, mean, standard deviation, median,
quartiles, IQR, mode, and category proportions.

The v8 analysis confirms that the arithmetic is reproducible and that the
source contains a stable respondent identifier suitable for a privacy-preserving
T1--T3 paired analysis. The published v8 CSV does not preserve respondent rows.

## V9 decision

M2 v1 preserves role separation and the original 1--5 scale. It produces:

- `m2_role_perception_distributions.csv`: counts and shares by score category;
- `m2_role_perception_by_team_semester.csv`: descriptive summaries by cohort,
  checkpoint, and role;
- `m2_role_perception_paired_t1_t3.csv`: paired descriptive changes using an
  internal hashed respondent key, without exporting respondent identifiers;
- article-ready trajectory and heatmap figures from the verification notebook.

The interpretation is **perceived role disruption agreement**, not objective
extinction risk, job displacement probability, or actual AI adoption.

## V8-to-V9 traceability

| V8 recommendation | V9 decision | Status | Evidence | Limitation |
|---|---|---|---|---|
| Preserve six roles separately | Keep one role dimension and no composite index | `applied` | M2 distributions and summary CSVs | None for role separation |
| Report full ordinal distributions and summaries | Publish counts, shares, mean, std, median, quartiles, IQR, and n | `applied` | M2 output family | Likert summaries remain descriptive |
| Avoid conflating extinction and transformation | Retain source wording but rename interpretation as perceived disruption agreement | `applied` | Metadata, notebook, and analysis text | Future collection should split the constructs |
| Use available respondent linkage for longitudinal sensitivity | Publish aggregate summaries plus hashed-key T1--T3 paired changes | `applied` | Paired CSV and metadata | Pairing is available only where identifiers recur |
| Do not interpret M2 as actual use or objective risk | Keep M2 complementary to M1 usage/perception outputs | `applied` | Metadata interpretation and notebook RQ cell | Self-report remains non-telemetric |

## Gate decision

M2 v1 is **APPROVED for the descriptive v9 scope** on 2026-09-24. The approval
covers role-separated ordinal distributions, cohort summaries, privacy-
preserving paired T1--T3 sensitivity analysis, and article-ready verification
artifacts. The combined survey wording remains a construct limitation: these
outputs describe perceived role-disruption agreement, not objective extinction
risk or separate measures of extinction and task transformation.
