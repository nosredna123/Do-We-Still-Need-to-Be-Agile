# ICSE 2027 SEET Track — Peer Review Report

**Paper Title:** *Do We Still Need to Be Agile? What Student Projects Reveal About Coordination Skills in the GenAI Era*

**Paper Type:** Research Paper (10 pages + 2 pages references)

---

## Step 1: Dynamic Reviewer Persona Generation

Based on the paper's focus on empirical software engineering education, GenAI adoption in student projects, repository mining, and pedagogical implications, the following three complementary reviewer personas were generated:

| Reviewer | Persona | Assigned Specialty |
|----------|---------|-------------------|
| **Reviewer 1** | **Empirical SE Methodologist** | Mixed-methods research design, repository mining, statistical analysis, threats to validity, replication |
| **Reviewer 2** | **CS Education/Pedagogy Researcher** | SE education, project-based learning, curriculum design, student learning outcomes, competency development |
| **Reviewer 3** | **GenAI/SE Tooling & HCI Expert** | Generative AI in software engineering, developer-AI interaction, coordination tools, human factors in AI-assisted development |

---

## Step 2: Policy Compliance Check

### Double-Anonymous Review
✅ **Compliant.** Author identities are hidden ("Anonymous Authors"). Prior work is cited in the third person. The data availability section refers to an anonymized snapshot ("research-data-001 snapshot anonymously via the data explorer"). No obvious self-identifying information is present in the main text.

⚠️ **Minor concern:** The specific institutional context ("a large public university in South America") combined with exact course codes (2025.2 and 2026.1) and enrollment numbers (N=9 and N=5) could potentially deanonymize the authors to someone familiar with the region's course offerings. However, this is a common and generally acceptable level of contextual detail in SE education research.

### Open Science Policy
✅ **Compliant.** A dedicated "Data Availability" section (Section VIII) appears after the Conclusion. The authors state that reviewers can access an approved snapshot via a data explorer, and that a replication package includes path rules, lexicon/regular expressions, extraction prompts/schemas, surveys, rubrics, and evaluator scorecards. Transcripts are withheld for privacy with justification. Upon acceptance, artifacts will be archived on Zenodo with a DOI.

⚠️ **Minor concern:** The paper mentions "the public data explorer [27]" but reference [27] is not listed in the provided reference list (the references jump from [23] to the duplicate listing of [1]-[23]). The authors should ensure reference [27] is properly included in the camera-ready version.

---

## Step 3: Individual Reviewer Reports

---

### Reviewer 1: Empirical SE Methodologist

#### 1. Scoring Summary

| Criterion | Score |
|-----------|-------|
| **Overall Recommendation** | **Weak Reject** |
| **Reviewer Confidence** | **4** (High — empirical SE methods, repository mining, mixed-methods) |

#### 2. Core Evaluation Criteria

| Criterion | Score | Justification |
|-----------|-------|---------------|
| **Relevance** | **5** | Directly addresses SE education through empirical study of student projects, which is the core of the SEET track. |
| **Significance** | **3** | The research question is timely and important, but the study's small sample (N=14), observational design, and largely null/weak findings limit the strength of the contribution. |
| **Soundness** | **3** | The authors demonstrate commendable methodological awareness (grain preservation, proxy transparency, multiple robustness checks), but the study is fundamentally underpowered and cannot support the weight of the claims made. |
| **Verifiability** | **4** | The replication package described is extensive and well-structured. The artifact snapshot, path rules, lexicon, prompts, and scorecards are all specified. Withholding transcripts for privacy is justified. |
| **Presentation** | **4** | The paper is well-structured, the tables are informative, and the figures are clear. However, some passages are overly dense and repetitive (e.g., the extensive repetition of "grain preservation" and "exploratory diagnostics" caveats). |

#### 3. Qualitative Assessment

**Summary:**
This paper presents an observational, multi-method study of 14 team-semesters across two cohorts of a project-based SE course at a South American university. The authors combine multi-checkpoint surveys, Git repository mining, independent evaluator scorecards, and transcript-based lexical analysis to examine GenAI adoption patterns, temporal repository activity, and associations between upfront architectural artifacts and late-stage rework/outcomes. The central finding is that GenAI use is widespread and task-oriented, repository activity concentrates near final integration, and observable T1 architectural artifacts do not show a simple monotonic association with T3 rework or independent outcomes. The authors propose Spec-Driven Development (SDD) as a testable hypothesis for addressing coordination gaps.

**Strengths:**

- **Methodological transparency and grain preservation.** The authors are to be commended for their explicit attention to analytical grains, denominators, and the incompatibility of pooling data across different observation units (student-level surveys vs. team-semester repository metrics vs. global transcript corpus). This is a level of methodological care that is often absent in SE education research.
- **Multi-method triangulation with robustness checks.** The combination of surveys, repository mining, evaluator scorecards, and transcripts is ambitious and appropriate for the research questions. The inclusion of non-overlapping phase bins, final-seven-day concentration contrasts, operational-regularity proxies, technical-complexity stratifications, and leave-one-out sensitivity analyses demonstrates a genuine effort to stress-test the findings.
- **Explicit treatment of proxy limitations.** The authors repeatedly and explicitly acknowledge that their measures are proxies (e.g., M8 clean-path rework as file-provenance proxy, M5 lexical markers as candidate signals, M6a as structural observation not quality measure). This intellectual honesty is valuable.

**Weaknesses:**

- **Fundamental underpowering.** The study reports N=14 team-semesters with no non-AI control group. The primary RQ3 associations (Table III) are all non-significant (p-values ranging from 0.296 to 0.931). The largest reported Spearman ρ is 0.301, and most are below 0.25. The authors' own leave-one-out diagnostics show that these associations are sensitive to individual cases. The study cannot meaningfully distinguish between "no association exists" and "insufficient power to detect an association." The conclusion that "observable upfront architectural artifacts do not translate into a simple monotonic pattern of rework or project outcomes" is technically true but largely uninformative — it is what one would expect from an underpowered observational study regardless of the underlying reality.
- **Confounding by process heterogeneity.** The authors acknowledge that "teams freely chose Scrum, Kanban, other Agile variants, or unguided approaches" and that "course records did not formally record teams' process selections or adherence to ceremonies." This is a critical omitted variable. Without knowing which teams were actually practicing Agile (or any structured process), the paper's framing around "Do we still need to be Agile?" is not empirically grounded. The repository activity patterns could reflect process choice, team composition, project difficulty, or other factors entirely.
- **Temporal misalignment between survey and evaluator checkpoints.** The authors note that "survey and evaluator dates do not coincide" and that survey waves fall in weeks 1, 9, and 13 (2025.2) while evaluator scorecards fall in weeks 7-8, 11-12, and 14-15. This misalignment complicates any attempt to link survey perceptions with repository or evaluator outcomes. The authors handle this by preserving grain separation, but it raises questions about whether the "checkpoint" framing is more nominal than substantive.
- **Overclaiming through framing.** The title asks "Do We Still Need to Be Agile?" but the study does not measure Agile adherence, Agile practices, or Agile outcomes. The paper's conclusion ("Yes, but Generative AI changes what effective agility requires") is a reasonable position, but it is not empirically derived from the data presented. The data show that repository activity concentrates near deadlines and that architectural artifacts are weakly associated with outcomes — neither of which directly addresses the value of Agile practices.

**Detailed Comments for Authors:**

1. **Statistical power and interpretation of null results.** The paper reports many non-significant Spearman correlations and interprets them as evidence of "weak, non-monotonic associations." While this is technically accurate, the authors should more explicitly discuss statistical power. With N=14 and an expected effect size of ρ=0.3, the power to detect significance at α=0.05 is approximately 0.18. The study is therefore severely underpowered for its primary RQ3 analyses. The authors should consider reporting effect sizes with confidence intervals (e.g., bootstrap CIs) rather than relying on p-values, and should temper their conclusions accordingly. The current framing ("these data do not test documentation requirements") is appropriately cautious but sits uneasily with the paper's broader narrative about the need for architectural planning.

2. **Process heterogeneity as a first-order confound.** The paper acknowledges that teams chose their own process models and that these choices were not recorded. This is not a minor limitation — it is a fundamental threat to the study's ability to answer its own research questions. If some teams were practicing disciplined Scrum with regular sprints and others were working ad hoc, the repository activity patterns (late concentration, distributed activity, etc.) would be driven by process choice, not by GenAI adoption or architectural planning. The authors should either (a) attempt to retrospectively classify teams' process approaches from repository evidence (e.g., branch patterns, commit cadence, PR merge patterns), or (b) more strongly caveat the findings as descriptive of "whatever processes teams happened to use" rather than of Agile practice per se.

3. **The SDD proposition is underdeveloped and somewhat unmoored.** The paper proposes Spec-Driven Development as a "plausible, testable response" to the coordination gap. However, the connection between the empirical findings and SDD is tenuous. The findings show that (a) students use GenAI for tasks, (b) repository activity concentrates late, and (c) T1 artifact scope is weakly associated with outcomes. None of these findings directly implicate the absence of specifications as the cause of coordination problems. The SDD proposal reads as a plausible hypothesis, but the paper would be stronger if it either (a) provided more direct evidence of specification-related coordination failures (e.g., from the transcript analysis), or (b) presented SDD as one of several possible responses rather than as the natural implication of the findings.

4. **The M5 transcript analysis is disconnected from the rest of the study.** The coordination-language evidence (M5) is presented as a global corpus analysis of 2025.2 transcripts with no team identifiers. This means it cannot be linked to any of the repository, survey, or evaluator data. The finding that "candidate coordination-language density increases across checkpoints" is interesting but does not directly support the paper's broader claims about coordination gaps. The authors should either (a) more explicitly justify why this global-level analysis is informative despite its inability to link to team-level outcomes, or (b) acknowledge that M5 is largely illustrative rather than analytically integrated.

5. **Reference [27] is missing.** The paper repeatedly cites "[27]" as the public data explorer, but this reference is not included in the reference list (which jumps from [23] to a duplicate of [1]-[23]). This should be corrected.

**Questions for the Rebuttal:**

1. **Statistical power and effect sizes:** Given that all RQ3 associations are non-significant, what is the minimum detectable effect size at 80% power for N=14? Would the authors consider reporting bootstrap confidence intervals for the Spearman correlations to better characterize uncertainty?

2. **Process heterogeneity:** Can the authors provide any retrospective classification of teams' process approaches from repository evidence (e.g., branch/merge patterns, commit cadence regularity)? If not, how do the authors respond to the concern that process heterogeneity is a first-order confound that undermines the study's ability to speak to "Agile" specifically?

3. **SDD connection:** The paper proposes SDD as a response to the coordination gap, but the empirical findings do not directly test any SDD-related mechanism. What specific evidence from this study would lead a reader to favor SDD over, say, improved onboarding, better tooling for dependency visualization, or more structured code review practices?

---

### Reviewer 2: CS Education/Pedagogy Researcher

#### 1. Scoring Summary

| Criterion | Score |
|-----------|-------|
| **Overall Recommendation** | **Borderline** |
| **Reviewer Confidence** | **4** (High — SE education, project-based learning, curriculum design) |

#### 2. Core Evaluation Criteria

| Criterion | Score | Justification |
|-----------|-------|---------------|
| **Relevance** | **5** | Highly relevant to SEET. The paper addresses a core concern of SE education: how to prepare students for professional practice in an AI-augmented world. |
| **Significance** | **4** | The paper makes a valuable contribution by documenting actual student GenAI adoption patterns and coordination challenges in a realistic project course. The pedagogical implications, while tentative, are important for educators. |
| **Soundness** | **3** | The educational research design is reasonable but limited. The lack of direct learning-outcome measures (e.g., grades, competency assessments, student reflections) is a significant gap for an education-focused venue. |
| **Verifiability** | **3** | The artifact package is strong for the repository and evaluator data, but the survey instruments and transcript analysis are less well-documented in the paper itself. The survey response rates (46/41/40 and 22/20/18) raise questions about representativeness and attrition. |
| **Presentation** | **4** | The paper is generally well-written and organized, though some sections are dense and could benefit from clearer signposting for education-focused readers. |

#### 3. Qualitative Assessment

**Summary:**
This paper investigates how student teams in a project-based SE course use GenAI and how their coordination patterns manifest in repository activity and evaluator outcomes. The authors find that students use GenAI broadly for task-oriented work, that repository activity concentrates near final integration, and that observable upfront architectural artifacts do not show a simple relationship with late-stage rework or project outcomes. The paper discusses Spec-Driven Development as a potential pedagogical response. From an education perspective, the paper provides valuable descriptive evidence about the current state of student GenAI practice and raises important questions about how to structure project courses to develop coordination competencies.

**Strengths:**

- **Authentic educational context.** The study is situated in a real project-based course with client-facing projects, integrated GenAI requirements, and independent evaluator scorecards. This ecological validity is a significant strength — the findings describe what actually happens in a realistic educational setting, not a contrived experiment.
- **Descriptive value of GenAI adoption patterns.** The finding that GenAI use is "widespread and task-oriented" with tasks concentrated in "research/questions, code generation, debugging, and documentation" provides useful baseline data for educators designing AI-integrated courses. The observation that "prior AI-project experience increases across checkpoints" is also pedagogically relevant.
- **Pedagogical implications of the late-concentration finding.** The finding that repository activity and clean source/test change concentrate near final integration — despite widespread GenAI use — challenges the naive assumption that AI tools will smooth out project timelines. This has direct implications for how educators structure checkpoints, assess process, and scaffold coordination.
- **The SDD pedagogical operationalization.** The four concrete practices proposed in Section V.C — (1) machine-checkable interface-contract tests rather than document-volume grading, (2) tasks and PRs linked to specification clauses, (3) checkpoint defenses of cross-component boundaries, and (4) convergence checks with acceptance tests — are pedagogically thoughtful and actionable. Even if SDD is not empirically validated here, these suggestions are valuable for educators.

**Weaknesses:**

- **No direct learning-outcome measures.** The study measures project outcomes via evaluator scorecards (engagement, progress, scope/applicability, technical complexity) but does not measure student learning. There are no data on what students learned about coordination, architecture, or Agile practices. For an education-focused venue, this is a significant gap. The paper would be much stronger if it included, for example, pre/post assessments of coordination competencies, student reflections on their coordination challenges, or comparisons with learning objectives.
- **Survey methodology is underspecified.** The paper mentions "multi-checkpoint surveys captured demographics, experience, GenAI adoption, perceived role disruption, and project expectations" but provides almost no detail on the survey instruments themselves. What were the specific questions? What was the response rate? How were non-responses handled? The respondent counts (46, 41, 40 in 2025.2 and 22, 20, 18 in 2026.1) suggest significant attrition, which raises questions about whether the later-checkpoint data are representative. The paper should either include the survey instruments as an appendix or provide much more detail in the main text.
- **The "perceived role disruption" analysis is thin.** The M2 results are described in a single paragraph: "Frontend tends to receive higher agreement scores, whereas project-management roles are not consistently high across checkpoints. Privacy-preserving paired summaries also move in mixed directions..." This is too vague to be informative. What are the actual Likert distributions? What are the effect sizes for the paired shifts? For an education audience, understanding how students perceive the impact of GenAI on different SE roles is potentially very valuable, but the current analysis does not deliver actionable insights.
- **The paper does not engage with the SE education literature on coordination and teamwork.** There is a substantial body of work on teaching teamwork, coordination, and communication in SE education (e.g., work on agile education, team-based learning, peer evaluation, and communication skills). The paper cites Bruegge et al. [16] on project courses with industrial clients but does not engage with the broader SE education literature on how to teach coordination skills. This is a missed opportunity to situate the findings in the existing pedagogical knowledge base.
- **The "Do We Still Need to Be Agile?" framing is misleading for an education audience.** The paper's conclusion ("Yes, but...") is reasonable, but the study does not actually compare Agile vs. non-Agile approaches, nor does it measure Agile practice adherence. For educators, the more relevant question is: "What kinds of course structures and scaffolding help students develop coordination skills in GenAI-assisted projects?" The current framing may alienate readers who are looking for practical pedagogical guidance.

**Detailed Comments for Authors:**

1. **Learning outcomes and assessment.** The paper would be significantly strengthened by including some measure of student learning. Even a simple pre/post self-assessment of coordination competencies, or a qualitative analysis of student reflections on their coordination challenges, would help connect the descriptive findings to educational outcomes. As it stands, the paper describes what students did but not what they learned.

2. **Survey instrument transparency.** The survey methodology needs much more detail. Please provide the full survey instruments (or at least the key items) in an appendix or supplementary material. Report response rates by checkpoint and cohort, and discuss whether non-response bias is a concern. The current description ("multi-checkpoint surveys captured demographics, experience, GenAI adoption, perceived role disruption, and project expectations") is too vague to allow replication or critical evaluation.

3. **Role disruption analysis.** The M2 analysis should be substantially expanded. Provide the actual Likert distributions for each role and checkpoint. Report effect sizes for paired shifts. Discuss the practical implications: what does it mean for SE education if students perceive frontend roles as more disrupted by GenAI? Should curricula change in response?

4. **Engagement with SE education literature.** The paper should engage more deeply with the SE education literature on teamwork, coordination, and project-based learning. How do the findings relate to what we already know about student team coordination? What does the GenAI context change, and what remains the same?

5. **Pedagogical framing.** Consider reframing the paper's contribution for an education audience. The current framing around Agile vs. not-Agile is less relevant to educators than questions about how to structure courses, scaffold coordination, and assess process skills in GenAI-assisted projects. The SDD practices proposed in Section V.C are a good start, but they could be developed into a more comprehensive pedagogical framework.

**Questions for the Rebuttal:**

1. **Learning outcomes:** Can the authors provide any data (even qualitative) on what students learned about coordination or architecture from these projects? If not, how do the authors justify the paper's relevance to an education-focused venue like SEET?

2. **Survey attrition:** The survey respondent counts drop from 46 to 40 in 2025.2 and from 22 to 18 in 2026.1. What explains this attrition, and how might it bias the longitudinal findings? Were non-respondents different from respondents in observable ways?

3. **Role disruption:** Could the authors provide the actual Likert distributions for the role disruption items? The current summary ("Frontend tends to receive higher agreement scores") is too vague to be useful for educators.

---

### Reviewer 3: GenAI/SE Tooling & HCI Expert

#### 1. Scoring Summary

| Criterion | Score |
|-----------|-------|
| **Overall Recommendation** | **Weak Accept** |
| **Reviewer Confidence** | **3** (Medium-High — GenAI in SE, developer-AI interaction, but less familiar with the specific educational context) |

#### 2. Core Evaluation Criteria

| Criterion | Score | Justification |
|-----------|-------|---------------|
| **Relevance** | **5** | Highly relevant to SEET and to the broader ICSE community interested in GenAI's impact on SE practice and education. |
| **Significance** | **3** | The paper provides useful descriptive data on GenAI adoption patterns, but the analytical contribution is limited by the lack of AI-use telemetry and the observational design. |
| **Soundness** | **3** | The authors are careful and transparent, but the study cannot observe the actual AI-use behaviors that are central to its research questions. Self-reported AI use is a weak proxy for actual behavior. |
| **Verifiability** | **4** | The artifact package is strong. The M6b extraction prompt/schema and the M5 lexicon are particularly valuable for replication. |
| **Presentation** | **3** | The paper is dense and sometimes hard to follow. The figures are informative but could be better explained. Some sections (especially the methodology) read as defensive rather than explanatory. |

#### 3. Qualitative Assessment

**Summary:**
This paper examines GenAI adoption and coordination patterns in student software engineering projects. The authors find widespread, task-oriented GenAI use, late-stage repository concentration, and weak associations between upfront architectural artifacts and project outcomes. The paper proposes Spec-Driven Development as a response to coordination gaps. From a GenAI tooling and HCI perspective, the paper provides useful descriptive data on how students actually use GenAI tools (or at least how they report using them), but the lack of behavioral telemetry and the coarse granularity of the AI-use measures limit the depth of the insights.

**Strengths:**

- **Realistic characterization of GenAI use.** The finding that GenAI use is "widespread and task-oriented" with tasks concentrated in "research/questions, code generation, debugging, and documentation" aligns with what we know from professional developer studies. The observation that "tool naming is dominated by widely available assistants such as ChatGPT and Gemini" is also consistent with broader trends.
- **The late-concentration finding is important and counterintuitive.** The assumption that GenAI will "smooth out" development timelines is widespread. The finding that repository activity still concentrates near final integration — despite widespread GenAI use — is an important empirical corrective. The internal contrasts (cases with score gains, cases without score gains, cases with distributed activity) add nuance.
- **Methodological transparency around AI-use measurement.** The authors are explicit that "Git captures only repository-visible evidence... rather than AI-use telemetry such as prompt logs, API calls, or IDE acceptance events." This is an honest acknowledgment of a fundamental limitation, and it appropriately frames the self-reported AI-use data as a proxy rather than a direct measure.
- **The SDD proposal is well-matched to the coordination problem.** The idea of carrying a specification through planning, task decomposition, implementation, and convergence checks is a plausible response to the coordination gaps the paper identifies. The four concrete practices proposed in Section V.C are actionable and testable.

**Weaknesses:**

- **No behavioral AI-use telemetry.** The paper's central claims about GenAI adoption rest entirely on self-reported survey data. There is no data on what prompts students actually used, how they interacted with AI tools, whether they accepted or rejected AI-generated code, or how AI use varied across tasks and over time. This is a fundamental limitation for a paper that aims to understand "GenAI adoption." The authors acknowledge this ("Neither metric is behavioral AI-use telemetry") but do not adequately discuss the implications: self-reported AI use is known to be biased (e.g., social desirability, recall bias), and the coarse task categories (research/questions, code generation, debugging, documentation) obscure important variation in how AI is used.
- **The M1 perception families are underspecified and the analysis is thin.** The paper mentions "six perception families" (AI benefit, autonomy/tool balance, career expectation, five-year career impact, project challenges, project feeling) but provides almost no detail on what these families contain, how they were derived, or what the individual items are. The figure (Fig. 1) shows means but no error bars or significance tests for the longitudinal changes. The statement that "the six perception families do not move as a single trajectory" is interesting but underexplored: why do some families increase while others decrease? What does this mean for our understanding of student attitudes toward GenAI?
- **The M5 coordination-language analysis is disconnected and lexically naive.** The M5 analysis counts matches to a Portuguese regex dictionary (alignment, handoff, integration, blockers, rework) in a global transcript corpus. This is a purely lexical approach with no semantic analysis. The finding that "candidate coordination-language density increases across checkpoints" could simply reflect the fact that later-stage presentations involve more discussion of integration and blockers, regardless of whether actual coordination friction increased. The authors acknowledge that these are "candidate textual signals, not diagnoses of coordination failure," but the analysis remains shallow. A more compelling approach would involve qualitative coding of the transcripts to identify specific coordination episodes and their resolution.
- **The M6b planning content extraction is underexplained.** The paper mentions that "a fixed JSON-schema prompt uses gpt-4o-mini at temperature 0 to classify T1 commit subjects for goals, architecture/design, task decomposition, and risk/dependency, requiring verbatim evidence quotes." This is a reasonable approach, but the paper provides almost no detail on the results: what did the extracted planning content actually look like? What were the most common categories? How did the extracted content relate to the repository-visible artifacts? The M6b analysis is presented as a table (Table III) but the underlying data are not described.

**Detailed Comments for Authors:**

1. **Self-reported AI use is a weak proxy for actual behavior.** The paper should more critically discuss the limitations of self-reported AI use. Consider citing the literature on self-report bias in technology use (e.g., overestimation of frequency, social desirability, recall limitations). If possible, consider triangulating self-reported AI use with other data sources — for example, commit messages that mention AI tools, or repository evidence of AI-generated code (e.g., characteristic patterns, comments like "// Generated by ChatGPT"). Even if imperfect, such triangulation would strengthen the claims.

2. **M1 perception families need more detail.** The six perception families are central to RQ1, but the paper provides almost no information about what they contain or how they were derived. Please provide the full item wording and the derivation procedure (e.g., factor analysis, theoretical grouping) in an appendix or supplementary material. Also, the longitudinal analysis would benefit from effect sizes and confidence intervals, not just visual inspection of Figure 1.

3. **M5 analysis should move beyond lexical counting.** The current lexical approach is a useful first step, but it does not provide insight into the nature of coordination friction. Consider adding a qualitative component: for example, code a sample of transcript segments for coordination episodes (e.g., a blocker being identified and resolved, an integration conflict being discussed, a handoff being negotiated) and analyze how these episodes unfold. This would provide much richer evidence about coordination dynamics than simple marker counts.

4. **M6b results should be described in more detail.** What did the planning content extraction actually reveal? What were the most common planning elements? Were there notable differences between teams with high vs. low T1 artifact scope? The current presentation (a brief mention in the text and a row in Table III) does not do justice to the analysis.

5. **The SDD connection needs more development.** The paper proposes SDD as a response to the coordination gap, but the empirical findings do not directly test any SDD-related mechanism. The authors should more explicitly acknowledge that SDD is one of several possible responses and discuss alternative approaches (e.g., improved tooling for dependency visualization, AI-assisted code review, structured onboarding). The four pedagogical practices in Section V.C are a good start but could be developed into a more comprehensive framework.

**Questions for the Rebuttal:**

1. **Triangulation of AI use:** Can the authors provide any evidence that self-reported AI use correlates with observable repository behaviors (e.g., commit messages mentioning AI tools, code comments indicating AI generation, or characteristic code patterns)? If not, how do the authors respond to the concern that self-report bias may undermine the RQ1 findings?

2. **M5 qualitative depth:** Can the authors provide any qualitative analysis of the transcript segments to complement the lexical marker counts? For example, are there specific episodes where coordination friction is visible and consequential?

3. **M6b planning content:** Could the authors provide a more detailed description of the M6b results? What were the most common planning elements, and how did they relate to the repository-visible artifacts?

---

## Step 4: Meta-Review / Consensus Summary

The three reviewers agree that the paper addresses a timely and relevant topic for the SEET track and demonstrates commendable methodological transparency. The multi-method design, grain-preservation principles, and extensive robustness checks are strengths that all reviewers acknowledge. The replication package and data availability are also viewed positively.

However, the reviewers converge on several significant concerns:

1. **Underpowering and weak findings.** Reviewer 1 (Empirical SE) is most concerned about the statistical power of the RQ3 analyses and the interpretation of null results. Reviewer 3 (GenAI/HCI) shares this concern but frames it more broadly as a limitation of the observational design. Reviewer 2 (Education) is less focused on statistical power but notes that the lack of direct learning-outcome measures weakens the paper's educational contribution.

2. **Disconnect between empirical findings and the SDD proposal.** All three reviewers note that the SDD proposition is underdeveloped and only tenuously connected to the empirical findings. Reviewer 1 calls it "unmoored," Reviewer 2 sees it as a missed opportunity for pedagogical development, and Reviewer 3 notes that alternative responses are not adequately considered.

3. **Measurement limitations.** Reviewer 3 is most critical of the self-reported AI-use data and the lexical naivety of the M5 analysis. Reviewer 2 is critical of the survey methodology (underspecified instruments, attrition, thin role-disruption analysis). Reviewer 1 is critical of the process heterogeneity confound and the temporal misalignment between survey and evaluator checkpoints.

4. **Framing issues.** The title's question ("Do We Still Need to Be Agile?") is viewed as somewhat misleading by all three reviewers, though for different reasons. Reviewer 1 notes that Agile practice adherence was not measured; Reviewer 2 argues that the question is less relevant for educators than questions about course structure and scaffolding; Reviewer 3 suggests that the paper does not directly test any Agile-related mechanisms.

**Preliminary consensus direction:** The paper is borderline. Reviewer 1 recommends weak reject, Reviewer 2 recommends borderline, and Reviewer 3 recommends weak accept. The primary reasons for the borderline assessment are: (a) the study is fundamentally underpowered for its primary RQ3 analyses, (b) the empirical findings do not strongly support the paper's broader claims about Agile and coordination, and (c) the SDD proposition is underdeveloped. However, the paper's descriptive contributions (GenAI adoption patterns, late-concentration finding, methodological transparency) are valuable, and the replication package is strong. If the authors can address the framing issues, strengthen the connection between findings and implications, and more thoroughly acknowledge the limitations of their measures, the paper could be a reasonable contribution to the SEET track. The Area Chair should consider inviting a revision that addresses these concerns, with particular attention to: (1) reframing the paper's contribution for an education audience, (2) more explicitly acknowledging the limitations of self-reported AI use and the underpowered RQ3 analyses, and (3) developing the SDD proposition into a more concrete and actionable framework for educators.

**Preliminary Recommendation:** **Borderline** (leaning weak reject due to underpowering and framing issues, but with potential for revision).

---

*End of Review Report*