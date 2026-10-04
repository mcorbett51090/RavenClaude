"""Decide which documentation URLs to fetch from vendor-published origins, then prove every origin.

A URL is only ever taken from a place the vendor itself publishes: an index file (llms.txt), a
sitemap, or a link on a page that was already fetched. Nothing here constructs a URL. The source of
every URL is kept, because vendor indexes are not complete (some real pages are linked from pages
but absent from the index, others are only in the sitemap). After fetching, ``provenance`` proves
that every fetched URL has such an origin.

Origin records are JSON lines: {"url", "source": "index" | "sitemap" | "closure", "origin"}, where
``origin`` is the index URL, sitemap URL or linking page URL the URL was found on.

Usage: python3 discover.py index --surface ID --file LLMS_TXT --base URL [--include REGEX ...]
                           [--exclude REGEX ...] [--section NAME ...] --out ORIGINS_JSONL
                           --dropped DROPPED_JSON
       python3 discover.py sitemap --surface ID --file SITEMAP_XML --base URL [--include REGEX ...]
                           [--exclude REGEX ...] --out ORIGINS_JSONL
       python3 discover.py closure --surface ID --known ORIGINS_JSONL [--known ...] --pages-dir DIR
                           --page-map JSON [--include REGEX ...] [--exclude REGEX ...]
                           --out ORIGINS_JSONL
       python3 discover.py provenance --manifest MANIFEST_JSONL --origins ORIGINS_JSONL
                           [--origins ...] --out REPORT_JSON
       python3 discover.py --selftest

``index`` and ``sitemap`` print the SHA-256 digest of the kept URL set on stdout (``sitemap`` then
prints one ``CHILD <url>`` line per child sitemap, for the caller to fetch). Counts go to stderr.

Exit codes: 0 success; 1 ``provenance`` found a fetched row with no origin (read the report);
2 usage error, unreadable or malformed input, or a refused sitemap.
"""

import argparse
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import parse_qsl, urldefrag, urlencode, urljoin, urlsplit, urlunsplit

from atlas_common import DATA_DIR, assert_worktree, dump_json, load_json, sha256_bytes

SOURCES = ("index", "sitemap", "closure")
DROP_REASONS = ("not_https", "off_allow_list", "not_included", "excluded", "wrong_section")

_MD_LINK = re.compile(
    r"(?<!!)\[(?P<text>(?:[^\[\]]|!\[[^\]]*\]\([^)]*\))*)\]"
    r"\(\s*(?:<(?P<angle>[^>\s]*)>|(?P<plain>[^()\s]*(?:\([^()\s]*\)[^()\s]*)*))"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
_HREF = re.compile(r"""\bhref\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)
_BARE_URL = re.compile(r"^\s*(?:[-*+]\s+)?(https?://\S+)\s*$", re.IGNORECASE)
_FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})")
_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
_DTD_DECLARATION = re.compile(r"<!(?:DOCTYPE|ENTITY)", re.IGNORECASE)


class DiscoverError(Exception):
    """A usage or input problem the CLI reports with exit code 2."""


def canonical(url):
    """A comparison key for a URL; the original URL is what gets fetched.

    Lower-cases scheme and host, drops the fragment, a trailing ``/``, one trailing ``.md`` or
    ``.html``, a default ``:443`` port and the query, except a ``pathname`` parameter: it names the
    page for the GitHub Article API (``/api/article/body?pathname=...``), so without it every
    page of that API would compare equal and provenance could not tell them apart.
    """
    parts = urlsplit(url.strip())
    netloc = parts.netloc.lower()
    if parts.scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[: -len(":443")]
    path = parts.path.rstrip("/")
    for suffix in (".md", ".html"):
        if path.endswith(suffix):
            path = path[: -len(suffix)]
            break
    identity = [(key, value) for key, value in parse_qsl(parts.query) if key == "pathname"]
    return urlunsplit((parts.scheme, netloc, path, urlencode(sorted(identity)), ""))


def _try_canonical(url):
    try:
        return canonical(url)
    except ValueError:
        return None


def _as_tuple(value):
    return (value,) if isinstance(value, str) else tuple(value)


def _resolve(base_url, target):
    """Resolve ``target`` against ``base_url``, drop the fragment; None unless http or https."""
    target = target.strip()
    if not target:
        return None
    try:
        absolute, _fragment = urldefrag(urljoin(base_url, target))
        scheme = urlsplit(absolute).scheme
    except ValueError:
        return None
    return absolute if scheme in ("http", "https") else None


def _outside_fences(lines):
    """Yield each line that is not inside a fenced code block; the fence lines are dropped."""
    fence = None
    for line in lines:
        if fence is None:
            opened = _FENCE_OPEN.match(line)
            if opened and not (opened.group(1)[0] == "`" and "`" in line[opened.end() :]):
                fence = opened.group(1)
                continue
            yield line
            continue
        closer = line.strip()
        if closer and set(closer) == {fence[0]} and len(closer) >= len(fence):
            fence = None


def parse_llms_txt(text, base_url):
    """Entries ``{"url", "title", "section"}`` in file order, deduplicated by ``canonical``.

    Finds Markdown links anywhere on a line and lines that are only a bare URL (an optional list
    marker is allowed). ``section`` is the most recent ``## `` heading, or "". Links inside fenced
    code blocks and links that do not resolve to http or https are ignored.
    """
    entries = []
    seen = set()
    section = ""
    for line in _outside_fences(text.splitlines()):
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        bare = _BARE_URL.match(line)
        if bare:
            found = [("", bare.group(1))]
        else:
            found = [
                (m.group("text").strip(), m.group("angle") or m.group("plain"))
                for m in _MD_LINK.finditer(line)
            ]
        for title, target in found:
            url = _resolve(base_url, target)
            if url is None:
                continue
            key = canonical(url)
            if key in seen:
                continue
            seen.add(key)
            entries.append({"url": url, "title": title, "section": section})
    return entries


def _local_name(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def parse_sitemap(xml_text):
    """``{"urls": [...], "sitemaps": [...]}`` from a ``<urlset>`` or a ``<sitemapindex>``.

    Matches on local tag names (namespaces are ignored) and only reads a ``<loc>`` that is a direct
    child of ``<url>`` or ``<sitemap>``, so image and video ``loc`` elements are not taken. A
    document containing ``<!DOCTYPE`` or ``<!ENTITY`` is refused (``ValueError``) before parsing,
    so no entity or DTD is ever processed. Malformed XML and any other root also raise
    ``ValueError``.
    """
    if _DTD_DECLARATION.search(xml_text):
        raise ValueError("sitemap refused: it contains a DOCTYPE or ENTITY declaration")
    try:
        root = ET.fromstring(xml_text.lstrip("﻿ \t\r\n"))
    except ET.ParseError as exc:
        raise ValueError(f"sitemap is not well-formed XML: {exc}") from exc
    kinds = {"urlset": ("url", "urls"), "sitemapindex": ("sitemap", "sitemaps")}
    root_name = _local_name(root.tag)
    if root_name not in kinds:
        raise ValueError(f"not a sitemap: root element is <{root_name}>")
    item_name, bucket = kinds[root_name]
    result = {"urls": [], "sitemaps": []}
    for item in root:
        if _local_name(item.tag) != item_name:
            continue
        for child in item:
            if _local_name(child.tag) == "loc" and child.text and child.text.strip():
                result[bucket].append(child.text.strip())
    return result


def extract_links(page_text, page_url):
    """Markdown ``[text](target)`` links and HTML ``href`` values, resolved against ``page_url``.

    Fragments are stripped, only http and https are kept, links are deduplicated by ``canonical``
    in order of first appearance, and links inside fenced code blocks and inline code spans are
    skipped. Images (``![alt](src)``) are not links.
    """
    lines = (_CODE_SPAN.sub(" ", line) for line in _outside_fences(page_text.splitlines()))
    text = "\n".join(lines)
    found = [(m.start(), m.group("angle") or m.group("plain")) for m in _MD_LINK.finditer(text)]
    for m in _HREF.finditer(text):
        value = m.group(1) if m.group(1) is not None else m.group(2)
        found.append((m.start(), html.unescape(value)))
    found.sort(key=lambda pair: pair[0])
    links = []
    seen = set()
    for _position, target in found:
        url = _resolve(page_url, target)
        if url is None:
            continue
        key = canonical(url)
        if key not in seen:
            seen.add(key)
            links.append(url)
    return links


def _scope_reason(url, hosts, include, exclude):
    """The first reason a URL is out of scope, or None. Section is tested by the caller."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return "not_https"
    if parts.scheme != "https":
        return "not_https"
    try:
        port = parts.port
    except ValueError:
        return "off_allow_list"
    if (parts.hostname or "").lower() not in hosts or port not in (None, 443):
        return "off_allow_list"
    if include and not any(pattern.search(parts.path) for pattern in include):
        return "not_included"
    if any(pattern.search(parts.path) for pattern in exclude):
        return "excluded"
    return None


def apply_scope(entries_or_urls, allow_hosts, include=(), exclude=(), sections=None):
    """Split items into ``(kept, dropped)``; each dropped item is ``{"url", "reason"}``.

    An item is a URL string or a dict with a ``url`` (and optionally a ``section``). It is kept only
    when it is https, on an allow-listed host (exact, case-insensitive, default port only), its
    path matches at least one ``include`` regex (when any are given; ``re.search``), matches no
    ``exclude`` regex, and, when ``sections`` is given, its ``section`` is one of them
    (case-insensitive; an item with no ``section`` key is exempt). Reasons: ``DROP_REASONS``.
    """
    hosts = {host.lower() for host in _as_tuple(allow_hosts)}
    include = [re.compile(pattern) for pattern in _as_tuple(include)]
    exclude = [re.compile(pattern) for pattern in _as_tuple(exclude)]
    wanted = None if sections is None else {s.strip().casefold() for s in _as_tuple(sections)}
    kept = []
    dropped = []
    for item in entries_or_urls:
        url = item["url"] if isinstance(item, dict) else item
        reason = _scope_reason(url, hosts, include, exclude)
        if (
            reason is None
            and wanted is not None
            and isinstance(item, dict)
            and "section" in item
            and str(item["section"]).strip().casefold() not in wanted
        ):
            reason = "wrong_section"
        if reason is None:
            kept.append(item)
        else:
            dropped.append({"url": url, "reason": reason})
    return kept, dropped


def closure_candidates(known_urls, pages, allow_hosts, include=(), exclude=()):
    """One hop of link closure: in-scope links on fetched pages that are not already known.

    ``pages`` maps a fetched page URL to its text. Returns ``{"url", "sources"}`` sorted by url,
    where ``sources`` are the sorted page URLs that link to it. "Known" is compared by ``canonical``.
    """
    known = {key for key in map(_try_canonical, known_urls) if key is not None}
    found = {}
    for page_url in sorted(pages):
        links = extract_links(pages[page_url], page_url)
        kept, _dropped = apply_scope(links, allow_hosts, include, exclude)
        for url in kept:
            key = canonical(url)
            if key not in known:
                found.setdefault(key, {"url": url, "sources": set()})["sources"].add(page_url)
    return [
        {"url": entry["url"], "sources": sorted(entry["sources"])}
        for entry in sorted(found.values(), key=lambda entry: entry["url"])
    ]


def url_set_digest(urls):
    """SHA-256 hex of the sorted, de-duplicated, newline-joined ``canonical`` forms."""
    keys = sorted({canonical(url) for url in urls})
    return sha256_bytes("\n".join(keys).encode("utf-8"))


def provenance(manifest_rows, origins):
    """Prove that every fetched manifest row has an origin.

    ``rows`` counts the fetched rows (the ones that need an origin), so ``rows == traced +
    len(untraced)``. A fetched row is traced when its ``url`` has the same ``canonical`` as some
    origin's ``url``. ``by_source`` counts each traced row once, under the most authoritative of
    its origins (index, then sitemap, then closure), so it sums to ``traced``.
    """
    best = {}
    for record in origins:
        source = record["source"]
        if source not in SOURCES:
            raise ValueError(f"unknown origin source {source!r} for {record.get('url')!r}")
        key = _try_canonical(record["url"])
        if key is not None and (key not in best or SOURCES.index(source) < best[key]):
            best[key] = SOURCES.index(source)
    fetched = [row for row in manifest_rows if row.get("outcome") == "fetched"]
    by_source = dict.fromkeys(SOURCES, 0)
    untraced = []
    for row in fetched:
        key = _try_canonical(row.get("url", ""))
        if key is not None and key in best:
            by_source[SOURCES[best[key]]] += 1
        else:
            untraced.append(row.get("url", ""))
    return {
        "rows": len(fetched),
        "traced": len(fetched) - len(untraced),
        "untraced": untraced,
        "by_source": by_source,
    }


def _surface_hosts(surface_id):
    surfaces = load_json(DATA_DIR / "surfaces.json")["surfaces"]
    for surface in surfaces:
        if surface["id"] == surface_id:
            return list(surface["docs_hosts"])
    known = ", ".join(sorted(s["id"] for s in surfaces))
    raise DiscoverError(f"unknown surface {surface_id!r}; known: {known}")


def _read_jsonl(path, required=()):
    records = []
    with open(path, encoding="utf-8") as fh:
        for number, raw in enumerate(fh, start=1):
            if not raw.strip():
                continue
            try:
                record = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise DiscoverError(f"{path}:{number}: not valid JSON: {exc}") from exc
            if not isinstance(record, dict) or any(key not in record for key in required):
                raise DiscoverError(f"{path}:{number}: expected an object with {list(required)}")
            records.append(record)
    return records


def _write_origins(path, records):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for url, source, origin in records:
            row = {"url": url, "source": source, "origin": origin}
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def _flat(groups):
    return [value for group in groups for value in group]


def _dedupe_by_canonical(urls):
    seen = set()
    unique = []
    for url in urls:
        key = _try_canonical(url)
        if key is not None and key not in seen:
            seen.add(key)
            unique.append(url)
    return unique


def _cmd_index(args):
    hosts = _surface_hosts(args.surface)
    text = Path(args.file).read_text(encoding="utf-8")
    entries = parse_llms_txt(text, args.base)
    sections = set(_flat(args.section)) or None
    kept, dropped = apply_scope(
        entries, hosts, _flat(args.include), _flat(args.exclude), sections=sections
    )
    urls = [entry["url"] for entry in kept]
    _write_origins(args.out, [(url, "index", args.base) for url in urls])
    dump_json(args.dropped, dropped)
    print(url_set_digest(urls))
    print(f"discover: index kept {len(kept)}, dropped {len(dropped)}", file=sys.stderr)
    return 0


def _cmd_sitemap(args):
    hosts = _surface_hosts(args.surface)
    text = Path(args.file).read_text(encoding="utf-8")
    try:
        parsed = parse_sitemap(text)
    except ValueError as exc:
        raise DiscoverError(str(exc)) from exc
    urls = _dedupe_by_canonical(parsed["urls"])
    kept, dropped = apply_scope(urls, hosts, _flat(args.include), _flat(args.exclude))
    _write_origins(args.out, [(url, "sitemap", args.base) for url in kept])
    print(url_set_digest(kept))
    children, off_list = apply_scope(_dedupe_by_canonical(parsed["sitemaps"]), hosts)
    for child in children:
        print(f"CHILD {child}")
    for item in off_list:
        print(
            f"discover: child sitemap not listed ({item['reason']}): {item['url']}", file=sys.stderr
        )
    print(
        f"discover: sitemap kept {len(kept)}, dropped {len(dropped)}, children {len(children)}",
        file=sys.stderr,
    )
    return 0


def _cmd_closure(args):
    hosts = _surface_hosts(args.surface)
    known = []
    for path in _flat(args.known):
        known.extend(record["url"] for record in _read_jsonl(path, required=("url",)))
    page_map = load_json(args.page_map)
    if not isinstance(page_map, dict):
        raise DiscoverError(f"{args.page_map}: expected a JSON object mapping page URL to file")
    pages = {}
    for page_url, name in page_map.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise DiscoverError(f"page file {name!r} for {page_url} is outside --pages-dir")
        pages[page_url] = (Path(args.pages_dir) / relative).read_text(
            encoding="utf-8", errors="replace"
        )
    candidates = closure_candidates(known, pages, hosts, _flat(args.include), _flat(args.exclude))
    _write_origins(
        args.out,
        [(c["url"], "closure", page) for c in candidates for page in c["sources"]],
    )
    print(
        f"discover: closure found {len(candidates)} new URLs from {len(pages)} pages",
        file=sys.stderr,
    )
    return 0


def page_map(rows, skip_urls=()):
    """``{url: raw_path}`` for each fetched page row, in manifest order, newest row per URL wins.

    Only rows with ``outcome == "fetched"`` and a ``raw_path`` count. ``skip_urls`` (compared by
    ``canonical``) leaves out index and sitemap files, which are origins and not pages.
    """
    skip = {key for key in map(_try_canonical, skip_urls) if key is not None}
    mapping = {}
    for row in rows:
        url = row.get("url")
        if row.get("outcome") != "fetched" or not row.get("raw_path") or not url:
            continue
        if _try_canonical(url) in skip:
            mapping.pop(url, None)
            continue
        mapping[url] = row["raw_path"]
    return mapping


def _cmd_pagemap(args):
    skip = []
    for path in _flat(args.skip_file):
        skip.extend(
            line.strip()
            for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    mapping = page_map(_read_jsonl(args.manifest, required=("url",)), skip)
    dump_json(args.out, mapping)
    print(f"discover: pagemap holds {len(mapping)} pages", file=sys.stderr)
    return 0


def _cmd_provenance(args):
    rows = _read_jsonl(args.manifest)
    origins = []
    for path in _flat(args.origins):
        origins.extend(_read_jsonl(path, required=("url", "source", "origin")))
    try:
        report = provenance(rows, origins)
    except ValueError as exc:
        raise DiscoverError(str(exc)) from exc
    dump_json(args.out, report)
    print(
        f"discover: provenance traced {report['traced']} of {report['rows']} fetched rows",
        file=sys.stderr,
    )
    for url in report["untraced"]:
        print(f"discover: UNTRACED {url}", file=sys.stderr)
    return 1 if report["untraced"] else 0


def _selftest():
    def check(condition, message):
        if not condition:
            raise AssertionError(message)

    base = "https://docs.example/llms.txt"
    index = (
        "# Docs\n\n## Core\n- [A](/docs/a.md): first\n- [B](https://docs.example/docs/b)\n"
        "- [A again](/docs/a)\n```\n[Fenced](/docs/fenced)\n```\n[Mail](mailto:x@y.example)\n"
        "[Other](https://elsewhere.example/c)\n"
    )
    entries = parse_llms_txt(index, base)
    check(
        [e["url"] for e in entries]
        == [
            "https://docs.example/docs/a.md",
            "https://docs.example/docs/b",
            "https://elsewhere.example/c",
        ],
        f"unexpected entries: {entries}",
    )
    kept, dropped = apply_scope(entries, {"docs.example"})
    urls = [e["url"] for e in kept]
    check(
        len(urls) == 2
        and dropped == [{"url": "https://elsewhere.example/c", "reason": "off_allow_list"}],
        f"unexpected scope result: {kept} {dropped}",
    )
    page = "[B](/docs/b.md) [New](/docs/new#top) `[code](/docs/code)`"
    page_url = "https://docs.example/docs/a.md"
    candidates = closure_candidates(urls, {page_url: page}, {"docs.example"})
    check(
        candidates == [{"url": "https://docs.example/docs/new", "sources": [page_url]}],
        f"unexpected closure: {candidates}",
    )
    sitemap = (
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        "<url><loc>https://docs.example/docs/s</loc></url></urlset>"
    )
    check(parse_sitemap(sitemap)["urls"] == ["https://docs.example/docs/s"], "sitemap not parsed")
    try:
        parse_sitemap('<!DOCTYPE x [<!ENTITY e "v">]><urlset/>')
    except ValueError:
        pass
    else:
        raise AssertionError("a DOCTYPE sitemap was not refused")
    origins = [{"url": u, "source": "index", "origin": base} for u in urls]
    origins.append({"url": candidates[0]["url"], "source": "closure", "origin": page_url})
    rows = [{"url": u, "outcome": "fetched"} for u in urls + [candidates[0]["url"]]]
    rows.append({"url": "https://docs.example/docs/unknown", "outcome": "fetched"})
    report = provenance(rows, origins)
    check(
        report["rows"] == 4
        and report["traced"] == 3
        and report["untraced"] == ["https://docs.example/docs/unknown"]
        and report["by_source"] == {"index": 2, "sitemap": 0, "closure": 1},
        f"unexpected provenance: {report}",
    )
    print("OK")


def _add_list_option(parser, name, **kwargs):
    parser.add_argument(name, nargs="+", action="append", default=[], **kwargs)


def _build_parser():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    commands = parser.add_subparsers(dest="command")

    index = commands.add_parser("index", help="origins from an llms.txt index")
    index.add_argument("--surface", required=True)
    index.add_argument("--file", required=True)
    index.add_argument("--base", required=True)
    _add_list_option(index, "--include")
    _add_list_option(index, "--exclude")
    _add_list_option(index, "--section")
    index.add_argument("--out", required=True)
    index.add_argument("--dropped", required=True)
    index.set_defaults(handler=_cmd_index)

    sitemap = commands.add_parser("sitemap", help="origins from a sitemap")
    sitemap.add_argument("--surface", required=True)
    sitemap.add_argument("--file", required=True)
    sitemap.add_argument("--base", required=True)
    _add_list_option(sitemap, "--include")
    _add_list_option(sitemap, "--exclude")
    sitemap.add_argument("--out", required=True)
    sitemap.set_defaults(handler=_cmd_sitemap)

    closure = commands.add_parser("closure", help="origins from links on fetched pages")
    closure.add_argument("--surface", required=True)
    _add_list_option(closure, "--known", required=True)
    closure.add_argument("--pages-dir", required=True)
    closure.add_argument("--page-map", required=True)
    _add_list_option(closure, "--include")
    _add_list_option(closure, "--exclude")
    closure.add_argument("--out", required=True)
    closure.set_defaults(handler=_cmd_closure)

    pages = commands.add_parser("pagemap", help="map fetched page URLs to raw files for closure")
    pages.add_argument("--manifest", required=True)
    _add_list_option(pages, "--skip-file")
    pages.add_argument("--out", required=True)
    pages.set_defaults(handler=_cmd_pagemap)

    proof = commands.add_parser("provenance", help="prove every fetched row has an origin")
    proof.add_argument("--manifest", required=True)
    _add_list_option(proof, "--origins", required=True)
    proof.add_argument("--out", required=True)
    proof.set_defaults(handler=_cmd_provenance)
    return parser


def main(argv=None):
    assert_worktree()
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    if not args.command:
        parser.error("choose a command: index, sitemap, closure, pagemap or provenance (or --selftest)")
    try:
        return args.handler(args)
    except (DiscoverError, OSError) as exc:
        print(f"discover: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
