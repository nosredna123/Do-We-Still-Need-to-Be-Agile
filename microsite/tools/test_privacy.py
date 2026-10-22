"""Whole-directory publication-boundary regressions, not human anonymity approval."""

from pathlib import Path
import re
import unittest


class PrivacyTests(unittest.TestCase):
    site = Path(__file__).resolve().parent.parent

    def test_no_hidden_backups_symlinks_or_unreviewed_file_types(self) -> None:
        allowed = {".md", ".html", ".css", ".js", ".svg", ".txt", ".json", ".csv", ".py", ".cjs"}
        for path in self.site.rglob("*"):
            relative = path.relative_to(self.site)
            self.assertFalse(path.is_symlink(), relative)
            self.assertTrue(all(not part.startswith(".") for part in relative.parts), relative)
            if path.is_file():
                self.assertIn(path.suffix, allowed, relative)
                self.assertNotIn("excerpt", path.name.lower(), relative)
                self.assertNotIn("lineage", path.name.lower(), relative)

    def test_no_private_input_projections_in_any_shipped_text(self) -> None:
        patterns = (
            r"paper_" + r"v\d+",
            r"\b(?:rq[123]|m[1-9])_[A-Za-z0-9_]+\.(?:csv|png|json)\b",
            "Sem" + "estre",
            "ID_" + "Equipe",
            "CONTRACT_" + "SHA256",
            "SUPPLEMENT_" + "SHA256",
        )
        for path in self.site.rglob("*"):
            if not path.is_file():
                continue
            content = path.read_text(encoding="utf-8")
            for pattern in patterns:
                self.assertIsNone(re.search(pattern, content), (path.relative_to(self.site), pattern))


if __name__ == "__main__":
    unittest.main()
