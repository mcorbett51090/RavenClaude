#!/usr/bin/env python3
"""reddit-scan.py — pull subreddit data through Reddit's OFFICIAL Data API.

Why this exists
---------------
`reddit.com` is blocked for Anthropic's web crawler, so a Claude Code session
cannot read subreddits via WebFetch/WebSearch. The sanctioned way "around" that
block is the front door: Reddit's official OAuth2 Data API, called with your own
app credentials. This script is that front door — it authenticates with a
registered app, reads public subreddit listings within the free tier's limits,
and writes the results to disk for the recurring `docs/research/*-claude-
subreddit-scan/` workflow.

This is NOT circumvention. It does not spoof a user-agent to evade a block, use
proxies, or touch any anti-bot surface. It uses the documented API with a
required, honestly-identifying User-Agent (Reddit's API *mandates* a unique UA
string — that requirement is the opposite of spoofing).

Auth & limits (free tier, verified 2026-06-10 against Reddit Data API docs)
---------------------------------------------------------------------------
* Create a **"script"-type app** at https://www.reddit.com/prefs/apps
  (redirect URI http://localhost:8080) → you get a client id + secret.
* This script uses the **application-only OAuth** (`client_credentials`) grant:
  client id + secret only, no password, read-only — all that public subreddit
  reads need.
* Free tier: OAuth required, ~100 requests/min, **non-commercial use only**
  (personal/research/open-source). Commercial use needs a paid contract.
  Sources: https://support.reddithelp.com/hc/en-us/articles/16160319875092
           https://redaccs.com/reddit-api-guide/

Credentials (env vars — never hard-code, never commit)
------------------------------------------------------
    REDDIT_CLIENT_ID        (required)
    REDDIT_CLIENT_SECRET    (required)
    REDDIT_USER_AGENT       (optional; a sensible default is built if unset)

Usage
-----
    export REDDIT_CLIENT_ID=...  REDDIT_CLIENT_SECRET=...
    python3 scripts/reddit-scan.py \
        --subreddits ClaudeAI Claude ClaudeCode \
        --listing top --time month --limit 50 \
        --min-score 25 \
        --out docs/research/$(date +%F)-claude-subreddit-scan/raw

Writes `<out>/<subreddit>.<listing>.json` (raw API posts, trimmed) and a single
`<out>/digest.md` (scannable table of the kept posts across all subreddits).
Stdlib-only — no pip install. Exit non-zero on auth/credential failure so CI
fails loudly rather than silently producing an empty scan.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_BASE = "https://oauth.reddit.com"
# Reddit's API requires a unique, descriptive User-Agent. This is mandated by
# the API rules and identifies the client honestly — it is not UA spoofing.
DEFAULT_UA = "ravenclaude-subreddit-scan/1.0 (marketplace research; +https://github.com/mcorbett51090/RavenClaude)"


def _die(msg: str, code: int = 1) -> None:
    print(f"reddit-scan: ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def get_token(client_id: str, client_secret: str, user_agent: str) -> str:
    """Application-only OAuth2 (client_credentials). Read-only, no password."""
    body = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=body,
        headers={
            "Authorization": f"Basic {basic}",
            "User-Agent": user_agent,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        _die(
            f"token request failed (HTTP {e.code}). Check REDDIT_CLIENT_ID/SECRET "
            f"and that the app is a 'script' type. Body: {detail}"
        )
    except urllib.error.URLError as e:
        _die(
            f"could not reach {TOKEN_URL} ({e.reason}). If this host blocks "
            "reddit.com, run this script from CI or a local machine instead."
        )
    token = payload.get("access_token")
    if not token:
        _die(f"no access_token in token response: {payload}")
    return token


def fetch_listing(
    token: str,
    user_agent: str,
    subreddit: str,
    listing: str,
    time_filter: str,
    limit: int,
) -> list[dict]:
    """Fetch one subreddit listing. Paginates with `after` up to `limit`."""
    out: list[dict] = []
    after: str | None = None
    while len(out) < limit:
        page = min(100, limit - len(out))  # API max page size is 100
        params = {"limit": page, "raw_json": 1}
        if listing == "top":
            params["t"] = time_filter
        if after:
            params["after"] = after
        url = f"{API_BASE}/r/{subreddit}/{listing}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {token}", "User-Agent": user_agent}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                _respect_rate_limit(resp.headers)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5)
                continue
            print(
                f"reddit-scan: WARN: r/{subreddit} {listing} HTTP {e.code}; skipping",
                file=sys.stderr,
            )
            break
        except urllib.error.URLError as e:
            print(f"reddit-scan: WARN: r/{subreddit} unreachable ({e.reason})", file=sys.stderr)
            break
        children = data.get("data", {}).get("children", [])
        if not children:
            break
        for c in children:
            out.append(c.get("data", {}))
        after = data.get("data", {}).get("after")
        if not after:
            break
        time.sleep(1)  # courteous pacing well under 100 req/min
    return out[:limit]


def _respect_rate_limit(headers) -> None:
    """If the rolling-window remaining quota is low, pause until it resets."""
    try:
        remaining = float(headers.get("x-ratelimit-remaining", "100"))
        reset = float(headers.get("x-ratelimit-reset", "0"))
    except (TypeError, ValueError):
        return
    if remaining <= 2 and reset > 0:
        time.sleep(min(reset + 1, 60))


def trim(post: dict) -> dict:
    """Keep only the fields the scan reasons over — no PII beyond public author."""
    return {
        "title": post.get("title", ""),
        "score": post.get("score", 0),
        "num_comments": post.get("num_comments", 0),
        "author": post.get("author", ""),
        "created_utc": post.get("created_utc", 0),
        "permalink": "https://www.reddit.com" + post.get("permalink", ""),
        "url": post.get("url", ""),
        "selftext": (post.get("selftext", "") or "")[:2000],
        "link_flair_text": post.get("link_flair_text", ""),
        "subreddit": post.get("subreddit", ""),
    }


def matches(post: dict, min_score: int, keywords: list[str]) -> bool:
    if post.get("score", 0) < min_score:
        return False
    if not keywords:
        return True
    hay = (post.get("title", "") + " " + post.get("selftext", "")).lower()
    return any(k.lower() in hay for k in keywords)


def main() -> None:
    ap = argparse.ArgumentParser(description="Pull subreddit data via Reddit's official API.")
    ap.add_argument("--subreddits", nargs="+", required=True, help="e.g. ClaudeAI Claude")
    ap.add_argument("--listing", default="top", choices=["top", "hot", "new", "rising"])
    ap.add_argument("--time", default="month", choices=["hour", "day", "week", "month", "year", "all"])
    ap.add_argument("--limit", type=int, default=50, help="max posts per subreddit (<=1000)")
    ap.add_argument("--min-score", type=int, default=0, help="drop posts below this score")
    ap.add_argument("--keywords", nargs="*", default=[], help="optional title/body filters (OR)")
    ap.add_argument("--out", default=None, help="output dir; if unset, prints digest to stdout")
    args = ap.parse_args()

    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        _die("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set (see module docstring).")
    user_agent = os.environ.get("REDDIT_USER_AGENT") or DEFAULT_UA

    token = get_token(client_id, client_secret, user_agent)

    kept: list[dict] = []
    for sub in args.subreddits:
        raw = fetch_listing(token, user_agent, sub, args.listing, args.time, args.limit)
        trimmed = [trim(p) for p in raw]
        sub_kept = [p for p in trimmed if matches(p, args.min_score, args.keywords)]
        kept.extend(sub_kept)
        if args.out:
            os.makedirs(args.out, exist_ok=True)
            path = os.path.join(args.out, f"{sub}.{args.listing}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(trimmed, f, indent=2, ensure_ascii=False)
            print(f"reddit-scan: wrote {len(trimmed)} posts ({len(sub_kept)} kept) -> {path}")

    kept.sort(key=lambda p: p.get("score", 0), reverse=True)
    digest = _render_digest(kept, args)
    if args.out:
        with open(os.path.join(args.out, "digest.md"), "w", encoding="utf-8") as f:
            f.write(digest)
        print(f"reddit-scan: wrote digest with {len(kept)} kept posts -> {args.out}/digest.md")
    else:
        print(digest)


def _render_digest(posts: list[dict], args) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    lines = [
        f"# Reddit scan digest — {now}",
        "",
        f"Subreddits: {', '.join(args.subreddits)} · listing: {args.listing}"
        + (f"/{args.time}" if args.listing == "top" else "")
        + f" · min-score: {args.min_score}"
        + (f" · keywords: {', '.join(args.keywords)}" if args.keywords else ""),
        f"Source: Reddit official Data API (oauth.reddit.com). Kept {len(posts)} posts.",
        "",
        "| Score | Comments | Subreddit | Title | Link |",
        "| ---: | ---: | --- | --- | --- |",
    ]
    for p in posts:
        title = p["title"].replace("|", "\\|")[:120]
        lines.append(
            f"| {p['score']} | {p['num_comments']} | r/{p['subreddit']} | {title} | "
            f"[link]({p['permalink']}) |"
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
