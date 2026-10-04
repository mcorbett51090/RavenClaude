"""Turn one surface's fetched mirror into the corpus that extraction reads.

For every fetched page this decides a role, neutralizes the text (line structure untouched),
marks near-duplicates, and cuts what extraction will read into chunks that cover every line.
Nothing here fetches or judges content; it only joins the manifest, the scope rules and the
neutralizer, deduper and chunker into one reproducible table.

Roles: ``extract`` (read by scouts), ``secondary`` (at least 90 percent contained in a larger
page, so skipped), ``aggregate`` (a combined file, never extracted), ``index`` (an index, sitemap
or page list), ``excluded`` (named in the scope rules with a reason), ``html`` (an app shell, not
documentation), ``out-of-scope`` (fails the surface's post-fetch scope rule).

Usage: python3 corpus.py build --surface ID --run-dir DIR [--rules FILE] [--origins FILE ...]
                              [--out-dir DIR] [--max-bytes N]
       python3 corpus.py summary --run-dir DIR
       python3 corpus.py --selftest
"""

import argparse
import glob
import json
import re
import shutil
import sys
from chunk import DEFAULT_MAX_BYTES, chunk_page, split_gemini
from pathlib import Path
from urllib.parse import urlsplit

from atlas_common import DATA_DIR, assert_worktree, dump_json, load_json, sha256_bytes
from dedupe import mark_secondary
from discover import SOURCES, _try_canonical
from neutralize import check_parity, neutralize_text

ROLES = ("extract", "secondary", "aggregate", "index", "excluded", "html", "out-of-scope")
GAP_OUTCOMES = ("negative", "refused", "rejected", "indeterminate", "failed")
ORIGIN_SKIP = ("-all.", "-raw.", "known-html")
_CHANGELOG_RE = re.compile(r"(/changelog|/whats-new|/release-notes|/updates/v)", re.IGNORECASE)
_NAME_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")
MAX_ID_LENGTH = 110


class CorpusError(Exception):
    """A usage or input problem the CLI reports with exit code 2."""


def sniff_kind(text):
    head = text.lstrip()[:200].lower()
    if head.startswith(("<!doctype html", "<html")):
        return "html"
    if head.startswith("<?xml"):
        return "xml"
    return "text"


def tier_for(url):
    return "E2" if _CHANGELOG_RE.search(urlsplit(url).path) else "E1"


def page_slug(url):
    """A filesystem-safe, human-readable name for a URL, unique per host, path and pathname."""
    parts = urlsplit(url)
    path = parts.path
    if parts.query.startswith("pathname="):
        path = parts.query[len("pathname=") :]
    path = re.sub(r"\.(md|html)$", "", path.strip("/"))
    host = parts.netloc.lower().replace(":443", "").replace(".", "-")
    slug = _NAME_UNSAFE.sub("-", f"{host}__{path.replace('/', '__')}").strip("-")
    if len(slug) > MAX_ID_LENGTH:
        slug = slug[: MAX_ID_LENGTH - 9] + "-" + sha256_bytes(url.encode("utf-8"))[:8]
    return slug


def page_id(surface, url):
    return f"{surface}__{page_slug(url)}"


def scope_decision(post_scope, url, text):
    """``(in_scope, reason)`` for a fetched page under a surface's ``post_fetch_scope`` rule.

    ``post_scope`` is None (everything is in scope) or a dict with optional ``allow_paths`` (an
    always-in list), ``deny_paths`` (out unless allowed) and ``mention`` ({"pattern", "min"}): a
    page that is neither allowed nor denied stays in only when its text matches the pattern at
    least ``min`` times. A page kept by the mention rule is reported as "mention" so a human can
    review that residual list.
    """
    if not post_scope:
        return True, "no post-fetch rule"
    path = urlsplit(url).path
    if any(re.search(pattern, path) for pattern in post_scope.get("allow_paths", [])):
        return True, "allow_paths"
    if any(re.search(pattern, path) for pattern in post_scope.get("deny_paths", [])):
        return False, "deny_paths"
    mention = post_scope.get("mention")
    if mention:
        count = len(re.findall(mention["pattern"], text, flags=re.IGNORECASE))
        if count >= mention.get("min", 1):
            return True, f"mention x{count}"
        return False, f"mention x{count} below {mention.get('min', 1)}"
    return True, "no matching rule"


def best_sources(origin_records):
    """``{canonical url: most authoritative source}`` over origin records (index first)."""
    best = {}
    for record in origin_records:
        key = _try_canonical(record["url"])
        if key is None:
            continue
        rank = SOURCES.index(record["source"])
        if key not in best or rank < SOURCES.index(best[key]):
            best[key] = record["source"]
    return best


def latest_rows(manifest_rows):
    """The newest manifest row per URL, in first-seen order."""
    latest = {}
    for row in manifest_rows:
        latest[row["url"]] = row
    return list(latest.values())


def _read_jsonl(path):
    out = []
    with open(path, encoding="utf-8") as fh:
        for number, raw in enumerate(fh, start=1):
            if raw.strip():
                try:
                    out.append(json.loads(raw))
                except json.JSONDecodeError as exc:
                    raise CorpusError(f"{path}:{number}: not valid JSON: {exc}") from exc
    return out


def _lines(text):
    return text.split("\n")


def build_corpus(surface, rows, rules, read_raw, sources, max_bytes=DEFAULT_MAX_BYTES):
    """Decide every page's role and build its neutral text and chunks.

    ``rows`` are manifest rows; ``rules`` is this surface's scope-rules entry; ``read_raw`` maps
    a manifest row to its raw bytes; ``sources`` is ``best_sources`` of the origin records.
    Returns ``(pages, gaps, texts)``: page dicts, rows that did not fetch, and
    ``{page_id: {"raw", "neutral", "chunks"}}`` for pages that get a neutral copy.
    """
    seed_urls = {_try_canonical(u) for u in rules.get("index_files", [])}
    excluded = {
        _try_canonical(item["url"]): item["reason"] for item in rules.get("excluded_urls", [])
    }
    aggregates = {_try_canonical(u) for u in rules.get("aggregates", [])}
    split_urls = {_try_canonical(u) for u in rules.get("gemini_split", [])}
    post_scope = rules.get("post_fetch_scope")

    pages, gaps, texts = [], [], {}
    candidates = {}  # page_id -> raw lines, for dedupe

    def base_record(row, pid, role, reason, **extra):
        return {
            "page_id": pid,
            "surface": surface,
            "url": row["url"],
            "url_effective": row.get("url_effective") or row["url"],
            "retrieved": row["retrieved"],
            "http_status": row["status"],
            "sha256": row["sha256"],
            "bytes": row["bytes"],
            "raw_path": row["raw_path"],
            "tier": tier_for(row["url"]),
            "origin_source": sources.get(_try_canonical(row["url"])),
            "role": role,
            "reason": reason,
            **extra,
        }

    for row in latest_rows(rows):
        if row["outcome"] != "fetched":
            gaps.append(
                {
                    "url": row["url"],
                    "outcome": row["outcome"],
                    "status": row.get("status"),
                    "reason": row.get("reason", ""),
                }
            )
            continue
        key = _try_canonical(row["url"])
        pid = page_id(surface, row["url"])
        raw_bytes = read_raw(row)
        try:
            raw = raw_bytes.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise CorpusError(f"{row['url']}: raw bytes are not valid UTF-8: {exc}") from exc
        kind = sniff_kind(raw)
        info = {"kind": kind, "lines": len(_lines(raw))}

        if key in split_urls:
            pages.append(
                base_record(row, pid, "aggregate", "split into the pages listed under it", **info)
            )
            for part in split_gemini(raw):
                if part["url"] is None:
                    continue
                virtual = page_id(surface, part["url"])
                record = base_record(
                    row,
                    virtual,
                    "extract",
                    "page of the aggregate",
                    kind="text",
                    lines=part["end_line"] - part["start_line"] + 1,
                    source_page_url=part["url"],
                    title=part["title"],
                    line_offset=part["start_line"] - 1,
                    aggregate_page_id=pid,
                )
                record["bytes"] = len(part["text"].encode("utf-8"))
                record["aggregate_bytes"] = row["bytes"]
                record["aggregate_sha256"] = row["sha256"]
                record["slice_sha256"] = sha256_bytes(part["text"].encode("utf-8"))
                pages.append(record)
                texts[virtual] = {"raw": part["text"]}
                candidates[virtual] = _lines(part["text"])
            continue
        if key in seed_urls or kind == "xml":
            pages.append(base_record(row, pid, "index", "index, sitemap or page list", **info))
            continue
        if key in excluded:
            pages.append(base_record(row, pid, "excluded", excluded[key], **info))
            continue
        if kind == "html":
            # An app shell often shares its slug with the page's .md twin; keep the ids apart.
            shell_id = f"{pid}~html"
            pages.append(
                base_record(row, shell_id, "html", "HTML app shell, not documentation", **info)
            )
            continue
        if key in aggregates:
            pages.append(
                base_record(row, pid, "aggregate", "combined file, never extracted", **info)
            )
            texts[pid] = {"raw": raw}
            candidates[pid] = _lines(raw)
            continue
        in_scope, why = scope_decision(post_scope, row["url"], raw)
        if not in_scope:
            pages.append(base_record(row, pid, "out-of-scope", why, **info))
            continue
        pages.append(base_record(row, pid, "extract", why, **info))
        texts[pid] = {"raw": raw}
        candidates[pid] = _lines(raw)

    by_id = {page["page_id"]: page for page in pages}
    if len(by_id) != len(pages):
        counts = {}
        for page in pages:
            counts[page["page_id"]] = counts.get(page["page_id"], 0) + 1
        clash = sorted(pid for pid, n in counts.items() if n > 1)
        raise CorpusError(f"{surface}: page ids are not unique: {clash[:5]}")
    aggregate_ids = {
        p["page_id"] for p in pages if p["role"] == "aggregate" and p["page_id"] in texts
    }
    for pid, mark in mark_secondary(candidates, aggregate_ids).items():
        page = by_id[pid]
        if page["role"] == "aggregate":
            continue
        page["containment"] = mark["containment"]
        if mark["role"] == "secondary":
            page["role"] = "secondary"
            page["secondary_of"] = mark["secondary_of"]
            page["reason"] = f"{mark['containment']:.2f} contained in {mark['secondary_of']}"

    for pid, entry in list(texts.items()):
        page = by_id[pid]
        if page["role"] not in ("extract", "secondary"):
            del texts[pid]
            continue
        # A secondary page is never read, but its line parity is still proven (RT1).
        neutral, flagged = neutralize_text(entry["raw"])
        check_parity(entry["raw"], neutral)
        page["flagged_lines"] = flagged
        if page["role"] == "extract":
            entry["neutral"] = neutral
            entry["chunks"] = chunk_page(pid, neutral, max_bytes)
    return pages, gaps, texts


OWNED_DIRS = ("neutral", "chunks", "slices")


def _reset_outputs(out):
    """Remove the three directories this tool writes, so a rebuild leaves no stale page behind."""
    out = Path(out).resolve()
    if len(out.parts) < 4:
        raise CorpusError(f"refusing to reset outputs under {out}")
    for name in OWNED_DIRS:
        shutil.rmtree(out / name, ignore_errors=True)


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")


def _surface_name(surface):
    for entry in load_json(DATA_DIR / "surfaces.json")["surfaces"]:
        if entry["id"] == surface:
            return entry["name"]
    known = ", ".join(sorted(e["id"] for e in load_json(DATA_DIR / "surfaces.json")["surfaces"]))
    raise CorpusError(f"unknown surface {surface!r}; known: {known}")


def _cmd_build(args):
    run_dir = Path(args.run_dir)
    mirror = run_dir / "mirror" / args.surface
    out = Path(args.out_dir) if args.out_dir else run_dir / "corpus" / args.surface
    rules_doc = load_json(args.rules or DATA_DIR / "scope-rules.json")["surfaces"]
    if args.surface not in rules_doc:
        raise CorpusError(f"{args.rules or 'scope-rules.json'} has no entry for {args.surface}")
    origin_files = args.origins or [
        path
        for path in sorted(glob.glob(str(run_dir / "p3" / f"{args.surface}.origins-*.jsonl")))
        if not any(token in path for token in ORIGIN_SKIP)
    ]
    records = [rec for path in origin_files for rec in _read_jsonl(path)]
    rows = _read_jsonl(mirror / "manifest.jsonl")
    raw_dir = mirror / "raw"

    def read_raw(row):
        return (raw_dir / row["raw_path"]).read_bytes()

    pages, gaps, texts = build_corpus(
        args.surface, rows, rules_doc[args.surface], read_raw, best_sources(records), args.max_bytes
    )
    product = _surface_name(args.surface)
    _reset_outputs(out)
    chunk_index, specs = [], {}
    for page in pages:
        pid = page["page_id"]
        entry = texts.get(pid)
        if entry is None or "neutral" not in entry:
            continue
        neutral_path = out / "neutral" / f"{pid}.txt"
        _write(neutral_path, entry["neutral"])
        page["neutral_path"] = str(neutral_path)
        raw_path = mirror / "raw" / page["raw_path"]
        if "line_offset" in page:
            raw_path = out / "slices" / f"{pid}.txt"
            _write(raw_path, entry["raw"])
        specs[pid] = {
            "raw_path": str(raw_path),
            "surface": args.surface,
            "tier": page["tier"],
            "url": page["url"],
            "url_effective": page["url_effective"],
            "retrieved": page["retrieved"],
            "http_status": page["http_status"],
            "sha256": page.get("aggregate_sha256", page["sha256"]),
            "bytes": page.get("aggregate_bytes", page["bytes"]),
            "product_version": None,
            "version_source": None,
        }
        if "line_offset" in page:
            specs[pid]["line_offset"] = page["line_offset"]
        for chunk in entry["chunks"]:
            chunk_path = out / "chunks" / pid / f"{chunk.id.rsplit('#', 1)[1]}.txt"
            _write(chunk_path, chunk.text)
            chunk_index.append(
                {
                    "id": chunk.id,
                    "page_id": pid,
                    "path": str(chunk_path),
                    "product": product,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "bytes": chunk.bytes,
                }
            )
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "pages.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for page in pages:
            fh.write(json.dumps(page, sort_keys=True, ensure_ascii=False) + "\n")
    dump_json(out / "gaps.json", gaps)
    dump_json(out / "pages-spec.json", specs)
    dump_json(out / "chunks.json", chunk_index)
    summary = summarize(args.surface, pages, gaps, chunk_index)
    dump_json(out / "summary.json", summary)
    print(json.dumps(summary, sort_keys=True))
    return 0


def summarize(surface, pages, gaps, chunk_index):
    roles = {role: {"pages": 0, "bytes": 0} for role in ROLES}
    for page in pages:
        roles[page["role"]]["pages"] += 1
        roles[page["role"]]["bytes"] += page["bytes"]
    extract = [p for p in pages if p["role"] == "extract"]
    return {
        "surface": surface,
        "roles": roles,
        "extract_pages": len(extract),
        "extract_bytes": roles["extract"]["bytes"],
        "extract_chunks": len(chunk_index),
        "extract_chunk_bytes": sum(c["bytes"] for c in chunk_index),
        "flagged_lines": sum(len(p.get("flagged_lines", [])) for p in extract),
        "pages_with_flags": sum(1 for p in extract if p.get("flagged_lines")),
        "gaps": len(gaps),
        "gap_reasons": sorted({f"{g['outcome']}:{g['reason']}" for g in gaps}),
    }


def _cmd_summary(args):
    rows = []
    for path in sorted(glob.glob(str(Path(args.run_dir) / "corpus" / "*" / "summary.json"))):
        rows.append(load_json(path))
    header = f"{'surface':16}{'extract':>9}{'KB':>9}{'chunks':>8}{'secondary':>10}{'flagged':>9}{'gaps':>6}"
    print(header)
    total = {"extract_pages": 0, "extract_bytes": 0, "extract_chunks": 0}
    for s in rows:
        print(
            f"{s['surface']:16}{s['extract_pages']:>9}{s['extract_bytes'] // 1024:>9}"
            f"{s['extract_chunks']:>8}{s['roles']['secondary']['pages']:>10}"
            f"{s['flagged_lines']:>9}{s['gaps']:>6}"
        )
        for key in total:
            total[key] += s[key]
    print(
        f"{'total':16}{total['extract_pages']:>9}{total['extract_bytes'] // 1024:>9}"
        f"{total['extract_chunks']:>8}   (bytes/4 = {total['extract_bytes'] // 4:,} tokens)"
    )
    return 0


def _selftest():
    if page_slug("https://docs.x.ai/build/overview.md") != "docs-x-ai__build__overview":
        raise AssertionError("slug")
    copilot = "https://docs.github.com/api/article/body?pathname=/en/copilot/a/b"
    if page_slug(copilot) != "docs-github-com__en__copilot__a__b":
        raise AssertionError("pathname slug")
    if scope_decision(None, "https://x.example/a", "t") != (True, "no post-fetch rule"):
        raise AssertionError("no rule")
    rule = {
        "allow_paths": ["^/keep"],
        "deny_paths": ["^/drop"],
        "mention": {"pattern": "codex", "min": 2},
    }
    cases = [
        ("/keep/x", "", True),
        ("/drop/x", "codex codex", False),
        ("/other", "Codex and codex", True),
        ("/other", "codex", False),
    ]
    for path, text, want in cases:
        if scope_decision(rule, f"https://x.example{path}", text)[0] is not want:
            raise AssertionError(f"scope {path}")
    print("OK")


def main(argv=None):
    assert_worktree()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    commands = parser.add_subparsers(dest="command")
    build = commands.add_parser("build", help="build one surface's corpus")
    build.add_argument("--surface", required=True)
    build.add_argument("--run-dir", required=True)
    build.add_argument("--rules")
    build.add_argument("--origins", nargs="+")
    build.add_argument("--out-dir")
    build.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    build.set_defaults(handler=_cmd_build)
    summary = commands.add_parser("summary", help="print every built surface's totals")
    summary.add_argument("--run-dir", required=True)
    summary.set_defaults(handler=_cmd_summary)
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    if not args.command:
        parser.error("choose a command: build or summary (or --selftest)")
    try:
        return args.handler(args)
    except (CorpusError, OSError, ValueError) as exc:
        print(f"corpus: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
