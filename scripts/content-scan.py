#!/usr/bin/env python3
"""content-scan.py — discover articles on a topic via a search API, digest them.

Why this exists
---------------
There is **no official API to read or search third-party LinkedIn posts/articles**
(LinkedIn's Posts API covers your own org only), and scraping LinkedIn article
*bodies* is ToS-prohibited and actively litigated (LinkedIn sued Proxycurl in
early 2025; the service shut down). So this script does NOT scrape LinkedIn.

What it does instead is the legitimate path: it uses a **web Search API** to
*discover* relevant articles on your topics — which surfaces LinkedIn article
titles + URLs + snippets the same way a normal search does — and then fetches
**full text only from the open web** (Substack / Medium / blogs / company
sites), where thought leaders typically cross-post the same content. LinkedIn
(and Reddit) URLs are kept as *discovery-only* rows: title + snippet + link,
never a body fetch. This mirrors `reddit-scan.py` and writes into the same
`docs/research/…` workflow.

Boundary baked in (NEVER_FETCH): no automated body fetch of linkedin.com or
reddit.com — only their public search snippets. No UA-spoofing, proxies, or
anti-bot evasion anywhere.

Search backend
--------------
Defaults to the **Brave Search API** (independent, documented REST, has a free
tier). Get a key at https://brave.com/search/api/ and set:

    SEARCH_API_KEY=...            # required (Brave subscription token)
    SEARCH_API_URL=...            # optional; defaults to Brave web-search endpoint

The result-parsing is isolated in `parse_brave()` so another backend (Bing,
Google Programmable Search) can be slotted in by adding a parser.

Usage
-----
    export SEARCH_API_KEY=...
    python3 scripts/content-scan.py \
        --queries "fractional CFO AI" "month-end close automation" \
        --count 15 --freshness pm --fetch-bodies \
        --out docs/research/$(date +%F)-content-scan

Writes `<out>/<slug>.json` per query (raw results, trimmed) and a combined
`<out>/digest.md` (ranked table + per-article notes, open-web bodies excerpted).
Stdlib-only. Exits non-zero on missing key / API failure so CI fails loudly.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"
# Discovery-only hosts: we use their SEARCH SNIPPETS but never fetch/scrape the
# body (crawler-blocked and/or ToS-prohibited — LinkedIn especially, post-hiQ /
# post-Proxycurl). The ethical boundary, enforced in code.
NEVER_FETCH = ("linkedin.com", "reddit.com")
UA = "ravenclaude-content-scan/1.0 (marketplace research; +https://github.com/mcorbett51090/RavenClaude)"
BODY_CAP = 4000  # chars of extracted text kept per open-web article


def _die(msg: str, code: int = 1) -> None:
    print(f"content-scan: ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _host(url: str) -> str:
    # Use .hostname (not .netloc): netloc keeps any userinfo, so a URL like
    # https://linkedin.com@evil.com/x would yield host "linkedin.com@evil.com" and
    # let an attacker-controlled host satisfy a never-fetch/allow check. .hostname
    # strips userinfo + port and is already lowercased.
    try:
        return (urllib.parse.urlparse(url).hostname or "").lower()
    except ValueError:
        return ""


def _is_never_fetch(url: str) -> bool:
    h = _host(url)
    return any(h == d or h.endswith("." + d) for d in NEVER_FETCH)


def search(query: str, count: int, freshness: str | None, site: str | None) -> list[dict]:
    """Query the Search API. Returns Brave's web results list."""
    key = os.environ.get("SEARCH_API_KEY")
    if not key:
        _die("SEARCH_API_KEY must be set (Brave Search API token — see module docstring).")
    q = f"site:{site} {query}" if site else query
    params = {"q": q, "count": min(count, 20)}
    if freshness:
        params["freshness"] = freshness  # Brave: pd / pw / pm / py
    url = (os.environ.get("SEARCH_API_URL") or BRAVE_URL) + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "X-Subscription-Token": key,
            "User-Agent": UA,
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return parse_brave(json.loads(resp.read().decode()))
        except urllib.error.HTTPError as e:
            if e.code == 429:  # rate limited — back off
                time.sleep(2 ** attempt)
                continue
            _die(f"search API HTTP {e.code} for {query!r}: {e.read().decode(errors='replace')[:200]}")
        except urllib.error.URLError as e:
            _die(f"could not reach search API ({e.reason}). Check SEARCH_API_URL / network.")
    _die(f"search API rate-limited after retries for {query!r}")
    return []  # unreachable


def parse_brave(payload: dict) -> list[dict]:
    out = []
    for r in payload.get("web", {}).get("results", []):
        out.append(
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "description": r.get("description", ""),
                "age": r.get("age", "") or r.get("page_age", ""),
                "host": _host(r.get("url", "")),
            }
        )
    return out


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _resolves_to_public_ip(url: str) -> bool:
    """True only if the URL's host resolves entirely to public IPs. Rejects
    loopback, private, link-local (incl. the 169.254.169.254 cloud-metadata
    endpoint), reserved, multicast, and unspecified addresses.

    Search-result URLs are attacker-influenceable (an SEO-poisoned result, or a
    hostile SEARCH_API_URL override), so without this a result pointing at
    http://169.254.169.254/… or http://127.0.0.1:… would be fetched and its
    body written into the committed digest — an SSRF-to-metadata exfiltration.
    Residual TOCTOU note: this resolves the host and the subsequent urlopen
    resolves again, so a DNS-rebind between the two is not fully closed here;
    this is a best-effort guard for an opt-in, human-invoked tool, matching the
    scheme-only guard it strengthens."""
    host = urllib.parse.urlparse(url).hostname
    if not host:
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except (socket.gaierror, UnicodeError, ValueError, OSError):
        return False
    if not infos:
        return False
    for info in infos:
        ip = info[4][0]
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False
        if (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_reserved
            or addr.is_multicast
            or addr.is_unspecified
        ):
            return False
    return True


def fetch_body_excerpt(url: str) -> str:
    """Fetch an OPEN-WEB article and return a crude text excerpt. Never called
    for NEVER_FETCH hosts. Fail-safe: returns '' on any error."""
    # SSRF guard: urllib will happily open file://, ftp://, etc. We only ever
    # want real web articles — refuse anything that isn't http/https so a
    # hostile search result can't coax a local-file or non-web fetch. The check
    # is repeated on the FINAL resolved URL after urlopen, because urllib follows
    # redirects by default and the input-URL check alone wouldn't catch a 3xx that
    # lands on a non-web scheme. Beyond scheme, we also reject any host that
    # resolves to a private/loopback/link-local/metadata IP (SSRF hardening).
    if urllib.parse.urlparse(url).scheme not in ("http", "https"):
        return ""
    if not _resolves_to_public_ip(url):
        return ""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            final = getattr(resp, "url", None) or url
            if urllib.parse.urlparse(final).scheme not in ("http", "https"):
                return ""
            if not _resolves_to_public_ip(final):
                return ""
            ctype = resp.headers.get("Content-Type", "")
            if "html" not in ctype and "text" not in ctype:
                return ""
            raw = resp.read(400_000).decode(errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError):
        return ""
    # Strip script/style, then tags, then collapse whitespace. Crude but stdlib.
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    text = _WS_RE.sub(" ", _TAG_RE.sub(" ", raw)).strip()
    return text[:BODY_CAP]


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "query"


def main() -> None:
    ap = argparse.ArgumentParser(description="Discover + digest articles on a topic via a search API.")
    ap.add_argument("--queries", nargs="+", required=True, help="one or more topic queries")
    ap.add_argument("--count", type=int, default=15, help="results per query (<=20)")
    ap.add_argument("--freshness", default=None, choices=["pd", "pw", "pm", "py"], help="recency window")
    ap.add_argument("--site", default=None, help="restrict to one domain (e.g. linkedin.com for discovery-only)")
    ap.add_argument("--fetch-bodies", action="store_true", help="fetch full text of OPEN-WEB results (skips LinkedIn/Reddit)")
    ap.add_argument("--out", default=None, help="output dir; if unset, prints digest to stdout")
    args = ap.parse_args()

    all_results: list[dict] = []
    for q in args.queries:
        results = search(q, args.count, args.freshness, args.site)
        for r in results:
            r["query"] = q
            if args.fetch_bodies and not _is_never_fetch(r["url"]):
                r["body_excerpt"] = fetch_body_excerpt(r["url"])
                time.sleep(1)  # courteous pacing
            elif _is_never_fetch(r["url"]):
                r["body_excerpt"] = ""  # discovery-only; snippet is all we use
            all_results.append(r)
        if args.out:
            os.makedirs(args.out, exist_ok=True)
            with open(os.path.join(args.out, f"{slug(q)}.json"), "w", encoding="utf-8") as f:
                json.dump([r for r in all_results if r["query"] == q], f, indent=2, ensure_ascii=False)
        time.sleep(1)

    digest = _render_digest(all_results, args)
    if args.out:
        with open(os.path.join(args.out, "digest.md"), "w", encoding="utf-8") as f:
            f.write(digest)
        print(f"content-scan: wrote {len(all_results)} results -> {args.out}/digest.md")
    else:
        print(digest)


def _render_digest(results: list[dict], args) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    lines = [
        f"# Content scan digest — {now}",
        "",
        f"Queries: {', '.join(args.queries)}"
        + (f" · freshness: {args.freshness}" if args.freshness else "")
        + (f" · site: {args.site}" if args.site else ""),
        f"{len(results)} results. LinkedIn/Reddit rows are **discovery-only** "
        "(title+snippet+link; body not fetched, by design).",
        "",
        "| Source | Title | Link |",
        "| --- | --- | --- |",
    ]
    for r in results:
        tag = "discovery" if _is_never_fetch(r["url"]) else r["host"]
        title = r["title"].replace("|", "\\|")[:110]
        lines.append(f"| {tag} | {title} | [link]({r['url']}) |")
    # Per-article notes for open-web bodies we excerpted.
    excerpted = [r for r in results if r.get("body_excerpt")]
    if excerpted:
        lines += ["", "## Open-web excerpts", ""]
        for r in excerpted:
            lines += [
                f"### [{r['title'][:120]}]({r['url']})",
                f"_{r['host']}_ · {r.get('age', '')}",
                "",
                r["body_excerpt"][:1200] + ("…" if len(r["body_excerpt"]) > 1200 else ""),
                "",
            ]
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
