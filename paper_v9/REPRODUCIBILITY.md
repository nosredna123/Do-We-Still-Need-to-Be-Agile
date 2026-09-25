# Paper V9 LaTeX Environment - Reproducibility Report

**Task:** 0.1 - Configure and Validate Local LaTeX Environment  
**Date:** 2026-09-24  
**Status:** ✓ COMPLETED

## Executive Summary

The LaTeX environment for Paper V9 has been successfully configured and validated. The PDF generation pipeline is functional and reproducible. All required components (pdfLaTeX, BibTeX, IEEEtran class, and supplementary packages) are installed and tested.

---

## 1. Environment Detection Results

### 1.1 System Information

| Component | Details |
|-----------|---------|
| **OS** | Debian/Linux |
| **Distribution** | TeX Live 2023 (Debian repository) |
| **Detected Date** | 2026-09-24 |

### 1.2 Core LaTeX Tools

| Tool | Status | Version | Location |
|------|--------|---------|----------|
| **pdfTeX** | ✓ Installed | 3.141592653-2.6-1.40.25 | `/usr/bin/pdflatex` |
| **BibTeX** | ✓ Installed | 0.99d (TeX Live 2023) | `/usr/bin/bibtex` |
| **TeX Live Manager** | ✓ Installed | 69653 (2024-01-31) | `/usr/bin/tlmgr` |
| **latexmk** | ✗ Not installed | — | (alternative: sequential compilation) |

### 1.3 Required Packages

| Package | Status | Location |
|---------|--------|----------|
| **IEEEtran** | ✓ Installed | `/usr/share/texlive/texmf-dist/tex/latex/ieeetran/` |
| **cite** | ✓ Installed | TeX Live core |
| **amsmath / amssymb** | ✓ Installed | TeX Live core |
| **graphicx** | ✓ Installed | TeX Live core |
| **booktabs** | ✓ Installed | TeX Live core |
| **tabularx** | ✓ Installed | TeX Live core |

### 1.4 Debian/APT Packages

The following packages are installed via `apt`:

```
texlive-base                  2023.20240207-1
texlive-binaries             2023.20230311.66589-9build3
texlive-fonts-recommended    2023.20240207-1
texlive-latex-base           2023.20240207-1
texlive-latex-extra          2023.20240207-1
texlive-latex-recommended    2023.20240207-1
texlive-pictures             2023.20240207-1
texlive-plain-generic        2023.20240207-1
texlive-publishers           2023.20240207-1    (← provides IEEEtran)
texlive-xetex                2023.20240207-1
```

---

## 2. Installation Summary

### 2.1 Initial Detection (without IEEEtran)

**Date:** 2026-09-24  
**Finding:** IEEEtran.cls was not available in the initial installation.

**Command executed:**
```bash
kpsewhich IEEEtran.cls
# Result: Not found
```

### 2.2 Installation of Missing Component

**Command executed:**
```bash
sudo apt-get install texlive-publishers
```

**Result:** ✓ Successfully installed.

**Verification:**
```bash
kpsewhich IEEEtran.cls
# Result: /usr/share/texlive/texmf-dist/tex/latex/ieeetran/IEEEtran.cls
```

---

## 3. Validation - Test Document Compilation

### 3.1 Test Document Setup

**Location:** `/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/paper_v9/latex/test_document.tex`

**Purpose:** Validate the LaTeX compilation pipeline with:
- IEEEtran document class
- Bibliography support (cite package)
- Tables (booktabs, tabularx)
- Figures (graphicx)
- Mathematical notation (amsmath, amssymb)

### 3.2 Compilation Sequence

#### Step 1: Initial pdflatex run

```bash
pdflatex -interaction=nonstopmode \
  -output-directory=build test_document.tex
```

**Result:** ✓ PDF generated (61666 bytes)  
**Warnings:** Expected undefined references (first pass)

#### Step 2: BibTeX processing

```bash
cd build && bibtex test_document
```

**Result:** ✓ Bibliography processed  
**Note:** Document uses embedded thebibliography, so bibtex messages are informational

#### Step 3: Final pdflatex run

```bash
pdflatex -interaction=nonstopmode \
  -output-directory=build test_document.tex
```

**Result:** ✓ PDF finalized (60466 bytes)  
**Status:** All cross-references resolved

### 3.3 Final Validation

```bash
file latex/build/test_document.pdf
# PDF document, version 1.5
```

**PDF Quality Checks:**
- ✓ File size: 60 KB (reasonable for 1-page conference paper)
- ✓ PDF version: 1.5 (ISO compliant, widely compatible)
- ✓ Fonts embedded: Type 1 fonts (PostScript format)
- ✓ Figure support: Verified with graphicx package
- ✓ Table support: Verified with booktabs and tabularx
- ✓ Mathematical notation: Verified with amsmath/amssymb
- ✓ Bibliography: Thebibliography environment functional
- ✓ Citations: cite package operational

---

## 4. Production Compilation Commands

### 4.1 Standard Single-Pass Compilation (for fast drafts)

```bash
cd paper_v9/latex
pdflatex -interaction=nonstopmode \
  -output-directory=build \
  main.tex
```

### 4.2 Full Reproducible Compilation (with bibliography)

```bash
cd paper_v9/latex
pdflatex -interaction=nonstopmode -output-directory=build main.tex
bibtex build/main
pdflatex -interaction=nonstopmode -output-directory=build main.tex
pdflatex -interaction=nonstopmode -output-directory=build main.tex
```

**Why three pdflatex passes?**
- Pass 1: Generate `.aux` file for bibliography
- Pass 2 (bibtex): Process citations from `.aux`
- Pass 3: Resolve bibliography references
- Pass 4 (if needed): Resolve remaining cross-references

### 4.3 Alternative: Sequential Bash Script

```bash
#!/bin/bash
cd paper_v9/latex
pdflatex -interaction=nonstopmode -output-directory=build main.tex && \
bibtex build/main && \
pdflatex -interaction=nonstopmode -output-directory=build main.tex && \
pdflatex -interaction=nonstopmode -output-directory=build main.tex && \
echo "✓ PDF compiled successfully: build/main.pdf"
```

---

## 5. Known Limitations and Constraints

| Limitation | Impact | Workaround |
|-----------|--------|-----------|
| **latexmk not installed** | Slightly less convenient automation | Use sequential shell script (Sec 4.3) |
| **User-mode tlmgr disabled** | Cannot install new packages via tlmgr user mode | Use `apt` or `sudo apt` for system packages |
| **Debian TeX Live 2023** | May not have extremely latest packages | Adequate for IEEE conference submission |
| **No Ghostscript** | EPS figures not supported; use PDF/PNG | All figures should be PDF or PNG |
| **No xdvipdfmx** | XeTeX output PDF generation may be limited | Use pdflatex (default, already tested) |

---

## 6. Directory Structure

```
paper_v9/
├── latex/
│   ├── test_document.tex         (validation test file)
│   ├── build/
│   │   ├── test_document.pdf     ✓ Successfully generated
│   │   ├── test_document.log     (compilation log)
│   │   ├── test_document.aux     (auxiliary file)
│   │   └── test_document.out     (hyperref bookmarks)
│   ├── main.tex                  (to be created in Task 6.1)
│   ├── references.bib            (to be created in Task 6.1)
│   ├── sections/
│   │   ├── methodology.tex
│   │   ├── results.tex
│   │   ├── discussion.tex
│   │   ├── threats_to_validity.tex
│   │   ├── conclusion.tex
│   │   ├── abstract.tex
│   │   ├── introduction.tex
│   │   └── background_related_work.tex
│   ├── tables/
│   └── figures/
└── REPRODUCIBILITY.md            (this file)
```

---

## 7. Robustness Artifact Pipeline

Run the following commands from the repository root. They regenerate the
robustness artifacts used in the Paper V9 Results, Discussion, Threats to
Validity, and reviewer-response analyses.

### 7.1 Common execution pattern

```bash
/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/.venv/bin/python \
  paper_v9/scripts/results/<script_name>.py
```

Focused syntax and contract checks should use the same interpreter:

```bash
/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/.venv/bin/python \
  -m py_compile paper_v9/scripts/results/<script_name>.py paper_v9/tests/<test_name>.py

/home/amg/projects/uece/Do-We-Still-Need-to-Be-Agile/.venv/bin/python \
  -m pytest paper_v9/tests/<test_name>.py
```

### 7.2 Script inventory, inputs, outputs, and focused tests

| Purpose | Command | Key inputs | Key outputs | Focused validation |
|---------|---------|------------|-------------|--------------------|
| Score trajectory base and final-seven-day concentration inputs | `.venv/bin/python paper_v9/scripts/results/generate_score_trajectory_base.py` | `paper_v9/data/metrics/m3_*`, `m4_*`, `m6*`, evaluator-score inputs | `paper_v9/figures/rq2_score_trajectory_base_*`, base metadata/data CSVs | `.venv/bin/python -m pytest paper_v9/tests/test_score_trajectory_base.py` |
| Score delta versus final-seven-day concentration | `.venv/bin/python paper_v9/scripts/results/generate_score_trajectory_concentration.py` | `paper_v9/figures/rq2_score_trajectory_base_data.csv` | `rq2_score_delta_vs_final7_commit_concentration.{pdf,svg,png}`, `rq2_score_delta_vs_final7_clean_churn_concentration.{pdf,svg,png}`, quadrant CSV/metadata | `.venv/bin/python -m pytest paper_v9/tests/test_score_trajectory_concentration.py` |
| Planning scope versus final-seven-day concentration quadrants | `.venv/bin/python paper_v9/scripts/results/generate_planning_concentration_quadrants.py` | score-trajectory base data, `paper_v9/data/metrics/m8_*` rework metrics | `rq2_planning_vs_final7_commit_concentration.{pdf,svg,png}`, `rq2_planning_vs_final7_clean_churn_concentration.{pdf,svg,png}`, quadrant summary/metadata | `.venv/bin/python -m pytest paper_v9/tests/test_planning_concentration_quadrants.py` |
| Operational regularity views | `.venv/bin/python paper_v9/scripts/results/generate_operational_regularity.py` | Git team-cut metrics, score trajectory base data | `rq2_regularity_vs_score_delta.{pdf,svg,png}`, `rq2_regularity_vs_final_concentration.{pdf,svg,png}`, `rq2_regularity_profile_heatmap.{pdf,svg,png}`, regularity CSV/metadata | `.venv/bin/python -m pytest paper_v9/tests/test_operational_regularity.py` |
| RQ3 influence map | `.venv/bin/python paper_v9/scripts/results/generate_influence_maps.py` | registered RQ2/RQ3 relationship artifacts, leave-one-out diagnostics | `rq3_influence_map.{pdf,svg,png}`, `rq3_influence_map_data.csv`, `rq3_influence_heatmap_matrix.csv`, metadata | Validate with `py_compile`; rerun after upstream metric tests such as `test_m9.py` when M9 inputs change. |
| Technical-complexity confounding profiles | `.venv/bin/python paper_v9/scripts/results/generate_complexity_confounding_profiles.py` | M9 planning/rework artifacts, M8 rework metrics, final concentration data | `rq3_technical_complexity_vs_rework.{pdf,svg,png}`, `rq3_complexity_vs_final_concentration.{pdf,svg,png}`, `rq3_planning_rework_complexity_overlay.{pdf,svg,png}`, complexity summary/metadata | Validate with `py_compile`; rerun `paper_v9/tests/test_m9.py` before generation if M9 source metrics changed. |
| Non-overlapping phase activity | `.venv/bin/python paper_v9/scripts/results/generate_nonoverlapping_phase_activity.py` | project phase boundaries, Git activity windows, score trajectory base data | `rq2_phase_commit_share_by_score_trajectory.{pdf,svg,png}`, `rq2_phase_clean_churn_share_by_score_trajectory.{pdf,svg,png}`, phase-share CSV/metadata | Validate with `py_compile`; inspect generated metadata and rerun upstream M3/M4 tests when temporal activity inputs change. |
| M5 2025.2 coverage-aware triangulation | `.venv/bin/python paper_v9/scripts/results/generate_m5_2025_triangulation.py` | `paper_v9/data/metrics/m5_marker_density.csv`, score/rework/concentration artifacts | `rq2_m5_2025_triangulation_panel.{pdf,svg,png}`, data CSV, summary CSV, metadata | `.venv/bin/python -m pytest paper_v9/tests/test_m5_2025_triangulation.py` |
| Team-semester evidence panel | `.venv/bin/python paper_v9/scripts/results/build_team_semester_evidence_panel.py` | core M1--M9 metric outputs, coverage flags | `paper_v9/figures/team_semester_evidence_panel.csv` and metadata | `.venv/bin/python -m pytest paper_v9/tests/test_team_semester_evidence_panel.py` |
| Legacy exploratory candidate figures | `.venv/bin/python paper_v9/scripts/results/generate_figure_candidates.py` | official metric artifacts | `candidate_rq1_*`, `candidate_rq2_*`, `candidate_rq3_*` figure/data files | `.venv/bin/python -m pytest paper_v9/tests/test_figure_candidates.py` |
| Traceable results summary | `.venv/bin/python paper_v9/scripts/results/build_results_summary.py` | official metric outputs under `paper_v9/data/metrics` | `paper_v9/data/results/results_summary.json` | `.venv/bin/python -m pytest paper_v9/tests/test_results_summary.py` |

### 7.3 Artifact governance

`paper_v9/ARTIFACT_USAGE_CATALOG.md` is the authoritative control plane for
editorial artifact decisions. It records which outputs are used in the main
text, appendix, reviewer response, diagnostics, or not promoted, together with
limitations and threat-mitigation roles. `paper_v9/FIGURES_CANDIDATES_WORKSHOP.md`
is a compact synchronized inventory for quick review; it should not supersede
the catalog.

When adding or regenerating an artifact, update the catalog if the artifact's
editorial role, limitation, or section mapping changes.

---

## 8. Validation Checklist

- [x] pdfTeX installed and functional
- [x] BibTeX installed and functional
- [x] IEEEtran.cls available via kpsewhich
- [x] cite package (citations) tested
- [x] booktabs package (table formatting) tested
- [x] tabularx package (table columns) tested
- [x] graphicx package (figure inclusion) tested
- [x] amsmath and amssymb (mathematical notation) tested
- [x] PDF generated without fatal errors
- [x] Bibliography processing verified
- [x] Cross-references resolved
- [x] Fonts embedded correctly (Type 1)
- [x] PDF version 1.5 (IEEE compliant)

---

## 9. Next Steps

### For Task 0.2 (Freeze V8 Baseline)

The LaTeX environment is ready. Proceed with:
1. Generating manifest of v8 LaTeX files and scripts
2. Recording invariant title, research questions, and sections
3. Documenting the v8-analysis notebooks

### For Task 6.1 (Modular LaTeX Initialization)

When ready, use:
```bash
cp paper_v8/latex_code/* paper_v9/latex/
pdflatex -interaction=nonstopmode -output-directory=build main.tex
```

To verify compilation of v8 content in v9 structure.

---

## 10. Support and Troubleshooting

### If compilation fails:

1. **Check LaTeX version compatibility:**
   ```bash
   pdflatex --version
   bibtex --version
   ```

2. **Verify IEEEtran availability:**
   ```bash
   kpsewhich IEEEtran.cls
   ```

3. **Check build directory permissions:**
   ```bash
   ls -ld paper_v9/latex/build/
   # Should be writable by current user
   ```

4. **Review compilation log:**
   ```bash
   cat paper_v9/latex/build/main.log | grep -E "Error|Fatal"
   ```

5. **Clear cached files and retry:**
   ```bash
   rm -rf paper_v9/latex/build/*.aux paper_v9/latex/build/*.log
   pdflatex -interaction=nonstopmode -output-directory=build main.tex
   ```

---

## 11. Approval Record

**Task 0.1 Status:** ✓ APPROVED FOR NEXT GATE

- Environment validated: 2026-09-24 13:47 UTC
- All dependencies installed: ✓
- Test PDF generated: ✓
- Reproducibility documented: ✓
- Ready for Task 0.2: ✓

---

**End of Reproducibility Report for Paper V9 LaTeX Environment**
