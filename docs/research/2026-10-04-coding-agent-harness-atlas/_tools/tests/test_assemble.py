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

import assemble  # noqa: E402
from assemble import candidates, cell_stats, normalize_rows, rank_ids  # noqa: E402

FACETS = {
    "facets": [
        {
            "id": "F01",
            "rows": [
                {"id": "F01.a", "slice": "P5"},
                {"id": "F01.b", "slice": "P5"},
                {"id": "F01.c", "slice": None},
            ],
        }
    ],
    "optional_facets": [{"id": "O1", "rows": []}],
    "unmapped": {"id": "U00"},
}


def item(quote, url=None, rows=("F01.a",), tier="E1", surface="cursor", local_id=None, **extra):
    """One batch entry: the evidence fields and the scout's fields for it."""
    return {
        "quote": quote,
        "url": url or f"https://x.example/page-{quote.replace(' ', '-')}",
        "rows": list(rows) if not isinstance(rows, str) else rows,
        "tier": tier,
        "surface": surface,
        "local_id": local_id,
        **extra,
    }


class AssembleCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.run_dir = self.root / "run"
        (self.run_dir / "extract" / "verified").mkdir(parents=True)
        (self.run_dir / "extract" / "out").mkdir(parents=True)
        self.facets_path = self.root / "facets.json"
        self.facets_path.write_text(json.dumps(FACETS))
        self.out = self.run_dir / "assembled"

    def add_batch(self, batch, items, record_order=None):
        """Write verified/<batch>.json and out/<batch>.json. ``record_order[i]`` is the index in
        out/ of the scout record for item i (default: the same position)."""
        order = record_order or list(range(len(items)))
        scouts = [None] * len(items)
        evidence, pairs = [], []
        counters = {}
        for position, spec in enumerate(items):
            surface = spec["surface"]
            counters[surface] = counters.get(surface, 0) + 1
            local_id = spec["local_id"] or f"E-{surface}-{counters[surface]:05d}"
            ev = {
                "id": local_id,
                "surface": surface,
                "tier": spec["tier"],
                "url": spec["url"],
                "url_effective": spec.get("url_effective", spec["url"]),
                "retrieved": "2026-10-04",
                "http_status": 200,
                "sha256": "0" * 64,
                "locator": {"heading": "h", "raw_line_start": 1, "raw_line_end": 1},
                "quote": spec["quote"],
                "context_before": [],
                "context_after": [],
                "quote_verified": True,
            }
            if "described_span" in spec:
                ev["described_span"] = spec["described_span"]
            evidence.append(ev)
            pairs.append({"evidence_id": local_id, "record_index": order[position]})
            # default: one page per url; page_id=None / chunk_id=None leaves the key out
            page_id = spec["page_id"] if "page_id" in spec else f"page-{spec['url']}"
            chunk_id = spec["chunk_id"] if "chunk_id" in spec else page_id and f"{page_id}#1"
            scout = {
                "rows": spec["rows"],
                "claim": spec.get("claim", f"claim of {batch} {local_id}"),
                "quote": spec["quote"],
            }
            if page_id is not None:
                scout["page_id"] = page_id
            if chunk_id is not None:
                scout["chunk_id"] = chunk_id
            scouts[order[position]] = scout
        verified = {"batch": batch, "evidence": evidence, "pairs": pairs, "dropped": []}
        base = self.run_dir / "extract"
        (base / "verified" / f"{batch}.json").write_text(json.dumps(verified))
        (base / "out" / f"{batch}.json").write_text(
            json.dumps({"batch_id": batch, "records": scouts, "pages_no_facts": []})
        )

    def cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = assemble.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def args(self, out=None):
        return [
            "--run-dir",
            str(self.run_dir),
            "--facets",
            str(self.facets_path),
            "--out",
            str(out or self.out),
        ]

    def build(self, out=None):
        code, _o, err = self.cli(*self.args(out))
        self.assertEqual((code, err), (0, ""))

    def check(self, out=None):
        return self.cli(*self.args(out), "--check")

    def load(self, *parts, out=None):
        return json.loads(Path(out or self.out, *parts).read_text(encoding="utf-8"))

    def evidence(self, surface="cursor"):
        return self.load("evidence", f"{surface}.json")

    def buckets(self, surface="cursor"):
        return self.load("buckets", f"{surface}.json")

    def write_json(self, parts, obj):
        Path(self.out, *parts).write_text(json.dumps(obj), encoding="utf-8")


class GlobalIdTests(AssembleCase):
    def test_the_same_local_id_in_two_batches_gets_two_global_ids_and_stays_traceable(self):
        self.add_batch("B-1", [item("first quote", local_id="E-cursor-00001")])
        self.add_batch("B-2", [item("second quote", local_id="E-cursor-00001")])
        self.build()
        records = self.evidence()
        self.assertEqual([r["id"] for r in records], ["E-cursor-00001", "E-cursor-00002"])
        self.assertEqual(
            [(r["source_batch"], r["source_id"], r["quote"]) for r in records],
            [
                ("B-1", "E-cursor-00001", "first quote"),
                ("B-2", "E-cursor-00001", "second quote"),
            ],
        )
        self.assertEqual(
            [r["claim"] for r in records],
            ["claim of B-1 E-cursor-00001", "claim of B-2 E-cursor-00001"],
        )

    def test_the_scout_record_is_found_through_record_index_not_position(self):
        self.add_batch(
            "B-1",
            [
                item("alpha quote", rows=["F01.a"], claim="about alpha"),
                item("beta quote", rows=["F01.b"], claim="about beta"),
            ],
            record_order=[1, 0],
        )
        self.build()
        by_quote = {r["quote"]: r for r in self.evidence()}
        self.assertEqual(
            (by_quote["alpha quote"]["claim"], by_quote["alpha quote"]["rows"]),
            ("about alpha", ["F01.a"]),
        )
        self.assertEqual(
            (by_quote["beta quote"]["claim"], by_quote["beta quote"]["rows"]),
            ("about beta", ["F01.b"]),
        )

    def test_batches_run_in_sorted_id_order_and_a_batch_in_file_order(self):
        self.add_batch("X-2", [item("x two a"), item("x two b")])
        self.add_batch("L-1", [item("l one a"), item("l one b")])
        self.build()
        self.assertEqual(
            [(r["id"], r["source_batch"], r["quote"]) for r in self.evidence()],
            [
                ("E-cursor-00001", "L-1", "l one a"),
                ("E-cursor-00002", "L-1", "l one b"),
                ("E-cursor-00003", "X-2", "x two a"),
                ("E-cursor-00004", "X-2", "x two b"),
            ],
        )

    def test_ids_are_numbered_per_surface_and_original_fields_survive(self):
        self.add_batch(
            "B-1",
            [item("cursor quote"), item("grok quote", surface="grok-bot")],
        )
        self.build()
        self.assertEqual(self.evidence("cursor")[0]["id"], "E-cursor-00001")
        grok = self.evidence("grok-bot")[0]
        self.assertEqual(grok["id"], "E-grok-bot-00001")
        for field in ("tier", "url", "url_effective", "sha256", "locator", "retrieved"):
            self.assertIn(field, grok)

    def test_an_evidence_record_without_a_pair_is_exit_2(self):
        self.add_batch("B-1", [item("one quote")])
        path = self.run_dir / "extract" / "verified" / "B-1.json"
        data = json.loads(path.read_text())
        data["pairs"] = []
        path.write_text(json.dumps(data))
        code, _o, err = self.cli(*self.args())
        self.assertEqual(code, 2)
        self.assertIn("has no pair", err)

    def test_a_pair_pointing_outside_the_scout_records_is_exit_2(self):
        self.add_batch("B-1", [item("one quote")])
        path = self.run_dir / "extract" / "verified" / "B-1.json"
        data = json.loads(path.read_text())
        data["pairs"][0]["record_index"] = 5
        path.write_text(json.dumps(data))
        code, _o, err = self.cli(*self.args())
        self.assertEqual(code, 2)
        self.assertIn("pairs with record 5", err)

    def test_a_batch_with_no_evidence_needs_no_scout_file(self):
        self.add_batch("B-1", [item("one quote")])
        (self.run_dir / "extract" / "verified" / "B-0.json").write_text(
            json.dumps({"batch": "B-0", "evidence": [], "pairs": [], "dropped": []})
        )
        self.build()
        self.assertEqual(len(self.evidence()), 1)


class PageIdTests(AssembleCase):
    def test_page_id_and_chunk_id_survive_into_the_evidence_from_the_paired_scout_record(self):
        self.add_batch(
            "B-1",
            [
                item("alpha quote", page_id="PA", chunk_id="PA#3"),
                item("beta quote", page_id="PB", chunk_id="PB#7"),
            ],
            record_order=[1, 0],
        )
        self.build()
        self.assertEqual(
            [(r["quote"], r["page_id"], r["chunk_id"]) for r in self.evidence()],
            [("alpha quote", "PA", "PA#3"), ("beta quote", "PB", "PB#7")],
        )

    def test_a_merged_duplicate_keeps_the_first_occurrences_page_id_and_chunk_id(self):
        url = "https://x.example/shared"
        self.add_batch("B-1", [item("shared quote", url=url, page_id="P1", chunk_id="P1#1")])
        self.add_batch("B-2", [item("shared quote", url=url, page_id="P2", chunk_id="P2#9")])
        self.build()
        (record,) = self.evidence()
        self.assertEqual(
            (record["page_id"], record["chunk_id"], record["duplicates"]), ("P1", "P1#1", 1)
        )

    def test_records_with_one_url_but_different_page_ids_are_still_different_records(self):
        url = "https://x.example/llms.txt"
        self.add_batch(
            "B-1",
            [item("one quote", url=url, page_id="P1"), item("two quote", url=url, page_id="P2")],
        )
        self.build()
        self.assertEqual([r["page_id"] for r in self.evidence()], ["P1", "P2"])

    def test_a_scout_record_without_page_or_chunk_id_writes_null(self):
        self.add_batch("B-1", [item("one quote", page_id=None, chunk_id=None)])
        self.build()
        (record,) = self.evidence()
        self.assertEqual((record["page_id"], record["chunk_id"]), (None, None))
        self.assertEqual(self.check()[0], 0)


class DedupeTests(AssembleCase):
    def test_the_same_url_and_quote_in_two_batches_is_one_record_with_the_rows_unioned(self):
        url = "https://x.example/shared"
        self.add_batch("B-1", [item("shared quote", url=url, rows=["F01.b"])])
        self.add_batch("B-2", [item("shared quote", url=url, rows=["F01.a", "F01.c"])])
        self.build()
        records = self.evidence()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["duplicates"], 1)
        self.assertEqual(records[0]["rows"], ["F01.a", "F01.b", "F01.c"])
        self.assertEqual(
            (records[0]["source_batch"], records[0]["source_id"]), ("B-1", "E-cursor-00001")
        )
        buckets = self.buckets()["rows"]
        self.assertEqual(
            [buckets[r] for r in ("F01.a", "F01.b", "F01.c")], [["E-cursor-00001"]] * 3
        )
        total = self.load("report.json")["total"]
        self.assertEqual((total["records_in"], total["records_after_dedupe"]), (2, 1))

    def test_a_different_quote_url_or_surface_is_not_a_duplicate(self):
        url = "https://x.example/p"
        self.add_batch(
            "B-1",
            [
                item("same quote", url=url),
                item("same quote", url="https://x.example/other"),
                item("another quote", url=url),
                item("same quote", url=url, surface="grok-bot"),
            ],
        )
        self.build()
        self.assertEqual(len(self.evidence("cursor")), 3)
        self.assertEqual(len(self.evidence("grok-bot")), 1)

    def test_the_effective_url_decides_when_there_is_one(self):
        self.add_batch(
            "B-1",
            [
                item(
                    "moved quote",
                    url="https://x.example/old",
                    url_effective="https://x.example/new",
                ),
                item(
                    "moved quote",
                    url="https://x.example/older",
                    url_effective="https://x.example/new",
                ),
            ],
        )
        self.build()
        self.assertEqual(len(self.evidence()), 1)

    def test_two_different_described_spans_on_one_page_are_not_duplicates(self):
        url = "https://x.example/install"

        def span(digit):
            return {
                "description": "install command",
                "raw_line_start": 1,
                "raw_line_end": 1,
                "span_sha256": digit * 64,
            }

        self.add_batch(
            "B-1",
            [
                item("", url=url, described_span=span("1")),
                item("", url=url, described_span=span("2")),
                item("", url=url, described_span=span("1")),
            ],
        )
        self.build()
        records = self.evidence()
        self.assertEqual(len(records), 2)
        self.assertEqual([r["duplicates"] for r in records], [1, 0])


class RowTests(AssembleCase):
    def test_an_unknown_row_id_is_counted_and_filed_in_no_bucket(self):
        self.add_batch(
            "B-1",
            [
                item("mixed quote", rows=["F01.a", "F09.gone"]),
                item("only bad quote", rows=["F09.gone"]),
            ],
        )
        self.build()
        buckets = self.buckets()
        self.assertEqual(buckets["unknown_rows"], {"F09.gone": 2})
        self.assertEqual(buckets["rows"]["F01.a"], ["E-cursor-00001"])
        self.assertNotIn("F09.gone", buckets["rows"])
        filed = {i for ids in buckets["rows"].values() for i in ids}
        self.assertEqual(filed, {"E-cursor-00001"})
        self.assertEqual(len(self.evidence()), 2)  # the record itself is kept
        report = self.load("report.json")
        self.assertEqual(report["surfaces"]["cursor"]["unknown_row_ids"], {"F09.gone": 2})
        self.assertEqual(report["total"]["unknown_row_ids"], {"F09.gone": 2})
        self.assertEqual(report["total"]["records_in_no_bucket"], 1)

    def test_u00_records_are_kept_and_counted(self):
        self.add_batch("B-1", [item("unmapped quote", rows=["U00"]), item("mapped quote")])
        self.build()
        self.assertEqual(self.buckets()["rows"]["U00"], ["E-cursor-00001"])
        self.assertEqual(self.buckets()["unknown_rows"], {})
        report = self.load("report.json")
        self.assertEqual(report["surfaces"]["cursor"]["u00_count"], 1)
        self.assertEqual(report["total"]["u00_count"], 1)

    def test_every_facet_row_and_u00_is_present_even_when_empty(self):
        self.add_batch("B-1", [item("one quote")])
        self.build()
        self.assertEqual(
            self.buckets()["rows"],
            {"F01.a": ["E-cursor-00001"], "F01.b": [], "F01.c": [], "U00": []},
        )

    def test_rows_may_be_a_string_and_are_deduplicated_and_sorted(self):
        self.assertEqual(normalize_rows("F01.b, F01.a F01.b"), ["F01.a", "F01.b"])
        self.assertEqual(normalize_rows(["F01.b", " F01.a ", "F01.b", ""]), ["F01.a", "F01.b"])
        self.assertEqual(normalize_rows(None), [])
        self.add_batch("B-1", [item("string rows quote", rows="F01.c")])
        self.build()
        self.assertEqual(self.buckets()["rows"]["F01.c"], ["E-cursor-00001"])


class RankingTests(AssembleCase):
    def test_ranking_puts_e1_before_e3_and_round_robins_across_urls(self):
        a, b, c = (f"https://x.example/{name}" for name in "abc")
        self.add_batch(
            "B-1",
            [
                item("e3 on a", url=a, tier="E3"),  # 00001, first in record order
                item("a1", url=a),  # 00002
                item("a2", url=a),  # 00003
                item("a3", url=a),  # 00004
                item("b1", url=b),  # 00005
                item("b2", url=b),  # 00006
                item("c1", url=c),  # 00007
            ],
        )
        self.build()
        ranked = self.buckets()["rows"]["F01.a"]
        ids = [f"E-cursor-{n:05d}" for n in (2, 5, 7, 3, 6, 4, 1)]
        self.assertEqual(ranked, ids)
        by_id = {r["id"]: r for r in self.evidence()}
        self.assertEqual(candidates(self.buckets(), by_id, "F01.a", 3), ids[:3])
        self.assertEqual(
            len({by_id[i]["url"] for i in candidates(self.buckets(), by_id, "F01.a", 3)}), 3
        )

    def test_round_robin_spreads_across_page_ids_when_every_record_shares_one_url(self):
        url = "https://x.example/llms.txt"
        self.add_batch(
            "B-1",
            [
                item("p1 a", url=url, page_id="P1"),  # 00001
                item("p1 b", url=url, page_id="P1"),  # 00002
                item("p1 c", url=url, page_id="P1"),  # 00003
                item("p2 a", url=url, page_id="P2"),  # 00004
                item("p2 b", url=url, page_id="P2"),  # 00005
                item("p3 a", url=url, page_id="P3"),  # 00006
            ],
        )
        self.build()
        by_id = {r["id"]: r for r in self.evidence()}
        self.assertEqual({r["url"] for r in by_id.values()}, {url})
        ids = [f"E-cursor-{n:05d}" for n in (1, 4, 6, 2, 5, 3)]
        self.assertEqual(self.buckets()["rows"]["F01.a"], ids)
        top = candidates(self.buckets(), by_id, "F01.a", 3)
        self.assertEqual([by_id[i]["page_id"] for i in top], ["P1", "P2", "P3"])

    def test_ranking_falls_back_to_the_url_when_there_is_no_page_id(self):
        a, b = "https://x.example/a", "https://x.example/b"
        self.add_batch(
            "B-1",
            [
                item("a1", url=a, page_id=None),  # 00001
                item("a2", url=a, page_id=None),  # 00002
                item("b1", url=b, page_id=None),  # 00003
            ],
        )
        self.build()
        self.assertEqual(self.buckets()["rows"]["F01.a"], [f"E-cursor-{n:05d}" for n in (1, 3, 2)])
        self.assertEqual([r["page_id"] for r in self.evidence()], [None, None, None])

    def test_a_page_id_is_never_taken_for_an_equal_url_string(self):
        records = {
            "1": {"tier": "E1", "url": "https://x/z", "page_id": "https://x/1"},
            "2": {"tier": "E1", "url": "https://x/z", "page_id": "https://x/1"},
            "3": {"tier": "E1", "url": "https://x/1"},
        }
        self.assertEqual(rank_ids(["1", "2", "3"], records), ["1", "3", "2"])

    def test_other_tiers_rank_after_e4_and_unknown_tiers_last(self):
        records = {
            "1": {"tier": "S", "url": "https://x/1"},
            "2": {"tier": "E4", "url": "https://x/2"},
            "3": {"tier": "ZZ", "url": "https://x/3"},
            "4": {"tier": "E2", "url": "https://x/4"},
            "5": {"tier": "R", "url": "https://x/5"},
            "6": {"tier": "E1", "url": "https://x/6"},
            "7": {"tier": "E3", "url": "https://x/7"},
        }
        self.assertEqual(rank_ids(list(records), records), ["6", "4", "7", "2", "5", "1", "3"])

    def test_candidates_take_n_from_the_top_and_refuse_a_row_or_id_it_does_not_have(self):
        self.add_batch("B-1", [item("one quote"), item("two quote")])
        self.build()
        buckets = self.buckets()
        by_id = {r["id"]: r for r in self.evidence()}
        self.assertEqual(candidates(buckets, by_id, "F01.a", 1), ["E-cursor-00001"])
        self.assertEqual(len(candidates(buckets, by_id, "F01.a", 99)), 2)
        self.assertEqual(candidates(buckets, by_id, "F01.a", 0), [])
        self.assertEqual(candidates(buckets, by_id, "F01.c", 5), [])
        with self.assertRaises(KeyError):
            candidates(buckets, by_id, "F01.typo", 5)
        with self.assertRaises(KeyError):
            candidates(buckets, {}, "F01.a", 1)


class ReportTests(AssembleCase):
    def setUp(self):
        super().setUp()
        self.add_batch(
            "C-1",
            [
                item("c one", rows=["F01.a"]),
                item("c two", rows=["F01.a"]),
                item("c three", rows=["F01.a"]),
                item("c four", rows=["F01.c"]),
                item("c five", rows=["U00"]),
            ],
        )
        self.add_batch(
            "G-1",
            [
                item("g one", rows=["F01.a"], surface="grok-bot"),
                item("g two", rows=["F01.b"], surface="grok-bot"),
            ],
        )
        self.build()
        self.report = self.load("report.json")

    def test_counts_per_surface_and_in_total(self):
        cursor = self.report["surfaces"]["cursor"]
        self.assertEqual((cursor["records_in"], cursor["records_after_dedupe"]), (5, 5))
        self.assertEqual((cursor["distinct_urls"], cursor["distinct_page_ids"]), (5, 5))
        self.assertEqual(cursor["row_counts"], {"F01.a": 3, "F01.b": 0, "F01.c": 1, "U00": 1})
        self.assertEqual(cursor["rows_with_zero_records"], ["F01.b"])
        grok = self.report["surfaces"]["grok-bot"]
        self.assertEqual(grok["rows_with_zero_records"], ["F01.c", "U00"])
        total = self.report["total"]
        self.assertEqual((total["records_in"], total["records_after_dedupe"]), (7, 7))
        self.assertEqual(total["row_counts"], {"F01.a": 4, "F01.b": 1, "F01.c": 1, "U00": 1})
        self.assertEqual(total["rows_with_zero_records"], [])
        self.assertEqual((total["distinct_urls"], total["distinct_page_ids"]), (7, 7))

    def test_the_lever_slice_counts_cells_of_the_p5_rows_only(self):
        lever = self.report["lever_slice"]
        self.assertEqual((lever["slice"], lever["rows"]), ("P5", ["F01.a", "F01.b"]))
        self.assertEqual(
            lever["total"],
            {
                "cells": 4,
                "empty_cells": 1,
                "populated_cells": 3,
                "median_records": 1,
                "p90_records": 3,
                "max_records": 3,
                "median_page_ids": 1,
            },
        )
        self.assertEqual(
            lever["by_surface"]["cursor"],
            {
                "cells": 2,
                "empty_cells": 1,
                "populated_cells": 1,
                "median_records": 3,
                "p90_records": 3,
                "max_records": 3,
                "median_page_ids": 3,
            },
        )

    def test_cell_stats_use_nearest_rank_and_survive_no_populated_cell(self):
        stats = cell_stats([0, 1, 2, 3, 10], [0, 1, 1, 2, 5])
        self.assertEqual(
            (stats["cells"], stats["empty_cells"], stats["populated_cells"]), (5, 1, 4)
        )
        self.assertEqual(
            (stats["median_records"], stats["p90_records"], stats["max_records"]), (2.5, 10, 10)
        )
        self.assertEqual(stats["median_page_ids"], 1.5)  # over the populated cells: 1, 1, 2, 5
        nothing = cell_stats([0, 0], [0, 0])
        self.assertEqual(
            (
                nothing["median_records"],
                nothing["p90_records"],
                nothing["max_records"],
                nothing["median_page_ids"],
            ),
            (None, None, None, None),
        )


class PageSpreadReportTests(AssembleCase):
    def setUp(self):
        super().setUp()
        url = "https://x.example/llms.txt"
        self.add_batch(
            "C-1",
            [
                item("c1", url=url, rows=["F01.a"], page_id="P1"),
                item("c2", url=url, rows=["F01.a"], page_id="P1"),
                item("c3", url=url, rows=["F01.a"], page_id="P2"),
                item("c4", url=url, rows=["F01.b"], page_id="P3"),
                item("c5", url=url, rows=["F01.b"], page_id="P3"),
            ],
        )
        self.add_batch(
            "G-1",
            [  # F01.a has no record on this surface: an empty cell, not a cell of zero pages
                item("g1", url=url, rows=["F01.b"], page_id="Q1", surface="grok-bot"),
                item("g2", url=url, rows=["F01.b"], page_id="Q2", surface="grok-bot"),
                item("g3", url=url, rows=["F01.b"], page_id="Q3", surface="grok-bot"),
                item("g4", url=url, rows=["F01.b"], page_id=None, surface="grok-bot"),
            ],
        )
        self.build()
        self.report = self.load("report.json")

    def test_distinct_page_ids_per_surface_and_in_total(self):
        surfaces = self.report["surfaces"]
        self.assertEqual(
            [(surfaces[s]["distinct_urls"], surfaces[s]["distinct_page_ids"]) for s in surfaces],
            [(1, 3), (1, 3)],  # a record without a page_id adds no page id
        )
        self.assertEqual(self.report["total"]["distinct_page_ids"], 6)

    def test_the_lever_slice_reports_the_median_page_ids_of_populated_cells_only(self):
        lever = self.report["lever_slice"]
        # populated cells: cursor F01.a (2 pages), cursor F01.b (1), grok-bot F01.b (3)
        self.assertEqual(lever["total"]["median_page_ids"], 2)
        self.assertEqual(lever["by_surface"]["cursor"]["median_page_ids"], 1.5)
        self.assertEqual(lever["by_surface"]["grok-bot"]["median_page_ids"], 3)
        self.assertEqual(lever["by_surface"]["grok-bot"]["empty_cells"], 1)


class DeterminismTests(AssembleCase):
    def files(self, out):
        return {
            str(p.relative_to(out)): p.read_bytes() for p in sorted(out.rglob("*")) if p.is_file()
        }

    def test_two_runs_write_byte_identical_files(self):
        self.add_batch("B-2", [item("shared quote", url="https://x.example/s", rows=["F01.b"])])
        self.add_batch(
            "B-1",
            [
                item("shared quote", url="https://x.example/s", rows=["F01.a", "F09.gone"]),
                item("é ünïcode quote", rows=["U00"]),
                item("grok quote", surface="grok-bot"),
            ],
        )
        self.build()
        first = self.files(self.out)
        self.build(self.root / "second")
        self.build()  # over the existing output
        self.assertEqual(self.files(self.root / "second"), first)
        self.assertEqual(self.files(self.out), first)
        self.assertEqual(
            sorted(first),
            [
                "buckets/cursor.json",
                "buckets/grok-bot.json",
                "evidence/cursor.json",
                "evidence/grok-bot.json",
                "report.json",
            ],
        )
        for name, data in first.items():
            text = data.decode("utf-8")
            self.assertTrue(text.endswith("}\n") or text.endswith("]\n"), name)
            self.assertNotIn("\r", text, name)
            self.assertNotIn(str(self.root), text, name)
        self.assertIn("é ünïcode quote", first["evidence/cursor.json"].decode("utf-8"))

    def test_a_surface_that_disappears_leaves_no_stale_file(self):
        self.add_batch("B-1", [item("cursor quote"), item("grok quote", surface="grok-bot")])
        self.build()
        (self.run_dir / "extract" / "verified" / "B-1.json").unlink()
        self.add_batch("B-1", [item("cursor quote")])
        self.build()
        self.assertFalse((self.out / "evidence" / "grok-bot.json").exists())
        self.assertFalse((self.out / "buckets" / "grok-bot.json").exists())
        self.assertEqual(self.check()[0], 0)


class CheckTests(AssembleCase):
    def setUp(self):
        super().setUp()
        self.add_batch("B-1", [item("one quote"), item("two quote", rows=["U00"])])
        self.build()

    def assert_check_fails(self, *fragments):
        code, _o, err = self.check()
        self.assertEqual(code, 1, err)
        for fragment in fragments:
            self.assertIn(fragment, err)

    def test_a_clean_build_passes(self):
        code, out, err = self.check()
        self.assertEqual((code, err), (0, ""))
        self.assertIn("check OK", out)

    def test_check_does_not_write_anything(self):
        before = {p: p.read_bytes() for p in self.out.rglob("*") if p.is_file()}
        self.check()
        self.assertEqual({p: p.read_bytes() for p in self.out.rglob("*") if p.is_file()}, before)

    def test_a_planted_bad_id_fails(self):
        records = self.evidence()
        records[1]["id"] = "E-cursor-2"
        self.write_json(("evidence", "cursor.json"), records)
        self.assert_check_fails("E-cursor-2", "does not match")

    def test_a_duplicate_id_fails(self):
        records = self.evidence()
        records[1]["id"] = records[0]["id"]
        self.write_json(("evidence", "cursor.json"), records)
        self.assert_check_fails("E-cursor-00001", "twice")

    def test_a_record_that_is_not_quote_verified_fails(self):
        for value in (False, None):
            with self.subTest(value=value):
                records = self.evidence()
                records[0]["quote_verified"] = value
                self.write_json(("evidence", "cursor.json"), records)
                self.assert_check_fails("E-cursor-00001", "quote_verified")

    def test_a_bucket_id_that_is_not_evidence_fails(self):
        buckets = self.buckets()
        buckets["rows"]["F01.a"].append("E-cursor-00099")
        self.write_json(("buckets", "cursor.json"), buckets)
        self.assert_check_fails("E-cursor-00099", "not evidence")

    def test_a_bucket_row_outside_facets_fails(self):
        buckets = self.buckets()
        buckets["rows"]["F09.gone"] = []
        self.write_json(("buckets", "cursor.json"), buckets)
        self.assert_check_fails("F09.gone", "facets.json")

    def test_a_missing_bucket_row_fails(self):
        buckets = self.buckets()
        del buckets["rows"]["F01.c"]
        self.write_json(("buckets", "cursor.json"), buckets)
        self.assert_check_fails("F01.c")

    def test_a_missing_report_fails(self):
        (self.out / "report.json").unlink()
        self.assert_check_fails("report.json")

    def test_an_id_from_another_surface_fails(self):
        records = self.evidence()
        records[0]["id"] = "E-grok-bot-00001"
        self.write_json(("evidence", "cursor.json"), records)
        self.assert_check_fails("E-grok-bot-00001", "cursor")


class CliTests(AssembleCase):
    def test_selftest_prints_ok(self):
        code, out, _e = self.cli("--selftest")
        self.assertEqual((code, out), (0, "OK\n"))

    def test_an_empty_run_dir_is_exit_2(self):
        code, _o, err = self.cli(*self.args())
        self.assertEqual(code, 2)
        self.assertIn("no verified batches", err)

    def test_the_default_output_is_assembled_under_the_run_dir(self):
        self.add_batch("B-1", [item("one quote")])
        code, out, _e = self.cli("--run-dir", str(self.run_dir), "--facets", str(self.facets_path))
        self.assertEqual(code, 0)
        self.assertIn("1 records in, 1 after dedupe", out)
        self.assertTrue((self.run_dir / "assembled" / "report.json").is_file())


if __name__ == "__main__":
    unittest.main()
