import copy
import os
import posixpath
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

os.environ["ATLAS_TEST_ALLOW_ANY_TREE"] = "1"
TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import lifecycle_common as lc  # noqa: E402
import render  # noqa: E402
import render_lifecycle as rl  # noqa: E402
from atlas_common import DATA_DIR, dump_json, load_json  # noqa: E402
from test_render import (  # noqa: E402
    EXPECTED_PAGES,
    LIFECYCLE_PAGES,
    XSS,
    XSS_ESCAPED,
    fixture,
    scan,
    write_data,
)

CC, CX = "claude-code", "codex-cli"
ROWS = ["F04.approval-modes", "F04.per-tool-rules"]


def skeleton():
    return {
        "schema_version": 1,
        "stages": [
            {"id": "A", "name": "Setup", "blurb": "Getting ready."},
            {"id": "B", "name": "Each turn", "blurb": "Before sending."},
        ],
        "glossary": {
            "harness": "The program around a model.",
            "tool": "An action the model can ask for.",
        },
        "concepts": [
            {
                "id": "safety",
                "stage": "A",
                "order": 1,
                "name_plain": "Set the safety posture",
                "what_it_does": "Settles how much the model may do without asking.",
                "predicate_general": "Modes differ between harnesses.",
                "typical_after": [],
                "depends_on": [],
                "who_normally_does_it": "harness code",
                "matters_for_model_choice": "Pick the mode first, then the model.",
                "rows": ROWS,
                "jargon": ["harness"],
                "gap": None,
            },
            {
                "id": "caching",
                "stage": "B",
                "order": 1,
                "name_plain": "Reuse the prompt",
                "what_it_does": "Keeps the unchanged start of a prompt.",
                "predicate_general": "Only some services.",
                "typical_after": ["safety"],
                "depends_on": ["safety"],
                "who_normally_does_it": "harness code",
                "matters_for_model_choice": "Not researched yet.",
                "rows": [],
                "jargon": [],
                "gap": "full",
            },
        ],
        "uncovered": [],
    }


def lines_for(data, plain):
    cells = data["cells"][CC]
    concept = skeleton()["concepts"][0]
    sub = lc.concept_cells({CC: cells}, CC, concept)
    return {
        "schema_version": 1,
        "agents": {
            CC: {
                "safety": {
                    "plain": plain,
                    "technical": "Detail text.",
                    "cells_sha": lc.cells_sha(sub),
                }
            }
        },
    }


class LayerCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.n = 0

    def data(
        self,
        with_lifecycle=True,
        plain="It asks before it runs a command.",
        trees=None,
        mutate=None,
    ):
        self.n += 1
        data = copy.deepcopy(fixture())
        base = write_data(self.root / str(self.n), data)
        if with_lifecycle:
            dump_json(base / "lifecycle.json", skeleton())
            dump_json(base / "lifecycle-lines.json", lines_for(data, plain))
            if trees is not None:
                dump_json(base / "trees.json", trees)
        if mutate:
            mutate(base)
        return base

    def pages(self, **kw):
        return render.render_all(self.data(**kw))


class PageSetTests(LayerCase):
    def test_pages_and_nav_appear_only_when_the_data_exists(self):
        without = self.pages(with_lifecycle=False)
        self.assertEqual(sorted(without), sorted(EXPECTED_PAGES))
        self.assertNotIn("lifecycle.html", without["index.html"])
        with_ = self.pages()
        self.assertEqual(sorted(with_), sorted(EXPECTED_PAGES + LIFECYCLE_PAGES))
        for name in ("lifecycle.html", "compare.html", "trees/index.html"):
            self.assertIn(name.split("/")[-1], with_["index.html"])

    def test_the_nav_state_does_not_leak_between_renders(self):
        self.pages()
        again = self.pages(with_lifecycle=False)
        self.assertNotIn("Lifecycle", again["index.html"])

    def test_every_internal_link_and_anchor_resolves(self):
        pages = self.pages(trees={"agents": {CC: {"decision_points": []}}})
        ids = {name: set(scan(text).ids) for name, text in pages.items()}
        for name, text in pages.items():
            for _kind, link in scan(text).links:
                if link.startswith(("http", "mailto:")):
                    continue
                target, _, fragment = link.partition("#")
                path = (
                    name
                    if not target
                    else posixpath.normpath(
                        posixpath.join(posixpath.dirname(name), unquote(target))
                    )
                )
                self.assertIn(path, pages, f"{name} -> {link}")
                if fragment:
                    self.assertIn(unquote(fragment), ids[path], f"{name} -> {link}")

    def test_the_same_data_renders_the_same_bytes(self):
        a = self.pages()
        b = render.render_all(self.root / "1" / "data")
        self.assertEqual(a, b)


class LifecyclePageTests(LayerCase):
    def test_a_planted_script_in_a_plain_line_is_escaped(self):
        pages = self.pages(plain=f"It asks first {XSS}.")
        for name in ("lifecycle.html", "trees/claude-code.html"):
            self.assertIn(XSS_ESCAPED, pages[name])
            self.assertNotIn("<script>alert(1)", pages[name])

    def test_labels_conditions_and_order_notes_are_shown(self):
        pages = self.pages()
        text = pages["lifecycle.html"]
        self.assertIn(rl.GENERAL_LABEL, text)
        self.assertIn(rl.EDITORIAL_LABEL, text)
        self.assertIn("Only if:", text)
        self.assertIn("Only ", text)
        self.assertIn("Documented conditions", text)  # the partial cell's limitation, filtered

    def test_a_gap_concept_says_it_is_not_researched_and_has_no_agent_table(self):
        text = self.pages()["lifecycle.html"]
        section = text.split('id="c-caching"', 1)[1].split("</section>", 1)[0]
        self.assertIn("Not yet researched for any agent", section)
        self.assertNotIn("<table", section)

    def test_an_agent_with_no_line_is_marked_not_blank(self):
        text = self.pages()["lifecycle.html"]
        self.assertIn("no line", text)

    def test_the_glossary_is_listed(self):
        text = self.pages()["lifecycle.html"]
        self.assertIn("<dt>harness</dt>", text)

    def test_the_badge_comes_from_the_cells(self):
        text = self.pages()["lifecycle.html"]
        self.assertIn(
            "documented, with limits", text
        )  # approval-modes supported + per-tool-rules partial
        self.assertIn("not documented", text)  # an agent with no cells for these rows


class CompareTests(LayerCase):
    def test_the_direction_is_computed_from_states_not_written(self):
        text = self.pages()["compare.html"]
        self.assertIn("Documents the most:", text)
        # Codex has only the supported cell for these rows; Claude Code also has a partial one.
        self.assertIn("OpenAI Codex CLI (100%)", text.split("Documents the most:", 1)[1][:80])

        def downgrade(base):
            path = base / "cells" / f"{CX}.json"
            doc = load_json(path)
            for c in doc["cells"]:
                if c["row"] == "F04.approval-modes":
                    c["state"] = "undocumented"
            dump_json(path, doc)

        text = render.render_all(self.data(mutate=downgrade))["compare.html"]
        self.assertNotIn("OpenAI Codex CLI (100%)", text.split("Documents the most:", 1)[1][:80])

    def test_the_caveat_names_every_agent_with_its_undocumented_count(self):
        text = self.pages()["compare.html"]
        self.assertIn("Undocumented cells out of 127", text)
        self.assertIn("Not documented is not the same as cannot", text)

    def test_the_editorial_view_is_boxed_and_labelled(self):
        text = self.pages()["compare.html"]
        self.assertIn('class="editorial"', text)
        self.assertIn(rl.EDITORIAL_LABEL, text)

    def test_the_limits_section_says_what_it_cannot_tell_you(self):
        text = self.pages()["compare.html"]
        self.assertIn("What this page cannot tell you", text)
        self.assertIn("no share is given", text)

    def test_the_model_panel_never_says_regardless_of_model(self):
        text = self.pages()["compare.html"]
        self.assertIn(
            "No documented model dependence", text.replace("<em>", "").replace("</em>", "")
        )
        self.assertNotIn("regardless of model", text.lower())


class TreeTests(LayerCase):
    def trees(self):
        cell = next(c for c in fixture()["cells"][CC] if c["row"] == "F04.per-tool-rules")
        corpus = lc.squash(f"{cell.get('value') or ''} {cell.get('limitation') or ''}")
        return {
            "agents": {
                CC: {
                    "decision_points": [
                        {
                            "id": "dp1",
                            "cell": cell["id"],
                            "question": "What happens in each case?",
                            "branches": [
                                {
                                    "answer": "Case one",
                                    "outcome": "One thing.",
                                    "clause": corpus[:25],
                                },
                                {
                                    "answer": "Case two",
                                    "outcome": "Another thing.",
                                    "clause": corpus[-25:],
                                },
                            ],
                        }
                    ]
                }
            }
        }

    def test_a_decision_point_sits_under_its_concept_with_quoted_branches(self):
        pages = self.pages(trees=self.trees())
        text = pages["trees/claude-code.html"]
        self.assertIn("Decision point:", text)
        self.assertIn("Case one", text)
        self.assertIn("<blockquote>", text)
        self.assertLess(text.index("Set the safety posture"), text.index("Decision point:"))
        self.assertIn("the order between decision points is not stated", text)

    def test_an_agent_with_no_decision_point_still_renders_its_flow(self):
        text = self.pages(trees=self.trees())["trees/codex-cli.html"]
        self.assertNotIn("Decision point:", text)
        self.assertIn("What happens to a request", text)

    def test_the_routing_appendix_is_labelled_as_ours(self):
        text = self.pages()["trees/claude-code.html"]
        self.assertIn("This is RavenClaude's own advice", text)
        self.assertIn("not vendor guidance", text)

    def test_the_lever_finder_lists_where_each_control_lives(self):
        text = self.pages()["trees/claude-code.html"]
        self.assertIn("--permission-mode", text)
        self.assertIn("Where to set: mode", text)


class RealDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.has_lines = (DATA_DIR / "lifecycle-lines.json").exists()
        cls.pages = render.render_all(DATA_DIR)

    def test_the_real_pages_exist(self):
        for name in LIFECYCLE_PAGES:
            self.assertIn(name, self.pages)

    def test_every_concept_has_a_card_and_every_agent_a_row_in_it(self):
        life = load_json(DATA_DIR / "lifecycle.json")
        text = self.pages["lifecycle.html"]
        sids = [s["id"] for s in load_json(DATA_DIR / "surfaces.json")["surfaces"]]
        for concept in life["concepts"]:
            self.assertIn(f'id="c-{concept["id"]}"', text)
            if concept["rows"]:
                for sid in sids:
                    self.assertIn(f'id="{concept["id"]}-{sid}"', text)

    def test_the_compare_grid_has_one_row_per_concept(self):
        life = load_json(DATA_DIR / "lifecycle.json")
        text = self.pages["compare.html"]
        for concept in life["concepts"]:
            self.assertIn(f'id="g-{concept["id"]}"', text)

    def test_every_authored_line_appears_in_its_page(self):
        if not self.has_lines:
            self.skipTest("no lines yet")
        lines = load_json(DATA_DIR / "lifecycle-lines.json")["agents"]
        text = self.pages["lifecycle.html"]
        for sid, entries in lines.items():
            for cid, entry in entries.items():
                self.assertIn(render.esc(entry["plain"]), text, f"{sid}/{cid}")

    def test_no_page_claims_a_share_of_work_or_a_ranking_of_quality(self):
        for name in ("lifecycle.html", "compare.html"):
            lowered = self.pages[name].lower()
            for banned in (
                "regardless of model",
                "the best agent",
                "is better than",
                "% of the work",
            ):
                self.assertNotIn(banned, lowered, name)


if __name__ == "__main__":
    unittest.main()
