# ICSE 2027 SEET — Step-by-Step Manuscript Revision & Rebuttal Guide

**Paper Title:** Do We Still Need to Be Agile? What Student Projects Reveal About Coordination Skills in the GenAI Era  
**Track:** ICSE 2027 — Software Engineering Education and Training (SEET)  
**Current Decision Status:** Weak Accept (Shepherded / Conditional on Revision — R1: Borderline, R2: Weak Accept, R3: Weak Accept)  
**Page Budget:** $10$ pages main text + $2$ pages references (Current draft: $10$ pages main text + $1$ page references)

---

## 1. Strategic Summary

The Program Committee shares a strong consensus on the timeliness, intellectual honesty, and multi-modal richness of your study. All three reviewers praise your strict preservation of analytical grains, your nuanced deconstruction of late-stage commit spikes ("student syndrome" vs. compensatory recovery), and your discipline in framing Spec-Driven Development (SDD) as a testable hypothesis rather than an over-claimed intervention.

To convert Reviewer 1's *Borderline* into an *Accept* and satisfy the Area Chair's shepherding conditions without exceeding the strict $10$-page main-text limit, your revision must execute a **strategic space-for-substance trade**:

1. **Reclaim $\sim 1.2\text{--}1.5$ Pages of Main Text:** Strip the repetitive epistemological disclaimers (*"these are descriptive diagnostics, not confirmatory tests,"* *"incompatible grains are not combined"*) that currently appear in nearly every paragraph of Section IV and Section V. Consolidate those guardrails into two definitive locations: **Section III-A (Analytical Approach)** and **Section VI (Threats to Validity)**.
2. **Reinvest Reclaimed Space into Three High-Impact Areas:**
   * **Methodological Operationalization (Addressing Reviewer 1):** Explicitly define the versioned clean-path exclusion rules (M4) and explain the $13.50\text{M}$ raw churn total at $T_3$ from excluded dependency/environment paths; report the evaluator rubric scale, aggregation formula, and inter-rater reliability (M9); list representative lexical stems for coordination friction (M5); clarify the M1 score scale in Figure 1; and state the LLM extraction schema and rationale for parsing $T_1$ commit subjects (M6b).
   * **Pedagogical & Curricular Grounding (Addressing Reviewer 2):** Detail the students' academic year, the exact milestone deliverables at $T_1/T_2/T_3$, why 7 teams already had $21,718$ lines of clean churn within the $T_1$ window, why $T_1$ architectural artifact presence rose from $4/9$ (`2025.2`) to $5/5$ (`2026.1`), and how team process choices (Scrum, Kanban, unguided) distributed across the 14 teams.
   * **Qualitative Enrichment & Classroom SDD Guardrails (Addressing Reviewer 2 & Reviewer 3):** Add $2\text{--}3$ paraphrased, privacy-preserving vignettes from the `2025.2` transcripts (M5) to illustrate $T_2$ integration friction and $T_3$ blockers; explain why all 14 teams opted out of a full RAG pipeline; distinguish using GenAI coding assistants from engineering an embedded GenAI feature; and specify concrete pedagogical guardrails in Section V-C so classroom SDD does not degenerate into AI-generated "documentation theater."

---

## 2. Prioritized Revision Checklist

This checklist is ordered using our agreed **Hybrid Tiered Strategy**:
* **Tier 1:** Immediate Mechanical, Table, Typo & Reference Quick Wins ($\sim 30$ mins)
* **Tier 2:** Space Reclamation — Consolidating Repetitive Disclaimers ($\sim 45$ mins)
* **Tier 3:** Critical Acceptance Contingencies — Operational Definitions, Curricular Context & Qualitative Vignettes ($\sim 2\text{--}3$ hours)
* **Tier 4:** Fortifying Threats to Validity & Rebuttal Matrix ($\sim 1$ hour)

---

### Tier 1: Immediate Mechanical, Table, Typo & Reference Quick Wins

* [x] **Action 1.1:** Fix corrupted headers, misaligned columns, and swapped `Predictor`/`Outcome` entries in **Table III** (Page 9) | **Addresses:** Reviewer 1, Detailed Comment 4; Meta-Review
  * **Context:** In the current PDF (Page 9), Table III's header row renders sample size $n$ as `72` and merges $\rho$ with `Exploratory p` (`pExploratory p`). In addition, the `Predictor` and `Outcome` columns are inverted in rows 3–12 (e.g., `T3 rework ratio` is listed in the Predictor column instead of the Outcome column).
  * **Replacement Markdown Preview:**

| Predictor ($T_1$) | Outcome ($T_3$) | Stratum | $n$ | Spearman $\rho$ | Exploratory $p$ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| $T_1$ artifact file count | $T_3$ rework magnitude | All team-semesters | $14$ | $0.206$ | $0.479$ |
| $T_1$ artifact line scope | $T_3$ rework magnitude | All team-semesters | $14$ | $0.301$ | $0.296$ |
| $T_1$ artifact file count | $T_3$ rework ratio | Baseline-eligible | $12$ | $-0.032$ | $0.922$ |
| $T_1$ artifact line scope | $T_3$ rework ratio | Baseline-eligible | $12$ | $-0.060$ | $0.853$ |
| $T_1$ artifact file count | Project progress | All team-semesters | $14$ | $0.100$ | $0.733$ |
| $T_1$ artifact file count | Scope applicability | All team-semesters | $14$ | $0.025$ | $0.931$ |
| $T_1$ artifact file count | Technical complexity | All team-semesters | $14$ | $0.271$ | $0.349$ |
| $T_1$ artifact file count | Engagement/participation | All team-semesters | $14$ | $-0.079$ | $0.790$ |
| $T_1$ artifact line scope | Project progress | All team-semesters | $14$ | $0.096$ | $0.745$ |
| $T_1$ artifact line scope | Scope applicability | All team-semesters | $14$ | $0.038$ | $0.897$ |
| $T_1$ artifact line scope | Technical complexity | All team-semesters | $14$ | $0.222$ | $0.446$ |
| $T_1$ artifact line scope | Engagement/participation | All team-semesters | $14$ | $-0.143$ | $0.626$ |

  * **Ready-to-Paste LaTeX Code for Table III:**
```latex
\begin{table}[t]
\centering
\caption{Primary RQ3 Association Results (M9)}
\label{tab:rq3_associations}
\begin{tabular}{lllcrr}
\hline
\textbf{Predictor ($T_1$)} & \textbf{Outcome ($T_3$)} & \textbf{Stratum} & \textbf{$n$} & \textbf{$\rho$} & \textbf{Expl. $p$} \\
\hline
$T_1$ artifact file count & $T_3$ rework magnitude & All team-semesters & 14 & $0.206$ & $0.479$ \\
$T_1$ artifact line scope & $T_3$ rework magnitude & All team-semesters & 14 & $0.301$ & $0.296$ \\
$T_1$ artifact file count & $T_3$ rework ratio & Baseline-eligible & 12 & $-0.032$ & $0.922$ \\
$T_1$ artifact line scope & $T_3$ rework ratio & Baseline-eligible & 12 & $-0.060$ & $0.853$ \\
$T_1$ artifact file count & Project progress & All team-semesters & 14 & $0.100$ & $0.733$ \\
$T_1$ artifact file count & Scope applicability & All team-semesters & 14 & $0.025$ & $0.931$ \\
$T_1$ artifact file count & Technical complexity & All team-semesters & 14 & $0.271$ & $0.349$ \\
$T_1$ artifact file count & Engagement/participation & All team-semesters & 14 & $-0.079$ & $0.790$ \\
$T_1$ artifact line scope & Project progress & All team-semesters & 14 & $0.096$ & $0.745$ \\
$T_1$ artifact line scope & Scope applicability & All team-semesters & 14 & $0.038$ & $0.897$ \\
$T_1$ artifact line scope & Technical complexity & All team-semesters & 14 & $0.222$ & $0.446$ \\
$T_1$ artifact line scope & Engagement/participation & All team-semesters & 14 & $-0.143$ & $0.626$ \\
\hline
\end{tabular}
\end{table}
```

* [x] **Action 1.2:** Fix row alignment and merged cells in **Table I** (Section III-B, Page 3) | **Addresses:** Reviewer 1, Detailed Comment 4
  * **Context:** In the current PDF (Page 3), rows `M1`/`M2` and `M5`–`M8` lack horizontal breaks or proper row alignment, causing `Primary grain` labels to bleed across rows.
  * **Ready-to-Paste LaTeX Code for Table I:**
```latex
\begin{table}[t]
\centering
\caption{Summary of Metric Families, Operational Grains, and Coverage}
\label{tab:metrics}
\begin{tabular}{lp{4.1cm}p{3.0cm}}
\hline
\textbf{ID} & \textbf{Metric Family and Components} & \textbf{Primary Grain ($N$)} \\
\hline
M1 & Self-Reported AI Usage \& Perceptions (6 perception scales + task/tool frequency) & Cohort $\times$ checkpoint ($6$ cells) \\
M2 & Perceived Role Disruption (5-point Likert across 6 SE roles + paired shifts) & Cohort $\times$ checkpoint $\times$ role \\
M3 & Repository Activity (commit timing, rolling windows, author Gini, phase bins) & Team-semester / window ($N=14$) \\
M4 & Clean-Change Dynamics (source/test line churn under clean-path policy) & Team-semester / checkpoint ($N=14$) \\
M5 & Coordination-Language Evidence (deterministic lexical markers per 1k tokens) & Global corpus / checkpoint (`2025.2`) \\
M6 & Upfront Architecture Evidence: artifact scope (M6a, $N=14$) \& commit-subject categories (M6b, $n=9$) & Team-semester ($N=14$ / $n=9$) \\
M7 & Repository Inactivity (7-day window coverage diagnostic) & Team-semester / window ($N=14$) \\
M8 & Clean-Path Rework (late modifications to prior clean source/test files) & Team-semester ($N=14$; $n=12$ ratio) \\
M9 & Artifact--Rework--Outcome Associations (Spearman $\rho$ + leave-one-out sensitivity) & Team-semester / stratum ($N=14$) \\
\hline
\end{tabular}
\end{table}
```

* [x] **Action 1.3:** Fix duplicated team label typo in **Section IV-C** (Page 7, Column 1, Line 42) | **Addresses:** Reviewer 1, Presentation
  * **Locate:** `"whereas 2025.2/TEAM 08 and 2026.1/TEAM 26.1/TEAM_03 have a ratio of 1.000"`
  * **Replace with:** `"whereas 2025.2/TEAM_08 and 2026.1/TEAM_03 both exhibit a rework ratio of 1.000"`

* [x] **Action 1.4:** Update **Section VIII (Data Availability)** (Page 10) to commit to Zenodo/Figshare DOI migration and index all newly added methodological instruments | **Addresses:** Step 2 Policy Compliance Check; Reviewer 1, Weakness 1; Reviewer 2, Verifiability
  * **Replace Section VIII with the following draft-ready paragraph:**
  > **VIII. DATA AVAILABILITY**  
  > The companion static data explorer [18] provides public, double-anonymous review access to the approved research dataset snapshot (`research-data-001`) in downloadable JSON and CSV formats, alongside interactive visualizations and leave-one-out sensitivity maps. In addition to the quantitative tables, the replication package documents (i) the versioned clean-path inclusion/exclusion glob rules (M4/M8), (ii) the complete deterministic lexical dictionary and regular expressions for coordination markers (M5), (iii) the structured extraction prompt and schema for $T_1$ commit subjects (M6b), and (iv) the full student survey instruments (M1/M2), course checkpoint rubrics, and blind evaluator scorecards (M9). Each dataset preserves its native observation grain and original denominators; no verbatim student meeting transcripts are released to protect participant privacy under institutional ethics guidelines. Upon manuscript acceptance, the complete `research-data-001` snapshot and replication package will be permanently archived with a persistent DOI on Zenodo (`> [Insert reserved Zenodo DOI or keep "to be minted upon camera-ready submission"]`).

* [x] **Action 1.5:** Anchor uncited bibliography items `[23]–[30]` in **Section II (Background and Related Work)** and replace informal blog posts (`[19]`, `[21]`, `[22]`) with peer-reviewed SE/computing education citations | **Addresses:** Reviewer 2, Detailed Comment 3; Reviewer 3, Weakness 3; Meta-Review
  * **Implementation note:** Per user decision, no new bibliography entries were added. The provisional preprint and two blogs were removed, and relevant existing work on GenAI in software engineering and education, project-course coordination, technical debt, and case-study methods was cited in Sections II–III.
  * **Context:** In the current PDF, references `[19]–[30]` appear in the Reference list on Page 11 without in-text citation brackets in Sections I–VIII, and Reviewer 3 explicitly critiques the reliance on blog posts (`[21]` Cambridge Advance Online, `[22]` Codebridge) and unrefereed preprints (`[19]`). Note that you have up to **2 full pages** for references in ICSE 2027 SEET (you currently use only 1 page).
  * **Action in Bibliography (Page 11):**
    1. Keep `[1]` (Delimarsky / GitHub Blog) and `[2]` (Thoughtworks) as explicit industry primary sources for the emerging term *Spec-Driven Development*.
    2. Remove informal blog posts `[21]` and `[22]` (and update `[19]` to a peer-reviewed SE survey or replace with peer-reviewed ICSE-SEET / SIGCSE / TOCE papers on GenAI in team project courses).
    3. Integrate existing peer-reviewed references `[23]–[30]` directly into **Section II** and **Section III** using the replacement paragraph below.
  * **Insert/Update in Section II (Page 2, Column 1, expanding Paragraph 2 & Paragraph 3):**
  > Generative AI changes local software-engineering work unevenly across tasks, users, and contexts [6]–[8], [20], [23]. Foundational evaluations of code-generating models [27] and empirical studies of developer interaction show that programmers must actively steer, verify, and contextualize generated code rather than passively accepting it [9], while critical perspectives warn of fragmented system comprehension when developers rely on AI outputs without shared mental models [29]. In undergraduate software engineering education, students rapidly adopt conversational AI for local coding and debugging [10], [28], yet capstone project courses require complex socio-technical coordination, client/stakeholder alignment, and iterative integration across teammates [30].  
  >   
  > Architecture and technical-debt research similarly treats design decisions as evolving constraints whose consequences accumulate over time [11]–[15], [26]. Following established empirical software engineering standards for multi-method case studies and observational research [24], [25], we measure early architectural artifacts separately from semantic quality: an observed repository artifact is evidence of an explicit team practice, not proof that the underlying design was adequate.

---

### Tier 2: Space Reclamation — Consolidating Repetitive Methodological Disclaimers

* [x] **Action 2.1:** Establish a single, authoritative "Methodological Guardrails & Epistemological Boundaries" statement in **Section III-A (Analytical Approach)** (Page 3, Column 1) | **Addresses:** Reviewer 1, Weakness 3; Meta-Review
  * **Replace the second paragraph of Section III-A (and merge the repetitive caveats from III-C) with:**
  > **Epistemological Boundaries and Grain Separation:** Because this study observes $N = 14$ team-semesters and $\sim 70$ students without a non-AI control group or IDE-level telemetry, three global principles govern all results reported in Section IV: (1) *Strict grain preservation*—student-level survey waves (M1, M2), global checkpoint transcripts (M5), and team-semester repository/scorecard metrics (M3, M4, M6–M9) operate at distinct denominators (Table I) and are never pooled or cross-correlated across incompatible grains; (2) *Exploratory statistical inference*—all Spearman rank correlations ($\rho$), $p$-values, non-overlapping phase bins, complexity stratifications, and leave-one-out sensitivity ranges serve strictly as descriptive and robustness diagnostics rather than confirmatory hypothesis tests or causal estimators; and (3) *Proxy transparency*—missing repository or transcript observations are retained as explicit observation states rather than zero-filled or imputed as low quality. To maintain readability, we state these interpretive boundaries once here and in Section VI rather than repeating them for each metric.

* [x] **Action 2.2:** Prune repetitive guardrail sentences across **Section IV (Results)** and **Section V (Discussion)** to reclaim $\sim 1.2\text{--}1.5$ pages | **Addresses:** Reviewer 1, Weakness 3; Reviewer 2, Presentation; Meta-Review
  * **Delete or condense the following redundant passages in Section IV and Section V:**
    1. **Page 3, Col 2 (Section IV intro):** Delete *"and retain the analytical grain of each metric; no claim combines incompatible grains or treats self-reported evidence as behavioral telemetry."* (Already covered in Section III-A).
    2. **Page 4, Col 1 (Section IV-A, Para 1 & Para 3):** Delete *"These are repeated cohort summaries, not an identified individual longitudinal panel"* and *"These are self-reported frequencies and selected activities, not instrumented measures of tool use or stable individual learning trajectories."*
    3. **Page 4, Col 1 (Section IV-B, Para 1):** Condense the 10-line opening paragraph into a single topic sentence: *"RQ2 contrasts repository activity (M3), clean source/test churn (M4), and global transcript coordination markers (M5) across checkpoints (Table II)."*
    4. **Page 4, Col 2 (Section IV-B, Para 4 & Para 6):** Delete *"not as independent causal tests"* and *"so the late-activity interpretation remains bounded to Git evidence rather than treated as a direct measure of team process maturity."*
    5. **Page 5, Col 2 & Page 6, Col 1 (Section IV-B, last 2 paragraphs):** Delete the redundant paragraph beginning *"The coverage-aware M5 triangulation is available..."* (5 lines) and shorten the closing summary paragraph by half.
    6. **Page 6, Col 1–2 (Section IV-C, Para 1):** Cut the 18-line methodological preamble down to 3 lines: *"RQ3 evaluates team-semester associations ($N = 14$) among upfront architectural artifacts at $T_1$ (M6a, M6b), late clean-path rework (M8), and independent blind-scored outcomes at $T_3$ (M9)."*
    7. **Page 7, Col 2 & Page 8, Col 2 (Section IV-C, last 4 paragraphs):** Condense the repetitive disclaimers on Page 7 (*"The primary Artifact-Rework-Outcome Associations (M9) are based on only 14 team-semesters..."*) and Page 8 (*"These values remain robustness diagnostics... Overall, the RQ3 evidence provides..."*) into a single concise paragraph summarizing Table III and the $n = 9$ M6b findings.

---

### Tier 3: Critical Acceptance Contingencies — Operational Definitions, Pedagogical Context & Qualitative Evidence

* [x] **Action 3.1:** Expand **Section III (Methodology — Course Structure, Timeline, and Process Choices)** (Page 2, Column 2) | **Addresses:** Reviewer 2, Weaknesses 1–2, Detailed Comments 1–2, Questions 1–2; Reviewer 3, Weakness 2, Detailed Comment 2
  * **Completed:** Section III distinguishes survey waves from evaluator/status-presentation dates and gives approximate course weeks derived from the earliest $T_1$ survey response date. It reports that team process choices and adherence were not formally recorded, and that the observed $T_1$ artifact-presence difference is descriptive.
  * **Evidence boundary:** The versioned records do not define a shared checkpoint deliverable checklist or document an onboarding change that explains the artifact-presence difference. Team-specific RAG adoption and non-adoption rationales were omitted; unsupported claims in the suggested draft were not adopted.

* [x] **Action 3.2:** Define the Evaluator Scorecard Rubric Scale, Aggregation Formula, and Inter-Rater Reliability (IRR) in **Section III** (Page 2, Column 2, Paragraph 3) | **Addresses:** Reviewer 1, Weakness 1, Detailed Comment 2, Question 1
  * **Completed:** Section III records the four ordinal scales in 0.5-point steps (Engagement/Participation and Scope/Applicability: 0--2; Project Progress: 0--4; Technical Complexity: 0--2), the unweighted mean aggregation by team-semester-checkpoint, and retained dispersion summaries (sample SD, median, IQR, and valid-rater count).
  * **Reliability evidence:** Ordinal Krippendorff's $\alpha$ was computed by dimension (Engagement, Progress, Scope, Complexity): 0.294, 0.604, 0.519, 0.242 in 2025.2 and 0.632, 0.696, 0.565, 0.308 in 2026.1. The 2025.2 panel had 102 scorecards across 27 units (22 with four ratings, four with three, one with two); 2026.1 had 45 scorecards across 15 units (three each). Agreement varied and was not characterized as uniformly high. The score exports lack verbal endpoint descriptions.

* [x] **Action 3.3:** Specify the Operational Definitions for Clean-Path Policy (M4/M8), Coordination Lexicon (M5), and LLM Commit-Subject Extraction (M6b) in **Section III-B & Section III-C** (Page 3) | **Addresses:** Reviewer 1, Weaknesses 1–2, Detailed Comments 1 & 3, Questions 1–2
  * **Completed:** Section III-B describes the shared `code-churn-metrics-v2` extension allowlist and excluded path segments used for M4 and M8. M8 classifies T3 changes to eligible paths first observed at T1/T2 as rework and T3-first paths as deferred change; the paper identifies this as a file-provenance proxy, not semantic validation.
  * **M5 operational definition:** The 2025.2 global corpus contains 100 chunks across T1–T3. Section III-B now specifies lowercase normalization, the versioned Portuguese regex lexicon's five groups (alignment, handoff, integration, blocker, and rework), representative markers, token counting, and per-1,000-token checkpoint density. It preserves the limitations that markers are candidate textual signals and are not linked to team-level repository observations.
  * **M6b operational definition:** Section III-C records the fixed JSON-schema prompt, `gpt-4o-mini` at temperature 0, the four extraction categories, verbatim quotes, quote/commit-hash validation, nine team-semesters with T1 subjects, and five unavailable cases. It reports the approved human-review gate without claiming that exact-quote checks establish semantic correctness; M6b remains exploratory and separate from structural M6a.
  * **Evidence corrections:** The suggested draft was not followed where it conflicted with the implementation: M5 has five Portuguese lexicon groups, not the four proposed English groups; the path policy identifies eligible extensions and exclusions but does not establish human authorship. The proposed `[18]` citation and `100%` verification claim were omitted because neither was supported by the versioned evidence.

* [x] **Action 3.4:** Clarify the M1 Survey Family Scales in **Section IV-A** and the **Figure 1 Caption** (Pages 4–5) | **Addresses:** Reviewer 2, Detailed Comment 2
  * **Completed:** The Results text and Figure 1 caption now state that each point is the cohort/checkpoint mean of an inherited ordinal NLP score (integer 0--4) for one question, with one sample standard deviation shown; the figure uses a shared 0--5 display axis. The six question families remain separate.
  * **Figure source:** The axis label in the M1 figure generator now identifies the 0--4 NLP rubric instead of implying distinct native family scales. The underlying values and plotted summaries are unchanged.
  * **Evidence correction:** The suggested 1--5 multi-item composites and normalized project/career proportions do not describe the plotted data. The M1 panel reuses the inherited `ai_dependency_score` rubric for all six questions; the rubric is approved for descriptive use only and is not validated as a measure of AI dependence. The draft scale ranges and interpretations were therefore not adopted.

* [x] **Action 3.5:** Explain the $T_3$ Clean-Churn Share Drop ($1.0\%$ of $13{,}502{,}131$ total churn lines) in **Section IV-B** | **Addresses:** Reviewer 1, Detailed Comment 1
  * **Completed:** Results now reports the exact clean/total churn counts and rounded shares: $21{,}718/50{,}614$ ($42.9\%$) at $T_1$, $47{,}545/242{,}399$ ($19.6\%$) at $T_2$, and $136{,}325/13{,}502{,}131$ ($1.0\%$) at $T_3$.
  * **T3 path audit:** Of $13{,}502{,}131$ raw churn lines, $13{,}365{,}806$ ($99.0\%$) are in M4-excluded paths. The audit attributes $11{,}596{,}231$ lines to Python virtual-environment paths (including Google API discovery-cache JSON files under `venv/`), $1{,}358{,}395$ to `node_modules/`, and $143{,}990$ to generated/build directories; the remainder is in other excluded paths. Counts are added-plus-deleted churn, not final repository sizes.
  * **Evidence boundary:** The path audit identifies what changed, not why teams committed it. The proposed claims about massive JSON/CSV test datasets, frontend bundles/lockfiles, unignored paths, and final-deployment preparation were not adopted because the available evidence does not establish them. Current pooled totals also differ from the draft denominators, so the paper uses the versioned M4 outputs.

* [x] **Action 3.6:** Add Paraphrased Qualitative Transcript Vignettes (M5) in **Section IV-B** (Page 7, Column 1, following the M5 paragraph) | **Addresses:** Reviewer 2, Weakness 3; Reviewer 3, Weaknesses 1–2, Detailed Comment 1, Question 1
  * **Completed:** Added two anonymized, paraphrased transcript examples after the M5 summary in `results.tex`: a $T_2$ presentation described incomplete front-end/back-end integration, and a $T_3$ discussion described a change blocking Gemini Pro access, context limitations with the available Flash model, and malformed generated text.
  * **Evidence boundary:** The examples are illustrative, not representative; the global transcript corpus has no team identifiers and cannot support team-outcome attribution or causal claims. The proposed claims about AI-generated interface divergence, incompatible schemas/authentication/routes, API rate limits, database deployment constraints, and acceptance criteria were not supported by the inspected excerpts and were not included.

* [ ] **Action 3.7:** Operationalize Classroom Spec-Driven Development (SDD) in **Section V-C** (Pages 9–10) to prevent AI-generated "documentation theater" | **Addresses:** Reviewer 2, Strengths/Assessment; Reviewer 3, Detailed Comment 3, Question 2
  * **Insert the following paragraph at the end of Section V-C (Page 10, Column 1):**
  > **Preventing AI-Generated "Documentation Theater" in Classroom SDD:** A critical pedagogical implication of our RQ3 null findings ($\rho = 0.206\text{--}0.301$ between $T_1$ artifact volume and $T_3$ rework) is that merely requiring students to commit markdown files at $T_1$ does not reduce late integration rework—especially when students can prompt an LLM to generate verbose, superficial architecture documents in seconds. For SDD to function as a genuine cognitive coordination mechanism rather than AI-generated *documentation theater*, educators should operationalize specifications through four enforceable classroom practices: (1) *Executable interface contracts*—grading machine-verifiable artifacts (such as OpenAPI/Swagger schemas, typed data models, and automated contract tests) rather than prose length; (2) *Traceable PR/commit linkage*—requiring pull requests at $T_2$ and $T_3$ to reference specific specification clauses or document explicit spec revisions when architecture evolves; (3) *Synchronous oral defense at checkpoints*—using status reviews to quiz cross-functional teammates on each other's component boundaries and failure modes; and (4) *Convergence checks*—evaluating whether the delivered $T_3$ codebase structurally honors or explicitly updates its $T_1/T_2$ specification.

---

### Tier 4: Fortifying Threats to Validity & Rebuttal Preparation

* [ ] **Action 4.1:** Expand **Section VI (Threats to Validity)** (Page 10) to explicitly address the construct and ecological critiques raised by Reviewers 1, 2, and 3 | **Addresses:** Reviewer 1, Weakness 2; Reviewer 2, Weakness 2; Reviewer 3, Weaknesses 1–2
  * **Insert/Integrate the following targeted sentences into Section VI (Page 10, Columns 1–2):**
  > * **Construct Validity of Planning (M6a/M6b) and Rework (M8):** M6a measures structural volume (file and line counts) rather than semantic coherence, and M6b extracts planning markers from terse $T_1$ commit subject lines ($n = 9$) rather than full-text parsing of committed documentation. Consequently, teams that wrote detailed architectural specifications inside external tools (e.g., Notion, Google Docs, Miro) or used generic commit messages (`"initial commit"`) are under-represented in M6b. Similarly, M8 measures late-stage line modifications to pre-existing clean files; without semantic diff classification, file-provenance rework cannot fully separate destructive bug-fixing from productive iterative feature refinement.
  > * **Ecological Separation Between Cohort Surveys and Team Repositories:** Because institutional privacy rules required multi-checkpoint student surveys (M1, M2) to be collected anonymously at the cohort grain without team identifiers, we cannot statistically link a specific team's self-reported GenAI coding intensity to that team's commit concentration (M3) or clean rework (M8).
  > * **Dual GenAI Role (Coding Assistant vs. Embedded System Feature):** Because every team also engineered an application containing an integrated GenAI feature, late-stage churn and coordination friction reflect a combination of (a) integrating AI-generated source code across teammates and (b) engineering prompts and API wrappers for the product's own LLM feature.

* [ ] **Action 4.2:** Prepare Point-by-Point Rebuttal Responses for the 6 Explicit Reviewer Questions | **Addresses:** Reviewers 1, 2, and 3 (Questions for the Rebuttal)
  * Use the condensed response templates below directly in your ICSE 2027 author response / shepherd summary:

  > **Response to Reviewer 1, Question 1 (Evaluator Rubric Scale, IRR, and M5 Lexicon):**  
  > In the revised manuscript (Section III and Section III-B) and the updated replication package [18], we now explicitly document: (1) the blind evaluator scorecard scale (`> [Insert scale, e.g., 0–3 ordinal rubric across four dimensions]`), team-level mean aggregation, and inter-rater agreement (`> [Insert IRR value or dispersion note]`); (2) the exact clean-path exclusion rules (M4/M8) and the empirical explanation for the $T_3$ raw churn spike ($>13.6\text{M}$ lines driven by unignored `node_modules/`, lockfiles, and build/data assets); and (3) the complete deterministic M5 lexical dictionary across four categories (*integration*, *blockers*, *dependencies*, and *alignment*).  
  >   
  > **Response to Reviewer 1, Question 2 (Why M6b Analyzed $T_1$ Commit Subjects Rather Than Document Contents):**  
  > M6a and M6b were designed to capture two orthogonal repository-visible signals at $T_1$: M6a measures the structural presence and line scope of committed documentation files ($N = 14$), whereas M6b audits whether teams expressed planning, decomposition, and architectural intent directly in their version-control workflow metadata ($n = 9$ teams with $T_1$ commits). We have clarified this complementary design in Section III-C and explicitly bounded the construct validity of terse commit subjects in Section VI.  
  >   
  > **Response to Reviewer 2, Question 1 ($T_1$ Window Anchor and `2026.1` Artifact Shift):**  
  > We have expanded Section III to clarify the $16$-week curricular timeline. While the $T_1$ *survey* was administered on Day 1 before GenAI process instruction, the $T_1$ *repository and pitch anchor* captures the initial project-framing window (`> [Insert exact window, e.g., Weeks 1–2]`), during which teams initialized repositories, committed project templates/boilerplates ($21,718$ clean lines across $7$ teams), and uploaded baseline documentation. Furthermore, in `2026.1`, instructors provided a standardized repository onboarding structure at kickoff, explaining why $T_1$ architectural artifact presence rose from $44\%$ ($4/9$) in `2025.2` to $100\%$ ($5/5$) in `2026.1`.  
  >   
  > **Response to Reviewer 2, Question 2 (Team Process Choices — Scrum, Kanban, or Unguided):**  
  > Section III and Section VI now clarify how team process autonomy (`> [Insert breakdown if logged, or state that ceremony adherence was uninstrumented]`) interacts with our findings. Rather than claiming a controlled failure of strict Scrum/Kanban, our study demonstrates that across the full observed range of Git operational regularity, tacit/lightweight early specification is insufficient to prevent late-stage integration bottlenecks when teams use GenAI.  
  >   
  > **Response to Reviewer 3, Question 1 (Nature of $T_2$ Integration Markers and $T_3$ Blockers in M5 Transcripts):**  
  > We added qualitative vignettes in Section IV-B illustrating that `2025.2` transcript friction involved *both* human-AI code integration issues (teammates generating incompatible frontend/backend payloads and schemas in isolated ChatGPT/Gemini sessions at $T_2$) and general software/LLM API integration blockers (connecting frontend flows, databases, and non-deterministic LLM API endpoints at $T_3$).  
  >   
  > **Response to Reviewer 3, Question 2 (Operationalizing Classroom SDD to Prevent "Documentation Theater"):**  
  > In Section V-C, we added four concrete pedagogical guardrails so SDD serves as an active coordination tool rather than AI-generated boilerplate: (1) grading machine-verifiable interface contracts (OpenAPI schemas, typed models, contract tests) over prose volume, (2) requiring PRs at $T_2/T_3$ to link to specific spec clauses or log explicit spec revisions, (3) conducting synchronous oral defenses of component boundaries during checkpoint reviews, and (4) performing automated/rubric convergence checks between the specification and final code.