#!/usr/bin/env python3
"""Harvest golfer complaints from Reddit for the golf-app opportunity research.

Why this exists
---------------
The 2026-08-10 research pass could not reach Reddit at all. Two independent
blockers, which need different fixes:

  1. This environment's egress proxy denies every reddit.com host (403 on
     CONNECT). Fixable by allowlisting the hosts in the environment's network
     policy.
  2. Reddit blocks Anthropic's search/fetch user-agent at their end, so the
     WebSearch/WebFetch route stays closed no matter what the network policy
     says. NOT fixable from this side.

This script takes the third door: Reddit's own OAuth2 API, which is subject to
(1) but not to (2). Once the hosts are allowlisted and credentials are set, it
runs unattended.

Setup
-----
1. Allowlist ``www.reddit.com`` and ``oauth.reddit.com`` in the environment's
   network policy (see https://code.claude.com/docs/en/claude-code-on-the-web).
2. Create a Reddit app at https://www.reddit.com/prefs/apps (type: ``script``).
3. Export credentials::

       export REDDIT_CLIENT_ID=...
       export REDDIT_CLIENT_SECRET=...
       # Optional: enables the password grant instead of app-only auth.
       export REDDIT_USERNAME=...
       export REDDIT_PASSWORD=...

Usage
-----
::

    python3 reddit-scan.py --preflight          # diagnose access, fetch nothing
    python3 reddit-scan.py                      # full scan, default themes
    python3 reddit-scan.py --themes pace,apps --limit 200
    python3 reddit-scan.py --since 2023-01-01 --comments 0

Output lands in a local run directory (gitignored, per the AGENTS.md storage
contract) as ``posts.jsonl``, ``comments.jsonl`` and ``summary.md``.

Terms note: Reddit distinguishes commercial from non-commercial API use. Read
their current developer terms before using this output to build a product.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_ROOT = "https://oauth.reddit.com"

# Reddit requires a descriptive User-Agent; generic ones get throttled or refused.
DEFAULT_UA = "python:ravenclaude.golf-research:v1.0 (opportunity research)"

SUBREDDITS = ["golf", "golftips", "GolfSwing", "golfclubs", "GolfGear", "Golfsimulator"]

# Search themes derived from the 40 complaints catalogued in README.md. Each maps
# to the evidence-table entries it is meant to corroborate or contradict.
THEMES = {
    "pace": [
        "slow play",
        "pace of play",
        "5 hour round",
        "group ahead",
        "waiting on every shot",
    ],
    "booking": [
        "tee time",
        "can't get a tee time",
        "tee time bots",
        "prepaid tee time",
        "cancellation policy",
    ],
    "apps": [
        "golf app",
        "wish there was an app",
        "app that would",
        "Arccos",
        "shot tracking",
        "strokes gained app",
        "GPS watch",
    ],
    "handicap": [
        "sandbagger",
        "handicap system",
        "GHIN",
        "vanity handicap",
        "posting scores",
    ],
    "practice": [
        "range session",
        "practice plan",
        "don't know what to practice",
        "wasting time at the range",
        "offseason practice",
    ],
    "instruction": [
        "conflicting advice",
        "too many swing tips",
        "youtube golf instruction",
        "wasted lessons",
        "finding an instructor",
    ],
    "beginner": [
        "new to golf",
        "first time on a course",
        "holding people up",
        "golf etiquette",
        "intimidated",
    ],
    "cost": [
        "golf is expensive",
        "green fees",
        "membership worth it",
        "cost of golf",
    ],
    "social": [
        "find playing partners",
        "solo golfer",
        "golf buddies",
        "getting paired up",
    ],
    "conditions": [
        "aerated greens",
        "punched greens",
        "course conditions",
        "cart path only",
    ],
    "equipment": [
        "club fitting worth it",
        "which golf ball",
        "used clubs",
        "regrip",
        "gapping",
    ],
    "gripes": [
        "biggest gripe",
        "pet peeve",
        "what annoys you",
        "unpopular opinion golf",
        "what would you change about golf",
    ],
}


class AccessError(RuntimeError):
    """Raised when Reddit cannot be reached or authenticated, with a diagnosis."""


def ssl_context() -> ssl.SSLContext:
    """Build a context that trusts the agent proxy's CA when one is configured."""
    ctx = ssl.create_default_context()
    bundle = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if bundle and Path(bundle).is_file():
        ctx.load_verify_locations(bundle)
    return ctx


def request(
    url: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 30,
) -> tuple[int, dict[str, str], bytes]:
    """Issue one HTTP request, returning (status, headers, body) instead of raising on 4xx/5xx.

    Transport-level failures are translated into AccessError with a diagnosis,
    because the proxy hides the reason on a failed CONNECT and the default
    exception text ("Tunnel connection failed") sends people down the wrong path.
    """
    req = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers or {}), exc.read()
    except urllib.error.URLError as exc:
        raise AccessError(
            f"Could not reach {urllib.parse.urlsplit(url).netloc}: {exc.reason}\n"
            "  Most likely: the egress proxy denies this host for the session.\n"
            "  Fix: allowlist www.reddit.com and oauth.reddit.com in the environment's\n"
            "  network policy. Confirm with:\n"
            '    curl -sS "$HTTPS_PROXY/__agentproxy/status"'
        ) from exc


def get_token(user_agent: str) -> str:
    """Fetch an OAuth2 access token, preferring the password grant when available."""
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise AccessError(
            "REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET are not set.\n"
            "  Create a 'script' app at https://www.reddit.com/prefs/apps, then export both."
        )

    username = os.environ.get("REDDIT_USERNAME")
    password = os.environ.get("REDDIT_PASSWORD")
    if username and password:
        # Script apps get higher, more predictable limits on the password grant.
        form = {"grant_type": "password", "username": username, "password": password}
    else:
        form = {"grant_type": "client_credentials"}

    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    status, _, body = request(
        TOKEN_URL,
        data=urllib.parse.urlencode(form).encode(),
        headers={
            "Authorization": f"Basic {basic}",
            "User-Agent": user_agent,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    if status == 401:
        raise AccessError(
            "Reddit rejected the credentials (401).\n"
            "  This is an authentication failure, not a network block — the host was reachable.\n"
            "  Check the client ID/secret pair, and that the app type is 'script'."
        )
    if status != 200:
        raise AccessError(f"Token request failed with HTTP {status}: {body[:300]!r}")

    token = json.loads(body).get("access_token")
    if not token:
        raise AccessError(f"Token response contained no access_token: {body[:300]!r}")
    return token


def respect_rate_limit(headers: dict[str, str]) -> None:
    """Sleep when Reddit says the current window is nearly spent."""
    try:
        remaining = float(headers.get("x-ratelimit-remaining", "100"))
        reset = float(headers.get("x-ratelimit-reset", "0"))
    except ValueError:
        return
    if remaining < 3 and reset > 0:
        time.sleep(min(reset + 1, 90))


def api_get(path: str, params: dict[str, str], token: str, user_agent: str) -> dict:
    """GET one API endpoint, retrying transient failures with a linear backoff."""
    url = f"{API_ROOT}{path}?{urllib.parse.urlencode(params)}"
    headers = {"Authorization": f"Bearer {token}", "User-Agent": user_agent}
    for attempt in range(4):
        status, resp_headers, body = request(url, headers=headers)
        respect_rate_limit(resp_headers)
        if status == 200:
            return json.loads(body)
        if status == 429 or status >= 500:
            time.sleep(2 * (attempt + 1))
            continue
        raise AccessError(f"GET {path} failed with HTTP {status}: {body[:300]!r}")
    raise AccessError(f"GET {path} still failing after retries (last status {status}).")


def search(
    subreddit: str, query: str, token: str, user_agent: str, cutoff: float, limit: int
) -> list[dict]:
    """Page through search results for one query, stopping at `limit` kept posts."""
    kept: list[dict] = []
    after = ""
    while len(kept) < limit:
        params = {
            "q": query,
            "restrict_sr": "1",
            "sort": "relevance",
            "t": "all",
            "limit": "100",
            "type": "link",
        }
        if after:
            params["after"] = after
        payload = api_get(f"/r/{subreddit}/search", params, token, user_agent).get("data", {})
        children = payload.get("children", [])
        if not children:
            break
        for child in children:
            post = child.get("data", {})
            # The 5-year recency filter is applied here rather than via `t`, so a
            # single pass can widen or narrow the window without re-querying.
            if post.get("created_utc", 0) < cutoff:
                continue
            kept.append(
                {
                    "id": post.get("id"),
                    "subreddit": subreddit,
                    "matched_query": query,
                    "title": post.get("title"),
                    "selftext": (post.get("selftext") or "")[:4000],
                    "score": post.get("score"),
                    "num_comments": post.get("num_comments"),
                    "created_utc": post.get("created_utc"),
                    "created_iso": datetime.fromtimestamp(
                        post.get("created_utc", 0), tz=timezone.utc
                    ).isoformat(),
                    "permalink": f"https://www.reddit.com{post.get('permalink', '')}",
                }
            )
        after = payload.get("after") or ""
        if not after:
            break
    return kept[:limit]


def fetch_comments(post_id: str, token: str, user_agent: str, top_n: int) -> list[dict]:
    """Fetch the top-scoring top-level comments for one post."""
    payload = api_get(
        f"/comments/{post_id}",
        {"limit": str(top_n), "sort": "top", "depth": "1"},
        token,
        user_agent,
    )
    if not isinstance(payload, list) or len(payload) < 2:
        return []
    out = []
    for child in payload[1].get("data", {}).get("children", []):
        data = child.get("data", {})
        if child.get("kind") != "t1" or not data.get("body"):
            continue
        out.append(
            {
                "post_id": post_id,
                "score": data.get("score"),
                "body": data.get("body", "")[:3000],
            }
        )
    return out[:top_n]


def preflight(user_agent: str) -> int:
    """Report exactly which of the known blockers is in play, fetching no data."""
    print("Reddit access preflight")
    print("-" * 60)
    creds = all(os.environ.get(k) for k in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"))
    print(f"  credentials present : {'yes' if creds else 'NO'}")
    try:
        token = get_token(user_agent)
    except AccessError as exc:
        print(f"  reachable + authed  : NO\n\n{exc}")
        return 1
    payload = api_get("/r/golf/about", {}, token, user_agent)
    subs = payload.get("data", {}).get("subscribers")
    print(f"  reachable + authed  : yes\n  r/golf subscribers  : {subs}")
    print("\nReady — run without --preflight to scan.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Harvest golfer complaints from Reddit via the official API."
    )
    parser.add_argument("--preflight", action="store_true", help="diagnose access, fetch nothing")
    parser.add_argument(
        "--themes",
        default="all",
        help=f"comma-separated subset of: {','.join(THEMES)} (default: all)",
    )
    parser.add_argument(
        "--subreddits", default=",".join(SUBREDDITS), help="comma-separated subreddits"
    )
    parser.add_argument("--since", default="2021-01-01", help="ISO date floor (default 2021-01-01)")
    parser.add_argument("--limit", type=int, default=60, help="max posts kept per query")
    parser.add_argument("--comments", type=int, default=8, help="top comments per post (0 to skip)")
    parser.add_argument(
        "--out", default="", help="output dir (default: .ravenclaude/runs/reddit-golf-scan)"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    user_agent = os.environ.get("REDDIT_USER_AGENT", DEFAULT_UA)

    if args.preflight:
        return preflight(user_agent)

    selected = list(THEMES) if args.themes == "all" else [t.strip() for t in args.themes.split(",")]
    unknown = [t for t in selected if t not in THEMES]
    if unknown:
        print(
            f"Unknown theme(s): {', '.join(unknown)}\nKnown: {', '.join(THEMES)}", file=sys.stderr
        )
        return 2

    cutoff = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc).timestamp()
    out_dir = Path(args.out or ".ravenclaude/runs/reddit-golf-scan")
    out_dir.mkdir(parents=True, exist_ok=True)

    token = get_token(user_agent)
    subreddits = [s.strip() for s in args.subreddits.split(",") if s.strip()]

    seen: set[str] = set()
    posts: list[dict] = []
    for theme in selected:
        for query in THEMES[theme]:
            for subreddit in subreddits:
                try:
                    found = search(subreddit, query, token, user_agent, cutoff, args.limit)
                except AccessError as exc:
                    # One dead subreddit or query must not abort the whole sweep.
                    print(f"  ! r/{subreddit} '{query}': {exc}", file=sys.stderr)
                    continue
                fresh = [p for p in found if p["id"] not in seen]
                seen.update(p["id"] for p in fresh)
                for post in fresh:
                    post["theme"] = theme
                posts.extend(fresh)
                print(f"  r/{subreddit:<16} {theme:<12} '{query}' -> {len(fresh)} new")

    posts.sort(key=lambda p: p.get("score") or 0, reverse=True)
    (out_dir / "posts.jsonl").write_text(
        "".join(json.dumps(p) + "\n" for p in posts), encoding="utf-8"
    )

    comments: list[dict] = []
    if args.comments > 0:
        # Comments are where the actual complaint detail lives, but they cost one
        # request each — so only the posts most likely to carry signal.
        for post in posts[:200]:
            try:
                comments.extend(fetch_comments(post["id"], token, user_agent, args.comments))
            except AccessError as exc:
                print(f"  ! comments {post['id']}: {exc}", file=sys.stderr)
        (out_dir / "comments.jsonl").write_text(
            "".join(json.dumps(c) + "\n" for c in comments), encoding="utf-8"
        )

    by_theme: dict[str, int] = {}
    for post in posts:
        by_theme[post["theme"]] = by_theme.get(post["theme"], 0) + 1
    lines = [
        "# Reddit golf-complaint scan",
        "",
        f"- Collected: {len(posts)} posts, {len(comments)} comments",
        f"- Subreddits: {', '.join(subreddits)}",
        f"- Date floor: {args.since}",
        "",
        "| Theme | Posts |",
        "|---|---|",
    ]
    lines += [f"| {t} | {n} |" for t, n in sorted(by_theme.items(), key=lambda kv: -kv[1])]
    lines += ["", "## Highest-scoring posts", ""]
    lines += [
        f"- [{p['score']}] [{p['title']}]({p['permalink']}) — r/{p['subreddit']}, {p['theme']}"
        for p in posts[:40]
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nWrote {len(posts)} posts and {len(comments)} comments to {out_dir}/")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AccessError as exc:
        print(f"\n{exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
