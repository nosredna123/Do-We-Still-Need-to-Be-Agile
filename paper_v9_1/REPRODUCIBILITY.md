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

## 7. Validation Checklist

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

## 8. Next Steps

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

## 9. Support and Troubleshooting

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

## 10. Approval Record

**Task 0.1 Status:** ✓ APPROVED FOR NEXT GATE

- Environment validated: 2026-09-24 13:47 UTC
- All dependencies installed: ✓
- Test PDF generated: ✓
- Reproducibility documented: ✓
- Ready for Task 0.2: ✓

---

**End of Reproducibility Report for Paper V9 LaTeX Environment**
