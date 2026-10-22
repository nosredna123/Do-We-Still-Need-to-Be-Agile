# Paper V9 Exploratory Visualization Inventory

Generated from official metric artifacts by `paper_v9/scripts/results/generate_figure_candidates.py`. This is an exploratory inventory, not a closed candidate list or a mandatory selection workshop.

## Candidate RQ1: separated perception panel

- Data: `paper_v9/figures/candidate_rq1_perception_panel_data.csv`
- Figure: `candidate_rq1_perception_panel.{pdf,svg,png}`
- Strength: preserves perception families and semester strata without a composite index.
- Limitation: dense family labels; usage distributions remain separate from perception.

## Candidate RQ2: temporal dynamics

- Data: `paper_v9/figures/candidate_rq2_temporal_dynamics_data.csv`
- Figure: `candidate_rq2_temporal_dynamics.{pdf,svg,png}`
- Strength: places M3, M4, and M5 on a temporal candidate view while retaining explicit units.
- Limitation: the measures have incompatible grains and scales; the figure must not be read as a correlation or common y-axis effect.

## Candidate RQ3: planning and clean rework profile

- Data: `paper_v9/figures/candidate_rq3_planning_rework_profile_data.csv`
- Figure: `candidate_rq3_planning_rework_profile.{pdf,svg,png}`
- Strength: shows structural T1 scope against M8a and marks baseline eligibility.
- Limitation: small sample and path-provenance interpretation; M6b structured content is not shown as a composite score.

## Candidate RQ3: leave-one-out association ranges

- Data: `paper_v9/figures/candidate_rq3_associations_leave_one_out_data.csv`
- Figure: `candidate_rq3_associations_leave_one_out.{pdf,svg,png}`
- Strength: exposes influence and sensitivity rather than hiding dominant cases.
- Limitation: ranges are descriptive diagnostics, not confidence intervals or significance evidence.

## Deferred selection decision

The user approved carrying candidate figures into a first LaTeX version. These
candidates are an evidence inventory, not a closed menu: the section workflow
may retain one, replace it, or create a new ad hoc analysis when the argument
requires a view not anticipated here. Any ad hoc result must have traceable
data, an explicit analytical grain, validation, and documented limitations.
Figures and prose will be reviewed together during the editorial pass. All
candidates preserve unavailable states, analytical grains, denominators, and
the non-causal interpretation boundary.