# Addressing the Reviewer's "Student Syndrome" Concern

## Critique being addressed

> Could the late-stage repository concentration be isolated from traditional
> "student syndrome" by analyzing the commit timestamps against the specific
> AI-usage peaks?

The new student-syndrome visualizations help address this critique by adding a
descriptive robustness layer around the late-stage repository peak. They do not
prove that the late peak was caused by AI use, nor do they provide event-level
AI-use timestamps. Instead, they make the procrastination explanation visible
and measurable: they show how much activity occurs near T3, whether this pattern
differs by evaluator/planning tier, and whether the same pattern appears in both
commit frequency and clean source/test changed lines.

## What the new evidence can and cannot establish

### What it can establish

The new figures can support three precise claims:

1. **Late-stage concentration is real in repository traces.** Both commit
   frequency and clean changed lines increase sharply near T3.
2. **The late peak is not confined to lower-performing/weaker-planning teams.**
   High evaluator score/good-planning teams also show a T3-adjacent rise.
3. **The lower evaluator/weaker-planning tier shows stronger final-seven-day
   concentration over the full project period.** This is consistent with a
   student-syndrome interpretation being stronger for that tier.

### What it cannot establish

The new figures should not be used to claim that AI usage caused the late peak.
The available data include checkpoint-level AI-related perceptions and usage
summaries, but not timestamped AI-use telemetry linked to individual commits.
Therefore, the strongest defensible interpretation is:

> The late-stage repository peak remains compatible with traditional student
> syndrome, but the tiered and full-period analyses make this alternative
> explanation explicit rather than leaving it implicit. The evidence suggests
> that end-loaded work is present broadly, while lower-scoring/weaker-planning
> teams concentrate a larger share of their total pre-T3 activity in the final
> seven days.

## Figure and data inventory

### Final seven-day timing plots

These figures zoom in on D-6 through D0, where D0 is the team-specific T3
anchor.

| Purpose | Figure | Data | Summary | Metadata |
|---|---|---|---|---|
| Commit timing inside the final seven-day window | [figures/rq2_student_syndrome_by_evaluator_planning_tier.png](figures/rq2_student_syndrome_by_evaluator_planning_tier.png) | [figures/rq2_student_syndrome_by_evaluator_planning_tier_data.csv](figures/rq2_student_syndrome_by_evaluator_planning_tier_data.csv) | [figures/rq2_student_syndrome_by_evaluator_planning_tier_summary.csv](figures/rq2_student_syndrome_by_evaluator_planning_tier_summary.csv) | [figures/rq2_student_syndrome_by_evaluator_planning_tier.metadata.json](figures/rq2_student_syndrome_by_evaluator_planning_tier.metadata.json) |
| Clean changed-line timing inside the final seven-day window | [figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn.png](figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn.png) | [figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn_data.csv](figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn_data.csv) | [figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn_summary.csv](figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn_summary.csv) | [figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn.metadata.json](figures/rq2_student_syndrome_by_evaluator_planning_tier_clean_churn.metadata.json) |

Key readings:

- In the commit-only final-window plot, D0 accounts for a similar mean share of
  each tier's D-6..D0 activity:
  - high evaluator/good planning: **61.5%** at D0;
  - lower evaluator/weaker planning: **59.4%** at D0.
- D-1 plus D0 account for most final-window commit activity in both groups:
  - high evaluator/good planning: **81.6%**;
  - lower evaluator/weaker planning: **74.3%**.
- In the clean changed-lines final-window plot, D0 is again similar:
  - high evaluator/good planning: **59.9%** at D0;
  - lower evaluator/weaker planning: **61.6%** at D0.
- D-1 plus D0 account for most final-window clean changed-line activity:
  - high evaluator/good planning: **77.0%**;
  - lower evaluator/weaker planning: **78.9%**.

Interpretation:

> Once teams are inside the final seven-day window, both tiers show a strong
> last-day concentration. This means the D0 spike itself should not be framed as
> a uniquely low-performing-team behavior.

### Full-period rolling trajectory plots

These figures place the late-stage peak in the context of the whole observed
project period. The x-axis is measured in days relative to each team's T3
anchor. T1/T2/T3 markers are derived from evaluator-form timestamps. T1 and T2
are shown as median vertical markers with min-max bands because checkpoint
dates vary by semester/team.

| Purpose | Figure | Data | Summary | Metadata |
|---|---|---|---|---|
| Full-period rolling commit intensity | [figures/rq2_student_syndrome_full_period_commits_by_tier.png](figures/rq2_student_syndrome_full_period_commits_by_tier.png) | [figures/rq2_student_syndrome_full_period_commits_by_tier_data.csv](figures/rq2_student_syndrome_full_period_commits_by_tier_data.csv) | [figures/rq2_student_syndrome_full_period_commits_by_tier_summary.csv](figures/rq2_student_syndrome_full_period_commits_by_tier_summary.csv) | [figures/rq2_student_syndrome_full_period_commits_by_tier.metadata.json](figures/rq2_student_syndrome_full_period_commits_by_tier.metadata.json) |
| Full-period rolling clean changed-line intensity | [figures/rq2_student_syndrome_full_period_clean_churn_by_tier.png](figures/rq2_student_syndrome_full_period_clean_churn_by_tier.png) | [figures/rq2_student_syndrome_full_period_clean_churn_by_tier_data.csv](figures/rq2_student_syndrome_full_period_clean_churn_by_tier_data.csv) | [figures/rq2_student_syndrome_full_period_clean_churn_by_tier_summary.csv](figures/rq2_student_syndrome_full_period_clean_churn_by_tier_summary.csv) | [figures/rq2_student_syndrome_full_period_clean_churn_by_tier.metadata.json](figures/rq2_student_syndrome_full_period_clean_churn_by_tier.metadata.json) |

Key readings:

- For commits, the highest mean rolling-intensity point is D0 for both tiers:
  - high evaluator/good planning: **72.9%** of each team's maximum rolling
    commit intensity;
  - lower evaluator/weaker planning: **84.4%** of each team's maximum rolling
    commit intensity.
- For clean changed lines, D0 is also the highest mean rolling-intensity point
  for the lower evaluator/weaker-planning tier:
  - lower evaluator/weaker planning: **71.2%** at D0.
- High evaluator/good-planning teams show substantial earlier changed-line
  intensity around the T2 region as well:
  - D-28: **43.2%**;
  - D-19: **42.9%**;
  - D0: **47.9%**.

Interpretation:

> The full-period view strengthens the student-syndrome analysis because it
> shows that D0 is not merely a local artifact of the final seven-day window. At
> the same time, high evaluator/good-planning teams show more visible earlier
> activity, especially in clean changed lines around the T2-to-T3 interval,
> while the lower evaluator/weaker-planning tier is more dominated by the final
> T3-adjacent rise.

### Final-seven-day concentration plot

This figure summarizes, for each team-semester, the share of all pre-T3 project
activity that occurred in the final seven days.

| Purpose | Figure | Data | Metadata |
|---|---|---|---|
| Team-level final-seven-day concentration for commits and clean changed lines | [figures/rq2_student_syndrome_final7_concentration_by_tier.png](figures/rq2_student_syndrome_final7_concentration_by_tier.png) | [figures/rq2_student_syndrome_final7_concentration_by_tier_data.csv](figures/rq2_student_syndrome_final7_concentration_by_tier_data.csv) | [figures/rq2_student_syndrome_final7_concentration_by_tier.metadata.json](figures/rq2_student_syndrome_final7_concentration_by_tier.metadata.json) |

Key readings:

| Metric | High evaluator/good planning | Lower evaluator/weaker planning |
|---|---:|---:|
| Mean final-seven-day commit share | **27.8%** | **50.7%** |
| Median final-seven-day commit share | **25.0%** | **51.4%** |
| Mean final-seven-day clean changed-line share | **23.6%** | **54.1%** |
| Median final-seven-day clean changed-line share | **15.3%** | **52.1%** |

Interpretation:

> This is the strongest single figure for addressing the reviewer. It directly
> compares how much of each team's pre-T3 project activity was compressed into
> the final seven days. The lower evaluator/weaker-planning tier has roughly
> double the final-seven-day concentration of the high evaluator/good-planning
> tier for both commits and clean changed lines.

## Recommended use in the paper

### Best figure to include in the main text

Use [figures/rq2_student_syndrome_final7_concentration_by_tier.png](figures/rq2_student_syndrome_final7_concentration_by_tier.png)
in the main Results section or as a compact robustness figure. It is the most
direct response to the reviewer because it operationalizes "student syndrome"
as final-seven-day concentration and shows the team-level distribution.

### Best figure to include as companion or appendix

Use one of the full-period trajectory figures as a companion:

- [figures/rq2_student_syndrome_full_period_commits_by_tier.png](figures/rq2_student_syndrome_full_period_commits_by_tier.png)
  if the paragraph emphasizes commit timing;
- [figures/rq2_student_syndrome_full_period_clean_churn_by_tier.png](figures/rq2_student_syndrome_full_period_clean_churn_by_tier.png)
  if the paragraph emphasizes that the pattern appears in source/test changed
  lines, not only commit counts.

The final-window line plots are useful as exploratory diagnostics or
supplementary figures because they show the within-week D0 spike, but they are
less rhetorically decisive than the concentration plot.

## Suggested Results paragraph

> To address the possibility that the late repository peak reflects ordinary
> student syndrome rather than a process specific to AI-assisted work, we added
> a tiered timing analysis around the final T3 checkpoint. We grouped the 14
> team-semesters using the same evaluator/planning rule used in the robustness
> figures: high T3 evaluator composite score, above-median T1 planning scope,
> and an observed T1 planning artifact versus the remaining lower/weaker-
> planning cases. The final-seven-day concentration plot shows that the lower
> evaluator/weaker-planning tier compressed a larger share of total pre-T3
> activity into the final week. Its median final-seven-day share was 51.4% for
> commits and 52.1% for clean changed lines, compared with 25.0% and 15.3%,
> respectively, in the high evaluator/good-planning tier. Thus, the data are
> consistent with a student-syndrome component, especially among lower-scoring
> or less planning-visible teams.

## Suggested follow-up Results paragraph

> The within-final-week trajectories qualify this interpretation. Once teams
> entered the final seven-day window, both tiers concentrated much of their
> remaining activity at D0. D0 accounted for 61.5% of the high evaluator/good-
> planning tier's D-6..D0 commits and 59.4% of the lower/weaker-planning tier's
> D-6..D0 commits; the corresponding clean changed-line shares were 59.9% and
> 61.6%. This suggests that the last-day spike is a broad deadline-proximal
> pattern, while the full-project concentration analysis distinguishes teams
> that deferred a larger share of their overall work into the final week.

## Suggested Discussion paragraph

> These robustness views sharpen the interpretation of the late-stage
> repository peak. The evidence does not allow us to attribute the peak to AI
> use directly, because the study does not contain timestamped AI telemetry
> aligned to commits. However, the new tiered analysis makes the traditional
> procrastination alternative empirically visible. The lower evaluator/weaker-
> planning tier shows substantially stronger final-week concentration across
> both commits and clean changed lines, which is compatible with student
> syndrome. At the same time, high evaluator/good-planning teams also show a
> deadline-adjacent increase, indicating that late activity is not only a
> low-performing-team artifact. We therefore interpret the late peak as a
> deadline-proximal repository pattern that likely includes ordinary student
> syndrome, rather than as independent evidence that AI use caused late-stage
> work concentration.

## Suggested response-to-reviewer paragraph

> We agree that the original late-stage activity peak could be conflated with
> traditional student syndrome. In response, we added a data-pipeline analysis
> that stratifies team-semesters by evaluator/planning tier and compares both
> commit frequency and clean source/test changed lines. The new final-seven-day
> concentration figure shows that lower evaluator/weaker-planning teams place a
> larger share of their pre-T3 activity in the final week, while high evaluator/
> good-planning teams exhibit lower full-project concentration but still show a
> final-day rise inside the last week. We now present this as a descriptive
> robustness analysis: the late peak is compatible with student syndrome and is
> stronger among lower/weaker-planning teams, but the available data do not
> support causal attribution to AI use because AI-use measurements are not
> timestamped at the commit level.

## Suggested Threats-to-Validity sentence

> The student-syndrome robustness plots reduce ambiguity around the late-stage
> repository peak by showing final-week concentration by evaluator/planning
> tier, but they do not isolate AI use as a causal mechanism because AI exposure
> is measured at survey/checkpoint granularity rather than as timestamped
> commit-level telemetry.

## Recommended interpretation boundary

Use this framing:

> "consistent with a student-syndrome component"

Avoid stronger framings such as:

> "student syndrome explains the peak"

or:

> "AI use caused the late peak"

The most defensible conclusion is that the new analysis **separates the
procrastination-compatible part of the pattern from the broader deadline
effect**, while preserving the study's observational boundary.
