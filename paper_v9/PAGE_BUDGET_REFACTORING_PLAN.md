# Paper V9 Page-Budget Refactoring Plan for ICSE/SEET

## Goal

Reduce `paper_v9` to the ICSE/SEET target of **10 pages of text plus 2 pages
of references** while preserving the paper's core empirical argument:

1. GenAI-era student teams still show a late repository-activity bottleneck.
2. Late activity is not reducible to a single "student syndrome" explanation.
3. Repository-visible planning, temporal concentration, score trajectories,
   rework, and technical complexity should be interpreted descriptively and
   non-causally.
4. Secondary robustness evidence remains available through the replication
   package, generated artifacts, and interactive/data-explorer surfaces.

This plan operationalizes the supplied page-reduction report against the
current `paper_v9` LaTeX artifacts.

## Constraint and Strategy

**Page constraint:** ICSE/SEET main paper target: 10 pages of text + 2 pages of
references.

**Strategy:** keep one representative visual per central narrative movement,
move robustness diagnostics out of the main paper, and force tables to carry
exact numerical detail. Main text should state high-level patterns and point to
tables or replication artifacts for exact values.

## Figure Number Mapping

The report refers to figure numbers. In the current `results.tex`, these map
as follows:

| Report figure | Current LaTeX label | Current file | Planned action |
|---|---|---|---|
| Figure 3 | `fig:rq2-m3` | `figures/rq2_m3_activity_pooled.png` | Keep; central bottleneck visual. |
| Figure 4 | `fig:rq2-phase-commit` | `figures/rq2_phase_commit_share_by_score_trajectory.png` | Remove from main text; summarize non-overlapping phase check in prose. |
| Figure 5 | `fig:rq2-phase-clean` | `figures/rq2_phase_clean_churn_share_by_score_trajectory.png` | Remove from main text; summarize clean-churn variant in prose. |
| Figure 6 | `fig:rq2-score-delta-commit` | `figures/rq2_score_delta_vs_final7_commit_concentration.png` | Remove if Figure 8 remains as representative. |
| Figure 7 | `fig:rq2-score-delta-clean` | `figures/rq2_score_delta_vs_final7_clean_churn_concentration.png` | Remove; summarize clean-churn variant in text. |
| Figure 8 | `fig:rq2-planning-commit` | `figures/rq2_planning_vs_final7_commit_concentration.png` | Keep as the single representative late-concentration/planning visual. |
| Figure 9 | `fig:rq2-planning-clean` | `figures/rq2_planning_vs_final7_clean_churn_concentration.png` | Remove; summarize clean-churn variant in text. |
| Figure 10 | `fig:rq2-regularity-final` | `figures/rq2_regularity_vs_final_concentration.png` | Remove; condense to a half-sentence robustness note. |
| Figure 11 | `fig:rq2-m5-triangulation` | `figures/rq2_m5_2025_triangulation_panel.png` | Remove; keep Figure 12 for M4/M5 trajectory summary. |
| Figure 12 | `fig:rq2-m4-m5` | `figures/rq2_m4_m5_checkpoint_panels.png` | Keep; more compact M4/M5 trajectory visual. |
| Figure 17 | `fig:rq3-sensitivity` | `figures/rq3_association_sensitivity.png` | Remove; describe as replication-package sensitivity diagnostic. |
| Figure 18 | `fig:rq3-influence-map` | `figures/rq3_influence_map.png` | Remove; describe leave-one-out stability in one sentence. |

The report says "six specific figures" but enumerates six removal groups that
correspond to **nine actual figure environments** in the current manuscript:
Figures 4, 5, 6, 7, 9, 10, 11, 17, and 18.

## Refactoring Phases

### Phase 1 — Establish Page Baseline

**Purpose:** quantify the current excess before editing.

**Tasks**

- Compile the current LaTeX PDF.
- Record total page count and approximate page at which references begin.
- Record figure count before removals.
- Save a short before/after note in this plan or in the implementation log.

**Validation**

```bash
cd paper_v9/latex
TEXINPUTS=.:../: pdflatex -synctex=1 -interaction=nonstopmode main.tex
TEXINPUTS=.:../: pdflatex -synctex=1 -interaction=nonstopmode main.tex
```

**Baseline recorded on 2026-09-25**

- Current PDF: 28 pages.
- References begin on page 27 (`main.bbl` starts after page 26 in the LaTeX
  log), so the current split is approximately 26 text pages + 2 reference
  pages.
- `\includegraphics` count before removals: 18 total, all in
  `latex/sections/results.tex`.
- Immediate target delta: remove or absorb at least 16 text pages to satisfy
  the 10-page text budget.

### Phase 2 — Remove Secondary Robustness Figures from Main Text

**Purpose:** reclaim the largest space without changing empirical claims.

**Remove from `latex/sections/results.tex`**

1. `fig:rq2-phase-commit`
2. `fig:rq2-phase-clean`
3. `fig:rq2-score-delta-commit`
4. `fig:rq2-score-delta-clean`
5. `fig:rq2-planning-clean`
6. `fig:rq2-regularity-final`
7. `fig:rq2-m5-triangulation`
8. `fig:rq3-sensitivity`
9. `fig:rq3-influence-map`

**Keep**

- `fig:rq2-m3` as the central temporal bottleneck figure.
- `fig:rq2-planning-commit` as the single representative scatter for planning,
  final concentration, and score.
- `fig:rq2-m4-m5` as the compact M4/M5 trajectory visual.
- Core RQ1/RQ3 figures unless a later page check requires additional pruning.

**Replacement prose**

- Replace Figures 4--5 with one sentence: non-overlapping phase bins preserve
  the late-phase concentration pattern and are available in the replication
  artifacts.
- Replace Figures 6--7 and 9 with one compact sentence: commit and clean-churn
  variants agree directionally with the representative planning/concentration
  view.
- Replace Figure 10 with half a sentence: operational-regularity checks did
  not attribute the late peak to a single observed process pattern.
- Replace Figure 11 with one sentence: M5 coverage is limited to 2025.2 and is
  summarized alongside M4 in the retained checkpoint panel.
- Replace Figures 17--18 with one sentence: leave-one-out diagnostics preserved
  the intended directional reading of the small-n associations; full influence
  maps remain in the replication package.

### Phase 3 — Condense Results Prose

**Purpose:** stop duplicating table contents in prose.

#### RQ1 Results

**Cut**

- Inline endpoint means and standard deviations already present in
  Table `tab:rq1-m1-endpoints`.
- Repeated cohort-by-checkpoint numeric detail for AI benefit, career impact,
  and project expectations.

**Keep**

- High-level directional trends.
- One explicit pointer: "Table~\\ref{tab:rq1-m1-endpoints} reports exact
  endpoint distributions."

#### RQ2 Results

**Cut**

- Granular raw commit counts and clean-churn line counts already summarized in
  Table `tab:rq2-summary`.
- Repeated numeric walk-through of rolling-window checkpoints.

**Keep**

- Shape of the concentration: the final-stage bottleneck visible in
  `fig:rq2-m3`.
- One concise table pointer: "Table~\\ref{tab:rq2-summary} reports checkpoint
  values and units."
- Condensed robustness sentence covering removed phase-bin, regularity, and
  M5-triangulation artifacts.

#### RQ3 Results

**Cut**

- Inline enumeration of individual Spearman rho and p-values already listed in
  Table `tab:rq3-associations`.
- Paragraph-level repetition of all M9 association rows.

**Keep**

- The interpretation: associations between early artifacts and late rework were
  weak, non-monotonic, and descriptive.
- One pointer: "Table~\\ref{tab:rq3-associations} reports the full association
  matrix."
- One robustness sentence directing readers to leave-one-out diagnostics in the
  replication package.

### Phase 4 — Update Artifact Governance

**Purpose:** keep the artifact catalog consistent with the new page-budget
decision.

**Files**

- `ARTIFACT_USAGE_CATALOG.md`
- `FIGURES_CANDIDATES_WORKSHOP.md`
- `data/results/results_summary.json` only if artifact statuses are materially
  changed in generated summary metadata.

**Status updates**

- Main-text retained:
  - `rq2_m3_activity_pooled`
  - `rq2_planning_vs_final7_commit_concentration`
  - `rq2_m4_m5_checkpoint_panels`
- Move from main text to replication/appendix/diagnostic role:
  - `rq2_nonoverlapping_phase_activity`
  - `rq2_score_delta_vs_final7_concentration`
  - clean-churn planning/concentration scatter
  - `rq2_operational_regularity`
  - `rq2_m5_2025_triangulation`
  - `rq3_influence_map`
  - `rq3_association_sensitivity`

**Required note**

Record that demotion is for page-budget and narrative economy, not because the
artifacts are invalid.

### Phase 5 — Compile, Count Pages, and Iterate

**Validation commands**

```bash
cd paper_v9/latex
TEXINPUTS=.:../: pdflatex -synctex=1 -interaction=nonstopmode main.tex
TEXINPUTS=.:../: pdflatex -synctex=1 -interaction=nonstopmode main.tex
TEXINPUTS=.:../: pdflatex -synctex=1 -interaction=nonstopmode -output-directory=build main.tex
TEXINPUTS=.:../: pdflatex -synctex=1 -interaction=nonstopmode -output-directory=build main.tex
```

**Checks**

- No undefined references after removing figure labels.
- No stale textual references to removed figures.
- No orphaned captions or labels.
- No overfull hboxes introduced by compressed prose.
- Main text is at or below the 10-page target before references.
- References remain within the 2-page target.

### Phase 6 — Commit as a Page-Budget Refactor

**Expected commit scope**

- `latex/sections/results.tex`
- Catalog/inventory documentation updates.
- Regenerated `latex/main.pdf` and `latex/build/main.pdf`.
- Any updated logs/aux files already tracked by the repository.

**Suggested commit message**

```text
Condense Results for ICSE page budget
```

## Acceptance Criteria

- The main paper satisfies the ICSE/SEET page target or records the remaining
  page delta explicitly.
- The Results section no longer repeats table-level exact statistics in prose.
- Figures 4, 5, 6, 7, 9, 10, 11, 17, and 18 are removed from the main text.
- Figure 8 remains as the representative planning/concentration visual.
- Figure 12 remains as the compact M4/M5 checkpoint visual.
- Removed robustness figures remain reproducible and discoverable through the
  replication artifacts/catalog.
- The paper still preserves the non-causal, descriptive interpretation
  boundary.

## Implementation Checkpoint — Careful First Pass

Recorded on 2026-09-25 after the first page-budget implementation pass.

**Applied without removing central evidence**

- Removed secondary robustness figures from the main text:
  - non-overlapping phase shares;
  - score-delta scatter variants;
  - clean-churn planning/concentration variant;
  - operational-regularity scatter;
  - coverage-aware M5 triangulation;
  - RQ3 sensitivity and influence-map diagnostics.
- Preserved the central visuals/tables identified as narrative anchors:
  - `fig:rq2-m3`;
  - `fig:rq2-planning-commit`;
  - `fig:rq2-m4-m5`;
  - `tab:rq1-m1-endpoints`;
  - `tab:rq2-summary`;
  - `tab:rq3-associations`.
- Condensed Results prose by removing table-level repeated numbers while
  keeping high-level trends, denominators, non-causal cautions, and pointers to
  replication artifacts.

**Measured effect**

- Baseline before refactor: 28 total pages; references began on page 27.
- Careful first pass: 18 total pages; references begin on page 17.
- Remaining delta: approximately 6 total pages, or about 6 text pages beyond
  the 10-page text budget.

**Decision point**

Further reduction cannot be achieved by the supplied report alone without
broader editorial compression of other sections (for example Background,
Methodology, Discussion, and Threats to Validity) or demotion of additional
core tables/figures. Those next cuts should be explicitly approved because
they carry higher narrative risk than the first-pass figure demotions.

## Risk Controls

- Do not delete generated figure files from `paper_v9/figures/`; remove only
  their main-text inclusion unless a separate cleanup task is approved.
- Do not weaken the Threats to Validity section by hiding limitations; compress
  the evidence presentation, not the methodological cautions.
- Do not remove exact values from tables.
- After deleting figure environments, search for stale `\ref{...}` references
  before compiling.
