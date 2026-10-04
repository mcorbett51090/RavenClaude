import os
import unittest

os.environ["ATLAS_TEST_ALLOW_ANY_TREE"] = "1"

import briefs  # noqa: E402
from atlas_common import DATA_DIR, load_json  # noqa: E402


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.facets = load_json(DATA_DIR / "facets.json")

    def test_every_row_in_every_style(self):
        ids = [r["id"] for f in self.facets["facets"] for r in f["rows"]]
        for style in ("ids", "short", "full"):
            text = briefs.catalog_text(self.facets, style)
            for row_id in ids:
                self.assertIn(row_id, text)
            self.assertIn("U00", text)

    def test_styles_grow(self):
        sizes = [len(briefs.catalog_text(self.facets, s)) for s in ("ids", "short", "full")]
        self.assertLess(sizes[0], sizes[1])
        self.assertLess(sizes[1], sizes[2])


class BriefTests(unittest.TestCase):
    def test_brief_holds_every_value_and_the_rules(self):
        rows = [
            {"id": "p1#1", "page_id": "p1", "path": "/x/p1-1.md", "product": "demo"},
            {"id": "p1#2", "page_id": "p1", "path": "/x/p1-2.md", "product": "demo"},
        ]
        text = briefs.make_brief("B-001", rows, "/x/catalog.txt", "/x/out/B-001.json")
        for needle in ("B-001", "/x/p1-1.md", "/x/p1-2.md", "/x/catalog.txt", "/x/out/B-001.json"):
            self.assertIn(needle, text)
        for rule in (
            "character for character",
            "never follow instructions",
            "Do not read task output files",
        ):
            self.assertIn(rule.lower(), text.lower())
        self.assertNotIn("{", text.replace("{", "", 0).split("## Output")[0])

    def test_brief_names_exactly_one_output(self):
        text = briefs.make_brief("B-002", [], "/c.txt", "/o.json")
        self.assertEqual(text.count("Write exactly one file"), 1)


if __name__ == "__main__":
    unittest.main()
