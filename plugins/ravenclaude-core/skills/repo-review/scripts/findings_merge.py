#!/usr/bin/env python3
"""Deterministic finding-shard merger for the repo-review skill.

Reads a directory of `<dimension>.<model>.<batch_id>.json` finding-shard files
(each a JSON array of finding objects emitted by a review-agent dispatch),
deduplicates/merges near-identical findings by a stable hash key, tags near
duplicates, applies an optional survivor cap, and writes one merged JSON
report. Pure function of its input files -> byte-identical output on a
re-run against the same commit (same input bytes, same flags). No model
calls, no network.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

SEVERITY_RANK = {"blocking": 0, "major": 1, "minor": 2, "nit": 3}
UNKNOWN_SEVERITY_RANK = len(SEVERITY_RANK)

TOKEN_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]{2,}")

# <dimension>.<model>.<batch_id>.json — batch_id may itself contain dots, so
# dimension and model are the first two dot-separated segments and batch_id
# is everything remaining before the final ".json".
SHARD_NAME_RE = re.compile(r"^(?P<dimension>[^.]+)\.(?P<model>[^.]+)\.(?P<batch_id>.+)\.json$")


# --------------------------------------------------------------------------- #
# Dedup key + shared helpers
# --------------------------------------------------------------------------- #


def title_tokens(title: str) -> list[str]:
    return sorted(set(TOKEN_RE.findall((title or "").lower())))


def _line_bucket(line) -> int:
    try:
        return int(line) // 5
    except (TypeError, ValueError):
        return 0


def compute_key(file: str, line, title: str) -> str:
    tokens = title_tokens(title)[:6]
    bucket = _line_bucket(line)
    raw = f"{os.path.normpath(file or '')}:{bucket}:{':'.join(tokens)}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def severity_rank(sev) -> int:
    return SEVERITY_RANK.get(sev, UNKNOWN_SEVERITY_RANK)


def parse_shard_filename(name: str):
    m = SHARD_NAME_RE.match(name)
    if not m:
        return None
    return m.group("dimension"), m.group("model"), m.group("batch_id")


# --------------------------------------------------------------------------- #
# Load
# --------------------------------------------------------------------------- #


def load_shards(in_dir: str) -> list[tuple[str, str, str, dict]]:
    """Return (dimension, model, batch_id, finding) tuples in deterministic order."""
    records: list[tuple[str, str, str, dict]] = []
    filenames = sorted(
        f
        for f in os.listdir(in_dir)
        if f.endswith(".json") and os.path.isfile(os.path.join(in_dir, f))
    )
    for fname in filenames:
        parsed = parse_shard_filename(fname)
        if parsed is None:
            # Not a shard-shaped filename — skip rather than guess.
            continue
        dimension, model, batch_id = parsed
        path = os.path.join(in_dir, fname)
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            continue
        for finding in data:
            if isinstance(finding, dict):
                records.append((dimension, model, batch_id, finding))
    return records


# --------------------------------------------------------------------------- #
# Merge
# --------------------------------------------------------------------------- #


def merge_findings(records: list[tuple[str, str, str, dict]]) -> list[dict]:
    groups: dict[str, dict] = {}
    order: list[str] = []

    for dimension, model, _batch_id, finding in records:
        file_ = finding.get("file", "")
        line = finding.get("line", 0)
        title = finding.get("title", "") or ""
        key = compute_key(file_, line, title)

        if key not in groups:
            groups[key] = {
                "id": finding.get("id"),
                "file": file_,
                "line": line,
                "severity": finding.get("severity"),
                "title": title,
                "failure_scenario": finding.get("failure_scenario", "") or "",
                "evidence_quote": finding.get("evidence_quote", "") or "",
                "models": set(),
                "dimensions": set(),
            }
            order.append(key)

        g = groups[key]
        g["models"].add(model)
        g["dimensions"].add(dimension)

        # Keep the HIGHER severity (lower rank number wins).
        cand_sev = finding.get("severity")
        if severity_rank(cand_sev) < severity_rank(g["severity"]):
            g["severity"] = cand_sev

        # Keep the longest evidence_quote / failure_scenario.
        fs = finding.get("failure_scenario", "") or ""
        if len(fs) > len(g["failure_scenario"]):
            g["failure_scenario"] = fs
        eq = finding.get("evidence_quote", "") or ""
        if len(eq) > len(g["evidence_quote"]):
            g["evidence_quote"] = eq
        # title/id: first-seen — never overwritten after initialization.

    survivors: list[dict] = []
    for key in order:
        g = groups[key]
        models_sorted = sorted(g["models"])
        dims_sorted = sorted(g["dimensions"])
        corroboration = "cross-model" if len(models_sorted) > 1 else None
        survivors.append(
            {
                "id": g["id"],
                "file": g["file"],
                "line": g["line"],
                "severity": g["severity"],
                "title": g["title"],
                "failure_scenario": g["failure_scenario"],
                "evidence_quote": g["evidence_quote"],
                "source_models": models_sorted,
                "dimensions": dims_sorted,
                "corroboration": corroboration,
                "near_duplicate": False,
                "near_duplicate_of": None,
            }
        )
    return survivors


# --------------------------------------------------------------------------- #
# Near-duplicate tagging
# --------------------------------------------------------------------------- #


def tag_near_duplicates(survivors: list[dict], policy: str) -> list[dict]:
    """Mutates survivor dicts in place (same objects, so callers see the tags)."""
    judge_candidates: list[dict] = []
    ordered = sorted(survivors, key=lambda s: (s["id"] is None, s["id"] or ""))
    n = len(ordered)

    for i in range(n):
        a = ordered[i]
        a_tokens = set(title_tokens(a["title"]))
        a_bucket = _line_bucket(a["line"])
        for j in range(i + 1, n):
            b = ordered[j]
            if a["file"] != b["file"]:
                continue
            b_bucket = _line_bucket(b["line"])
            if abs(a_bucket - b_bucket) != 1:
                continue
            b_tokens = set(title_tokens(b["title"]))
            if len(a_tokens & b_tokens) < 4:
                continue

            a["near_duplicate"] = True
            b["near_duplicate"] = True
            if a["near_duplicate_of"] is None:
                a["near_duplicate_of"] = b["id"]
            if b["near_duplicate_of"] is None:
                b["near_duplicate_of"] = a["id"]
            if policy == "judge":
                judge_candidates.append({"a": a["id"], "b": b["id"]})

    return judge_candidates


# --------------------------------------------------------------------------- #
# Cap
# --------------------------------------------------------------------------- #


def apply_cap(survivors: list[dict], cap: int) -> tuple[list[dict], list[dict]]:
    ordered = sorted(survivors, key=lambda s: (severity_rank(s["severity"]), s["id"] or ""))
    if cap and cap > 0:
        return ordered[:cap], ordered[cap:]
    return ordered, []


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #


def run_merge(in_dir: str, cap: int, near_dup_policy: str) -> dict:
    records = load_shards(in_dir)
    raw_input_count = len(records)

    survivors = merge_findings(records)
    after_dedup_count = len(survivors)

    judge_candidates = tag_near_duplicates(survivors, near_dup_policy)
    capped_survivors, over_cap = apply_cap(survivors, cap)

    return {
        "schema_version": 1,
        "survivors": capped_survivors,
        "over_cap": over_cap,
        "judge_candidates": judge_candidates,
        "stats": {
            "raw_input_count": raw_input_count,
            "after_dedup_count": after_dedup_count,
            "survivors_count": len(capped_survivors),
            "over_cap_count": len(over_cap),
        },
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="in_dir", default=None, help="directory of shard JSON files")
    parser.add_argument("--out", dest="out_path", default=None, help="write merged JSON here")
    parser.add_argument("--cap", type=int, default=0, help="0 = no cap")
    parser.add_argument(
        "--near-dup-policy",
        choices=["keep-separate", "judge"],
        default="keep-separate",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    if not args.in_dir or not args.out_path:
        parser.error("--in and --out are required unless --self-test is given")

    result = run_merge(args.in_dir, args.cap, args.near_dup_policy)
    text = json.dumps(result, indent=2, sort_keys=True)

    out_path = Path(args.out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text + "\n", encoding="utf-8")
    return 0


# --------------------------------------------------------------------------- #
# Self-test — synthetic finding-shard fixtures, no network, no formal
# audit-gate wiring yet (mirrors the sibling repo_map.py precedent).
# --------------------------------------------------------------------------- #


def _write_json(root: str, rel: str, data) -> str:
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


def _self_test() -> int:
    failures: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        status = "ok" if cond else "FAIL"
        print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        # ------------------------------------------------------------- #
        # Test 1 — cross-model, same-dimension merge -> corroboration
        # ------------------------------------------------------------- #
        t1 = os.path.join(tmp, "t1")
        os.makedirs(t1, exist_ok=True)
        _write_json(
            t1,
            "correctness.sonnet.b01.json",
            [
                {
                    "id": "c-s-1",
                    "file": "app/server.py",
                    "line": 42,
                    "severity": "major",
                    "title": "Null pointer dereference in request handler",
                    "failure_scenario": "Handler crashes on null input.",
                    "evidence_quote": "if req.body is None: raise",
                    "category": "correctness",
                }
            ],
        )
        _write_json(
            t1,
            "correctness.opus.b01.json",
            [
                {
                    "id": "c-o-1",
                    "file": "app/server.py",
                    "line": 44,
                    "severity": "major",
                    "title": "Null pointer dereference in request handler",
                    "failure_scenario": "Server crashes when handler receives a null body under load, causing a 500.",
                    "evidence_quote": "req.body.decode()  # no null check anywhere",
                    "category": "correctness",
                }
            ],
        )
        r1 = run_merge(t1, cap=0, near_dup_policy="keep-separate")
        survivors1 = r1["survivors"]
        check("test1: exactly one survivor", len(survivors1) == 1, str(len(survivors1)))
        if survivors1:
            s = survivors1[0]
            check(
                "test1: source_models == [opus, sonnet]",
                s["source_models"] == ["opus", "sonnet"],
                str(s["source_models"]),
            )
            check(
                "test1: corroboration == cross-model",
                s["corroboration"] == "cross-model",
                str(s["corroboration"]),
            )

        # ------------------------------------------------------------- #
        # Test 2 — same-model, cross-dimension merge -> higher severity kept
        # ------------------------------------------------------------- #
        t2 = os.path.join(tmp, "t2")
        os.makedirs(t2, exist_ok=True)
        _write_json(
            t2,
            "correctness.sonnet.b01.json",
            [
                {
                    "id": "c-1",
                    "file": "lib/auth.py",
                    "line": 100,
                    "severity": "major",
                    "title": "Hardcoded credentials in config loader",
                    "failure_scenario": "Credentials are read from a literal string.",
                    "evidence_quote": "PASSWORD = 'hunter2'",
                    "category": "correctness",
                }
            ],
        )
        _write_json(
            t2,
            "security.sonnet.b01.json",
            [
                {
                    "id": "s-1",
                    "file": "lib/auth.py",
                    "line": 101,
                    "severity": "blocking",
                    "title": "Hardcoded credentials in config loader",
                    "failure_scenario": "A hardcoded credential ships to every deployment and cannot be rotated.",
                    "evidence_quote": "PASSWORD = 'hunter2'  # TODO rotate",
                    "category": "security",
                }
            ],
        )
        r2 = run_merge(t2, cap=0, near_dup_policy="keep-separate")
        survivors2 = r2["survivors"]
        check("test2: exactly one survivor", len(survivors2) == 1, str(len(survivors2)))
        if survivors2:
            s = survivors2[0]
            check(
                "test2: dimensions == [correctness, security]",
                s["dimensions"] == ["correctness", "security"],
                str(s["dimensions"]),
            )
            check("test2: severity == blocking", s["severity"] == "blocking", str(s["severity"]))

        # ------------------------------------------------------------- #
        # Test 3 — near-dup, keep-separate: two survivors, both tagged
        # ------------------------------------------------------------- #
        t3 = os.path.join(tmp, "t3")
        os.makedirs(t3, exist_ok=True)
        _write_json(
            t3,
            "performance.sonnet.b01.json",
            [
                {
                    "id": "nd-1",
                    "file": "db/query.py",
                    "line": 10,
                    "severity": "minor",
                    "title": "SQL injection risk in query builder module",
                    "failure_scenario": "A raw string is concatenated into a query.",
                    "evidence_quote": "f'SELECT * FROM {table}'",
                    "category": "security",
                },
                {
                    "id": "nd-2",
                    "file": "db/query.py",
                    "line": 15,
                    "severity": "minor",
                    "title": "SQL injection risk in query builder module",
                    "failure_scenario": "The same builder is reused for a second unsanitized query.",
                    "evidence_quote": "f'DELETE FROM {table}'",
                    "category": "security",
                },
            ],
        )
        r3 = run_merge(t3, cap=0, near_dup_policy="keep-separate")
        survivors3 = r3["survivors"]
        check("test3: exactly two survivors", len(survivors3) == 2, str(len(survivors3)))
        check(
            "test3: both survivors tagged near_duplicate",
            len(survivors3) == 2 and all(s["near_duplicate"] for s in survivors3),
            str(survivors3),
        )
        check(
            "test3: no judge_candidates under keep-separate",
            r3["judge_candidates"] == [],
            str(r3["judge_candidates"]),
        )

        # ------------------------------------------------------------- #
        # Test 4 — identical fixture under --near-dup-policy judge
        # ------------------------------------------------------------- #
        r4 = run_merge(t3, cap=0, near_dup_policy="judge")
        survivors4 = r4["survivors"]
        check("test4: exactly two survivors", len(survivors4) == 2, str(len(survivors4)))
        check(
            "test4: both survivors tagged near_duplicate",
            len(survivors4) == 2 and all(s["near_duplicate"] for s in survivors4),
            str(survivors4),
        )
        jc = r4["judge_candidates"]
        check("test4: exactly one judge_candidates pair", len(jc) == 1, str(jc))
        if len(jc) == 1 and len(survivors4) == 2:
            ids4 = {s["id"] for s in survivors4}
            pair_ids = {jc[0]["a"], jc[0]["b"]}
            check(
                "test4: judge pair names both survivor ids",
                pair_ids == ids4,
                f"pair={pair_ids} survivors={ids4}",
            )

        # ------------------------------------------------------------- #
        # Test 5 — cap N: nothing silently dropped
        # ------------------------------------------------------------- #
        t5 = os.path.join(tmp, "t5")
        os.makedirs(t5, exist_ok=True)
        cap_findings = [
            {
                "id": f"cap-{i}",
                "file": f"module_{i}.py",
                "line": 10 * i,
                "severity": sev,
                "title": f"Distinct issue number {i} in module {i}",
                "failure_scenario": f"Scenario {i}.",
                "evidence_quote": f"evidence {i}",
                "category": "correctness",
            }
            for i, sev in enumerate(["blocking", "major", "minor", "nit", "major"], start=1)
        ]
        _write_json(t5, "correctness.sonnet.b01.json", cap_findings)
        r5 = run_merge(t5, cap=2, near_dup_policy="keep-separate")
        check("test5: len(survivors) == 2", len(r5["survivors"]) == 2, str(len(r5["survivors"])))
        check("test5: len(over_cap) == 3", len(r5["over_cap"]) == 3, str(len(r5["over_cap"])))
        all_ids_out = {s["id"] for s in r5["survivors"]} | {s["id"] for s in r5["over_cap"]}
        all_ids_in = {f["id"] for f in cap_findings}
        check(
            "test5: union of ids equals all 5 original ids",
            all_ids_out == all_ids_in,
            f"out={all_ids_out} in={all_ids_in}",
        )

        # ------------------------------------------------------------- #
        # Test 6 — determinism: two runs, byte-identical output
        # ------------------------------------------------------------- #
        out_a = os.path.join(tmp, "merged-a.json")
        out_b = os.path.join(tmp, "merged-b.json")
        rc_a = main(["--in", t1, "--out", out_a, "--near-dup-policy", "judge"])
        rc_b = main(["--in", t1, "--out", out_b, "--near-dup-policy", "judge"])
        text_a = Path(out_a).read_text(encoding="utf-8")
        text_b = Path(out_b).read_text(encoding="utf-8")
        check("test6: both CLI runs exit 0", rc_a == 0 and rc_b == 0, f"{rc_a},{rc_b}")
        check("test6: two runs are byte-identical", text_a == text_b)

        # ------------------------------------------------------------- #
        # Test 7 — false-merge guard: unrelated findings stay independent
        # ------------------------------------------------------------- #
        t7 = os.path.join(tmp, "t7")
        os.makedirs(t7, exist_ok=True)
        _write_json(
            t7,
            "correctness.sonnet.b01.json",
            [
                {
                    "id": "u-1",
                    "file": "moduleA.py",
                    "line": 10,
                    "severity": "minor",
                    "title": "Off by one error in loop boundary",
                    "failure_scenario": "Loop reads one element past the end.",
                    "evidence_quote": "for i in range(len(items) + 1):",
                    "category": "correctness",
                },
                {
                    "id": "u-2",
                    "file": "moduleB.py",
                    "line": 12,
                    "severity": "minor",
                    "title": "Off by one error in loop boundary",
                    "failure_scenario": "A second, unrelated loop makes the same mistake.",
                    "evidence_quote": "while i <= len(items):",
                    "category": "correctness",
                },
                {
                    "id": "u-3",
                    "file": "moduleA.py",
                    "line": 400,
                    "severity": "minor",
                    "title": "Off by one error in loop boundary",
                    "failure_scenario": "A third, unrelated loop far away in the same file.",
                    "evidence_quote": "for i in range(len(items) + 1):  # again",
                    "category": "correctness",
                },
            ],
        )
        r7 = run_merge(t7, cap=0, near_dup_policy="keep-separate")
        survivors7 = r7["survivors"]
        check("test7: three independent survivors", len(survivors7) == 3, str(len(survivors7)))
        check(
            "test7: no survivor flagged near_duplicate (different file / distant bucket)",
            not any(s["near_duplicate"] for s in survivors7),
            str(survivors7),
        )

    print(f"\n{'ALL PASS' if not failures else f'{len(failures)} FAILED'}: {len(failures)} failing")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
