# ICSE 2027 - Software Engineering Education and Training (SEET) Track
## Peer Review Report

**Paper Title:** Do We Still Need to Be Agile? What Student Projects Reveal About Coordination Skills in the GenAI Era  
**Authors:** Anonymous Authors  
**Track:** Software Engineering Education and Training (SEET)  

---

## Step 1: Dynamic Reviewer Persona Generation

Based on the paper's focus on multi-method empirical analysis of student software projects, repository mining, Agile coordination, and Generative AI adoption across two university cohorts, the following three complementary reviewer personas have been assigned to evaluate this submission:

*   **Reviewer 1: Empirical Software Engineering & Repository Mining Specialist**  
    *Specialty:* Multi-method empirical study design, software repository mining (MSR), construct validity of code churn and rework proxies, inter-rater reliability, and statistical robustness in small-sample longitudinal panels.
*   **Reviewer 2: Software Engineering Pedagogy & Agile Education Researcher**  
    *Specialty:* Project-based software engineering curricula, Agile team processes in undergraduate education, team coordination dynamics, assessment rubrics, and pedagogical interventions.
*   **Reviewer 3: GenAI in Software Engineering & Socio-Technical Coordination Expert**  
    *Specialty:* Human-AI developer workflows, LLM-assisted coding and specification practices (e.g., Spec-Driven Development), qualitative/NLP analysis of developer communication, and Open Science replication artifacts.

---

## Step 2: Policy Compliance Check

*   **Double-Anonymous Review Policy: COMPLIANT**  
    *   *Evaluation:* Author identities are masked as "Anonymous Authors." The institution is described generically as "a large public university in South America" (Section III), with contextual clues limited to Portuguese lexical markers in the transcript analysis (which does not identify a specific institution). Prior literature is cited exclusively in the third person, and the online artifact is hosted on an anonymized domain (`netlify.app`) under a generic snapshot identifier (`research-data-001`).
*   **Open Science & Data Availability Policy: COMPLIANT**  
    *   *Evaluation:* Section VIII (*Data Availability*) appears immediately after the Conclusion (Section VII). It provides an anonymized link to an interactive data explorer and replication package containing JSON/CSV datasets, path-filtering rules (M4/M8), regular expressions (M5), LLM prompts/schemas (M6b), survey instruments (M1/M2), and evaluator scorecards (M9). Raw meeting transcripts are appropriately withheld to protect student privacy, and the authors commit to archiving the package on Zenodo with a persistent DOI upon acceptance.

---

## Step 3: Individual Reviewer Reports

### Reviewer 1 (Empirical Software Engineering & Repository Mining Specialist)

#### 1. Scoring Summary
*   **Overall Recommendation:** Borderline
*   **Reviewer Confidence:** 5 (Expert)

#### 2. Core Evaluation Criteria
*   **Relevance (4/5):** Studying how Generative AI shifts effort between local code authoring and team-level integration in student capstone/project courses is squarely aligned with the ICSE SEET call for empirical studies at the intersection of AI and SE education.
*   **Significance (3/5):** While the paper offers a commendable example of transparent reporting and proxy hygiene, the empirical findings for its primary research question (RQ3) are predominantly noisy and null, limiting the strength of the conclusions that can be drawn.
*   **Soundness (3/5):** The authors are exceptionally honest about what their metrics can and cannot claim ("strict grain preservation"), yet fundamental design breaks—such as unlinked analytical grains, $N = 14$ team-semesters, and low evaluator inter-rater agreement—severely constrain internal and construct validity.
*   **Verifiability (5/5):** The replication package, explicit regular expressions, clean-churn path exclusion audits, and leave-one-out diagnostics set a high bar for transparency and computational reproducibility.
*   **Presentation (4/5):** The manuscript is well-written, logically organized, and visually clear, though the prose occasionally reads like an audit log of methodological disclaimers rather than a cohesive narrative.

#### 3. Qualitative Assessment
*   **Summary:**  
    This paper presents an observational, multi-method study of $N = 14$ undergraduate software engineering project teams across two academic cohorts (2025.2 and 2026.1) over three checkpoints ($T_1, T_2, T_3$). By triangulating student surveys (M1–M2), Git repository activity and clean-path churn/rework metrics (M3–M4, M6–M8), global meeting transcripts (M5), and independent evaluator scorecards (M9), the authors investigate whether GenAI adoption shifts project bottlenecks toward late-stage integration and whether upfront architectural artifacts mitigate late rework.

*   **Strengths:**
    *   **Exemplary Methodological Candor and "Grain Preservation":** Rarely do we see an empirical SE paper so scrupulously refuse to overclaim. The authors explicitly refuse to pool incompatible denominators, conduct a rigorous path audit of raw vs. clean churn (identifying over $13.36 \times 10^6$ lines of `venv/` and `node_modules/` pollution at $T_3$), and report leave-one-out sensitivity ranges.
    *   **Multi-Stream Triangulation:** Combining four distinct data sources (surveys, Git provenance, blind-scored status evaluations, and presentation transcripts) provides a multifaceted descriptive view of student project lifecycles.
    *   **Thorough Robustness Diagnostics:** The use of non-overlapping phase bins, operational regularity proxies, and complexity stratifications demonstrates strong awareness of confounds like "student syndrome" (deadline procrastination).

*   **Weaknesses:**
    *   **Disconnected Analytical Grains Prevent True Triangulation:** Because survey responses (M1/M2) carry no team identifiers and the transcript corpus (M5) is pooled globally without team tags (and exists only for 2025.2), the study *cannot* test whether the teams that used GenAI most heavily—or experienced the most verbal coordination friction—are the same teams that suffered late repository spikes or rework.
    *   **Low Evaluator Reliability on Key Stratification Variables:** Ordinal Krippendorff's $\alpha$ for evaluator scorecards is concerningly low on several dimensions, most notably Technical Complexity ($\alpha = 0.242$ in 2025.2 and $\alpha = 0.308$ in 2026.1) and Engagement ($\alpha = 0.294$ in 2025.2). Using the median $T_3$ Technical Complexity score ($1.875$) to stratify Spearman correlations in RQ3 builds a sensitivity analysis on top of a noisy measurement instrument.
    *   **Severely Underpowered Primary Analysis (RQ3) and Fragile Proxies:** With $N = 14$ teams ($n = 12$ for rework ratios; $n = 9$ for M6b commit-subject analysis), Spearman correlations in Table III are all statistically indistinguishable from noise ($p \in [0.296, 0.931]$). Furthermore, three teams have fewer than 10 commits across the entire semester, meaning their repository metrics represent sparse commit habits (e.g., squashed or infrequent mega-commits) rather than true development cadence.

*   **Detailed Comments for Authors:**
    *   **Construct Validity of M6a, M6b, and M8:** In M6a, upfront architectural scope at $T_1$ is operationalized via repository-visible file counts and line deltas ($\log(1 + \text{lines})$). In 2025.2, the median $T_1$ file count is $0$ (5 of 9 teams had no $T_1$ repo artifact), whereas in 2026.1 all 5 teams had artifacts. As you note, you cannot explain whether an instructional onboarding change caused this jump between cohorts. Pooling 2025.2 and 2026.1 into an $N = 14$ rank correlation in Table III therefore conflates a massive cohort shift with team-level variation. What happens to the M9 associations if computed *within* cohorts or after standardizing by cohort?
    *   **M8 File-Provenance Rework Proxy:** Defining "clean-path rework" as any $T_3$ line modification to a source/test file first observed at $T_1$ or $T_2$ penalizes iterative Agile refinement. In an iterative project, modifying `main.py` or a core controller file created at $T_1$ during $T_3$ is normal feature accretion and refactoring, not necessarily "destructive rework." Calling this a proxy for destructive rework (Section IV-C) stretches construct validity.
    *   **Temporal Misalignment of Anchors:** Section III notes that survey waves ($T_1$–$T_3$) fell around weeks $1, 9, 13$ (or $1, 11, 15$), whereas evaluator scorecards fell around weeks $7\text{--}8, 11\text{--}12, 14\text{--}15$ (or $8, 12, 16$). Because $T_1$ surveys occurred in Week 1 and $T_1$ evaluator anchors occurred in Weeks 7–8, please clarify in Section III exactly which timestamp defines the "$T_1$" cutoff for repository metrics M4, M6a, M6b, and M8.
    *   **Typo in Table III:** In Table III, the column header for sample size appears to be rendered as an italic "$72$" (or misformatted "$n$") instead of "$n$". Also, the first row lists "$T_2$ rework magnitude" under the "Outcome ($T_3$)" column—please verify if this is a typographical error for "$T_3$ rework magnitude."

*   **Questions for the Rebuttal:**
    1.  Given that $T_1$ architectural artifact presence jumped from $4/9$ in 2025.2 to $5/5$ in 2026.1, how sensitive are the RQ3 rank correlations in Table III to cohort fixed effects (i.e., evaluating 2025.2 and 2026.1 separately)?
    2.  Could you clarify the exact temporal cutoff used to extract $T_1$ repository artifacts (M6a/M6b) and baseline files (M8)—was it anchored to the Week 1 survey date or the Week 7–8 first evaluator presentation date?

---

### Reviewer 2 (Software Engineering Pedagogy & Agile Education Researcher)

#### 1. Scoring Summary
*   **Overall Recommendation:** Weak Accept
*   **Reviewer Confidence:** 5 (Expert)

#### 2. Core Evaluation Criteria
*   **Relevance (5/5):** The provocative title question—"Do We Still Need to Be Agile?"—and the investigation of team coordination vs. upfront design in AI-assisted student capstone projects address one of the most urgent pedagogical debates in the SEET community today.
*   **Significance (4/5):** Even though the correlational findings are modest, the conceptual framing of the "shifted bottleneck" (from local code authoring to shared architectural intent) and the concrete operationalization of Spec-Driven Development (SDD) for educators provide high value for curriculum designers.
*   **Soundness (3/5):** From an educational research standpoint, the complete lack of visibility into how teams actually practiced Agile (e.g., whether they used Scrum, Kanban, or ad-hoc chaos) makes it difficult to attribute coordination friction to "Agile in the GenAI era" versus poor student process adherence.
*   **Verifiability (4/5):** The survey instruments, rubrics, and aggregated datasets are openly shared, though the absence of verbal endpoint anchors on the course grading rubrics limits pedagogical replication of the assessment instrument.
*   **Presentation (4/5):** Engaging introduction and discussion sections that frame the pedagogical tension exceptionally well, bookending a very dense empirical results section.

#### 3. Qualitative Assessment
*   **Summary:**  
    This study examines how undergraduate software engineering teams navigate project development when using Generative AI tools, focusing on the tension between rapid local code generation and team-wide coordination/integration. Drawing on two semesters of project course data ($N = 14$ teams), the authors demonstrate that despite high individual AI adoption, teams still face severe late-stage integration crunches and rising coordination friction, motivating a pedagogical shift toward iterative Spec-Driven Development (SDD).

*   **Strengths:**
    *   **Timely and Provocative Pedagogical Framing:** The paper moves beyond the saturated literature on "CS1 students using ChatGPT for homework" to examine multi-person software engineering team dynamics, architectural alignment, and integration across a full semester.
    *   **Nuanced Critique of "Student Syndrome":** Rather than dismissing late commit spikes as mere undergraduate procrastination, Figure 3 and the internal contrasts distinguish between compensatory late recovery (high late activity with score gains), failed late crunches, and steady progress.
    *   **Actionable Pedagogical Recommendations (Section V-C):** The four proposed classroom practices for operationalizing Spec-Driven Development—such as machine-checkable interface-contract tests instead of grading document volume, and brief checkpoint defenses of component boundaries—are practical and inspiring for SE educators.

*   **Weaknesses:**
    *   **"Agile" is in the Title, But Unobserved in the Classroom:** The central premise of the paper is testing the "Agile bet" in the GenAI era. Yet Section III admits that *"Course records did not formally record teams' process selections or adherence to ceremonies, so we cannot report a distribution across Scrum, Kanban, other Agile variants, or unguided work."* If we do not know whether students were actually practicing Agile (versus waterfall or chaotic "code-and-fix"), how can their coordination struggles be framed as a limitation of Agile?
    *   **Disconnect Between Empirical Findings and the SDD Prescription:** In RQ3, teams that produced larger upfront architectural artifacts at $T_1$ actually had a positive (though non-significant) rank correlation with $T_3$ rework magnitude ($\rho = 0.301$) and virtually zero correlation with project outcomes ($\rho = 0.096$ for progress). While the authors acknowledge that artifact *volume* does not equal specification *quality*, nearly two pages of the paper advocate for Spec-Driven Development (SDD)—an intervention that was neither taught nor tested in the study.
    *   **Opaque Pedagogical Context and Assessment Rubrics:** Readers learn very little about the instructional scaffolding of the course. Were students taught software architecture, Git branching workflows, or prompt engineering? Furthermore, the evaluator scorecard dimensions (e.g., 0–2 scale in 0.5 steps) lack verbal rubric descriptions in the versioned records, making it unclear how instructors defined "Project Progress" or "Scope/Applicability."

*   **Detailed Comments for Authors:**
    *   **Refining the Agile Argument:** In many undergraduate project courses, when teams are given complete autonomy over their process model without enforced sprint ceremonies or coaching, they default to ad-hoc work followed by deadline-driven integration. Without a pre-GenAI baseline cohort from the same course or observation of Agile practices, the late commit spike in Figure 2 looks remarkably like classic pre-GenAI student project behavior. I encourage the authors to temper the claim that GenAI *caused* or *relocated* this bottleneck, and instead frame the data as showing that *GenAI fails to alleviate* classic student integration bottlenecks unless paired with explicit coordination mechanisms.
    *   **Highlighting Task Decomposition (M6b):** One of your most pedagogically interesting exploratory findings is buried briefly in Section IV-C: within the M6b commit-subject subset ($n = 9$), *task-decomposition evidence* had the strongest negative association with clean-rework magnitude ($\rho = -0.408$) and the strongest positive association with scope applicability ($\rho = 0.479$). In an Agile education context, breaking work down into manageable tasks is far closer to Agile backlog refinement than writing big upfront architecture documents. Emphasizing this contrast would strengthen your bridge to iterative SDD!
    *   **Role Disruption Perceptions (M2):** In RQ1 (Section IV-A), you note that students perceive Frontend roles as more disrupted by GenAI than Project Management roles. Discussing *why* students experience this in their projects (e.g., LLMs easily generate React/HTML boilerplate, whereas human teammates still have to negotiate scope and chase blocked tasks) would enrich the pedagogical narrative in Section V.

*   **Questions for the Rebuttal:**
    1.  What instructional guidance, templates, or grading incentives were given to students regarding Agile ceremonies and $T_1$ architectural documentation in 2025.2 versus 2026.1?
    2.  Since your course did not track whether teams used Agile practices, how do you distinguish between "Agile is insufficient in the GenAI era" and "students did not actually follow Agile practices"?

---

### Reviewer 3 (GenAI in Software Engineering & Socio-Technical Coordination Expert)

#### 1. Scoring Summary
*   **Overall Recommendation:** Weak Accept
*   **Reviewer Confidence:** 4 (High)

#### 2. Core Evaluation Criteria
*   **Relevance (5/5):** Directly addresses the socio-technical impact of GenAI coding assistants on collaborative software engineering skills, a core theme for ICSE SEET.
*   **Significance (4/5):** Bridges the gap between individual developer-AI interaction studies (e.g., Barke et al.) and team-level software engineering education, highlighting that AI-generated local code exacerbates interface and context mismatches across teammates.
*   **Soundness (4/5):** The lexical and LLM-assisted extraction pipelines (M5 and M6b) are well-constrained with deterministic validation and human review gates, though the "inherited ordinal NLP score" in M1 is insufficiently explained in the manuscript.
*   **Verifiability (5/5):** Outstanding open science practices; prompts, JSON schemas, regex dictionaries, and interactive sensitivity maps are openly accessible.
*   **Presentation (3/5):** Some figures (notably Figure 1 and Figure 7) suffer from visual clutter or cramped legends, and several methodological constructs ("inherited ordinal NLP rubric") require clearer self-contained explanations in the text.

#### 3. Qualitative Assessment
*   **Summary:**  
    This paper investigates how Generative AI adoption interacts with human coordination and software architecture in undergraduate team projects. Using longitudinal student surveys, repository mining, LLM-assisted commit classification, and lexical transcript analysis, the authors show that while students heavily adopt GenAI for local tasks (coding, debugging, research) and build AI-integrated systems, team coordination friction and integration bottlenecks intensify toward final delivery.

*   **Strengths:**
    *   **Disciplined Use of LLMs and NLP in Research Methodology:** In Section III-C, the authors clearly separate deterministic lexical matching (M5) from bounded LLM extraction (`gpt-4o-mini` at temperature $0$ with verbatim quote verification against commit hashes for M6b). This is a textbook example of how to use LLMs for qualitative coding in SE research without hallucinating composite scores.
    *   **Dual Lens on GenAI (GenAI as Assistant vs. GenAI as System Component):** The studied teams both *used* GenAI to write their software and *built* GenAI-integrated applications (e.g., chatbots, summarization, profile analysis). The qualitative transcript excerpt at $T_3$ (where a model tier limitation switched a team from Gemini Pro to Flash, breaking context handling and output formatting) is a fantastic real-world illustration of AI-specific architectural fragility.
    *   **Rich Open Science Explorer:** The accompanying web-based data explorer (`research-data-001`) makes inspecting the small-sample data and leave-one-out sensitivity completely transparent.

*   **Weaknesses:**
    *   **Unexplained "Inherited Ordinal NLP Score" in RQ1 (M1):** In Section IV-A and Figure 1, the paper states that each plotted point is *"the mean of an inherited ordinal NLP score (integer 0–4) for one question... approved for descriptive use only, not as a validated measure of AI dependence."* What is an "inherited ordinal NLP score"? Was an NLP model or LLM used in a prior study to score open-ended survey text onto a 0–4 scale? Because the paper must be self-contained, leaving this primary RQ1 metric unexplained is a notable presentation gap.
    *   **Conflation of Developing *with* GenAI vs. Developing *a* GenAI Application:** All 14 teams were required to build a software system containing an integrated GenAI component (Section III). Building LLM-backed features introduces unique non-determinism, API quota blockers, and prompt-output parsing bugs (as seen in the $T_3$ transcript example). The paper does not disentangle whether the coordination friction and late rework stemmed from *using GenAI coding assistants* to write code or from the technical complexity of *integrating external LLM APIs* into their products.
    *   **Surface-Level Lexical Matching in M5:** Counting Portuguese regex tokens (`merge`, `conflito`, `alinhamento`, `retrabalho`) per 1,000 tokens in status presentations (M5) is a very coarse proxy for coordination friction. As projects approach final delivery at $T_2$ and $T_3$, teams naturally discuss code integration (`merge`) and final review (`revisão`) more frequently than at project kickoff ($T_1$), regardless of whether they are experiencing dysfunctional friction.

*   **Detailed Comments for Authors:**
    *   **Clarifying M1 Survey Scoring:** Please expand Section III-B and Section IV-A to explain the exact provenance of the M1 survey scales. What were the actual survey questions asked to students, were the responses open-ended text or Likert items, and how was the 0–4 "inherited ordinal NLP rubric" constructed and validated?
    *   **Visual Presentation Fixes:**
        *   *Figure 1:* The standard deviation error bars for the six perception families overlap heavily, making it difficult to read individual intervals, and plotting a 0–4 scale on a 0–5 vertical axis leaves unnecessary whitespace while compressing the bottom three trajectories ("Career expectation", "Project feeling", "Project challenges") near zero.
        *   *Figure 7:* The legend at the top ("High planning - 2025.2", "Lower planning - 2026.1", etc.) is cramped and overlaps with the top of the plot area, and the y-axis label ("$T_3$ clean rework magnitude (changed lines)") is slightly clipped on the left margin.
        *   *Table I:* In the row combining M6, M7, and M8, the text wraps awkwardly across columns ("Team-semester ($N=14 / n=9$)" appears above "Upfront Architecture Evidence"). Please separate M6, M7, and M8 into distinct table rows with horizontal rules or clean padding.
    *   **Disentangling AI-as-Tool vs. AI-as-Product:** In Section V or Section VI, please explicitly discuss the duality that students were simultaneously *using* GenAI coding assistants and *building* GenAI-powered applications. How much of the late architectural friction is attributable to the former versus the latter?

*   **Questions for the Rebuttal:**
    1.  Can you explain in self-contained terms how the "inherited ordinal NLP score (0–4)" in M1 (Figure 1) was generated from the raw student survey responses?
    2.  To what extent do the coordination blockers observed in the transcripts (M5) reflect friction caused by *using AI coding assistants* (e.g., incompatible AI-generated code across teammates) versus friction caused by *building AI-integrated product features* (e.g., LLM API rate limits, prompt formatting bugs)?

---

## Step 4: Meta-Review / Consensus Summary

The Program Committee reviewers agree that this submission tackles a highly relevant, timely, and engaging topic for the ICSE 2027 SEET track: how Generative AI reshapes the balance between local coding speed, upfront architectural specification, and team coordination in student software engineering projects. All three reviewers praise the authors' exceptional methodological candor, rigorous proxy hygiene (such as auditing excluded virtual-environment churn and refusing to pool incompatible analytical grains), and exemplary Open Science replication package. However, the reviewers also converge on several critical limitations: (1) the primary empirical analysis in RQ3 ($N = 14$ teams) yields weak, statistically non-significant associations and suffers from unmeasured cohort shifts between 2025.2 and 2026.1, low inter-rater reliability on key scorecard dimensions (especially Technical Complexity), and disconnected grains that prevent linking student survey responses or meeting transcripts directly to team repositories; (2) the course did not record what Agile practices teams actually followed, creating a gap between the title's framing ("Do We Still Need to Be Agile?") and the observational evidence; and (3) several presentation and construct details—such as the "inherited ordinal NLP score" in M1 and the duality of using GenAI as a coding tool versus building a GenAI product component—require clarification. **Preliminary Consensus Direction for the Area Chair:** **Borderline / Weak Accept (Lean Accept subject to Rebuttal and Shepherding).** Despite the small sample size and null correlational findings in RQ3, the paper's rich multi-method transparency, honest characterization of observational limits, and actionable pedagogical framework around Spec-Driven Development (SDD) make it a valuable and thought-provoking contribution to SEET, provided the authors can address the cohort sensitivity, clarify the M1/cutoff definitions in the rebuttal, and temper the Agile causal framing in the final camera-ready version.