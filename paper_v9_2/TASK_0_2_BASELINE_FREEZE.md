# Task 0.2 - Freeze V8 Baseline and Register Inventory

**Date:** 2026-09-24  
**Status:** ✓ COMPLETED  
**Gate Decision:** APPROVED for Task 1.1

---

## Objective

Make all V8→V9 differences traceable by establishing an immutable, hashed baseline of:
- Paper title and research questions (literal invariants)
- All paper sections
- All 9 metric (M1–M9) definitions, scripts, and data
- LaTeX source, figures, and supporting documentation

---

## Scope Completed

### 1. Extract and Register V8 Invariants

**Title (IMMUTABLE):**
```
Do We Still Need to Be Agile? What Two Cohorts of Student Projects 
Reveal About Planning Discipline in the GenAI-Era
```

**Research Questions (LITERAL, UNCHANGED):**

| ID | Type | Text |
|---|---|---|
| **RQ1** | Descriptive | How do student developers utilize Generative AI, and how does this adoption shape their longitudinal perceptions of software engineering roles and project expectations? |
| **RQ2** | Descriptive | How does the temporal density of repository activity contrast with the qualitative typification of human coordination friction across the project lifecycle? |
| **RQ3** | Primary | How does the quality of upfront architectural artifacts (evaluated at baseline T_1) associate with late-stage destructive rework and independent, blind-scored project outcomes? |

**Paper Sections:**
1. Introduction
2. Background and Related Work
3. Methodology
4. Results
5. Discussion
6. Threats to Validity
7. Conclusion

**Study Design Summary:**
- Cohorts: 2 (semesters 2025.2 and 2026.1)
- Teams: 14 total (9 in 2025.2, 5 in 2026.1)
- Students: ~70
- Temporal checkpoints: T_1 (Baseline), T_2 (Mid-Semester), T_3 (Final Integration)
- AI requirement: Advanced architectural patterns (RAG, LLM-driven pipelines)
- Problem constraint: Real-world community/educational/business problems (no toy apps)

### 2. Inventory All Metrics (M1–M9)

**Metric families registered with hashes:**

| M | Name | RQ | Script Hash | Data Hash | Status |
|---|---|---|---|---|---|
| M1 | AI Dependency Trajectory | RQ1 | e8da2d23... | 7349a5e8... | Frozen ✓ |
| M2 | Role Disruption Risk | RQ1 | c02b534f... | c438f919... | Frozen ✓ |
| M3 | Author Concentration Density | RQ2 | 986768d4... | 7d2f4926... | Frozen ✓ |
| M4 | Repository Activity Density | RQ2 | f3c371c5... | d3436daa... | Frozen ✓ |
| M5 | Coordination Friction Trajectory | RQ2 | 7e0d0122... | 102852cd... | Frozen ✓ |
| M6 | T1 Planning Quality | RQ3 | 1fa9026e... | 0c7fdbd4... | Frozen ✓ |
| M7 | Planning Omission Rate | RQ3 | 680afa00... | 676f2977... | Frozen ✓ |
| M8 | Rework Severity Ratio | RQ3 | b39747fb... | 683577d5... | Frozen ✓ |
| M9 | Planning vs. Rework Association | RQ3 | 9fe408bc... | 4 variants | Frozen ✓ |

**Total data artifacts:** 12 CSV files (M9 has 4 variants for sensitivity/contrast analyses)

### 3. Hash All V8 Files

**LaTeX sources:**
```
paper_v8/latex_code/main.tex
  SHA256: 68bb2bbe3bd74611d7a2517844e943ca615845af21b8ec55433cb47f1d09fa5f

paper_v8/latex_code/ (aggregate)
  SHA256: 5d0d619346b08d73c3312c6ff58e2c88ea07a1cba3ca41681d3b73e063b3942b
```

**Figures:**
```
paper_v8/figures/ (aggregate)
  SHA256: 97d9e511b88780bc119381043eed00f510c49c0e92d480023aa467cf64d3dcdf
```

**Supporting documentation:**
- `paper_v8/METRICS_PLAN.md` (M1–M9 operationalizations)
- `paper_v8/LLM_USAGE_PLAN.md` (LLM policy for data extraction)

### 4. Register metricas_v8-analysis Status

**Finding:** Directory `metricas_v8-analysis/` does **NOT** exist as of 2026-09-24.

**Status:** Planned in V9 Conversion Plan (Section 2: Target Structure) as a reorganization space for exploratory notebook-based analysis.

**Decision:** Will be created on demand if notebook validation is required before v9 script conversion. Not currently a gate blocker.

---

## Deliverables

### [1] V8 Baseline Manifest (JSON)
**Location:** `paper_v9/data/manifests/v8_baseline_manifest.json`

**Contents:**
- Baseline date and purpose
- V8 invariants: title, 3 RQs, 7 sections, study design parameters
- File hashes for LaTeX, figures, all M1–M9 scripts and data
- Supporting documentation inventory
- metricas_v8-analysis status
- V8 baseline lock policy (read-only invariants)
- V9 conversion readiness checklist

**Format:** Structured JSON, machine-readable, suitable for validation scripts

**Size:** ~12 KB

### [2] Task 0.2 Summary (this document)
**Location:** (current file)

**Purpose:** Narrative documentation of baseline freeze process, decisions, and gate readiness

---

## Validation

### Manifest Integrity Check

✓ All 9 metric scripts located and hashed  
✓ All 12 data CSV files located and hashed  
✓ LaTeX main.tex extracted: title, RQs verified  
✓ Paper sections registered (7 sections: Intro, Background, Methodology, Results, Discussion, Threats, Conclusion)  
✓ Aggregate hashes for directories calculated (latex_code, figures)  
✓ Supporting documentation inventoried  
✓ Study design metadata (2 cohorts, 14 teams, ~70 students) recorded  

### Baseline Lock Verification

✓ `paper_v8/` designated as read-only reference  
✓ Title and RQs marked as IMMUTABLE invariants  
✓ V9 directory structure prepared (`paper_v9/data/manifests/`)  
✓ No modifications made to v8 files during baseline freeze  

---

## Known Constraints and Decisions

| Constraint | Resolution |
|---|---|
| **metricas_v8-analysis does not exist** | Noted in manifest; to be created on demand if notebook validation required |
| **M9 has 4 data variants** | All variants hashed separately; sensitivity and contrast analyses preserved |
| **V8 scripts location** | Found in `paper_v8/scripts/metrics/`; not in separate notebook directory |
| **Supporting docs** | METRICS_PLAN.md and LLM_USAGE_PLAN.md inventoried; preserved as read-only |

---

## V8 Baseline Lock Policy

### Invariant Properties (MUST NOT CHANGE)
- Title: literal reproduction in v9
- RQ1, RQ2, RQ3: exact text preserved
- Paper sections: structure and content frozen
- M1–M9 definitions: operationalizations preserved exactly
- All paper_v8/ files: baseline references only

### Permitted Actions
- Read any file in paper_v8/
- Calculate hashes to verify integrity
- Copy templates to v9 for adaptation
- Reference in manifests and documentation

### Forbidden Actions
- Modify any file in paper_v8/
- Rename or move files in paper_v8/
- Delete or archive paper_v8/ during v9 work

---

## Gate Checklist

| Item | Status | Evidence |
|---|---|---|
| Title extracted | ✓ | v8_baseline_manifest.json line ~6 |
| RQs registered | ✓ | v8_baseline_manifest.json lines ~7-17 |
| All metrics inventoried | ✓ | M1–M9 script and data hashes present |
| LaTeX hashes frozen | ✓ | aggregate SHA256 for latex_code/ and figures/ |
| Supporting docs inventoried | ✓ | METRICS_PLAN.md and LLM_USAGE_PLAN.md recorded |
| metricas_v8-analysis status | ✓ | Noted as non-existent (not a blocker) |
| V8 directory protected | ✓ | Baseline lock policy documented |
| V9 directory ready | ✓ | paper_v9/data/manifests/ prepared |

---

## Next Steps

### Task 1.1: Create Common Contract and Utilities V9

When approved:
1. Create `paper_v9/scripts/common/paths.py` for directory resolution
2. Create `paper_v9/scripts/common/provenance.py` for hash/checksum utilities
3. Create `paper_v9/scripts/common/resume.py` for resume and caching logic
4. Create `paper_v9/scripts/common/statistics.py` for descriptive statistics
5. Create `paper_v9/scripts/common/artifact_policy.py` (adapter to central policy)
6. Create v9 orchestrator with stages: `metrics`, `results`, `figures`, `latex-check`, `all`
7. Create contract tests for keys, schemas, policy, manifests, checksums, idempotence

---

## Approval Record

**Task 0.2 Status:** ✓ APPROVED FOR NEXT GATE

- Baseline frozen: 2026-09-24
- Manifest generated: ✓
- Documentation complete: ✓
- V8 invariants recorded: ✓
- Ready for Task 1.1: ✓

**Gate Decision:** Proceed to Task 1.1 (Create Common Contract and Utilities V9)

---

**End of Task 0.2 Report**
