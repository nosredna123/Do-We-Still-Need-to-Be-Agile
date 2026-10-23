# ICSE 2027 - Software Engineering Education and Training (SEET) Track
## Peer Review Report

**Paper Title:** Do We Still Need to Be Agile? What Student Projects Reveal About Coordination Skills in the GenAI Era  
**Authors:** Anonymous Authors  
**Format Check:** 10 pages main text + 1 page references (Complies with the 10 + 2 page limit)

---

## Step 1: Dynamic Reviewer Persona Generation

Based on the paper's multi-method observational design—which triangulates multi-checkpoint student surveys, Git repository mining, blind-scored evaluator rubrics, and lexical transcript analysis across $N = 14$ student project teams to motivate Spec-Driven Development (SDD)—the following three complementary Program Committee personas have been assigned:

*   **Reviewer 1 — Empirical SE & Mining Software Repositories (MSR) Methodologist:** Specializes in multi-modal empirical software engineering, repository mining metrics (churn, file-provenance rework, commit concentration), construct validity, and statistical inference in small-$N$ observational studies.
*   **Reviewer 2 — SE Pedagogy & Agile Capstone Education Specialist:** Specializes in project-based learning (PBL), Agile/Scrum pedagogy in undergraduate software engineering courses, student team coordination dynamics (e.g., "student syndrome" vs. iterative delivery), and educational assessment design.
*   **Reviewer 3 — GenAI Workflows & Socio-Technical Coordination Researcher:** Specializes in human-AI software engineering workflows, architectural technical debt in AI-assisted coding, Spec-Driven Development (SDD), and qualitative/textual analysis of developer coordination.

---

## Step 2: Policy Compliance Check

*   **Double-Anonymous Review Policy: COMPLIANT (with minor note on artifact hosting)**  
    The manuscript lists "Anonymous Authors," describes the institutional context generically as *"a large public university in South America,"* and cites all prior work in the third person. Individual and team identifiers are scrubbed from the text and figures (using labels such as `2025.2/TEAM_09`). The Data Availability link ([18]) points to an anonymized Netlify subdomain (`https://moonlit-mochi-1dcef0.netlify.app/#explore`); while this preserves double-anonymity during review, the authors should migrate the archival snapshot (`research-data-001`) to a permanent, DOI-minting repository (e.g., Zenodo or Figshare) upon acceptance.
*   **Open Science Policy: COMPLIANT**  
    The paper includes an explicit **Section VIII. DATA AVAILABILITY** immediately following the Conclusion on Page 10. It provides public access to the aggregated dataset snapshot (`research-data-001`) in JSON and CSV formats via an interactive data explorer and explicitly justifies the omission of raw, verbatim meeting transcript excerpts to protect student privacy.

---

## Step 3: Individual Reviewer Reports

### Reviewer 1: Empirical SE & Mining Software Repositories (MSR) Methodologist

#### 1. Scoring Summary
*   **Overall Recommendation:** Borderline
*   **Reviewer Confidence:** 5 (Expert)

#### 2. Core Evaluation Criteria
*   **Relevance (4/5):** Investigating how Generative AI shifts effort from local coding to team-level integration in student software projects is timely and directly aligned with the ICSE SEET track.
*   **Significance (3/5):** While the multi-stream dataset is rich, the primary empirical tests (RQ3, Table III) yield uniformly null/weak associations ($|\rho| \le 0.301$, $p \ge 0.296$) across only $N = 14$ teams, limiting the strength of the empirical takeaways.
*   **Soundness (4/5):** The authors demonstrate exceptional epistemological discipline regarding grain separation, missingness, and non-causal interpretation, though several proxy constructs (such as commit-subject extraction for planning content and file provenance for rework) suffer from thin construct validity.
*   **Verifiability (4/5):** A public data explorer with downloadable JSON/CSV data (`research-data-001`) is provided, though key operational definitions (e.g., exact regular expressions/lexicons for M5 and path-filtering rules for M4/M8) are missing from the paper text.
*   **Presentation (3/5):** The paper is overly repetitive in its methodological disclaimers, reading in places like an automated statistical audit log at the expense of concrete domain examples and operational clarity.

#### 3. Qualitative Assessment

**Summary:**  
This paper presents an observational study of $N = 14$ undergraduate software engineering project teams across two semesters (`2025.2` with 9 teams and `2026.1` with 5 teams) examined at three checkpoints ($T_1, T_2, T_3$). By triangulating cohort-level surveys (M1–M2), Git repository metrics (M3–M4, M6–M8), global meeting transcript lexical markers (M5), and blind evaluator scores (M9), the authors examine whether upfront architectural artifacts mitigate late-stage integration bottlenecks and rework in GenAI-assisted projects.

**Strengths:**
*   **Exemplary Analytical Grain Separation:** In contrast to many educational mining studies that improperly pool student-level, window-level, and team-level observations, the authors rigorously maintain grain boundaries (Table I) and refuse to over-claim statistical significance on $N = 14$ team-semesters.
*   **Thoughtful Robustness Diagnostics:** The inclusion of non-overlapping phase bins, baseline-eligibility filtering ($n = 12$ for rework ratios), leave-one-out sensitivity checks, and technical-complexity stratification (Figure 7) demonstrates mature empirical awareness.
*   **Multi-Modal Triangulation:** Combining self-reported perceptions, Git activity, independent multi-evaluator blind scorecards, and transcript marker density provides a multifaceted view of student project execution.

**Weaknesses:**
*   **Opaque Operationalization of Key Constructs in the Text:** Critical methodological details are outsourced to the external data explorer or omitted altogether. Specifically, the exact "versioned clean-path policy" (M4), the deterministic lexical dictionary for coordination friction (M5), the prompt/schema used for LLM extraction of $T_1$ commit subjects (M6b), and the evaluator scorecard scale and inter-rater reliability (IRR) are not defined in the manuscript.
*   **Weak Construct Validity of M6a/M6b and M8:** Measuring upfront architectural planning via $T_1$ file counts/line deltas (M6a) and LLM-extracted *commit subject lines* (M6b) is a very noisy proxy. Commit subject lines rarely contain substantive architectural specifications or risk decompositions. Similarly, defining "destructive rework" (M8) purely as late-stage line modifications to previously touched clean files conflates normal iterative feature refinement with rework.
*   **Repetitive Guardrail Prose:** Almost every subsection repeats variations of *"these are descriptive diagnostics, not confirmatory tests"* and *"incompatible grains are not combined."* While accurate, stating this once clearly in Section III-A and Section VI would free up roughly 1.5 pages for substantive empirical details.

**Detailed Comments for Authors:**
1.  **Clean Churn Drop at $T_3$ (Section IV-B):** You report that clean change accounts for $42.9\%$ at $T_1$, $19.6\%$ at $T_2$, and only $1.0\%$ of all recorded churn at $T_3$ (even though pooled clean churn is $136,325$ lines at $T_3$, implying over $13.6\text{M}$ total churn lines at $T_3$). What were teams committing at $T_3$ that generated $>13\text{M}$ lines of non-clean churn (e.g., `node_modules`, datasets, build binaries, vendor lockfiles), and what specific path exclusions define the "clean-path policy"?
2.  **Evaluator Scorecard Psychometrics:** In Section III, you note that projects were blind-scored by 4 evaluators in `2025.2` and 3 evaluators in `2026.1` across dimensions like Project Progress, Scope Applicability, Technical Complexity, and Engagement. What was the rating scale (Figures 3 and 7 suggest values clustered around $1.1$ to $2.5$)? How were evaluator scores aggregated, and what was the inter-rater agreement (e.g., ICC or Krippendorff's $\alpha$)?
3.  **M6b Commit Subject Extraction:** Extracting "goals, architecture/design, task decomposition, risk/dependency" from *commit subjects* at $T_1$ (usually a single line under 72 characters, such as `"Initial commit"` or `"Add architecture docs"`) seems highly constrained. Why did M6b analyze commit subjects rather than parsing the actual markdown/documentation files committed at $T_1$ (M6a)?
4.  **Table Formatting Issues:** Table I and Table III have minor alignment and header formatting glitches (e.g., in Table III, the column headers read `Predictor Outcome | Stratum | 72 | | pExploratory p`, where sample size $n$ appears to be misrendered as `72` and $\rho$ is merged with `Exploratory p`; also Predictor and Outcome columns are swapped in rows 3–4 and 6–8). Please fix the LaTeX table syntax.

**Questions for the Rebuttal:**
1.  Can you provide the exact rubric scale and inter-rater reliability metrics for the blind evaluator scorecards across the two cohorts, as well as the specific lexical dictionary used to compute M5?
2.  Why did M6b extract planning content from $T_1$ *commit subjects* ($n = 9$) rather than analyzing the actual contents of the repository-visible architectural artifacts identified in M6a?

---

### Reviewer 2: SE Pedagogy & Agile Capstone Education Specialist

#### 1. Scoring Summary
*   **Overall Recommendation:** Weak Accept
*   **Reviewer Confidence:** 5 (Expert)

#### 2. Core Evaluation Criteria
*   **Relevance (5/5):** The central question—"Do we still need to be Agile in the GenAI era?"—is one of the most pressing curricular debates among SE educators running capstone and project courses today.
*   **Significance (4/5):** The paper provides valuable empirical pushback against two naive extremes: the belief that GenAI eliminates the need for software process, and the belief that late commit spikes in AI-assisted student teams are nothing more than classic "student syndrome."
*   **Soundness (3/5):** While the data analysis is cautious, the pedagogical context (course structure, instructional scaffolding, team coaching, and how Agile was actually taught or practiced) is significantly under-described.
*   **Verifiability (4/5):** The companion data explorer is a strong artifact for the SEET community, though replication in another university setting would require the survey instruments, course syllabus checkpoints, and evaluation rubrics.
*   **Presentation (3/5):** The framing in the Introduction and Discussion is compelling and well-written, but the Results section is bogged down by dense metric codes (M1–M9) and lacks concrete qualitative examples of student team behaviors.

#### 3. Qualitative Assessment

**Summary:**  
This paper investigates how undergraduate software engineering teams use GenAI across a semester-long project course and how their work patterns, perceptions of SE roles, and upfront planning artifacts relate to late-stage integration and project grades. Based on findings that repository activity and coordination friction spike near final delivery regardless of simple upfront artifact volume, the authors argue that SE pedagogy must evolve from lightweight/tacit Agile toward explicit, iterative specification practices such as Spec-Driven Development (SDD).

**Strengths:**
*   **Nuanced Deconstruction of "Student Syndrome":** By cross-tabulating final-7-day commit concentration against evaluator score changes and planning scope (Figure 3), the authors convincingly show that late-stage repository spikes represent multiple distinct phenomena—compensatory recovery, uncoordinated late dumping, and complex system integration—rather than simple procrastination.
*   **Important Longitudinal Perception Findings (RQ1):** Showing that students' perceived "autonomy/tool balance" increases over the semester while perceived "AI benefit" diverges between cohorts (increasing in `2025.2`, declining in `2026.1` as shown in Figure 1) captures a realistic maturation (or disillusionment) curve as students move from toy prompts to full system integration.
*   **Actionable Pedagogical Thesis:** The argument in Section V-C—that educators should shift assessment toward explicit API contracts, cross-component dependencies, and verifiable acceptance criteria—offers a constructive path forward for modernizing Agile project courses.

**Weaknesses:**
*   **Missing Pedagogical and Curricular Context:** For an ICSE SEET paper, we learn surprisingly little about the educational setting. What year of study are these ~70 students in? What were the deliverables required at $T_1$, $T_2$, and $T_3$? You note that $T_1$ was administered on the *"first day of class, before formal instruction on GenAI processes."* If $T_1$ is the first day of class (or a 7-day window around it), why would teams already have code commits or architectural artifacts in Git on Day 1?
*   **Uncontrolled Process Heterogeneity vs. Title Claim:** The title asks *"Do We Still Need to Be Agile?"*, yet Section III states that teams *"had autonomy over process model and project management approach, including Scrum, Kanban, other Agile variants, or unguided work."* Because the paper never reports how many of the 14 teams actually used Scrum/Kanban versus "unguided work," it is difficult to attribute coordination bottlenecks to a limitation of *Agile* rather than a lack of basic process compliance in unguided student teams.
*   **Lack of Qualitative Illustration from Transcripts (M5):** You have 100 chunks of status presentations and supervisor discussions from `2025.2` showing a $2.5\times$ increase in coordination-language marker density from $T_1$ ($0.515$) to $T_3$ ($1.287$), with integration markers peaking at $T_2$ ($20/54$) and blockers at $T_3$ ($7/40$). Even if verbatim quotes cannot be shared in the public dataset for privacy, paraphrased pedagogical vignettes illustrating *what* integration issues students struggled with would vastly enrich the paper.

**Detailed Comments for Authors:**
1.  **Clarify the Timeline of $T_1$, $T_2$, and $T_3$:** In Section III, you state that $T_1$ occurred on the first day of class, $T_2$ followed instructional modules, and $T_3$ occurred one week before final delivery. Yet at $T_1$, 7 teams already had $21,718$ lines of clean churn (Table II), and 4 teams in `2025.2` plus all 5 teams in `2026.1` had repository-visible $T_1$ architectural artifacts (Figure 5). Why did all 5 teams in `2026.1` have architectural artifacts at $T_1$ compared to $4/9$ in `2025.2`? Did instructor expectations or templates change between cohorts?
2.  **Unpack Survey Scales in Figure 1:** In Figure 1, "Autonomy/tool balance" hovers around $3.0–3.5$, "AI benefit" around $1.6–2.2$, and "Project challenges" / "Project feeling" near $0.1–0.5$ on a $0–5$ y-axis labeled `"Mean score (family scale)"`. Why are the bottom three families near zero? Were they binary counts or proportions rather than 5-point Likert scales? Explaining what these scales mean pedagogically is essential for interpreting RQ1.
3.  **Strengthen the SE Education Literature Grounding:** The related work cites classic software engineering texts (Brooks [4], DeMarco & Lister [5], Beck et al. [3]) and several industry blog posts ([1], [2], [21], [22]), but cites very little peer-reviewed computing education literature on student team coordination, capstone assessment, or GenAI in SE courses (beyond Yabaku & Ouhbi [10], Haindl & Weinberger [28], and Bruegge et al. [30]). Integrating recent ICSE-SEET / SIGCSE / TOCE work on how GenAI affects student collaboration and design comprehension would strengthen the scholarly foundation.

**Questions for the Rebuttal:**
1.  How is the $T_1$ measurement window defined relative to project kickoff, and did the instructor introduce an explicit repository template or rubric requirement in `2026.1` that explains why $100\%$ ($5/5$) of `2026.1` teams had $T_1$ architectural artifacts compared to $44\%$ ($4/9$) in `2025.2`?
2.  Do you have records of which process model (Scrum, Kanban, or unguided) each of the 14 teams adopted, and how did that choice relate to operational regularity and $T_3$ coordination friction?

---

### Reviewer 3: GenAI Workflows & Socio-Technical Coordination Researcher

#### 1. Scoring Summary
*   **Overall Recommendation:** Weak Accept
*   **Reviewer Confidence:** 4 (High)

#### 2. Core Evaluation Criteria
*   **Relevance (5/5):** The intersection of GenAI coding assistants, architectural coordination, and specification practices is at the forefront of contemporary software engineering education and practice.
*   **Significance (4/5):** The paper conceptualizes and empirically motivates the "shifted bottleneck" hypothesis—that GenAI lowers the cost of local code synthesis while increasing the socio-technical cost of architectural alignment and integration.
*   **Soundness (3/5):** Because the study lacks direct AI-use telemetry or code-provenance tracking for AI-generated code, the link between GenAI usage (measured at the cohort grain in RQ1) and team repository/rework dynamics (measured at the team grain in RQ2/RQ3) remains indirect and ecological.
*   **Verifiability (4/5):** The released data artifact and transparent reporting of null results and sensitivity maps support high research integrity.
*   **Presentation (4/5):** The conceptual framing around Agile vs. Spec-Driven Development (SDD) is insightful and intellectually honest about distinguishing observational motivation from intervention testing.

#### 3. Qualitative Assessment

**Summary:**  
This study examines the tension between rapid, AI-assisted local code generation and team-level architectural coordination across 14 student software engineering projects that built GenAI-enabled applications. Combining cohort surveys on AI tool usage and role disruption with Git activity/rework analysis and meeting transcript markers, the authors demonstrate that naive structural volume of early documentation does not prevent late integration churn, motivating Spec-Driven Development (SDD) as an iterative specification framework for human-AI teams.

**Strengths:**
*   **Intellectual Honesty Regarding Spec-Driven Development (SDD):** In an era where many papers over-hype new AI methodologies, the authors are commendably transparent that SDD was *not* implemented or tested in this study, framing it rigorously as a testable hypothesis derived from the observed coordination bottleneck.
*   **Dual Focus on GenAI as Both Development Tool and System Component:** The studied projects did not just use GenAI (ChatGPT, Gemini) to write code; each team also had to engineer a working software system containing an integrated GenAI component (e.g., chatbots, summarization, document analysis). This mirrors modern software engineering reality.
*   **Insightful Role-Disruption Findings (M2):** The finding that students perceive frontend roles as highly susceptible to GenAI disruption while project-management and coordination roles remain more resilient aligns well with the paper's core socio-technical thesis.

**Weaknesses:**
*   **Ecological Disconnect Between RQ1 (Cohort AI Use) and RQ2/RQ3 (Team Repo Dynamics):** Because the multi-checkpoint surveys (M1/M2) carried *no team identifiers*, the authors cannot link the intensity or nature of a specific team's GenAI usage to that team's commit concentration (M3), clean rework (M8), or evaluator outcomes (M9). Thus, we cannot tell if the teams experiencing severe $T_3$ rework were the heaviest users of GenAI code generation or the lightest.
*   **Conflation of Building a GenAI Feature vs. Using GenAI to Code:** All 14 teams were tasked with building an application with an integrated GenAI component (after learning about RAG between $T_1$ and $T_2$, though none built a full RAG pipeline). Late-stage integration spikes and rework could stem from students struggling with LLM API integration, prompt engineering, and non-deterministic outputs in their product domain, rather than from using GenAI coding assistants to generate source code.
*   **Informal Literature in Bibliography:** References [1], [2], [19], [20], [21], and [22] rely heavily on blog posts (Codebridge, Cambridge Advance Online, GitHub Blog, Thoughtworks) and unrefereed preprints. While citing [1] and [2] is understandable to contextualize the emerging industry term "Spec-Driven Development," general claims about GenAI contextual gaps and hidden costs should be anchored in peer-reviewed SE venues (e.g., ICSE, FSE, TOSEM, TSE).

**Detailed Comments for Authors:**
1.  **Bridging the Gap Between Cohort AI Usage and Team Rework:** You rightly refuse to correlate M1 (cohort grain) with M3/M8 (team grain). However, did the evaluator scorecards, commit messages, or `2025.2` transcripts provide any team-level qualitative evidence of *how* GenAI-generated code contributed to the integration bottlenecks at $T_2$ and $T_3$ (e.g., mismatched interfaces generated by different teammates' LLM sessions, hallucinated dependencies, or inconsistent coding styles)?
2.  **Why Did No Team Implement RAG?** In Section III, you mention that RAG was taught between $T_1$ and $T_2$ as a domain-dependent example, yet *"none of the 14 projects implemented a full RAG pipeline."* From a socio-technical and educational perspective, why did all 14 teams opt out of RAG in favor of simpler API integrations (summarization, chatbots)? Was RAG too architecturally complex for the timeframe, and how did that affect the Evaluator Technical Complexity score (which had a median of $1.875$)?
3.  **Refining the SDD Proposition for SE Education:** In Section V-C, you propose SDD as a way to maintain an explicit specification across planning, task decomposition, and convergence checks. In a classroom setting, how can instructors prevent SDD from degenerating into students using GenAI to auto-generate bloated, superficial markdown specifications at $T_1$—which your own RQ3 results show have no correlation with reduced rework ($\rho = 0.206$ to $0.301$)?

**Questions for the Rebuttal:**
1.  In the `2025.2` meeting transcripts (M5), did the integration markers at $T_2$ ($20/54$) and blockers at $T_3$ ($7/40$) explicitly reference problems caused by integrating AI-generated code fragments across teammates, or were they general software integration issues (e.g., frontend-to-backend API mismatches, database deployment)?
2.  How would you operationalize SDD in a future iteration of this course so that students' specifications serve as genuine cognitive coordination tools rather than AI-generated documentation theater?

---

## Step 4: Meta-Review / Consensus Summary

The Program Committee reviewers agree that this submission tackles a highly relevant and timely problem for the ICSE 2027 SEET community: understanding how Generative AI reshapes the balance between local coding speed, upfront architectural planning, and team coordination in undergraduate software projects. All three reviewers praise the authors' methodological honesty, strict preservation of analytical grains, compliance with Open Science practices via an interactive data explorer, and nuanced deconstruction of late-stage commit spikes ("student syndrome" vs. compensatory integration recovery). However, the reviewers also share critical concerns that must be addressed: (1) the manuscript's prose is overly defensive and repetitive with methodological disclaimers, which crowds out essential operational definitions (rubric scales, inter-rater reliability, clean-path rules, and M5 lexical dictionaries) and concrete pedagogical context; (2) the construct validity of measuring planning via $T_1$ line counts and commit subjects (M6) is thin, and the lack of team identifiers on surveys prevents linking team-level AI usage intensity directly to rework; and (3) there are minor presentation issues (e.g., malformed headers in Table III and reliance on blog posts in the bibliography). **Preliminary Consensus Direction for the Area Chair: Weak Accept (shepherded / conditional on revision).** If the authors can clarify the curricular timeline and rubric details in the rebuttal, fix the table formatting, and commit to streamlining the repetitive meta-commentary in favor of concrete operational definitions and qualitative pedagogical examples, this paper will make a thought-provoking and methodologically responsible contribution to the SEET program.