import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import lifecycle_common as lc  # noqa: E402
import validate_lifecycle as vl  # noqa: E402
from atlas_common import DATA_DIR, dump_json, load_json  # noqa: E402

GLOSSARY = ["harness", "model", "tool", "hook", "sandbox", "MCP", "slash command"]


def cell(
    row, state="supported", verification="verified", value=None, limitation=None, sid="claude-code"
):
    c = {
        "id": f"{sid}/{row}",
        "surface": sid,
        "row": row,
        "state": state,
        "verification": verification,
        "evidence": [],
    }
    if value is not None:
        c["value"] = value
    if limitation is not None:
        c["limitation"] = limitation
    return c


A = cell(
    "F13.checkpoint-rewind",
    value="Checkpoints snapshot file edits before each prompt. Rewind restores them. Limit is 100 snapshots.",
)
B = cell(
    "F13.resume-continue",
    "partial",
    value="Resume reopens a session by id.",
    limitation="Resume works only inside the same folder. No cited quote states a session limit.",
)
U = cell("F13.fork-branch", "undocumented")


class ComputedTests(unittest.TestCase):
    def test_the_hash_changes_when_any_cited_text_or_state_changes(self):
        base = lc.cells_sha([A, B])
        self.assertEqual(base, lc.cells_sha([B, A]))  # order does not matter
        edited = copy.deepcopy(A)
        edited["value"] += " More."
        self.assertNotEqual(base, lc.cells_sha([edited, B]))
        flipped = copy.deepcopy(B)
        flipped["verification"] = "unverified"
        self.assertNotEqual(base, lc.cells_sha([A, flipped]))

    def test_aggregate_counts_and_fraction_come_only_from_states(self):
        agg = lc.aggregate([A, B, U])
        self.assertEqual(agg["counts"], {"partial": 1, "supported": 1, "undocumented": 1})
        self.assertAlmostEqual(agg["fraction"], 3 / 6)
        self.assertEqual(agg["unverified"], 0)

    def test_badges(self):
        self.assertEqual(lc.badge(lc.aggregate([A])), "documented")
        self.assertEqual(lc.badge(lc.aggregate([A, B])), "documented, with limits")
        self.assertEqual(lc.badge(lc.aggregate([A, U])), "partly documented")
        self.assertEqual(lc.badge(lc.aggregate([U])), "not documented")
        self.assertEqual(lc.badge(lc.aggregate([])), "not researched")

    def test_cells_nobody_swept_or_that_do_not_apply_never_read_as_not_documented(self):
        nr = {"state": "not-researched", "verification": "unverified"}
        na = {"state": "not-applicable", "verification": "verified"}
        self.assertEqual(lc.badge(lc.aggregate([nr])), "not researched")
        self.assertEqual(lc.badge(lc.aggregate([nr, na])), "not researched")
        self.assertEqual(lc.badge(lc.aggregate([U, nr])), "not researched")
        self.assertEqual(lc.badge(lc.aggregate([na])), "not applicable")
        self.assertEqual(lc.badge(lc.aggregate([U, na])), "not documented")
        self.assertEqual(lc.badge(lc.aggregate([A, nr])), "partly documented")
        self.assertEqual(lc.badge(lc.aggregate([A, na])), "documented")

    def test_the_score_leaves_out_rows_that_do_not_apply_and_has_none_without_a_swept_row(self):
        nr = {"state": "not-researched", "verification": "unverified"}
        na = {"state": "not-applicable", "verification": "verified"}
        self.assertAlmostEqual(lc.aggregate([A, na])["fraction"], 1.0)
        self.assertAlmostEqual(lc.aggregate([A, nr])["fraction"], 0.5)
        self.assertIsNone(lc.aggregate([nr])["fraction"])
        self.assertIsNone(lc.aggregate([na])["fraction"])
        self.assertIsNone(lc.aggregate([nr, na])["fraction"])
        self.assertEqual(lc.aggregate([U])["fraction"], 0.0)

    def test_conditions_drop_evidence_gap_sentences_and_count_them(self):
        conditions, gaps = lc.derived_conditions([A, B])
        self.assertEqual(
            conditions,
            [("claude-code/F13.resume-continue", "Resume works only inside the same folder.")],
        )
        self.assertEqual(gaps, 1)

    def test_a_sentence_about_which_quotes_name_a_command_is_not_a_product_condition(self):
        c = cell(
            "copilot-cli/F04.auto-review",
            "partial",
            limitation="Approval still asks each time. Quotes name it /permissions assisted (E-x-00001).",
        )
        conditions, gaps = lc.derived_conditions([c])
        self.assertEqual([s for _cid, s in conditions], ["Approval still asks each time."])
        self.assertEqual(gaps, 1)

    def test_concept_cells_follow_the_concept_row_order(self):
        concept = {"rows": ["F13.resume-continue", "F13.checkpoint-rewind", "F13.missing"]}
        got = lc.concept_cells({"claude-code": [A, B]}, "claude-code", concept)
        self.assertEqual([c["row"] for c in got], ["F13.resume-continue", "F13.checkpoint-rewind"])


class LayTests(unittest.TestCase):
    def test_a_clean_plain_line_passes(self):
        line = "It saves a snapshot of your files before each change, so you can rewind a bad edit."
        self.assertEqual(lc.lay_problems(line, GLOSSARY), [])

    def test_code_jargon_and_scaffolding_are_rejected(self):
        cases = {
            "It uses `foo` to snapshot.": "backtick",
            "Run the --rewind option to snapshot.": "code-like token",
            "Set max_turns to limit it.": "code-like token",
            "Edit AGENTS.md to change it.": "code-like token",
            "Type /rewind to undo it.": "code-like token",
            "It reads a YAML file to snapshot.": "jargon",
            "The cited quote says it snapshots.": "scaffolding",
            "It snapshots files": "does not end like a sentence",
            "Too short.": "too short",
        }
        for line, expected in cases.items():
            problems = " | ".join(lc.lay_problems(line, GLOSSARY))
            self.assertIn(expected, problems, line)

    def test_glossary_words_and_listed_acronyms_are_fine(self):
        self.assertEqual(
            lc.lay_problems(
                "The harness connects other tools through MCP, an open socket.", GLOSSARY
            ),
            [],
        )

    def test_length_limit(self):
        self.assertIn("over 280", " ".join(lc.lay_problems("A " * 150 + "end.", GLOSSARY)))


class TechnicalTests(unittest.TestCase):
    def test_names_and_numbers_must_come_from_the_cells(self):
        cells = [A]
        self.assertEqual(lc.technical_problems("Checkpoints keep up to 100 snapshots.", cells), [])
        problems = lc.technical_problems("Set `max_snapshots` to 250.", cells)
        self.assertTrue(any("max_snapshots" in p for p in problems))
        self.assertTrue(any("250" in p for p in problems))

    def test_a_flag_with_an_equals_sign_matches_its_name(self):
        cells = [cell("F18.effort-values", value="The --effort flag takes low, medium or high.")]
        self.assertEqual(lc.technical_problems("--effort=high sets it.", cells), [])

    def test_absence_claims_need_support(self):
        text = "It does not have a nesting limit."
        self.assertIn("absence claim", " ".join(lc.wording_problems(text, [U])))
        self.assertEqual(
            lc.wording_problems("The documentation does not mention a nesting limit.", [U]), []
        )
        vendor = cell(
            "F17.model-picker",
            "not-exposed",
            value="There is no model picker; Cursor manages selection.",
        )
        self.assertEqual(
            lc.wording_problems("The vendor says there is no model picker.", [vendor]), []
        )

    def test_quantifiers_need_support(self):
        self.assertIn(
            "quantifier", " ".join(lc.wording_problems("It always snapshots every file.", [A]))
        )
        everything = cell("F01.tool-inventory", value="All built-in tools load upfront.")
        self.assertEqual(lc.wording_problems("All built-in tools load upfront.", [everything]), [])

    def test_a_contraction_in_the_cells_counts_as_a_negation(self):
        vendor = cell("F20.deprecation-policy", "partial", value="Cursor doesn't publish how long.")
        self.assertEqual(
            lc.wording_problems("The vendor does not publish how long.", [vendor]), []
        )

    def test_invented_negation_is_caught(self):
        self.assertIn(
            "negation", " ".join(lc.wording_problems("It cannot rewind shell changes.", [A]))
        )


class LineTests(unittest.TestCase):
    def entry(self, **over):
        cells = [A, B]
        base = {
            "plain": "It snapshots your files before each prompt so you can rewind. Resuming works only inside the same folder.",
            "technical": "Checkpoints snapshot file edits before each prompt; rewind restores them; limit is 100 snapshots. Resume works only inside the same folder.",
            "cells_sha": lc.cells_sha(cells),
        }
        base.update(over)
        return base, cells

    def test_a_good_line_has_no_problems(self):
        entry, cells = self.entry()
        self.assertEqual(lc.line_problems(entry, cells, GLOSSARY), [])

    def test_a_stale_hash_is_caught(self):
        entry, cells = self.entry(cells_sha="0" * 64)
        self.assertIn("cells_sha", " ".join(lc.line_problems(entry, cells, GLOSSARY)))

    def test_a_dropped_limitation_is_caught(self):
        entry, cells = self.entry(
            plain="It snapshots your files before each prompt so you can rewind or resume a session.",
            technical="Checkpoints snapshot file edits; rewind restores them; limit is 100 snapshots; resume reopens a session by id.",
        )
        self.assertIn("left no trace", " ".join(lc.line_problems(entry, cells, GLOSSARY)))

    def test_an_order_note_must_name_a_cited_cell_and_quote_it(self):
        note = {
            "text": "Rewind restores them.",
            "cell": "claude-code/F13.checkpoint-rewind",
            "quote": "Rewind restores them.",
        }
        entry, cells = self.entry(order_note=note)
        self.assertEqual(lc.line_problems(entry, cells, GLOSSARY), [])
        for bad in (
            {"text": "x", "cell": "claude-code/F99.none", "quote": "y"},
            {
                "text": "x",
                "cell": "claude-code/F13.checkpoint-rewind",
                "quote": "not in the cell at all",
            },
        ):
            entry, cells = self.entry(order_note=bad)
            self.assertTrue(lc.line_problems(entry, cells, GLOSSARY))


def mini_data(root, life, lines=None, trees=None):
    base = Path(root) / "data"
    (base / "cells").mkdir(parents=True)
    for name in ("facets.json", "surfaces.json"):
        shutil.copy(DATA_DIR / name, base / name)
    for sid_file in (DATA_DIR / "cells").glob("*.json"):
        shutil.copy(sid_file, base / "cells" / sid_file.name)
    dump_json(base / "lifecycle.json", life)
    if lines is not None:
        dump_json(base / "lifecycle-lines.json", lines)
    if trees is not None:
        dump_json(base / "trees.json", trees)
    return base


def messages(findings):
    return " || ".join(f"{w}: {m}" for _lvl, _rule, w, m in findings)


class SkeletonTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.life = load_json(DATA_DIR / "lifecycle.json")

    n = 0

    def check(self, life):
        SkeletonTests.n += 1
        return vl.check(mini_data(Path(self._tmp.name) / str(SkeletonTests.n), life))

    def test_the_real_skeleton_has_no_findings(self):
        self.assertEqual(vl.check(DATA_DIR), [])

    def test_every_row_is_mapped_exactly_once(self):
        life = copy.deepcopy(self.life)
        row = life["concepts"][0]["rows"][0]
        life["concepts"][1]["rows"].append(row)
        self.assertIn(f"row {row} is also mapped", messages(self.check(life)))
        life = copy.deepcopy(self.life)
        life["concepts"][0]["rows"].pop(0)
        self.assertIn(
            "neither mapped to a concept nor listed as uncovered", messages(self.check(life))
        )

    def test_unknown_references_are_errors(self):
        life = copy.deepcopy(self.life)
        life["concepts"][0]["rows"].append("F99.nope")
        life["concepts"][1]["depends_on"] = ["ghost"]
        life["concepts"][2]["stage"] = "Z"
        text = messages(self.check(life))
        self.assertIn("unknown row F99.nope", text)
        self.assertIn("unknown concept 'ghost'", text)
        self.assertIn("unknown stage 'Z'", text)

    def test_uncovered_rows_need_a_closed_reason_and_stay_under_the_cap(self):
        life = copy.deepcopy(self.life)
        row = life["concepts"][0]["rows"].pop(0)
        life["uncovered"] = [{"row": row, "reason": "because"}]
        self.assertIn("bad uncovered entry", messages(self.check(life)))
        life["uncovered"] = [{"row": row, "reason": "packaging"}]
        self.assertNotIn("neither mapped", messages(self.check(life)))
        many = []
        for concept in life["concepts"][:6]:
            while concept["rows"] and len(many) < 25:
                many.append({"row": concept["rows"].pop(), "reason": "packaging"})
        life["uncovered"] = many
        self.assertIn("is over 15%", messages(self.check(life)))

    def test_gap_concepts_have_no_rows_and_only_they_do(self):
        # No step is fully unresearched in the shipped data any more, so make one both ways.
        life = copy.deepcopy(self.life)
        life["concepts"][0]["gap"] = "full"
        self.assertIn("no rows exactly when its gap is 'full'", messages(self.check(life)))
        life = copy.deepcopy(self.life)
        life["concepts"][0]["rows"] = []
        self.assertIn("no rows exactly when its gap is 'full'", messages(self.check(life)))

    def test_general_text_must_not_carry_code_and_must_fit(self):
        life = copy.deepcopy(self.life)
        life["concepts"][0]["what_it_does"] = "Run `foo --bar` now."
        life["concepts"][1]["matters_for_model_choice"] = "x" * 300
        text = messages(self.check(life))
        self.assertIn("contains code-like text", text)
        self.assertIn("matters_for_model_choice is empty or over 250", text)

    def test_jargon_must_be_in_the_glossary_and_orders_must_run_one_to_n(self):
        life = copy.deepcopy(self.life)
        life["concepts"][0]["jargon"] = ["nonsense"]
        life["concepts"][1]["order"] = 7
        text = messages(self.check(life))
        self.assertIn("no glossary entry", text)
        self.assertIn("order must run 1..", text)


class LinesAndTreesTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup) if hasattr(self, "tmp") else None
        self.life = load_json(DATA_DIR / "lifecycle.json")
        self.cells = {
            c["row"]: c for c in load_json(DATA_DIR / "cells" / "claude-code.json")["cells"]
        }
        self.n = 0

    def tearDown(self):
        self._tmp.cleanup()

    def data(self, lines=None, trees=None):
        self.n += 1
        return mini_data(Path(self._tmp.name) / str(self.n), self.life, lines, trees)

    def test_missing_unknown_and_gap_lines_are_errors(self):
        text = messages(vl.check(self.data(lines={"agents": {"claude-code": {"nonsense": {}}}})))
        self.assertIn("missing line", text)
        self.assertIn("line for an unknown concept", text)
        self.assertIn("no lines for this agent", text)
        life = copy.deepcopy(self.life)
        gap = life["concepts"][0]
        gap["rows"], gap["gap"] = [], "full"
        self.n += 1
        base = mini_data(
            Path(self._tmp.name) / str(self.n),
            life,
            {"agents": {"claude-code": {gap["id"]: {"plain": "x"}}}},
        )
        text = messages(vl.check(base))
        self.assertIn("a gap concept (no rows) must not have an authored line", text)

    def test_a_stale_or_ungrounded_line_is_reported_against_its_cells(self):
        concept = next(c for c in self.life["concepts"] if c["id"] == "undo-point")
        entry = {
            "plain": "It saves a snapshot of your files before it changes them.",
            "technical": "Use `--made-up-flag` to rewind 999 steps.",
            "cells_sha": "0" * 64,
        }
        text = messages(
            vl.check(self.data(lines={"agents": {"claude-code": {concept["id"]: entry}}}))
        )
        self.assertIn("lifecycle-lines.json claude-code/undo-point", text)
        self.assertIn("token not in the cited cells", text)
        self.assertIn("cells_sha does not match", text)

    def test_trees_need_verbatim_distinct_clauses_and_at_least_two_branches(self):
        cell = next(c for c in self.cells.values() if c.get("value") and len(c["value"]) > 80)
        clause = cell["value"][:40]
        good = {
            "id": "dp1",
            "cell": cell["id"],
            "question": "What happens in each case?",
            "branches": [
                {"answer": "Case one", "outcome": "One thing happens.", "clause": clause},
                {
                    "answer": "Case two",
                    "outcome": "Another thing happens.",
                    "clause": cell["value"][40:90],
                },
            ],
        }
        self.assertEqual(
            [
                m
                for m in vl.check(
                    self.data(trees={"agents": {"claude-code": {"decision_points": [good]}}})
                )
                if "trees.json" in m[2]
            ],
            [],
        )
        bad = copy.deepcopy(good)
        bad["branches"][1]["clause"] = "words that are not in the cell at all, invented"
        text = messages(
            vl.check(self.data(trees={"agents": {"claude-code": {"decision_points": [bad]}}}))
        )
        self.assertIn("not a verbatim stretch", text)
        bad = copy.deepcopy(good)
        bad["branches"] = bad["branches"][:1]
        self.assertIn(
            "fewer than 2 branches",
            messages(
                vl.check(self.data(trees={"agents": {"claude-code": {"decision_points": [bad]}}}))
            ),
        )
        bad = copy.deepcopy(good)
        bad["branches"][1]["clause"] = bad["branches"][0]["clause"]
        self.assertIn(
            "same clause",
            messages(
                vl.check(self.data(trees={"agents": {"claude-code": {"decision_points": [bad]}}}))
            ),
        )
        bad = copy.deepcopy(good)
        bad["cell"] = "claude-code/F99.none"
        self.assertIn(
            "unknown cell",
            messages(
                vl.check(self.data(trees={"agents": {"claude-code": {"decision_points": [bad]}}}))
            ),
        )

    def test_zero_decision_points_is_a_valid_answer(self):
        text = messages(
            vl.check(self.data(trees={"agents": {"claude-code": {"decision_points": []}}}))
        )
        self.assertNotIn("trees.json", text)

    def test_lines_without_a_skeleton_are_an_error(self):
        base = Path(self._tmp.name) / "orphan" / "data"
        base.mkdir(parents=True)
        dump_json(base / "lifecycle-lines.json", {"agents": {}})
        self.assertIn("missing, but lines or trees exist", messages(vl.check(base)))

    def test_no_lifecycle_files_means_nothing_to_check(self):
        base = Path(self._tmp.name) / "empty" / "data"
        base.mkdir(parents=True)
        self.assertEqual(vl.check(base), [])


if __name__ == "__main__":
    unittest.main()
