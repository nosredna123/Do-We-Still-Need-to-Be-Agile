# Reference Audit Report — `paper_v9`

Date: 2026-09-26

Scope: entry-by-entry review of `latex/references.bib` after the recent BibTeX cleanup. This report does **not** modify the `.bib` file; it records the audit findings and gives exact replacement snippets for entries that should be corrected while preserving their current BibTeX keys.

Implementation status: the corrective snippets and optional completeness improvements identified here were applied to `latex/references.bib` on 2026-09-26. The post-fix LaTeX/BibTeX compilation completed successfully and kept the paper at 11 pages.

## Method

- Parsed all 31 BibTeX entries in `latex/references.bib`.
- Checked DOI-bearing entries against Crossref/DOI metadata where possible.
- Checked URL-bearing entries for resolvability and page-level evidence where possible.
- Compared current BibTeX fields with retrieved metadata and the rendered `latex/main.bbl`.
- Classified anonymous replication/explorer entries separately because their `example.org` URLs are intentional blind-review placeholders.

Severity labels:

- **OK**: metadata is consistent enough for submission.
- **Minor**: authentic source, but formatting or completeness could be improved.
- **Medium**: authentic or plausibly authentic source, but the BibTeX has a material metadata mismatch or weak provenance.
- **High**: DOI/source metadata contradicts the current entry, or the current substitution is semantically risky.

## Executive summary

The bibliography compiles cleanly, but the audit found several entries whose current `[VERIFICADA]`, `[CORRIGIDA]`, or `[SUBSTITUÍDA]` comments are stronger than the available evidence supports.

Recommended fixes before submission:

1. Correct four metadata mismatches:
   - `yabaku2024usage`
   - `runeson2009case`
   - `williams_2024_ai_software_engineering_education`
   - `miller_2023_coordination_ai_teams`
2. Reclassify `chen_2021_evaluating_code_llms` as an arXiv article/misc entry rather than an inproceedings entry.
3. Treat `nguyenduc2026systematic` as provisional because the Preprints page exists but could not be independently verified beyond the URL/search result in this audit.
4. Keep `prism_replication_package` and `prism_explorer` only as deliberate blind-review placeholders; replace them with real archival URLs before camera-ready or artifact evaluation.

## Entry-by-entry findings

| # | Key | Status | Evidence checked | Finding | Recommendation |
|---|-----|--------|------------------|---------|----------------|
| 1 | `lewis2020retrieval` | OK | NeurIPS metadata known; local fields complete | Entry matches the canonical RAG paper metadata. | Keep. Optional: add URL to NeurIPS proceedings if desired. |
| 2 | `nguyenduc2026systematic` | Medium | URL exists in search results; direct fetch returned HTTP 403 | The Preprints URL appears to exist, but the audit could not verify full authorship or article metadata from the page. The author field `Anh and others` is weak. | Keep only if the paper text needs a very recent preprint. Otherwise replace with a peer-reviewed SLR or soften the citation claim. Do not mark as fully verified unless metadata is confirmed. |
| 3 | `ieee2025transforming` | Medium | URL resolves to IEEE Computer Society CSDL page, but page extraction returned only generic CSDL text | The URL is resolvable, but title/authorship/date were not fully verifiable from extracted metadata. `author={{IEEE Computer Society}}` may be an organizational fallback rather than the actual author. | Keep provisionally; before final submission, open IEEE CSDL and capture exact authors/title/issue/pages. |
| 4 | `cambridge2026contextual` | Minor | URL resolves; page content matches the contextual-gap theme | Source exists as a web/blog article. Author/date were not captured in the current BibTeX. | Keep if a practitioner/web source is acceptable; add actual author/date if visible on the page. |
| 5 | `github2025spec` | OK | URL resolves; content matches spec-driven development with Spec Kit | Current author/date look plausible and the link is stable. `journal` in `@misc` is not rendered by IEEEtran. | Keep. Optional: move `The GitHub Blog` into `howpublished` or `note` for rendering consistency. |
| 6 | `thoughtworks202Xspec` | OK | URL resolves; page title and topic match | Entry is authentic and semantically aligned. The key still contains `202X`, but this does not affect compilation. | Keep. Optional: rename key only if all citations are updated; not necessary. |
| 7 | `codebridge2026hidden` | Minor | URL resolves; article content matches AI-generated software cost/debt theme | Source exists, but it is a practitioner article rather than scholarly literature. | Keep if used for industry-facing motivation; avoid using it as primary evidence for empirical claims. |
| 8 | `banh2025copiloting` | OK | DOI `10.1016/j.infsof.2025.107751` verified | Crossref metadata matches title, venue, year, volume, and article number. | Keep. |
| 9 | `russo2024navigating` | Minor | DOI `10.1145/3652154` verified | Entry is authentic. `author={Russo, Daniel and others}` is acceptable for compactness but less precise. Missing issue/article/page details may reduce completeness. | Keep, or expand authors/issue/article number if space/style permits. |
| 10 | `staron2025exploring` | OK | DOI `10.1109/MS.2025.3533754` verified | Metadata matches Crossref: IEEE Software, vol. 42, no. 3, pp. 142--145. | Keep. |
| 11 | `carleton2024generative` | OK | DOI `10.1109/MS.2024.3441889` verified | Metadata matches Crossref. | Keep. |
| 12 | `barke2023grounded` | Minor | DOI `10.1145/3586030` verified | Current entry is authentic, but Crossref includes issue `OOPSLA1` and pages `85--111`, which are missing. | Keep, but consider adding issue/pages for completeness. |
| 13 | `yabaku2024usage` | High | DOI `10.1109/CSEET62301.2024.10663035` verified | DOI resolves to **"University Students' Perception and Expectations of Generative AI Tools for Software Engineering"**, not the current title. Pages are `1--5`. | Replace with the exact corrected entry below. |
| 14 | `verdecchia2018architectural` | OK | DOI `10.1109/ICSA-C.2018.00018` verified | Metadata matches. | Keep. |
| 15 | `nayebi2019longitudinal` | OK | DOI `10.1109/ICSE-SEIP.2019.00026` verified | Metadata matches. | Keep. |
| 16 | `stol2018abc` | Minor | DOI `10.1145/3241743` verified | Authentic. Missing issue/page/article information could be improved. | Keep, or complete metadata if desired. |
| 17 | `runeson2009case` | High | DOI `10.1007/s10664-008-9102-8` verified | Current entry combines the **book** title/authors with the **journal article** DOI. The DOI metadata is for Runeson and Höst, "Guidelines for conducting and reporting case study research in software engineering," Empirical Software Engineering 14(2), 131--164. | Replace with the exact corrected entry below. |
| 18 | `spearman1904proof` | Minor | DOI `10.2307/1412159` verified | Entry is authentic. DOI is missing. | Keep, or add DOI for completeness. |
| 19 | `agile_manifesto_2001` | OK | URL resolves | Entry is authentic and complete enough for the Agile Manifesto. | Keep. |
| 20 | `cunningham_1992_technical_debt` | Minor | Known OOPSLA experience-report source | Entry is authentic enough, but the venue formatting is sparse and no URL/DOI is present. | Keep. Optional: add a stable URL if available. |
| 21 | `fowler2009technicaldebt` | OK | URL resolves | Entry is authentic. | Keep. |
| 22 | `kruchten2012technicaldebt` | OK | DOI `10.1109/MS.2012.167` verified | Metadata matches. | Keep. |
| 23 | `brooks_1975_mythical_man_month` | OK | Canonical book metadata | Entry is authentic. | Keep. |
| 24 | `demarco_lister_1987_peopleware` | OK | Canonical book metadata | Entry is authentic. | Keep. |
| 25 | `li_2015_technical_debt_mapping` | OK | DOI `10.1016/j.jss.2014.12.027` verified | Metadata matches. | Keep. |
| 26 | `chen_2021_evaluating_code_llms` | Medium | arXiv `2107.03374` verified | Source is real, but it is not a conference proceeding. Current `booktitle={arXiv preprint...}` and long author list contain likely author-name errors. | Replace with the exact arXiv-style entry below. |
| 27 | `williams_2024_ai_software_engineering_education` | High | Current DOI returned 404; corrected DOI `10.1109/ACCESS.2024.3380909` verified | The substituted paper is real, but the current title, author spelling, pages, and DOI are wrong. Correct title is **"Students' Experiences of Using ChatGPT in an Undergraduate Programming Course"**, authors Philipp Haindl and Gerald Weinberger, pages 43519--43529. | Replace with the exact corrected entry below. |
| 28 | `miller_2023_coordination_ai_teams` | High | Current DOI returned 404; search/Crossref found `10.1109/MC.2026.3686931` | Current substitute metadata is wrong: the article is in **Computer**, not IEEE Software; year 2026, vol. 59, no. 7, pp. 96--99; authors Spinellis, Baudry, and Voas. Also, it is not a course/team-coordination study, so semantic fit depends on the claim being cited. | Replace metadata if retaining this source; if the citation supports student-team coordination, replace the citation in the paper with a more directly relevant education/teamwork source instead. |
| 29 | `prism_replication_package` | OK placeholder | URL intentionally `example.org`, fetch returns 404 | This is a blind-review placeholder, not an external factual reference. | Keep for anonymous submission only. Replace with real archive DOI/URL before camera-ready. |
| 30 | `prism_explorer` | OK placeholder | URL intentionally `example.org`, fetch returns 404 | This is a blind-review placeholder, not an external factual reference. | Keep for anonymous submission only. Replace with real explorer/archive URL before camera-ready. |
| 31 | `perez_2022_planning_and_rework` | OK | DOI `10.1145/2732155` verified | Substituted source is real and metadata matches Crossref. The key name no longer describes the actual source, but preserving the key avoids LaTeX citation changes. | Keep. |

## Exact replacement snippets for entries needing correction

The snippets below preserve the existing BibTeX keys. If applied to `references.bib`, keep the history comments but avoid commented-out raw BibTeX entries in the `.bib` file, because BibTeX can still misinterpret `@...` blocks in comments.

### `yabaku2024usage`

```bibtex
% [CORRIGIDA]: DOI verificado em Crossref. O registro anterior usava o mesmo DOI,
% mas com título diferente do metadado oficial. Mantido o ID para preservar as
% citações no LaTeX.
% REGISTRO ANTERIOR: inproceedings yabaku2024usage; title={On Usage and
% Assessment of Generative AI by Computer Science Students in Software
% Development Projects}; booktitle={2024 36th International Conference on
% Software Engineering Education and Training (CSEE&T)}; year={2024};
% doi={10.1109/CSEET62301.2024.10663035}
@inproceedings{yabaku2024usage,
  author    = {Yabaku, Mounika and Ouhbi, Sofia},
  title     = {University Students' Perception and Expectations of Generative AI Tools for Software Engineering},
  booktitle = {2024 36th International Conference on Software Engineering Education and Training (CSEE\&T)},
  pages     = {1--5},
  year      = {2024},
  doi       = {10.1109/CSEET62301.2024.10663035}
}
```

### `runeson2009case`

```bibtex
% [CORRIGIDA]: DOI verificado em Crossref. O registro anterior misturava o título
% e autores do livro "Case Study Research in Software Engineering: Guidelines and
% Examples" com o DOI do artigo de Runeson e Höst em Empirical Software Engineering.
% Mantido o ID para preservar as citações no LaTeX.
% REGISTRO ANTERIOR: article runeson2009case; author={Runeson, Per and Host,
% Martin and Rainer, A. J. and Regnell, Bjorn}; title={Case Study Research in
% Software Engineering: Guidelines and Examples}; journal={Empirical Software
% Engineering}; volume={14}; year={2009}; doi={10.1007/s10664-008-9102-8}
@article{runeson2009case,
  author  = {Runeson, Per and H{\"o}st, Martin},
  title   = {Guidelines for Conducting and Reporting Case Study Research in Software Engineering},
  journal = {Empirical Software Engineering},
  volume  = {14},
  number  = {2},
  pages   = {131--164},
  year    = {2009},
  doi     = {10.1007/s10664-008-9102-8}
}
```

### `chen_2021_evaluating_code_llms`

```bibtex
% [CORRIGIDA]: Fonte verificada como preprint arXiv 2107.03374, não como
% inproceedings. A lista longa de autores anterior continha prováveis erros de
% transcrição; "and others" evita introduzir nomes incorretos e preserva a
% renderização IEEE compacta.
% REGISTRO ANTERIOR: inproceedings chen_2021_evaluating_code_llms;
% booktitle={arXiv preprint arXiv:2107.03374}; year={2021}
@article{chen_2021_evaluating_code_llms,
  author  = {Chen, Mark and others},
  title   = {Evaluating Large Language Models Trained on Code},
  journal = {arXiv preprint arXiv:2107.03374},
  year    = {2021},
  url     = {https://arxiv.org/abs/2107.03374}
}
```

### `williams_2024_ai_software_engineering_education`

```bibtex
% [CORRIGIDA]: A substituição por Haindl e Weinberger é real, mas o registro
% anterior tinha título, grafia do segundo autor, páginas e DOI incorretos.
% Metadados conferidos via Crossref. Mantido o ID para preservar as citações no LaTeX.
% REGISTRO ANTERIOR: article williams_2024_ai_software_engineering_education;
% author={Haindl, Philipp and Weinberger, Georg};
% title={Experiences of Using ChatGPT in an Undergraduate Programming Course};
% journal={IEEE Access}; volume={12}; pages={43518--43537}; year={2024};
% doi={10.1109/ACCESS.2024.3378945}
@article{williams_2024_ai_software_engineering_education,
  author  = {Haindl, Philipp and Weinberger, Gerald},
  title   = {Students' Experiences of Using ChatGPT in an Undergraduate Programming Course},
  journal = {IEEE Access},
  volume  = {12},
  pages   = {43519--43529},
  year    = {2024},
  doi     = {10.1109/ACCESS.2024.3380909}
}
```

### `miller_2023_coordination_ai_teams`

Use this only if the paper citation is meant to support a broad industry/practice claim about AI changing software-development work. If the cited claim is specifically about student teams, coordination signals, or software-engineering courses, this substitute is semantically weak and the citation should be replaced in the LaTeX prose rather than only corrected in BibTeX.

```bibtex
% [CORRIGIDA]: A substituição por Spinellis et al. é real, mas o registro
% anterior apontava para DOI inexistente e informava periódico, ano, volume,
% número, páginas e autoria incorretos. Metadados conferidos via Crossref.
% Mantido o ID para preservar as citações no LaTeX, embora a adequação semântica
% deva ser reavaliada no trecho citado.
% REGISTRO ANTERIOR: article miller_2023_coordination_ai_teams;
% author={Spinellis, Diomidis}; title={AI: The Blind-Men Elephant in the Software
% Developers' Room}; journal={IEEE Software}; volume={41}; number={4};
% pages={4--8}; year={2024}; doi={10.1109/MS.2024.3387819}
@article{miller_2023_coordination_ai_teams,
  author  = {Spinellis, Diomidis and Baudry, Benoit and Voas, Jeffrey},
  title   = {AI: The Blind-Men Elephant in the Software Developers' Room},
  journal = {Computer},
  volume  = {59},
  number  = {7},
  pages   = {96--99},
  year    = {2026},
  doi     = {10.1109/MC.2026.3686931}
}
```

## Optional completeness improvements

These are not urgent, but they would make the bibliography more robust:

```bibtex
% Optional DOI addition for Spearman.
doi = {10.2307/1412159}
```

```bibtex
% Optional completion for Grounded Copilot.
number = {OOPSLA1},
pages  = {85--111}
```

## Final coherence check

- Duplicate keys: none detected.
- BibTeX syntax: previously confirmed clean after the last cleanup; this audit did not alter the file.
- Broken external URLs:
  - `prism_replication_package` and `prism_explorer` intentionally use `example.org` placeholders.
  - `nguyenduc2026systematic` returned HTTP 403 on direct fetch, although the URL appears in search results.
- DOI mismatches requiring correction:
  - `yabaku2024usage`
  - `runeson2009case`
  - `williams_2024_ai_software_engineering_education`
  - `miller_2023_coordination_ai_teams`
- Entry-type mismatch requiring correction:
  - `chen_2021_evaluating_code_llms`
- Semantic-risk entry:
  - `miller_2023_coordination_ai_teams`, because the real Spinellis/Baudry/Voas article is not an education/course/team-coordination study.

Overall assessment: the bibliography is syntactically usable, but the five correction snippets above should be applied before relying on the current `[VERIFICADA]` / `[SUBSTITUÍDA]` labels as a traceable reference-verification record.
