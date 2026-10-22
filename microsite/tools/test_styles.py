"""Static stylesheet contract checks; browser geometry is verified separately."""

from pathlib import Path
import re
import unittest

from test_page import PageParser


def luminance(color: str) -> float:
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


class StylesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.site = Path(__file__).resolve().parent.parent
        cls.css = (cls.site / "assets/styles.css").read_text()

    def test_local_stylesheet_is_wired_once(self) -> None:
        parser = PageParser()
        parser.feed((self.site / "index.html").read_text())
        styles = [attrs["href"] for tag, attrs in parser.elements
                  if tag == "link" and attrs.get("rel") == "stylesheet"]
        self.assertEqual(styles, ["assets/styles.css"])

    def test_system_fonts_and_no_network_or_hidden_content(self) -> None:
        self.assertIn("system-ui", self.css)
        for marker in ("@import", "@font-face", "url(", "http:", "https:", "display: none",
                       "outline: none", "outline: 0", "overflow-x: hidden"):
            self.assertNotIn(marker, self.css)

    def test_palette_contrast(self) -> None:
        colors = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-f]{6})", self.css))
        for foreground, background, threshold in (
            ("ink", "surface", 4.5), ("muted", "surface", 4.5),
            ("link", "surface", 4.5), ("link", "soft", 4.5),
            ("surface", "action", 4.5), ("focus", "surface", 3),
            ("focus", "soft", 3), ("border", "surface", 3),
        ):
            a, b = sorted((luminance(colors[foreground]), luminance(colors[background])))
            self.assertGreaterEqual((b + 0.05) / (a + 0.05), threshold,
                                    (foreground, background))

    def test_focus_controls_and_table_contract(self) -> None:
        for marker in (":focus-visible", "outline-offset:", "min-block-size: 2.75rem",
                       "input", "select", "button", "label", "fieldset",
                       ".table-scroll", "overflow-x: auto", "font-variant-numeric: tabular-nums",
                       "caption", "th", "td", "@media", "prefers-reduced-motion"):
            self.assertIn(marker, self.css)


if __name__ == "__main__":
    unittest.main()
