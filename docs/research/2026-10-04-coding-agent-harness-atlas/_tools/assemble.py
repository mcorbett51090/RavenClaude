"""Assemble the verified extraction batches into one deduplicated evidence set per surface.

Evidence ids are local to a batch (``E-claude-code-00001`` exists in hundreds of batches), so every
record is keyed on ``(batch, local id)`` and only gets a global id here. Each verified evidence
record is joined to its scout record through ``pairs``, deduplicated within its surface, numbered
``E-<surface>-NNNNN`` and filed under the rows the scouts named. ``rows`` that are not in
``facets.json`` are never filed: they are counted under ``unknown_rows`` and in the report (the
evidence record still lists them, so the scout's wording stays traceable).

Output, all canonical JSON (sorted keys, LF, no timestamps, no absolute paths), so two runs on the
same input are byte-identical:

    assembled/evidence/<surface>.json  evidence records plus rows, claim, page_id, chunk_id,
                                       source_batch, source_id, duplicates
    assembled/buckets/<surface>.json   {"surface", "rows": {row id: ranked global ids},
                                       "unknown_rows": {bad row id: count}}
    assembled/report.json              counts per surface and in total, and the lever slice

``--check`` is a separate, read-only mode: it re-reads the assembled files and exits 1 on the first
inconsistency. ``candidates`` is the entry point the briefing code uses to take the top ids of a row.

Usage: python3 assemble.py --run-dir DIR [--facets FILE] [--out DIR]
       python3 assemble.py --run-dir DIR [--facets FILE] [--out DIR] --check
       python3 assemble.py --selftest
"""

import argparse
import math
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

from atlas_common import DATA_DIR, assert_worktree, dump_json, load_json, run_dir
from quotes import load_scout_json

ID_RE = re.compile(r"^E-([a-z0-9-]+)-([0-9]{5})$")
SURFACE_RE = re.compile(r"^[a-z0-9-]+$")
UNMAPPED_ROW = "U00"
LEVER_SLICE = "P5"
MAX_SEQUENCE = 99999
# Evidence tiers in ranking order; a tier not listed here sorts after all of them, by name.
TIER_ORDER = ("E1", "E2", "E3", "E4", "R", "S", "U")
_ROW_SPLIT = re.compile(r"[\s,;]+")


class AssembleError(Exception):
    """A usage or input problem the CLI reports with exit code 2."""


class CheckError(Exception):
    """An assembled file that is inconsistent; the CLI reports it with exit code 1."""


# ---------------------------------------------------------------------------------------------
# Rows
# ---------------------------------------------------------------------------------------------


def facet_rows(facets):
    """Every row entry in ``facets.json`` (frozen facets, then optional ones)."""
    rows = []
    for key in ("facets", "optional_facets"):
        for facet in facets.get(key) or []:
            rows.extend(facet.get("rows") or [])
    return rows


def all_row_ids(facets):
    """Every row id in ``facets.json``, in file order, then the catch-all ``U00``."""
    ids = []
    for row in facet_rows(facets):
        if row["id"] not in ids:
            ids.append(row["id"])
    if UNMAPPED_ROW not in ids:
        ids.append(UNMAPPED_ROW)
    return ids


def lever_row_ids(facets):
    return sorted(r["id"] for r in facet_rows(facets) if r.get("slice") == LEVER_SLICE)


def normalize_rows(value):
    """A scout's ``rows`` (a list of ids, or one string) as a sorted list of distinct ids."""
    if value is None:
        return []
    parts = _ROW_SPLIT.split(value) if isinstance(value, str) else [str(x) for x in value]
    return sorted({p.strip() for p in parts if p and p.strip()})


# ---------------------------------------------------------------------------------------------
# Load, dedupe, number
# ---------------------------------------------------------------------------------------------


def _scout_records(path):
    data, _repaired = load_scout_json(path.read_text(encoding="utf-8"))
    records = data["records"] if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise AssembleError(f"{path.name}: no records list")
    return records


def load_records(run_directory):
    """Every verified evidence record joined to its scout record.

    Batches come in sorted batch-id order and, inside a batch, in file order, so the result (and
    every global id derived from it) is deterministic. The join is ``pairs`` -> ``record_index``
    into the batch's own ``out/<batch>.json``; the local evidence id is never a key on its own.
    """
    base = Path(run_directory) / "extract"
    verified_dir, out_dir = base / "verified", base / "out"
    batches = sorted(p.stem for p in verified_dir.glob("*.json"))
    if not batches:
        raise AssembleError(f"no verified batches under {verified_dir}")
    records = []
    for batch in batches:
        verified = load_json(verified_dir / f"{batch}.json")
        if verified.get("batch", batch) != batch:
            raise AssembleError(f"{batch}: file names a different batch {verified['batch']!r}")
        evidence = verified.get("evidence") or []
        if not evidence:
            continue
        index_of = {}
        for pair in verified.get("pairs") or []:
            index_of[pair["evidence_id"]] = pair["record_index"]
        scouts = _scout_records(out_dir / f"{batch}.json")
        seen = set()
        for ev in evidence:
            local_id = ev["id"]
            if local_id in seen:
                raise AssembleError(f"{batch}: evidence id {local_id} appears twice in the batch")
            seen.add(local_id)
            index = index_of.get(local_id)
            if index is None:
                raise AssembleError(f"{batch}: evidence {local_id} has no pair")
            if not isinstance(index, int) or not 0 <= index < len(scouts):
                raise AssembleError(f"{batch}: evidence {local_id} pairs with record {index!r}")
            if not SURFACE_RE.match(ev["surface"]):
                raise AssembleError(f"{batch}: surface {ev['surface']!r} cannot form an id")
            scout = scouts[index]
            records.append(
                {
                    "batch": batch,
                    "evidence": ev,
                    "rows": normalize_rows(scout.get("rows")),
                    "claim": scout.get("claim", ""),
                    "page_id": scout.get("page_id"),
                    "chunk_id": scout.get("chunk_id"),
                }
            )
    return records


def page_url(record):
    return record.get("url_effective") or record["url"]


def dedupe_key(ev):
    """``(surface, page url, quote)``. A described span has an empty quote, so its span hash joins
    the key: two different install commands on one page are not duplicates of each other."""
    span = (ev.get("described_span") or {}).get("span_sha256", "")
    return (ev["surface"], page_url(ev), ev["quote"], span)


def assemble_records(records):
    """``(evidence_by_surface, records_in)``: deduplicated, numbered evidence per surface.

    The first occurrence is kept; its ``rows`` become the sorted union over all duplicates and
    ``duplicates`` counts the records folded into it. ``source_batch``, ``source_id``, ``page_id``
    and ``chunk_id`` are the first occurrence's (a scout record without a page or chunk id gives
    ``null``).
    """
    kept = {}
    by_surface = {}
    records_in = Counter()
    for rec in records:
        ev = rec["evidence"]
        surface = ev["surface"]
        records_in[surface] += 1
        key = dedupe_key(ev)
        first = kept.get(key)
        if first is not None:
            first["duplicates"] += 1
            first["rows"].update(rec["rows"])
            continue
        items = by_surface.setdefault(surface, [])
        number = len(items) + 1
        if number > MAX_SEQUENCE:
            raise AssembleError(f"{surface}: more than {MAX_SEQUENCE} evidence records")
        item = dict(ev)
        item.update(
            id=f"E-{surface}-{number:05d}",
            rows=set(rec["rows"]),
            claim=rec["claim"],
            page_id=rec.get("page_id"),
            chunk_id=rec.get("chunk_id"),
            source_batch=rec["batch"],
            source_id=ev["id"],
            duplicates=0,
        )
        kept[key] = item
        items.append(item)
    for items in by_surface.values():
        for item in items:
            item["rows"] = sorted(item["rows"])
    return by_surface, records_in


# ---------------------------------------------------------------------------------------------
# Buckets and ranking
# ---------------------------------------------------------------------------------------------


def _tier_sort_key(tier):
    return (TIER_ORDER.index(tier), "") if tier in TIER_ORDER else (len(TIER_ORDER), str(tier))


def diversity_key(record):
    """The page a record comes from, for spreading a ranking: its ``page_id``, else its url.

    One url can hold many pages (a vendor's single ``llms.txt`` split into 97 corpus pages), so the
    page id is the finer key; the tag keeps a page id and a url from ever being taken as equal.
    """
    if record.get("page_id"):
        return ("page", record["page_id"])
    return ("url", page_url(record))


def _round_robin(ids, evidence_by_id):
    """``ids`` interleaved one per distinct page at a time; inside a page, the given order."""
    lanes = {}
    for item_id in ids:
        lanes.setdefault(diversity_key(evidence_by_id[item_id]), []).append(item_id)
    lanes = list(lanes.values())
    ranked, depth = [], 0
    while lanes:
        ranked.extend(lane[depth] for lane in lanes)
        depth += 1
        lanes = [lane for lane in lanes if len(lane) > depth]
    return ranked


def rank_ids(ids, evidence_by_id):
    """Evidence ids ranked best first: tier E1, E2, E3, E4 (then R, S, U, anything else), and
    inside a tier round-robin across distinct pages (``page_id``, else url) so the first N ids span
    as many pages as possible. Ids on one page keep their incoming (record) order."""
    by_tier = {}
    for item_id in ids:
        by_tier.setdefault(evidence_by_id[item_id]["tier"], []).append(item_id)
    ranked = []
    for tier in sorted(by_tier, key=_tier_sort_key):
        ranked.extend(_round_robin(by_tier[tier], evidence_by_id))
    return ranked


def build_buckets(surface, evidence, row_list):
    """One surface's buckets: every row in ``row_list`` present (empty when nothing names it),
    each a ranked id list. A row id outside ``row_list`` is counted, never filed."""
    by_id = {item["id"]: item for item in evidence}
    members = {row: [] for row in row_list}
    unknown = Counter()
    for item in evidence:
        for row in item["rows"]:
            if row in members:
                members[row].append(item["id"])
            else:
                unknown[row] += 1
    return {
        "surface": surface,
        "rows": {row: rank_ids(ids, by_id) for row, ids in members.items()},
        "unknown_rows": dict(sorted(unknown.items())),
    }


def candidates(surface_buckets, evidence_by_id, row, n):
    """The top ``n`` ranked evidence ids for ``row`` on one surface.

    ``surface_buckets`` is a ``buckets/<surface>.json`` object and ``evidence_by_id`` maps that
    surface's global ids to their records. An empty row gives ``[]``; a row the buckets do not have
    (a typo, or a stale facets file) raises ``KeyError`` rather than looking like an empty row, and
    so does an id the evidence does not have.
    """
    rows = surface_buckets["rows"]
    if row not in rows:
        raise KeyError(f"{surface_buckets.get('surface')}: no bucket for row {row!r}")
    top = rows[row][: max(n, 0)]
    for item_id in top:
        if item_id not in evidence_by_id:
            raise KeyError(f"{item_id} is in the {row} bucket but not in the evidence")
    return top


# ---------------------------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------------------------


def _percentile(sorted_values, fraction):
    """Nearest-rank percentile of a non-empty ascending list."""
    return sorted_values[max(math.ceil(fraction * len(sorted_values)), 1) - 1]


def cell_stats(counts, page_counts):
    """Stats for a set of (surface, row) cells given each cell's record count and its number of
    distinct page ids (``page_counts[i]`` belongs to ``counts[i]``)."""
    populated = sorted(c for c in counts if c > 0)
    pages = [p for c, p in zip(counts, page_counts) if c > 0]
    return {
        "cells": len(counts),
        "empty_cells": len(counts) - len(populated),
        "populated_cells": len(populated),
        "median_records": statistics.median(populated) if populated else None,
        "p90_records": _percentile(populated, 0.9) if populated else None,
        "max_records": populated[-1] if populated else None,
        "median_page_ids": statistics.median(pages) if pages else None,
    }


def _page_ids(records):
    """The distinct, non-empty ``page_id`` values among ``records``."""
    return {r["page_id"] for r in records if r.get("page_id")}


def build_report(evidence, buckets, records_in, row_list, lever_rows):
    surfaces = {}
    total_rows = Counter()
    total_unknown = Counter()
    total_urls = set()
    total_pages = set()
    lever_pages = {}
    for surface in sorted(evidence):
        items = evidence[surface]
        rows = buckets[surface]["rows"]
        counts = {row: len(ids) for row, ids in rows.items()}
        urls = {page_url(item) for item in items}
        pages = _page_ids(items)
        by_id = {item["id"]: item for item in items}
        lever_pages[surface] = [len(_page_ids(by_id[i] for i in rows[row])) for row in lever_rows]
        total_rows.update(counts)
        total_unknown.update(buckets[surface]["unknown_rows"])
        total_urls |= urls
        total_pages |= pages
        surfaces[surface] = {
            "records_in": records_in[surface],
            "records_after_dedupe": len(items),
            "distinct_urls": len(urls),
            "distinct_page_ids": len(pages),
            "rows_with_zero_records": sorted(row for row, n in counts.items() if n == 0),
            "row_counts": counts,
            "unknown_row_ids": dict(buckets[surface]["unknown_rows"]),
            "u00_count": counts.get(UNMAPPED_ROW, 0),
            "records_in_no_bucket": sum(1 for i in items if not any(r in rows for r in i["rows"])),
        }
    lever_cells = {
        s: [report["row_counts"][row] for row in lever_rows] for s, report in surfaces.items()
    }
    return {
        "surfaces": surfaces,
        "total": {
            "records_in": sum(s["records_in"] for s in surfaces.values()),
            "records_after_dedupe": sum(s["records_after_dedupe"] for s in surfaces.values()),
            "distinct_urls": len(total_urls),
            "distinct_page_ids": len(total_pages),
            "rows_with_zero_records": sorted(row for row in row_list if total_rows[row] == 0),
            "row_counts": {row: total_rows[row] for row in row_list},
            "unknown_row_ids": dict(sorted(total_unknown.items())),
            "u00_count": total_rows[UNMAPPED_ROW],
            "records_in_no_bucket": sum(s["records_in_no_bucket"] for s in surfaces.values()),
        },
        "lever_slice": {
            "slice": LEVER_SLICE,
            "rows": lever_rows,
            "total": cell_stats(
                [n for counts in lever_cells.values() for n in counts],
                [n for pages in lever_pages.values() for n in pages],
            ),
            "by_surface": {
                s: cell_stats(counts, lever_pages[s]) for s, counts in lever_cells.items()
            },
        },
    }


# ---------------------------------------------------------------------------------------------
# Write and check
# ---------------------------------------------------------------------------------------------


def assemble_all(records, facets):
    """``(evidence, buckets, report)`` from joined records and the loaded ``facets.json``."""
    row_list = all_row_ids(facets)
    evidence, records_in = assemble_records(records)
    buckets = {s: build_buckets(s, items, row_list) for s, items in evidence.items()}
    report = build_report(evidence, buckets, records_in, row_list, lever_row_ids(facets))
    return evidence, buckets, report


def write_assembled(out_dir, evidence, buckets, report):
    out = Path(out_dir)
    for surface in sorted(evidence):
        dump_json(out / "evidence" / f"{surface}.json", evidence[surface])
        dump_json(out / "buckets" / f"{surface}.json", buckets[surface])
    dump_json(out / "report.json", report)
    for sub in ("evidence", "buckets"):  # a surface that no longer exists leaves no stale file
        for stale in sorted((out / sub).glob("*.json")):
            if stale.stem not in evidence:
                stale.unlink()


def check_assembled(out_dir, facets):
    """Re-read ``out_dir`` and raise ``CheckError`` on the first inconsistency.

    Returns ``(surfaces, evidence records)`` checked.
    """
    out = Path(out_dir)
    valid_rows = set(all_row_ids(facets))
    if not (out / "report.json").is_file():
        raise CheckError(f"{out / 'report.json'} is missing")
    evidence_files = {p.stem: p for p in (out / "evidence").glob("*.json")}
    bucket_files = {p.stem: p for p in (out / "buckets").glob("*.json")}
    if not evidence_files:
        raise CheckError(f"no evidence files under {out / 'evidence'}")
    if set(evidence_files) != set(bucket_files):
        raise CheckError(
            "evidence and bucket files cover different surfaces: "
            f"{sorted(set(evidence_files) ^ set(bucket_files))}"
        )
    total = 0
    for surface in sorted(evidence_files):
        name = f"evidence/{surface}.json"
        records = load_json(evidence_files[surface])
        if not isinstance(records, list):
            raise CheckError(f"{name}: not a list of records")
        ids = set()
        for rec in records:
            item_id = rec.get("id")
            match = ID_RE.match(item_id) if isinstance(item_id, str) else None
            if not match:
                raise CheckError(f"{name}: id {item_id!r} does not match E-<surface>-NNNNN")
            if match.group(1) != surface or rec.get("surface") != surface:
                raise CheckError(f"{name}: {item_id} does not belong to surface {surface}")
            if item_id in ids:
                raise CheckError(f"{name}: id {item_id} appears twice")
            ids.add(item_id)
            if rec.get("quote_verified") is not True:
                raise CheckError(
                    f"{name}: {item_id} has quote_verified {rec.get('quote_verified')!r}"
                )
        total += len(records)
        bname = f"buckets/{surface}.json"
        rows = load_json(bucket_files[surface]).get("rows")
        if not isinstance(rows, dict):
            raise CheckError(f"{bname}: no rows object")
        for row, bucket in rows.items():
            if row not in valid_rows:
                raise CheckError(f"{bname}: bucket row {row!r} is not in facets.json or U00")
            if len(set(bucket)) != len(bucket):
                raise CheckError(f"{bname}: row {row} lists an id twice")
            for item_id in bucket:
                if item_id not in ids:
                    raise CheckError(f"{bname}: row {row} names {item_id}, which is not evidence")
        missing = sorted(valid_rows - set(rows))
        if missing:
            raise CheckError(f"{bname}: rows missing from the buckets: {missing[:5]}")
    return len(evidence_files), total


# ---------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------


def _selftest():
    def rec(batch, local_id, url, quote, rows, tier="E1"):
        ev = {
            "id": local_id,
            "surface": "cursor",
            "tier": tier,
            "url": url,
            "url_effective": url,
            "quote": quote,
            "quote_verified": True,
        }
        return {"batch": batch, "evidence": ev, "rows": rows, "claim": "c"}

    facets = {"facets": [{"rows": [{"id": "F01.a", "slice": "P5"}, {"id": "F01.b"}]}]}
    records = [
        rec("A-1", "E-cursor-00001", "https://x.example/1", "one", ["F01.a"], "E3"),
        rec("B-1", "E-cursor-00001", "https://x.example/2", "two", ["F01.a", "F09.gone"]),
        rec("B-2", "E-cursor-00002", "https://x.example/1", "one", ["F01.b"], "E3"),
    ]
    evidence, buckets, report = assemble_all(records, facets)
    items = evidence["cursor"]
    if [i["id"] for i in items] != ["E-cursor-00001", "E-cursor-00002"]:
        raise AssertionError(f"unexpected ids {[i['id'] for i in items]}")
    if (items[0]["rows"], items[0]["duplicates"]) != (["F01.a", "F01.b"], 1):
        raise AssertionError("dedupe did not merge the duplicate")
    if buckets["cursor"]["rows"]["F01.a"] != ["E-cursor-00002", "E-cursor-00001"]:
        raise AssertionError("E1 must rank before E3")
    if buckets["cursor"]["unknown_rows"] != {"F09.gone": 1}:
        raise AssertionError("unknown row not reported")
    if report["total"]["records_in"] != 3 or report["total"]["records_after_dedupe"] != 2:
        raise AssertionError("report totals")
    print("OK")


def main(argv=None):
    assert_worktree()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--run-dir", help="the run directory (or set ATLAS_RUN_DIR)")
    parser.add_argument("--facets", default=str(DATA_DIR / "facets.json"))
    parser.add_argument("--out", help="output directory (default: <run-dir>/assembled)")
    parser.add_argument("--check", action="store_true", help="verify --out instead of writing it")
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    try:
        out_dir = Path(args.out) if args.out else run_dir(args.run_dir) / "assembled"
        facets = load_json(args.facets)
        if args.check:
            surfaces, records = check_assembled(out_dir, facets)
            print(f"assemble: check OK, {surfaces} surfaces, {records} evidence records")
            return 0
        evidence, buckets, report = assemble_all(load_records(run_dir(args.run_dir)), facets)
        write_assembled(out_dir, evidence, buckets, report)
        total = report["total"]
        print(
            f"assemble: {total['records_in']} records in, {total['records_after_dedupe']} after "
            f"dedupe, {len(evidence)} surfaces, {len(total['unknown_row_ids'])} unknown row ids"
        )
        return 0
    except CheckError as exc:
        print(f"assemble: check failed: {exc}", file=sys.stderr)
        return 1
    except (AssembleError, OSError, KeyError, ValueError) as exc:
        print(f"assemble: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
