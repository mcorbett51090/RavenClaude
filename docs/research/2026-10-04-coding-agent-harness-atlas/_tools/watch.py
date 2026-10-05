"""Watch the vendor documentation behind the atlas for change.

check    re-fetch every cited page and index, compare with the stored quotes and with a rolling
         baseline, and write a report (report.json, report.md) to --out; spends no model tokens
accept   after the findings are dealt with, write the baseline the last check saw
versions the live version of each column, from its recorded version source

Tiers: T0 version of each column, T1 source drift (a cited quote that vanished, a page that
disappeared, links added or removed, changelog entries naming a lever), T2 the cells, levers and
register entries each change touches. Revising the cells (T3) is a separate, model-driven job.

A report is CLEAN, MATERIAL or UNKNOWN. UNKNOWN means a host could not be reached: it is never
reported as "no change". Docs drift is not behaviour drift: a page can change while the product
does not, and the reverse.

Usage: python3 watch.py check --out DIR [--surface ID ...] [--date YYYY-MM-DD]
       python3 watch.py accept --report DIR/report.json [--force]
       python3 watch.py versions [--surface ID ...]
       python3 watch.py --selftest
Exit codes (check): 0 CLEAN, 1 MATERIAL, 3 UNKNOWN, 2 usage error or unreadable data.
"""

import argparse
import copy
import datetime
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import discover
import fetch
import reverify
from atlas_common import DATA_DIR, assert_worktree, dump_json, load_json, sha256_bytes

SCHEMA_VERSION = 1
BASELINE_NAME = "watch-baseline.json"
REGISTRY_HOST = "registry.npmjs.org"  # watcher-only: it is in no column's docs_hosts
CHANGELOG_URL = re.compile(r"changelog|whats-new", re.IGNORECASE)
GENERAL_TERMS = ("deprecat", "no longer", "removed", "breaking change", "renamed")
MD_CAP = 40  # findings listed per kind in report.md
MDY = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? (\d{1,2}), (\d{4})\b"
)
ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
VSCODE_VERSION = re.compile(r"/v(\d+)_(\d+)")
SECTION_HEADINGS = {
    # The Gemini CLI docs are one aggregate file; each page starts with a heading that links to it.
    "gemini_split": re.compile(r"^# \[[^\]]*\]\((https?://[^)\s]+)\)", re.MULTILINE),
}
MONTHS = {
    m: i
    for i, m in enumerate(
        ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1
    )
}


class WatchError(Exception):
    """Unreadable data or bad usage: reported on stderr, exit 2."""


# --- inputs ------------------------------------------------------------------------------------


def load_inputs(data_dir):
    data_dir = Path(data_dir)
    try:
        surfaces = load_json(data_dir / "surfaces.json")["surfaces"]
        scope = load_json(data_dir / "scope-rules.json")["surfaces"]
        snapshot = load_json(data_dir / "snapshot.json")
    except (OSError, ValueError, KeyError) as exc:
        raise WatchError(f"cannot read atlas data in {data_dir}: {exc}") from exc
    evidence, cells = {}, {}
    for surface in surfaces:
        sid = surface["id"]
        evidence[sid] = _records(data_dir / "evidence" / f"{sid}.json", "evidence")
        cells[sid] = _records(data_dir / "cells" / f"{sid}.json", "cells")
    path = data_dir / BASELINE_NAME
    return {
        "surfaces": {s["id"]: s for s in surfaces},
        "order": [s["id"] for s in surfaces],
        "scope": scope,
        "snapshot": snapshot,
        "evidence": evidence,
        "cells": cells,
        "levers": _records(data_dir / "levers.json", "levers"),
        "register": _records(data_dir / "register.json", "entries"),
        "baseline": load_json(path) if path.exists() else None,
    }


def _records(path, key):
    if not path.exists():
        return []
    doc = load_json(path)
    return doc.get(key, []) if isinstance(doc, dict) else []


def plan_urls(inputs, only=None):
    """The URLs to fetch per column: cited pages, index files, sitemaps, a version page."""
    plan = {}
    for sid in inputs["order"]:
        if only and sid not in only:
            continue
        surface = inputs["surfaces"][sid]
        scope = inputs["scope"].get(sid, {})
        urls = [e["url"] for e in inputs["evidence"][sid] if e.get("url")]
        urls += as_list(surface.get("index_urls")) + as_list(surface.get("sitemap_candidates"))
        urls += as_list(scope.get("index_files")) + as_list(scope.get("gemini_split"))
        source = as_dict(surface.get("version_source"))
        if source.get("kind") in ("release-notes", "changelog-html") and source.get("url"):
            urls.append(source["url"])
        plan[sid] = sorted(set(urls))
    return plan


def as_list(value):
    return value if isinstance(value, list) else []


def as_dict(value):
    return value if isinstance(value, dict) else {}


# --- fetching ----------------------------------------------------------------------------------


def collect(inputs, plan, opener=None, workers=6, sleep=None):
    """Fetch every planned URL once, under each column's own host allow-list.

    Returns ``{url: {"row": manifest row, "text": decoded body or None}}``.
    """
    opener = opener or fetch.http_opener
    pages = {}
    for sid, urls in plan.items():
        todo = [u for u in urls if u not in pages]
        if not todo:
            continue
        bodies = {}

        def keep(row, body, bodies=bodies):
            bodies[row["url"]] = body

        kwargs = {} if sleep is None else {"sleep": sleep}
        fetcher = fetch.Fetcher(
            inputs["surfaces"][sid]["docs_hosts"], opener, on_result=keep, **kwargs
        )
        for row in fetch.fetch_many(fetcher, todo, workers=workers):
            body = bodies.get(row["url"])
            pages[row["url"]] = {
                "row": row,
                "text": None if body is None else body.decode("utf-8", errors="replace"),
            }
    return pages


def live_versions(inputs, pages, opener=None, only=None, sleep=None):
    """``{sid: {"version", "source", "status"}}``; status is ok, none or unknown."""
    opener = opener or fetch.http_opener
    out = {}
    for sid in inputs["order"]:
        if only and sid not in only:
            continue
        source = as_dict(inputs["surfaces"][sid].get("version_source"))
        kind = source.get("kind")
        entry = {"version": None, "source": kind, "status": "none"}
        if kind == "npm" and source.get("package"):
            url = f"https://{REGISTRY_HOST}/{source['package']}/latest"
            entry.update(_npm_latest(url, opener, sleep))
        elif kind == "release-notes" and source.get("url") in pages:
            row = pages[source["url"]]["row"]
            found = VSCODE_VERSION.search(row.get("url_effective") or "")
            entry.update(
                {"version": f"{found.group(1)}.{found.group(2)}", "status": "ok"}
                if found
                else {"status": "unknown"}
            )
        elif kind == "changelog-html" and source.get("url") in pages:
            text = pages[source["url"]]["text"]
            newest = newest_date(text) if text else None
            entry.update({"version": newest, "status": "ok"} if newest else {"status": "unknown"})
        out[sid] = entry
    return out


def _npm_latest(url, opener, sleep):
    kwargs = {} if sleep is None else {"sleep": sleep}
    holder = {}
    fetcher = fetch.Fetcher(
        {REGISTRY_HOST}, opener, on_result=lambda row, body: holder.update(body=body), **kwargs
    )
    row = fetcher.fetch(url)
    body = holder.get("body")
    if row["outcome"] != "fetched" or body is None:
        return {"status": "unknown"}
    try:
        version = json.loads(body.decode("utf-8")).get("version")
    except (ValueError, AttributeError):
        return {"status": "unknown"}
    return (
        {"version": version, "status": "ok"} if isinstance(version, str) else {"status": "unknown"}
    )


def newest_date(text):
    """The latest calendar date written in the text (ISO or 'Sep 23, 2026'), as ISO, or None."""
    found = []
    for m in MDY.finditer(text):
        found.append((int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2))))
    for m in ISO.finditer(text):
        found.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
    valid = []
    for year, month, day in found:
        try:
            valid.append(datetime.date(year, month, day))
        except ValueError:
            continue
    return max(valid).isoformat() if valid else None


# --- analysis ----------------------------------------------------------------------------------


def split_sections(text, pattern):
    """``{section key: text}`` for a file made of sections, each starting at a heading match."""
    matches = list(pattern.finditer(text))
    out = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.setdefault(m.group(1), text[m.start() : end])
    return out


def section_hashes(text, pattern):
    return {
        key: sha256_bytes(body.encode("utf-8"))
        for key, body in split_sections(text, pattern).items()
    }


def index_links(url, text):
    """The page URLs an index file lists: llms.txt, sitemap or the plain-path page list."""
    if url.endswith(".xml"):
        try:
            parsed = discover.parse_sitemap(text)
        except ValueError:
            return None
        return sorted(set(parsed["urls"]) | set(parsed["sitemaps"]))
    if "/api/pagelist/" in url:
        base = "https://" + url.split("/")[2]
        return sorted({base + ln.strip() for ln in text.splitlines() if ln.strip().startswith("/")})
    return sorted({entry["url"] for entry in discover.parse_llms_txt(text, url)})


def lever_terms(levers, sid):
    """Regexes for the flags, keys and variables a column's lever records name."""
    terms = set()
    for rec in levers:
        literal = rec.get("literal")
        if rec.get("surface") != sid or not isinstance(literal, str):
            continue
        token = literal.split("=")[0].strip()
        if len(token) >= 6 and (re.search(r"[-_./]", token) or re.search(r"[A-Z]", token)):
            terms.add(re.escape(token))
    return sorted(terms)


def analyze(inputs, pages, versions, today, only=None):
    """Build the report from fetched pages; pure, so tests drive it with fabricated pages."""
    baseline = inputs["baseline"]
    findings, unknown = [], []
    per_surface = {}
    touched = defaultdict(set)  # url -> evidence ids touched by a change
    quote_intact = 0
    for sid in inputs["order"]:
        if only and sid not in only:
            continue
        records = inputs["evidence"][sid]
        usable, unreachable = {}, set()
        for url in {e["url"] for e in records if e.get("url")}:
            page = pages.get(url)
            row = page["row"] if page else None
            if row and row["outcome"] == "fetched":
                usable[url] = {"raw_text": page["text"], "sha256": row["sha256"]}
            elif row and row["outcome"] != "negative":
                unreachable.add(url)
                unknown.append(
                    {"surface": sid, "kind": "fetch_unknown", "url": url, "why": row["outcome"]}
                )
        reachable = [e for e in records if e.get("url") not in unreachable]
        presence = reverify.check_quote_presence(reachable, usable)
        for kind, ids in (
            (
                "quote_drifted",
                [i for i in presence["drifted_ids"] if presence["status_by_id"][i] == "drifted"],
            ),
            (
                "span_changed",
                [
                    i
                    for i in presence["drifted_ids"]
                    if presence["status_by_id"][i] == "span_changed"
                ],
            ),
            ("page_missing", presence["page_missing_ids"]),
        ):
            for evidence_id in ids:
                findings.append(
                    {"surface": sid, "kind": kind, "severity": "material", "evidence": evidence_id}
                )
        by_id = {e["id"]: e for e in records}
        base_pages = as_dict(as_dict(baseline).get("pages"))
        changed = []
        for url, page in usable.items():
            known = as_dict(base_pages.get(url))
            if known and known.get("sha256") != page["sha256"]:
                changed.append(url)
        for evidence_id, status in presence["status_by_id"].items():
            url = by_id[evidence_id].get("url")
            if status in ("quote_present", "span_unchanged") and url in changed:
                quote_intact += 1
        scope = inputs["scope"].get(sid, {})
        section_info, section_touched = _sections(sid, inputs, usable, scope, baseline, findings)
        for url in changed:
            touched[url] |= section_touched.get(
                url, {e["id"] for e in records if e.get("url") == url}
            )
        _index_changes(sid, inputs, pages, baseline, findings)
        _changelog(sid, inputs, usable, baseline, findings)
        live = as_dict(versions.get(sid))
        if live.get("status") == "unknown":
            unknown.append({"surface": sid, "kind": "version_unknown", "why": "source unreadable"})
        base_version = as_dict(as_dict(as_dict(baseline).get("versions")).get(sid)).get("version")
        if live.get("status") == "ok" and base_version and live.get("version") != base_version:
            findings.append(
                {
                    "surface": sid,
                    "kind": "version_changed",
                    "severity": "info",
                    "was": base_version,
                    "now": live.get("version"),
                }
            )
        per_surface[sid] = {
            "evidence_records": len(records),
            "status": dict(sorted(presence["counts"].items())),
            "pages_changed_since_baseline": len(changed),
            "unreachable_pages": len(unreachable),
            "version": live.get("version"),
            "sections": section_info,
        }
    findings.sort(
        key=lambda f: (
            f["severity"] != "material",
            f["surface"],
            f["kind"],
            str(f.get("evidence") or f.get("url") or f.get("date") or ""),
        )
    )
    material = [f for f in findings if f["severity"] == "material"]
    verdict = "MATERIAL" if material else ("UNKNOWN" if unknown else "CLEAN")
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated": today,
        "verdict": verdict,
        "baseline": "none" if baseline is None else as_dict(baseline).get("accepted"),
        "counts": {
            "material": len(material),
            "info": len(findings) - len(material),
            "unknown": len(unknown),
            "changed_pages_quote_intact": quote_intact,
        },
        "findings": findings,
        "unknown": unknown,
        "surfaces": per_surface,
        "impact": impact(inputs, findings, touched),
    }
    report["baseline_candidate"] = build_baseline(inputs, pages, versions, today, only)
    return report


def _squash(text):
    return " ".join(text.split())


def _sections(sid, inputs, usable, scope, baseline, findings):
    """Section-level change for an aggregate file; returns (summary, {url: touched evidence ids}).

    A cited quote counts as touched only when its text sits in a section whose hash changed, so
    one edited page of a 960 KB file does not touch every record that cites the file.
    """
    out, touched = {}, {}
    for url in as_list(scope.get("gemini_split")):
        page = usable.get(url)
        if not page:
            continue
        texts = split_sections(page["raw_text"], SECTION_HEADINGS["gemini_split"])
        live = {key: sha256_bytes(body.encode("utf-8")) for key, body in texts.items()}
        known = as_dict(as_dict(as_dict(as_dict(baseline).get("pages")).get(url)).get("sections"))
        out[url] = {"sections": len(live)}
        if not known:
            continue
        changed = sorted(k for k in live if k in known and live[k] != known[k])
        added = sorted(set(live) - set(known))
        removed = sorted(set(known) - set(live))
        out[url].update({"changed": len(changed), "added": len(added), "removed": len(removed)})
        for key in changed:
            findings.append(
                {"surface": sid, "kind": "section_changed", "severity": "info", "url": key}
            )
        for key in added:
            if _in_scope(key, sid, inputs):
                findings.append(
                    {
                        "surface": sid,
                        "kind": "page_added_in_scope",
                        "severity": "material",
                        "url": key,
                    }
                )
        for key in removed:
            findings.append(
                {"surface": sid, "kind": "page_removed", "severity": "material", "url": key}
            )
        edited = _squash(" ".join(texts[k] for k in changed + added))
        touched[url] = {
            e["id"]
            for e in inputs["evidence"][sid]
            if e.get("url") == url and e.get("quote") and _squash(e["quote"]) in edited
        }
    return out, touched


def _in_scope(url, sid, inputs):
    scope = inputs["scope"].get(sid, {})
    hosts = inputs["surfaces"][sid]["docs_hosts"]
    https_url = (
        "https://" + url.split("://", 1)[-1]
    )  # the aggregate writes its page URLs as http://
    kept, _ = discover.apply_scope(
        [https_url], hosts, scope.get("include", ()), scope.get("exclude", ())
    )
    return bool(kept)


def index_files(sid, inputs):
    scope = inputs["scope"].get(sid, {})
    return sorted(
        set(
            as_list(scope.get("index_files"))
            + as_list(inputs["surfaces"][sid].get("sitemap_candidates"))
        )
    )


def scoped_links(url, text, sid, inputs):
    """The links of an index file that fall inside the column's scope rules, or None if unreadable."""
    links = index_links(url, text)
    return None if links is None else [link for link in links if _in_scope(link, sid, inputs)]


def _index_changes(sid, inputs, pages, baseline, findings):
    """Pages added to or removed from a column's index files; only in-scope links are kept."""
    cited = {e["url"] for e in inputs["evidence"][sid]}
    known = as_dict(as_dict(as_dict(baseline).get("indexes")).get(sid))
    for url in index_files(sid, inputs):
        page = pages.get(url)
        if not page or page["row"]["outcome"] != "fetched" or url not in known:
            continue
        live = scoped_links(url, page["text"], sid, inputs)
        if live is None:
            continue
        was = set(known[url])
        for link in sorted(set(live) - was):
            findings.append(
                {
                    "surface": sid,
                    "kind": "page_added_in_scope",
                    "severity": "material",
                    "url": link,
                    "index": url,
                }
            )
        for link in sorted(was - set(live)):
            findings.append(
                {
                    "surface": sid,
                    "kind": "page_removed",
                    "severity": "material" if link in cited else "info",
                    "url": link,
                    "index": url,
                }
            )


def _changelog(sid, inputs, usable, baseline, findings):
    since = as_dict(baseline).get("changelog_since") or inputs["snapshot"].get("freeze_end")
    if not since:
        return
    urls = sorted(u for u in usable if CHANGELOG_URL.search(u))
    levers = lever_terms(inputs["levers"], sid)
    for url in urls:
        text = usable[url]["raw_text"]
        for severity, terms in (
            ("material", levers),
            ("info", [re.escape(t) for t in GENERAL_TERMS]),
        ):
            if not terms:
                continue
            for entry in reverify.scan_changelog(text, since, terms):
                if severity == "info" and any(
                    f.get("url") == url
                    and f.get("date") == entry["date"]
                    and f["severity"] == "material"
                    for f in findings
                ):
                    continue
                findings.append(
                    {
                        "surface": sid,
                        "kind": "changelog_lever_entry"
                        if severity == "material"
                        else "changelog_general_entry",
                        "severity": severity,
                        "url": url,
                        "date": entry["date"],
                        "lines": [entry["start_line"], entry["end_line"]],
                        "terms": entry["matched_terms"][:5],
                    }
                )


def _touch(inputs, evidence_ids):
    cells = sorted(
        c["id"]
        for sid in inputs["order"]
        for c in inputs["cells"][sid]
        if evidence_ids & set(c.get("evidence", []))
    )
    rows = {tuple(c.split("/", 1)) for c in cells}
    levers = sum(1 for lv in inputs["levers"] if (lv.get("surface"), lv.get("row")) in rows)
    entries = sorted(r["id"] for r in inputs["register"] if set(r.get("cells", [])) & set(cells))
    return {
        "evidence": len(evidence_ids),
        "cells": cells,
        "lever_records": levers,
        "register_entries": entries,
    }


def impact(inputs, findings, touched):
    """The cells, levers and register entries a change sits under (T2): material, and any change."""
    ids_by_url = defaultdict(set)
    for sid in inputs["order"]:
        for e in inputs["evidence"][sid]:
            ids_by_url[e.get("url")].add(e["id"])
    material = set()
    for f in findings:
        if f["severity"] == "material":
            if f.get("evidence"):
                material.add(f["evidence"])
            elif f.get("url") in ids_by_url:
                material |= ids_by_url[f["url"]]
    changed = set().union(*touched.values()) if touched else set()
    return {"material": _touch(inputs, material), "changed_pages": _touch(inputs, changed)}


def build_baseline(inputs, pages, versions, today, only=None):
    """What an accept writes: the hash of every fetched page, index link lists and versions."""
    old = as_dict(inputs["baseline"])
    out = {
        "schema_version": SCHEMA_VERSION,
        "accepted": today,
        "changelog_since": today,
        "pages": copy.deepcopy(as_dict(old.get("pages"))),
        "indexes": copy.deepcopy(as_dict(old.get("indexes"))),
        "versions": copy.deepcopy(as_dict(old.get("versions"))),
    }
    for sid in inputs["order"]:
        if only and sid not in only:
            continue
        scope = inputs["scope"].get(sid, {})
        for url in sorted({e["url"] for e in inputs["evidence"][sid] if e.get("url")}):
            page = pages.get(url)
            if page and page["row"]["outcome"] == "fetched":
                entry = {"sha256": page["row"]["sha256"]}
                if url in as_list(scope.get("gemini_split")):
                    entry["sections"] = section_hashes(
                        page["text"], SECTION_HEADINGS["gemini_split"]
                    )
                out["pages"][url] = entry
        for url in index_files(sid, inputs):
            page = pages.get(url)
            if page and page["row"]["outcome"] == "fetched":
                links = scoped_links(url, page["text"], sid, inputs)
                if links is not None:
                    out["indexes"].setdefault(sid, {})[url] = links
        live = as_dict(versions.get(sid))
        if live.get("status") == "ok":
            out["versions"][sid] = {"version": live["version"]}
    return out


# --- report ------------------------------------------------------------------------------------


def render_report_md(report):
    """A short summary safe to post: ids, counts, URLs and dates, never vendor prose."""
    lines = [
        f"# Atlas watch: {report['verdict']}",
        "",
        f"Checked {report['generated']} against baseline {report['baseline']}. "
        f"{report['counts']['material']} material, {report['counts']['info']} informational, "
        f"{report['counts']['unknown']} unknown. {report['counts']['changed_pages_quote_intact']} "
        "cited pages changed with their quotes still present.",
        "",
    ]
    if report["verdict"] == "UNKNOWN":
        lines += ["A host could not be reached, so this is **not** a clean result.", ""]
    material = [f for f in report["findings"] if f["severity"] == "material"]
    if material:
        lines += ["## Material findings", ""]
        for kind in sorted({f["kind"] for f in material}):
            group = [f for f in material if f["kind"] == kind]
            lines.append(f"### {kind} ({len(group)})")
            for f in group[:MD_CAP]:
                ref = f.get("evidence") or f.get("url") or ""
                extra = f" {f['date']}" if f.get("date") else ""
                lines.append(f"- {f['surface']} {ref}{extra}")
            if len(group) > MD_CAP:
                lines.append(f"- … {len(group) - MD_CAP} more in report.json")
            lines.append("")
    if report["unknown"]:
        lines += ["## Unknown", ""]
        for u in report["unknown"][:MD_CAP]:
            lines.append(f"- {u['surface']} {u['kind']} {u.get('url', '')} ({u['why']})")
        lines.append("")
    lines += ["## Impact", ""]
    for key, label in (("material", "material findings"), ("changed_pages", "changed pages")):
        part = report["impact"][key]
        lines.append(
            f"- Under {label}: {part['evidence']} evidence records, {len(part['cells'])} cells, "
            f"{part['lever_records']} lever records, {len(part['register_entries'])} register entries."
        )
    lines += [
        "",
        "Revise the touched cells, then `python3 _tools/watch.py accept --report report.json` "
        "in a pull request.",
    ]
    return "\n".join(lines) + "\n"


def write_report(out, report):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    dump_json(out / "report.json", report)
    (out / "report.md").write_text(render_report_md(report), encoding="utf-8", newline="\n")


def run_check(data_dir, out, only=None, today=None, opener=None, workers=6, sleep=None):
    inputs = load_inputs(data_dir)
    today = today or datetime.date.today().isoformat()
    plan = plan_urls(inputs, only)
    pages = collect(inputs, plan, opener, workers, sleep)
    versions = live_versions(inputs, pages, opener, only, sleep)
    report = analyze(inputs, pages, versions, today, only)
    write_report(out, report)
    return report


def accept(data_dir, report_path, force=False):
    report = load_json(report_path)
    if report.get("schema_version") != SCHEMA_VERSION or "baseline_candidate" not in report:
        raise WatchError("not a watch report this version can accept")
    if report["verdict"] != "CLEAN" and not force:
        raise WatchError(
            f"the report is {report['verdict']}: deal with the findings first, or pass --force"
        )
    dump_json(Path(data_dir) / BASELINE_NAME, report["baseline_candidate"])


# --- CLI ---------------------------------------------------------------------------------------


def _selftest():
    if newest_date("Sep 23, 2026 and 2026-08-01") != "2026-09-23":
        raise AssertionError("newest_date")
    text = "# [A](http://x.example/a.md)\nbody\n# [B](http://x.example/b.md)\nbody 2\n"
    got = section_hashes(text, SECTION_HEADINGS["gemini_split"])
    if sorted(got) != ["http://x.example/a.md", "http://x.example/b.md"]:
        raise AssertionError(f"section_hashes: {got}")
    if index_links("https://d.example/api/pagelist/en", "/en\n/en/a\n") != [
        "https://d.example/en",
        "https://d.example/en/a",
    ]:
        raise AssertionError("page list")
    print("OK")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    sub = parser.add_subparsers(dest="command")
    check = sub.add_parser("check")
    check.add_argument("--out", required=True)
    check.add_argument("--surface", action="append")
    check.add_argument("--date")
    check.add_argument("--data-dir", default=str(DATA_DIR))
    check.add_argument("--workers", type=int, default=6)
    acc = sub.add_parser("accept")
    acc.add_argument("--report", required=True)
    acc.add_argument("--force", action="store_true")
    acc.add_argument("--data-dir", default=str(DATA_DIR))
    ver = sub.add_parser("versions")
    ver.add_argument("--surface", action="append")
    ver.add_argument("--data-dir", default=str(DATA_DIR))
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    try:
        if args.command == "check":
            report = run_check(
                args.data_dir, args.out, args.surface, args.date, workers=args.workers
            )
            print(f"watch: {report['verdict']} ({report['counts']}) -> {args.out}/report.md")
            return {"CLEAN": 0, "MATERIAL": 1, "UNKNOWN": 3}[report["verdict"]]
        if args.command == "accept":
            assert_worktree()
            accept(args.data_dir, args.report, args.force)
            print(f"watch: baseline written to {Path(args.data_dir) / BASELINE_NAME}")
            return 0
        if args.command == "versions":
            inputs = load_inputs(args.data_dir)
            plan = plan_urls(inputs, args.surface)
            pages = collect(inputs, plan)
            print(
                json.dumps(
                    live_versions(inputs, pages, only=args.surface), indent=2, sort_keys=True
                )
            )
            return 0
    except WatchError as exc:
        print(f"watch: {exc}", file=sys.stderr)
        return 2
    parser.error("a command (check, accept or versions) or --selftest is required")
    return 2


if __name__ == "__main__":
    sys.exit(main())
