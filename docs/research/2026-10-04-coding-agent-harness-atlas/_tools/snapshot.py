"""Assemble the atlas snapshot: product versions, index hashes, per-surface coverage, baselines.

``versions`` reads the version files P3 saved beside each mirror (an npm registry answer, the
redirect target of the VS Code updates page, the first date on the Cursor changelog) and writes
``data/versions.json``. ``build`` reads the manifests, the scope rules and the corpus summaries
and writes ``data/snapshot.json`` plus one enumeration record and one URL baseline per surface.
Nothing here fetches.

Usage: python3 snapshot.py versions --run-dir DIR [--out FILE]
       python3 snapshot.py build --run-dir DIR [--out FILE] [--enum-dir DIR] [--freeze-end DATE]
       python3 snapshot.py --selftest
"""

import argparse
import glob
import json
import re
import sys
from chunk import split_gemini
from pathlib import Path

from atlas_common import DATA_DIR, assert_worktree, dump_json, load_json
from corpus import ORIGIN_SKIP
from discover import _try_canonical, parse_llms_txt, parse_sitemap, url_set_digest

SURFACE_IDS = (
    "claude-code",
    "codex-cli",
    "copilot-cli",
    "copilot-vscode",
    "cursor",
    "gemini-cli",
    "grok-build",
    "grok-bot",
)
COUNTED_ROLES = ("extract", "secondary", "out-of-scope")
_VSCODE_RELEASE = re.compile(r"/updates/v(\d+)_(\d+)$")
_DATE = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? (\d{1,2}), (\d{4})\b"
)
_MONTHS = {m: i for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}


class SnapshotError(Exception):
    """A usage or input problem the CLI reports with exit code 2."""


def _read_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def npm_version(latest_json, dist_tags_json):
    """``(version, note)`` from an npm ``/latest`` answer and a dist-tags answer."""
    latest = json.loads(latest_json)
    version = latest.get("version")
    if not version:
        raise SnapshotError("npm answer has no version")
    tags = {
        k: v
        for k, v in json.loads(dist_tags_json).items()
        if k in ("latest", "stable", "next", "preview")
    }
    return version, tags


def vscode_version(effective_url):
    match = _VSCODE_RELEASE.search(effective_url or "")
    return f"{match.group(1)}.{match.group(2)}" if match else None


def first_changelog_date(html_text):
    """The first ``Mon D, YYYY`` date in the visible text of a changelog page, as ISO."""
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html_text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    match = _DATE.search(text)
    if not match:
        return None
    return f"{int(match.group(3)):04d}-{_MONTHS[match.group(1)]:02d}-{int(match.group(2)):02d}"


def _row_for(manifest_rows, url):
    found = None
    for row in manifest_rows:
        if row["url"] == url and row["outcome"] == "fetched":
            found = row
    return found


def _read_version_file(run_dir, surface, name):
    path = Path(run_dir) / "mirror" / surface / "version" / name
    return path.read_text(encoding="utf-8") if path.is_file() else None


def collect_versions(run_dir, surfaces):
    """One record per surface: version, where it came from, the retrieval date."""
    records = []
    for entry in surfaces:
        sid = entry["id"]
        source = entry.get("version_source", {})
        kind = source.get("kind")
        manifest = _read_jsonl(Path(run_dir) / "mirror" / sid / "manifest.jsonl")
        retrieved = max((r["retrieved"] for r in manifest if r.get("retrieved")), default=None)
        record = {"surface": sid, "retrieved": retrieved, "version": None, "version_source": None}
        if kind == "npm":
            latest = _read_version_file(run_dir, sid, "npm-latest.json")
            tags = _read_version_file(run_dir, sid, "npm-dist-tags.json")
            if latest is not None and tags is not None:
                version, tag_map = npm_version(latest, tags)
                record["version"] = version
                record["version_source"] = (
                    f"https://registry.npmjs.org/{source['package']}/latest (dist-tags {tag_map})"
                )
        elif kind == "release-notes":
            row = _row_for(manifest, source["url"])
            if row:
                record["version"] = vscode_version(row.get("url_effective"))
                record["version_source"] = (
                    f"{source['url']} redirected to {row.get('url_effective')}"
                )
        elif kind == "changelog-html":
            row = _row_for(manifest, source["url"])
            if row:
                raw = (Path(run_dir) / "mirror" / sid / "raw" / row["raw_path"]).read_text(
                    encoding="utf-8"
                )
                date = first_changelog_date(raw)
                if date:
                    record["version"] = f"changelog entry {date}"
                    record["version_source"] = (
                        f"{source['url']} (newest entry date; no version number is published there)"
                    )
        elif kind == "hosted-service":
            record["version_source"] = "hosted service; documentation as of the retrieval date"
        else:
            record["version_source"] = (
                "no version published; documentation as of the retrieval date"
            )
        records.append(record)
    return records


def url_set_for(row, raw, rules):
    """The URL list one index, sitemap, page list or aggregate file names."""
    url = row["url"]
    key = _try_canonical(url)
    split_urls = {_try_canonical(u) for u in rules.get("gemini_split", [])}
    if key in split_urls:
        return [part["url"] for part in split_gemini(raw) if part["url"]]
    if raw.lstrip().startswith("<?xml"):
        return list(parse_sitemap(raw)["urls"])
    if "/api/pagelist/" in url:
        host = re.match(r"https://[^/]+", url).group(0)
        return [host + line.strip() for line in raw.splitlines() if line.strip().startswith("/")]
    return [entry["url"] for entry in parse_llms_txt(raw, row.get("url_effective") or url)]


def index_hashes(surface, manifest_rows, rules, read_raw):
    """``{file url: {"sha256": url-set digest, "entries": n}}`` for every index-like file."""
    index_keys = {_try_canonical(u) for u in rules.get("index_files", [])}
    split_keys = {_try_canonical(u) for u in rules.get("gemini_split", [])}
    out = {}
    for row in manifest_rows:
        if row["outcome"] != "fetched":
            continue
        raw = read_raw(row).decode("utf-8", errors="replace")
        key = _try_canonical(row["url"])
        if key in index_keys or key in split_keys or raw.lstrip().startswith("<?xml"):
            urls = url_set_for(row, raw, rules)
            out[row["url"]] = {"sha256": url_set_digest(urls), "entries": len(set(urls))}
    return out


def coverage_metrics(summary, pages, gaps, index_info):
    roles = summary["roles"]
    by_source = {"index": 0, "sitemap": 0, "closure": 0}
    for page in pages:
        if page["role"] in COUNTED_ROLES and page.get("origin_source") in by_source:
            by_source[page["origin_source"]] += 1
    return {
        "index and sitemap files mirrored": len(index_info),
        "pages found by index": by_source["index"],
        "pages found only by sitemap or page list": by_source["sitemap"],
        "pages found only by link closure": by_source["closure"],
        "pages read by extraction": summary["extract_pages"],
        "pages skipped as near-duplicates": roles["secondary"]["pages"],
        "pages excluded as out of scope": roles["out-of-scope"]["pages"],
        "aggregate files not extracted": roles["aggregate"]["pages"],
        "HTML app shells not extracted": roles["html"]["pages"],
        "extraction text (KB)": summary["extract_bytes"] // 1024,
        "chunks": summary["extract_chunks"],
        "lines flagged by the neutralizer": summary["flagged_lines"],
        "fetches that returned nothing usable": len(gaps),
    }


MANIFEST_FIELDS = (
    "url",
    "url_effective",
    "outcome",
    "status",
    "reason",
    "bytes",
    "sha256",
    "retrieved",
    "redirects",
    "cross_host",
    "listed_as",
)


def compact_manifest(rows):
    """Manifest rows without the local raw file name, sorted by URL: the committed integrity record."""
    return [{k: row[k] for k in MANIFEST_FIELDS if k in row} for row in sorted(rows, key=lambda r: r["url"])]


def merged_origins(run_dir, surface):
    """Every origin record for a surface, de-duplicated and sorted, from the P3 origin files."""
    seen = {}
    pattern = str(Path(run_dir) / "p3" / f"{surface}.origins-*.jsonl")
    for path in sorted(glob.glob(pattern)):
        if any(token in path for token in ORIGIN_SKIP):
            continue
        for record in _read_jsonl(path):
            seen[(record["url"], record["source"], record["origin"])] = record
    return [seen[key] for key in sorted(seen)]


def split_rows(pages):
    """Manifest rows for pages cut out of an aggregate file (Gemini): derived, never fetched alone."""
    rows = []
    for page in pages:
        if "aggregate_page_id" not in page:
            continue
        listed = page["source_page_url"]
        rows.append(
            {
                "url": re.sub(r"^http://", "https://", listed),
                "listed_as": listed,
                "url_effective": page["url"],
                "outcome": "split-from-aggregate",
                "status": 200,
                "reason": f"page of {page['url']}",
                "bytes": page["bytes"],
                "sha256": page["slice_sha256"],
                "retrieved": page["retrieved"],
            }
        )
    return rows


def split_origins(pages):
    return [
        {"url": row["url"], "source": "index", "origin": row["url_effective"]}
        for row in split_rows(pages)
    ]


def unmatched_origins(origins, manifest_rows):
    """Origin URLs with no manifest row, compared by ``canonical``: enumerated but never accounted for."""
    have = {_try_canonical(row["url"]) for row in manifest_rows}
    return sorted({o["url"] for o in origins if _try_canonical(o["url"]) not in have})


def _write_jsonl(path, records):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for record in records:
            fh.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def _surface_rules(surface):
    return load_json(DATA_DIR / "scope-rules.json")["surfaces"][surface]


def _cmd_versions(args):
    surfaces = load_json(DATA_DIR / "surfaces.json")["surfaces"]
    records = collect_versions(args.run_dir, surfaces)
    dump_json(args.out or DATA_DIR / "versions.json", {"versions": records})
    for record in records:
        print(f"{record['surface']:16} {record['version']}")
    return 0


def _cmd_build(args):
    run_dir = Path(args.run_dir)
    versions = {
        v["surface"]: v for v in load_json(args.versions or DATA_DIR / "versions.json")["versions"]
    }
    known_gaps_path = Path(args.known_gaps) if args.known_gaps else DATA_DIR / "known-gaps.json"
    known_gaps = load_json(known_gaps_path)["gaps"] if known_gaps_path.is_file() else []
    enum_dir = Path(args.enum_dir) if args.enum_dir else DATA_DIR / "enumeration"
    columns, hashes, coverage = [], {}, {}
    for sid in SURFACE_IDS:
        mirror = run_dir / "mirror" / sid
        corpus = run_dir / "corpus" / sid
        if not (corpus / "summary.json").is_file():
            raise SnapshotError(
                f"{sid}: run corpus.py build first ({corpus}/summary.json is missing)"
            )
        rows = _read_jsonl(mirror / "manifest.jsonl")
        rules = _surface_rules(sid)
        summary = load_json(corpus / "summary.json")
        gaps = load_json(corpus / "gaps.json")
        pages = _read_jsonl(corpus / "pages.jsonl")
        provenance_path = run_dir / "p3" / f"{sid}.provenance.json"
        provenance = load_json(provenance_path) if provenance_path.is_file() else None
        info = index_hashes(
            sid, rows, rules, lambda r, m=mirror: (m / "raw" / r["raw_path"]).read_bytes()
        )
        hashes.update({url: item["sha256"] for url, item in info.items()})
        coverage[sid] = coverage_metrics(summary, pages, gaps, info)
        version = versions[sid]
        columns.append(
            {
                "surface": sid,
                "retrieved": version["retrieved"],
                "version": version["version"],
                "version_source": version["version_source"],
                "pages": summary["extract_pages"],
                "bytes": summary["extract_bytes"],
            }
        )
        baseline = sorted(
            {p["url"] for p in pages if p["role"] != "index" and p["role"] != "html"}
            | {p["source_page_url"] for p in pages if p.get("source_page_url")}
        )
        manifest_out = sorted(compact_manifest(rows) + split_rows(pages), key=lambda r: r["url"])
        origins_out = sorted(
            merged_origins(run_dir, sid) + split_origins(pages),
            key=lambda r: (r["url"], r["source"], r["origin"]),
        )
        missing = unmatched_origins(origins_out, manifest_out)
        if missing:
            raise SnapshotError(
                f"{sid}: {len(missing)} enumerated URLs have no manifest row, for example {missing[:3]}"
            )
        enum_dir.mkdir(parents=True, exist_ok=True)
        _write_jsonl(enum_dir / f"{sid}.manifest.jsonl", manifest_out)
        _write_jsonl(enum_dir / f"{sid}.origins.jsonl", origins_out)
        (enum_dir / f"{sid}.urls.txt").write_text("\n".join(baseline) + "\n", encoding="utf-8")
        dump_json(
            enum_dir / f"{sid}.json",
            {
                "surface": sid,
                "retrieved": version["retrieved"],
                "index_files": info,
                "origins_by_source": provenance["by_source"] if provenance else None,
                "roles": summary["roles"],
                "gaps": gaps,
                "out_of_scope": sorted(p["url"] for p in pages if p["role"] == "out-of-scope"),
                "secondary": {
                    p["url"]: p["secondary_of"] for p in pages if p["role"] == "secondary"
                },
            },
        )
    snapshot = {
        "freeze_start": min(c["retrieved"] for c in columns),
        "freeze_end": args.freeze_end or max(c["retrieved"] for c in columns),
        "columns": columns,
        "index_hashes": hashes,
        "coverage": coverage,
        "known_gaps": known_gaps,
    }
    out = Path(args.out) if args.out else DATA_DIR / "snapshot.json"
    if out.is_file():
        previous = load_json(out)
        for key in ("matrix_sha", "params", "matrix_pending", "verification"):
            if key in previous:
                snapshot[key] = previous[key]
    dump_json(out, snapshot)
    print(f"snapshot: {len(columns)} columns, {len(hashes)} index hashes -> {out}")
    return 0


def _selftest():
    tags = '{"latest":"1.2.3","next":"1.2.4","beta":"0.1"}'
    version, kept = npm_version('{"name":"p","version":"1.2.3"}', tags)
    if version != "1.2.3" or kept != {"latest": "1.2.3", "next": "1.2.4"}:
        raise AssertionError("npm")
    if vscode_version("https://code.visualstudio.com/updates/v1_140") != "1.140":
        raise AssertionError("vscode")
    if vscode_version("https://code.visualstudio.com/updates") is not None:
        raise AssertionError("vscode no release")
    if first_changelog_date("<p>Sep 23, 2026 · Changelog</p>") != "2026-09-23":
        raise AssertionError("cursor date")
    print("OK")


def main(argv=None):
    assert_worktree()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    commands = parser.add_subparsers(dest="command")
    versions = commands.add_parser("versions", help="write data/versions.json from saved files")
    versions.add_argument("--run-dir", required=True)
    versions.add_argument("--out")
    versions.set_defaults(handler=_cmd_versions)
    build = commands.add_parser("build", help="write data/snapshot.json and the enumeration files")
    build.add_argument("--run-dir", required=True)
    build.add_argument("--out")
    build.add_argument("--versions")
    build.add_argument("--known-gaps")
    build.add_argument("--enum-dir")
    build.add_argument("--freeze-end")
    build.set_defaults(handler=_cmd_build)
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    if not args.command:
        parser.error("choose a command: versions or build (or --selftest)")
    try:
        return args.handler(args)
    except (SnapshotError, OSError, KeyError, ValueError) as exc:
        print(f"snapshot: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
