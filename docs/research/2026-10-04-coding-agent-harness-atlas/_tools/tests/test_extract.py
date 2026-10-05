import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ["ATLAS_TEST_ALLOW_ANY_TREE"] = "1"
TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import extract  # noqa: E402
from extract import build_plan, classify_result, lever_hits, split_ids  # noqa: E402

LEVER_TEXT = "The model and the reasoning effort set the permission and sandbox mode."
PLAIN_TEXT = "A page about colours and fonts with nothing of interest to scouts."


def chunk(cid, size=1000, page="p"):
    return {"id": cid, "page_id": page, "bytes": size}


class LeverTests(unittest.TestCase):
    def test_hits_count_whole_words_case_insensitively(self):
        self.assertGreaterEqual(lever_hits(LEVER_TEXT), 5)
        self.assertEqual(lever_hits("models and permissions"), 0)
        self.assertEqual(lever_hits("Plan Mode and YOLO"), 2)


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.rows = {
            "claude-code": [chunk("c#1"), chunk("c#2"), chunk("c#3", 40000), chunk("c#4", 40000)],
            "cursor": [chunk("u#1"), chunk("u#2")],
        }
        self.texts = {
            "c#1": LEVER_TEXT,
            "c#2": PLAIN_TEXT,
            "c#3": PLAIN_TEXT,
            "c#4": LEVER_TEXT * 4,
            "u#1": LEVER_TEXT,
            "u#2": PLAIN_TEXT,
        }

    def test_lever_batches_come_first_and_never_mix_columns(self):
        plan = build_plan(self.rows, self.texts, batch_bytes=48000, wave_size=16)
        order = [b["id"] for b in plan["batches"]]
        self.assertEqual(
            [b["lever"] for b in plan["batches"]], sorted(b["lever"] for b in plan["batches"])[::-1]
        )
        for batch in plan["batches"]:
            surfaces = {c.split("#")[0] for c in batch["chunks"]}
            self.assertEqual(len(surfaces), 1, order)
        self.assertEqual(sum(len(b["chunks"]) for b in plan["batches"]), 6)

    def test_batches_respect_the_byte_limit_and_waves_the_wave_size(self):
        plan = build_plan(self.rows, self.texts, batch_bytes=48000, wave_size=2)
        self.assertTrue(all(b["bytes"] <= 48000 for b in plan["batches"]))
        self.assertTrue(all(len(w["batches"]) <= 2 for w in plan["waves"]))
        flat = [i for w in plan["waves"] for i in w["batches"]]
        self.assertEqual(sorted(flat), sorted(b["id"] for b in plan["batches"]))

    def test_the_densest_lever_batch_of_a_column_goes_first(self):
        rows = {"claude-code": [chunk("c#1"), chunk("c#2", 47000), chunk("c#3")]}
        texts = {"c#1": LEVER_TEXT, "c#2": LEVER_TEXT, "c#3": LEVER_TEXT * 6}
        plan = build_plan(rows, texts, batch_bytes=48000)
        self.assertGreater(len(plan["batches"]), 1)
        densities = [b["lever_density"] for b in plan["batches"] if b["lever"]]
        self.assertEqual(densities, sorted(densities, reverse=True))

    def test_columns_alternate_inside_a_wave(self):
        rows = {s: [chunk(f"{s}#1")] for s in ("claude-code", "codex-cli", "cursor")}
        texts = {f"{s}#1": LEVER_TEXT for s in rows}
        plan = build_plan(rows, texts)
        self.assertEqual(
            [b["surface"] for b in plan["batches"]], ["claude-code", "codex-cli", "cursor"]
        )


class RuleTests(unittest.TestCase):
    def test_a_batch_at_the_cap_or_unparseable_or_missing_is_split(self):
        self.assertEqual(classify_result([0] * 89, None, 90), ("capped", "split"))
        self.assertEqual(classify_result([0] * 40, None, 90), ("ok", None))
        self.assertEqual(classify_result(None, None, 90), ("missing", "split"))
        self.assertEqual(classify_result(None, "bad json", 90), ("malformed", "split"))

    def test_split_ids_halves_and_refuses_one_chunk(self):
        self.assertEqual(split_ids(["a", "b", "c"]), (["a"], ["b", "c"]))
        self.assertIsNone(split_ids(["a"]))


class CliTests(unittest.TestCase):
    PAGE = (
        "Intro.\n"
        + "\n".join(f"Line {i} says the model effort is set by a flag." for i in range(1, 6))
        + "\n"
    )

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.run_dir = Path(self._tmp.name) / "a" / "b" / "run"
        for surface in extract.SURFACES:
            (self.run_dir / "corpus" / surface).mkdir(parents=True)
            (self.run_dir / "corpus" / surface / "chunks.json").write_text("[]")
        base = self.run_dir / "corpus" / "claude-code"
        (base / "chunks").mkdir()
        raw = self.run_dir / "raw-p.md"
        raw.write_text(self.PAGE, encoding="utf-8")
        rows, ids = [], []
        for n in range(1, 5):
            path = base / "chunks" / f"{n}.txt"
            path.write_text(
                f"Line {n} says the model effort is set by a flag. " * 4, encoding="utf-8"
            )
            ids.append(f"p#{n}")
            rows.append(
                {"id": f"p#{n}", "page_id": "p", "path": str(path), "product": "Claude Code",
                 "start_line": n, "end_line": n, "bytes": path.stat().st_size}
            )  # fmt: skip
        (base / "chunks.json").write_text(json.dumps(rows))
        spec = {
            "p": {
                "raw_path": str(raw), "surface": "claude-code", "tier": "E1", "url": "https://x.example/p",
                "url_effective": "https://x.example/p", "retrieved": "2026-10-05", "http_status": 200,
                "sha256": "0" * 64, "bytes": raw.stat().st_size, "product_version": None, "version_source": None,
            }
        }  # fmt: skip
        (base / "pages-spec.json").write_text(json.dumps(spec))
        self.cli("plan", "--run-dir", str(self.run_dir), "--batch-bytes", "400", "--cap", "4")
        self.plan = json.loads((self.run_dir / "extract" / "plan.json").read_text())

    def cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = extract.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def write_out(self, batch_id, records):
        path = self.run_dir / "extract" / "out" / f"{batch_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"batch_id": batch_id, "records": records, "pages_no_facts": []})
        )

    def record(self, quote="Line 1 says the model effort is set by a flag."):
        return {
            "page_id": "p",
            "chunk_id": "p#1",
            "rows": ["F17.model-flag-env"],
            "claim": "c",
            "quote": quote,
        }

    def test_brief_writes_the_brief_and_one_combined_file_naming_the_cap(self):
        batch = self.plan["batches"][0]
        code, out, _e = self.cli("brief", "--run-dir", str(self.run_dir), "--batches", batch["id"])
        self.assertEqual(code, 0)
        brief = Path(out.strip()).read_text(encoding="utf-8")
        self.assertIn("At most 4 records", brief)
        combined = self.run_dir / "extract" / "batches" / f"{batch['id']}.txt"
        self.assertIn("[[[CHUNK id=p#1", combined.read_text(encoding="utf-8"))

    def test_collect_verifies_quotes_and_records_the_outcome(self):
        batch = self.plan["batches"][0]
        self.write_out(
            batch["id"], [self.record(), self.record("this quote is not on the page at all")]
        )
        code, out, _e = self.cli(
            "collect", "--run-dir", str(self.run_dir), "--batches", batch["id"]
        )
        self.assertEqual(code, 0)
        summary = json.loads(out.strip().splitlines()[0])
        self.assertEqual((summary["status"], summary["records"], summary["verified"]), ("ok", 2, 1))
        self.assertEqual(summary["queued"], [])
        verified = json.loads(
            (self.run_dir / "extract" / "verified" / f"{batch['id']}.json").read_text()
        )
        self.assertEqual(len(verified["evidence"]), 1)

    def test_a_batch_at_the_cap_is_split_and_the_halves_are_queued_as_a_new_wave(self):
        multi = next(b for b in self.plan["batches"] if len(b["chunks"]) > 1)
        self.write_out(multi["id"], [self.record() for _ in range(4)])
        code, out, _e = self.cli(
            "collect", "--run-dir", str(self.run_dir), "--batches", multi["id"]
        )
        self.assertEqual(code, 0)
        summary = json.loads(out.strip().splitlines()[0])
        self.assertEqual(summary["status"], "capped")
        self.assertEqual(summary["queued"], [f"{multi['id']}a", f"{multi['id']}b"])
        plan = json.loads((self.run_dir / "extract" / "plan.json").read_text())
        self.assertEqual(plan["waves"][-1]["batches"], summary["queued"])
        child = next(b for b in plan["batches"] if b["id"] == f"{multi['id']}a")
        self.assertEqual(child["parent"], multi["id"])

    def test_a_missing_or_malformed_output_is_split_and_a_single_chunk_is_accepted(self):
        multi = next(b for b in self.plan["batches"] if len(b["chunks"]) > 1)
        _c, out, _e = self.cli("collect", "--run-dir", str(self.run_dir), "--batches", multi["id"])
        self.assertEqual(json.loads(out.strip().splitlines()[0])["status"], "missing")
        path = self.run_dir / "extract" / "out" / "single.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        plan = json.loads((self.run_dir / "extract" / "plan.json").read_text())
        plan["batches"].append(
            {
                "id": "single",
                "surface": "claude-code",
                "lever": True,
                "chunks": ["p#1"],
                "bytes": 10,
            }
        )
        (self.run_dir / "extract" / "plan.json").write_text(json.dumps(plan))
        path.write_text("{not json")
        _c, out, _e = self.cli("collect", "--run-dir", str(self.run_dir), "--batches", "single")
        summary = json.loads(out.strip().splitlines()[0])
        self.assertEqual((summary["status"], summary["queued"]), ("malformed", []))
        self.assertIn("single chunk", summary["note"])

    def test_status_counts_collected_and_pending_batches(self):
        batch = self.plan["batches"][0]
        self.write_out(batch["id"], [self.record()])
        self.cli("collect", "--run-dir", str(self.run_dir), "--batches", batch["id"])
        code, out, _e = self.cli("status", "--run-dir", str(self.run_dir))
        self.assertEqual(code, 0)
        self.assertIn("collected 1", out)
        self.assertIn("next pending", out)

    def test_an_unknown_batch_is_exit_2(self):
        code, _o, err = self.cli("collect", "--run-dir", str(self.run_dir), "--batches", "nope")
        self.assertEqual(code, 2)
        self.assertIn("nope", err)

    def test_selftest_prints_ok(self):
        code, out, _e = self.cli("--selftest")
        self.assertEqual((code, out), (0, "OK\n"))


if __name__ == "__main__":
    unittest.main()
