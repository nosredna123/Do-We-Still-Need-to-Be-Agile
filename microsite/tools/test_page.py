"""Check the static page shell using only the copied site's public files."""

from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import urlsplit


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str | None]]] = []
        self.words: list[str] = []
        self.declarations: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.elements.append((tag, dict(attrs)))

    def handle_data(self, data: str) -> None:
        self.words.append(data)

    def handle_decl(self, decl: str) -> None:
        self.declarations.append(decl.lower())


class PageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.site = Path(__file__).resolve().parent.parent
        cls.source = (cls.site / "index.html").read_text(encoding="utf-8")
        cls.page = PageParser()
        cls.page.feed(cls.source)
        cls.content = " ".join(" ".join(cls.page.words).split())

    def test_document_landmarks_and_language(self) -> None:
        self.assertEqual(self.page.declarations, ["doctype html"])
        self.assertIn(("html", {"lang": "en"}), self.page.elements)
        for tag in ("main", "h1", "title"):
            self.assertEqual(sum(t == tag for t, _ in self.page.elements), 1)
        self.assertIn(("meta", {"charset": "utf-8"}), self.page.elements)
        self.assertTrue(any(t == "meta" and a.get("name") == "viewport" for t, a in self.page.elements))
        sections = [a["id"] for t, a in self.page.elements if t == "section"]
        self.assertEqual(sections[:3], ["overview", "explore", "methods"])
        for tag, attrs in self.page.elements:
            if tag in ("section", "nav"):
                self.assertTrue(attrs.get("aria-labelledby") or attrs.get("aria-label"))
        self.assertIn(("a", {"href": "#main-content"}), self.page.elements)

    def test_neutral_favicon_stays_inside_the_portable_directory(self) -> None:
        icons = [a["href"] for t, a in self.page.elements if t == "link" and a.get("rel") == "icon"]
        self.assertEqual(icons, ["assets/favicon.svg"])
        self.assertTrue((self.site / icons[0]).is_file())

    def test_unique_ids_and_all_links_resolve_locally(self) -> None:
        ids = [a["id"] for _, a in self.page.elements if "id" in a]
        self.assertEqual(len(ids), len(set(ids)))
        for tag, attrs in self.page.elements:
            for key in ("aria-labelledby", "aria-describedby"):
                for target in (attrs.get(key) or "").split():
                    self.assertIn(target, ids)
            for key in ("href", "src"):
                if key not in attrs:
                    continue
                url = urlsplit(attrs[key])
                self.assertFalse(url.scheme or url.netloc or url.query)
                self.assertFalse(url.path.startswith("/") or ".." in Path(url.path).parts)
                if url.path:
                    self.assertTrue((self.site / url.path).is_file(), (tag, url.path))
                elif url.fragment:
                    self.assertIn(url.fragment, ids)

    def test_research_question_cards_and_metric_scope(self) -> None:
        for rq in ("rq1", "rq2", "rq3"):
            self.assertTrue(any(t == "a" and a.get("href") == "#" + rq for t, a in self.page.elements))
            self.assertTrue(any(t == "article" and a.get("id") == rq for t, a in self.page.elements))
        for metric in range(1, 10):
            self.assertIn("M" + str(metric), self.content)
        for phrase in ("Survey summaries", "Repository activity", "Transcript lexical aggregates",
                       "cohort and checkpoint", "cohort plus team", "2025.2",
                       "not individual teams", "descriptive and exploratory"):
            self.assertIn(phrase, self.content)

    def test_methods_and_catalog_navigation_state(self) -> None:
        for phrase in ("not zero", "original sample sizes", "not recalculated",
                       "none selected means all", "combined with OR", "different filters use AND",
                       "not a defect count", "0-4", "1-5",
                       "Catalog navigation requires JavaScript",
                       "Publication approval is pending"):
            self.assertIn(phrase, self.content)
        self.assertTrue(any(t == "dl" for t, _ in self.page.elements))
        for target in ("data/catalog.json", "data/release.json", "dataset-contracts.md"):
            self.assertTrue(any(t == "a" and a.get("href") == target for t, a in self.page.elements))
        self.assertFalse(any(t in ("iframe", "form") for t, _ in self.page.elements))
        self.assertFalse(any(a.get("role") == "tab" for _, a in self.page.elements))
        self.assertEqual([a.get("src") for t, a in self.page.elements if t == "script"], [
            "assets/vendor/plotly-cartesian-4.1.2.min.js", "assets/charts.js", "assets/app.js"])
        labels = {a["for"] for t, a in self.page.elements if t == "label"}
        controls = {a["id"] for t, a in self.page.elements if t in ("input", "select")}
        self.assertEqual(labels, controls)
        self.assertTrue(any(t == "script" and "defer" in a for t, a in self.page.elements))
        self.assertTrue(any(t == "fieldset" and a.get("id") == "dataset-navigation" and
                            "disabled" in a for t, a in self.page.elements))
        self.assertTrue(any(t == "noscript" for t, _ in self.page.elements))
        self.assertTrue(any(a.get("id") == "metadata-error" and a.get("role") == "alert"
                            for _, a in self.page.elements))
        self.assertTrue(any(t == "div" and a.get("id") == "dataset-table" and
                            a.get("role") == "region" and a.get("tabindex") == "0"
                            for t, a in self.page.elements))
        self.assertTrue(any(a.get("id") == "row-error" and a.get("role") == "alert"
                            for _, a in self.page.elements))
        self.assertTrue(any(t == "button" and a.get("id") == "row-reset"
                            for t, a in self.page.elements))

    def test_no_external_assets_or_unapproved_features(self) -> None:
        for tag, attrs in self.page.elements:
            self.assertNotIn(tag, ("base", "object", "embed"))
            self.assertFalse(any(key.startswith("on") for key in attrs))
            self.assertFalse(any("excerpt" in str(value).lower() for value in attrs.values()))
        for marker in ("http://", "https://", "file://", "/home/", "paper_v9", "github.com"):
            self.assertNotIn(marker, self.source)

    def test_excerpt_omission_has_no_view_or_placeholder(self) -> None:
        for tag, attrs in self.page.elements:
            self.assertNotIn(tag, ("blockquote", "q"))
            for key in ("id", "class", "href", "src", "aria-label", "aria-labelledby"):
                self.assertNotIn("excerpt", (attrs.get(key) or "").lower())
        self.assertNotIn("No excerpts", self.content)
        self.assertNotIn("Approved excerpts", self.content)
        self.assertNotIn("Excerpts unavailable", self.content)

    def test_figure_loading_scope_and_recovery_are_explicit(self) -> None:
        for phrase in ("full approved snapshot", "exact mapped source dataset", "Fixed published summaries",
                       "Exact source tables", "Reset figure view"):
            self.assertIn(phrase, self.content)
        for target in ("figure-controls", "figure-select", "figure-status", "figure-error",
                       "figure-retry", "figure-reset", "figure-output"):
            self.assertTrue(any(a.get("id") == target for _, a in self.page.elements))
        self.assertTrue(all("defer" in a for t, a in self.page.elements if t == "script"))

    def test_download_scope_missingness_and_recovery_are_explicit(self) -> None:
        for phrase in ("Full links contain all original", "observation table selection",
                       "headers only", "Formula-leading text is rejected", "Typed JSON"):
            self.assertIn(phrase, self.content)
        for target in ("downloads-heading", "full-downloads", "export-status", "export-error",
                       "export-retry", "filtered-downloads"):
            self.assertTrue(any(a.get("id") == target for _, a in self.page.elements))

    def test_reuse_guide_covers_the_complete_researcher_workflow_without_javascript(self) -> None:
        self.assertTrue(any(t == "article" and a.get("id") == "reuse-guide"
                            and a.get("aria-labelledby") == "reuse-heading" for t, a in self.page.elements))
        self.assertTrue(any(t == "a" and a.get("href") == "#reuse-guide" for t, a in self.page.elements))
        guide = PageParser()
        guide.feed(self.source.split('<article id="reuse-guide"', 1)[1].split("</article>", 1)[0])
        content = " ".join(" ".join(guide.words).split())
        for phrase in ("Choose the evidence", "Check units and denominators",
                       "Record the snapshot", "Choose the download scope",
                       "Import without changing values", "Preserve interpretation limits",
                       "percentage points", "cohort plus team", "not a license",
                       "SD bars are not confidence intervals", "Do not infer individual",
                       "do not mix snapshots", "not observation rows", "2025.2 only, not 2026.1",
                       "No verbatim quotations", "visible retry control"):
            self.assertIn(phrase, content)
        self.assertTrue(any(t == "a" and a.get("href") == "#snapshot-details"
                            for t, a in self.page.elements))
        self.assertNotIn("research-data-001", self.source)

    def test_readme_reuse_guide_retains_scope_identity_and_import_instructions(self) -> None:
        readme = (self.site / "README.md").read_text(encoding="utf-8").split("## Page shell", 1)[0]
        for phrase in ("Researcher quick start (T020)", "Choose the evidence",
                       "Check units and denominators", "Record the snapshot",
                       "Choose the download scope", "Import without changing values",
                       "Preserve interpretation limits", "UTF-8", "percentage points",
                       "not a license", "do not mix snapshots", "SD bars are not confidence intervals"):
            self.assertIn(phrase, readme)
        for target in ("index.html#reuse-guide", "index.html#snapshot-details"):
            self.assertIn(f"]({target})", readme)

    def test_acceptance_audit_records_every_check_without_claiming_release_approval(self) -> None:
        readme = (self.site / "README.md").read_text(encoding="utf-8")
        audit = readme.split("## Acceptance audit (T021)", 1)[1].split("## Public-safe naming", 1)[0]
        for prefix, count in (("S", 8), ("R", 6), ("A", 5), ("P", 6)):
            for number in range(1, count + 1):
                self.assertEqual(audit.count(f"| {prefix}{number} |"), 1)
        self.assertIn("Overall: NEEDS_SIGNOFF", audit)
        self.assertIn("NOT PASSED", audit)
        self.assertEqual(readme.count("- [ ]"), 11)

    def test_isolated_copy_report_preserves_portability_and_release_boundaries(self) -> None:
        readme = (self.site / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Independent-copy verification (T022)", readme)
        report = readme.split("## Independent-copy verification (T022)", 1)[1].split("## Public-safe naming", 1)[0]
        for phrase in ("read-only", "Nginx", "/review/explorer/", "125",
                       "808", "text/csv", "deny-only proxy", "no Python, Node, npm or Git",
                       "T023-T026", "not publication approval", "unchanged"):
            self.assertIn(phrase, report)
        self.assertEqual(readme.count("- [ ]"), 11)


if __name__ == "__main__":
    unittest.main()
