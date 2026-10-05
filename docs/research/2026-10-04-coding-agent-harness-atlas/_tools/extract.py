"""Plan, collect and re-queue the extraction waves.

``plan`` cuts every column's chunks into batches of about 48 KB that never mix columns,
puts the chunks that carry lever content (model, effort, mode, permission, sandbox, parallelism)
first, and groups batches into waves of at most 16 dispatches. ``collect`` verifies each finished
batch's quotes against the raw pages and records the outcome; a batch that came back unparseable,
missing or at the record cap is split in two and queued again, so a capped batch never loses facts
silently. Nothing here dispatches: the Team Lead dispatches a wave, waits for every completion
notice, then collects those batch ids.

``brief --cap N`` writes the record cap into the brief and remembers it on the batch, so ``collect``
judges the batch by the cap its scout was told; ``clone`` copies batches under ``K-`` ids to test a
different cap without touching the originals' evidence (a clone is never split).

Usage: python3 extract.py plan --run-dir DIR [--batch-bytes N] [--cap N] [--wave-size N]
       python3 extract.py brief --run-dir DIR --batches ID [ID ...] [--cap N]
       python3 extract.py clone --run-dir DIR --batches ID [ID ...] --cap N
       python3 extract.py collect --run-dir DIR --batches ID [ID ...]
       python3 extract.py status --run-dir DIR
       python3 extract.py --selftest
"""

import argparse
import json
import math
import re
import sys
from chunk import make_batches
from pathlib import Path
from types import SimpleNamespace

from atlas_common import Ledger, assert_worktree, dump_json, load_json
from briefs import DEFAULT_CAP, combine_chunks, make_brief
from quotes import load_scout_json, verify_batch

SURFACES = (
    "claude-code",
    "codex-cli",
    "copilot-cli",
    "copilot-vscode",
    "cursor",
    "gemini-cli",
    "grok-build",
    "grok-bot",
)
BATCH_BYTES = 48000
WAVE_SIZE = 16
LEVER_MIN_HITS = 4
LEVER_RE = re.compile(
    r"\b(model|effort|reasoning|thinking|permission|sandbox|approval|autonom\w*|parallel|"
    r"subagent|sub-agent|worktree|context window|compact\w*|router|yolo|bypass|"
    r"auto[- ]?(?:run|review|mode|approve)|plan mode)\b",
    re.IGNORECASE,
)


class ExtractError(Exception):
    """A usage or input problem the CLI reports with exit code 2."""


def lever_hits(text):
    return len(LEVER_RE.findall(text))


def split_ids(ids):
    """Two halves of a batch's chunk ids; a single chunk cannot be split."""
    if len(ids) < 2:
        return None
    middle = len(ids) // 2
    return ids[:middle], ids[middle:]


def build_plan(
    chunks_by_surface, texts, batch_bytes=BATCH_BYTES, cap=DEFAULT_CAP, wave_size=WAVE_SIZE
):
    """Batches and waves from per-surface chunk lists.

    ``chunks_by_surface`` maps a surface to its chunk rows (id, page_id, bytes, ...); ``texts``
    maps a chunk id to its text, used only to score lever content.
    """
    batches = []
    for surface in SURFACES:
        rows = chunks_by_surface.get(surface, [])
        lever = [r for r in rows if lever_hits(texts[r["id"]]) >= LEVER_MIN_HITS]
        lever_ids = {r["id"] for r in lever}
        rest = [r for r in rows if r["id"] not in lever_ids]
        for kind, group in (("L", lever), ("X", rest)):
            objs = [SimpleNamespace(id=r["id"], bytes=r["bytes"]) for r in group]
            sizes = {o.id: o.bytes for o in objs}
            for number, ids in enumerate(make_batches(objs, batch_bytes), start=1):
                size = sum(sizes[i] for i in ids)
                hits = sum(lever_hits(texts[i]) for i in ids)
                batches.append(
                    {
                        "id": f"{kind}-{surface}-{number:03d}",
                        "surface": surface,
                        "lever": kind == "L",
                        "chunks": ids,
                        "bytes": size,
                        "lever_density": round(hits * 1000 / max(size, 1), 2),
                    }
                )
    ordered = []
    for lever in (True, False):
        queues = {
            s: [b for b in batches if b["surface"] == s and b["lever"] is lever] for s in SURFACES
        }
        if lever:  # the densest lever batches go first, so the first waves are the lever slice
            for queue in queues.values():
                queue.sort(key=lambda b: -b["lever_density"])
        while any(queues.values()):
            for surface in SURFACES:
                if queues[surface]:
                    ordered.append(queues[surface].pop(0))
    waves = [
        {"wave": n + 1, "batches": [b["id"] for b in ordered[i : i + wave_size]]}
        for n, i in enumerate(range(0, len(ordered), wave_size))
    ]
    return {
        "batch_bytes": batch_bytes,
        "cap": cap,
        "wave_size": wave_size,
        "batches": ordered,
        "waves": waves,
    }


def classify_result(records, parse_error, cap):
    """``(status, action)`` for one finished batch."""
    if parse_error is not None:
        return "malformed", "split"
    if records is None:
        return "missing", "split"
    # A scout stops just under the cap it was told (cap-90 runs clustered at 89 to 91), so
    # "capped" starts at 95% of the cap, not only at cap - 1.
    if len(records) >= min(cap - 1, math.ceil(cap * 0.95)):
        return "capped", "split"
    return "ok", None


def _surface_chunks(run_dir, surface):
    return load_json(Path(run_dir) / "corpus" / surface / "chunks.json")


def _read_chunk_texts(rows):
    return {r["id"]: Path(r["path"]).read_text(encoding="utf-8") for r in rows}


def _paths(run_dir):
    base = Path(run_dir) / "extract"
    return {
        "base": base,
        "plan": base / "plan.json",
        "briefs": base / "briefs",
        "batches": base / "batches",
        "out": base / "out",
        "verified": base / "verified",
    }


def _cmd_plan(args):
    chunks, texts = {}, {}
    for surface in SURFACES:
        rows = _surface_chunks(args.run_dir, surface)
        chunks[surface] = rows
        texts.update(_read_chunk_texts(rows))
    plan = build_plan(chunks, texts, args.batch_bytes, args.cap, args.wave_size)
    paths = _paths(args.run_dir)
    paths["base"].mkdir(parents=True, exist_ok=True)
    dump_json(paths["plan"], plan)
    lever = [b for b in plan["batches"] if b["lever"]]
    print(
        f"extract: {len(plan['batches'])} batches ({len(lever)} lever, "
        f"{len(plan['batches']) - len(lever)} rest) in {len(plan['waves'])} waves; "
        f"{sum(b['bytes'] for b in plan['batches']) // 1024} KB"
    )
    return 0


def _plan_batch(plan, batch_id):
    for batch in plan["batches"]:
        if batch["id"] == batch_id:
            return batch
    raise ExtractError(f"unknown batch {batch_id!r}")


def batch_cap(plan, batch):
    """The record cap this batch's scout was told (set by ``brief --cap``), else the plan's."""
    return batch.get("cap") or plan["cap"]


def _cmd_brief(args):
    plan = load_json(_paths(args.run_dir)["plan"])
    paths = _paths(args.run_dir)
    for directory in ("briefs", "batches", "out"):
        paths[directory].mkdir(parents=True, exist_ok=True)
    catalog = paths["base"] / "catalog-short.md"
    if not catalog.is_file():
        from briefs import catalog_text

        facets = load_json(Path(__file__).resolve().parent.parent / "data" / "facets.json")
        catalog.write_text(catalog_text(facets, "short"), encoding="utf-8", newline="\n")
    for batch_id in args.batches:
        batch = _plan_batch(plan, batch_id)
        by_id = {c["id"]: c for c in _surface_chunks(args.run_dir, batch["surface"])}
        rows = [by_id[i] for i in batch["chunks"]]
        combined = paths["batches"] / f"{batch_id}.txt"
        body = combine_chunks(rows, lambda r: Path(r["path"]).read_text(encoding="utf-8"))
        combined.write_text(body, encoding="utf-8", newline="")
        out_json = paths["out"] / f"{batch_id}.json"
        batch["cap"] = args.cap or batch_cap(plan, batch)
        text = make_brief(batch_id, rows, str(catalog), str(out_json), str(combined), batch["cap"])
        (paths["briefs"] / f"{batch_id}.md").write_text(text, encoding="utf-8", newline="\n")
        print(str(paths["briefs"] / f"{batch_id}.md"))
    dump_json(paths["plan"], plan)
    return 0


def _cmd_clone(args):
    """Copy batches as ``K-`` test batches with their own cap; never queued, never split."""
    paths = _paths(args.run_dir)
    plan = load_json(paths["plan"])
    for batch_id in args.batches:
        source = _plan_batch(plan, batch_id)
        new_id = "K-" + batch_id.split("-", 1)[1]
        clone = {k: v for k, v in source.items() if k not in ("parent", "cap")}
        clone.update({"id": new_id, "cap": args.cap, "test_of": batch_id})
        if not any(b["id"] == new_id for b in plan["batches"]):
            plan["batches"].append(clone)
        print(new_id)
    dump_json(paths["plan"], plan)
    return 0


def _append_split_children(plan, batch, rows):
    halves = split_ids(batch["chunks"])
    if halves is None:
        return []
    sizes = {c["id"]: c["bytes"] for c in rows}
    children = []
    for suffix, ids in zip("ab", halves):
        child = {
            "id": f"{batch['id']}{suffix}",
            "surface": batch["surface"],
            "lever": batch["lever"],
            "chunks": ids,
            "bytes": sum(sizes[i] for i in ids),
            "parent": batch["id"],
        }
        if not any(b["id"] == child["id"] for b in plan["batches"]):
            plan["batches"].append(child)
        children.append(child["id"])
    return children


def _cmd_collect(args):
    run_dir = Path(args.run_dir)
    paths = _paths(run_dir)
    paths["verified"].mkdir(parents=True, exist_ok=True)
    plan = load_json(paths["plan"])
    ledger = Ledger(run_dir)
    queued = []
    for batch_id in args.batches:
        batch = _plan_batch(plan, batch_id)
        surface = batch["surface"]
        rows = _surface_chunks(run_dir, surface)
        out = paths["out"] / f"{batch_id}.json"
        records, parse_error, repaired = None, None, False
        if out.is_file():
            try:
                data, repaired = load_scout_json(out.read_text(encoding="utf-8"))
                records = data["records"] if isinstance(data, dict) else data
            except (ValueError, KeyError) as exc:
                parse_error = str(exc)
        cap = batch_cap(plan, batch)
        status, action = classify_result(records, parse_error, cap)
        if batch.get("test_of"):
            action = None  # a test clone reports its status; it is never split or queued
        summary = {
            "batch": batch_id,
            "surface": surface,
            "cap": cap,
            "status": status,
            "records": len(records) if records is not None else None,
            "json_repaired": repaired,
        }
        if records is not None:
            spec = load_json(run_dir / "corpus" / surface / "pages-spec.json")
            by_id = {c["id"]: c for c in rows}
            page_ids = {by_id[i]["page_id"] for i in batch["chunks"]}
            pages = {}
            for pid in page_ids:
                item = dict(spec[pid])
                item["raw_text"] = Path(item.pop("raw_path")).read_text(encoding="utf-8")
                pages[pid] = item
            result = verify_batch(records, pages)
            result["batch"] = batch_id
            dump_json(paths["verified"] / f"{batch_id}.json", result)
            summary.update(
                {
                    "verified": len(result["evidence"]),
                    "pass_rate": round(result["pass_rate"], 4),
                    "dropped": len(result["dropped"]),
                }
            )
        children = _append_split_children(plan, batch, rows) if action == "split" else []
        if action == "split" and not children:
            summary["note"] = "single chunk: accepted as returned"
            action = None
        summary["queued"] = children
        queued.extend(children)
        ledger.append(f"extract:{batch_id}", **summary)
        print(json.dumps(summary, sort_keys=True))
    if queued:
        plan["waves"].append({"wave": len(plan["waves"]) + 1, "batches": queued})
        dump_json(paths["plan"], plan)
    return 0


def _cmd_status(args):
    plan = load_json(_paths(args.run_dir)["plan"])
    state = Ledger(args.run_dir).latest()
    done = {k[len("extract:") :]: v for k, v in state.items() if k.startswith("extract:")}
    total_kb = sum(b["bytes"] for b in plan["batches"] if not b.get("parent")) // 1024
    ok = [b for b, v in done.items() if v["status"] == "ok"]
    print(
        f"batches planned {len(plan['batches'])}, collected {len(done)}, ok {len(ok)}, "
        f"queued after split {sum(len(v.get('queued', [])) for v in done.values())}; "
        f"corpus {total_kb} KB, waves {len(plan['waves'])}"
    )
    pending = [b["id"] for b in plan["batches"] if b["id"] not in done]
    print("next pending:", pending[: plan["wave_size"]])
    return 0


def _selftest():
    rows = {
        "cursor": [
            {"id": "a#1", "page_id": "a", "bytes": 30000},
            {"id": "a#2", "page_id": "a", "bytes": 30000},
        ]
    }
    texts = {"a#1": "model effort thinking permission", "a#2": "nothing here"}
    plan = build_plan(rows, texts)
    kinds = [(b["id"], b["lever"]) for b in plan["batches"]]
    if kinds != [("L-cursor-001", True), ("X-cursor-001", False)]:
        raise AssertionError(f"unexpected plan {kinds}")
    if classify_result([1] * 89, None, 90) != ("capped", "split"):
        raise AssertionError("cap rule")
    print("OK")


def main(argv=None):
    assert_worktree()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    commands = parser.add_subparsers(dest="command")
    plan = commands.add_parser("plan")
    plan.add_argument("--run-dir", required=True)
    plan.add_argument("--batch-bytes", type=int, default=BATCH_BYTES)
    plan.add_argument("--cap", type=int, default=DEFAULT_CAP)
    plan.add_argument("--wave-size", type=int, default=WAVE_SIZE)
    plan.set_defaults(handler=_cmd_plan)
    brief = commands.add_parser("brief")
    brief.add_argument("--run-dir", required=True)
    brief.add_argument("--batches", nargs="+", required=True)
    brief.add_argument("--cap", type=int, default=None)
    brief.set_defaults(handler=_cmd_brief)
    clone = commands.add_parser("clone")
    clone.add_argument("--run-dir", required=True)
    clone.add_argument("--batches", nargs="+", required=True)
    clone.add_argument("--cap", type=int, required=True)
    clone.set_defaults(handler=_cmd_clone)
    collect = commands.add_parser("collect")
    collect.add_argument("--run-dir", required=True)
    collect.add_argument("--batches", nargs="+", required=True)
    collect.set_defaults(handler=_cmd_collect)
    status = commands.add_parser("status")
    status.add_argument("--run-dir", required=True)
    status.set_defaults(handler=_cmd_status)
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    if not args.command:
        parser.error("choose a command: plan, brief, clone, collect or status (or --selftest)")
    try:
        return args.handler(args)
    except (ExtractError, OSError, KeyError, ValueError) as exc:
        print(f"extract: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
