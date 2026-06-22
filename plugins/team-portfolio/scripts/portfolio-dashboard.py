#!/usr/bin/env python3
"""portfolio-dashboard.py — render a self-contained HTML portfolio dashboard.

Consumes portfolio-activity.json and emits a single, dependency-free HTML file:
no CDN, no build step, no server required — open it in a browser or publish it
to GitHub Pages. It is the interactive, browse-and-go counterpart to the
committed markdown reports (portfolio-report.py).

Sections:
  * Header — window, repo count, generation time, auth/error banners.
  * People — one card per team member with per-type totals.
  * Repos — a table of activity per repository.
  * Projects — cross-repo project roll-up.
  * Recent activity — the newest events as a feed.

Pure standard library; deterministic output for a given input.

Usage:
    python3 portfolio-dashboard.py --activity portfolio-activity.json --out portfolio.html
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from collections import defaultdict

CSS = """
:root {
  --bg: #0f1117; --panel: #1a1d27; --ink: #e7e9ee; --muted: #9aa0ad;
  --line: #2a2e3a; --accent: #7c5cff; --commit: #3fb950; --pr: #58a6ff; --issue: #d29922;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
header { padding: 28px 32px; border-bottom: 1px solid var(--line); }
h1 { margin: 0 0 6px; font-size: 22px; }
.sub { color: var(--muted); font-size: 13px; }
.banner { margin: 12px 0 0; padding: 8px 12px; border-radius: 8px; font-size: 13px;
  background: #3a2a12; color: #f0c060; border: 1px solid #5a4420; }
main { padding: 24px 32px; max-width: 1100px; }
section { margin-bottom: 34px; }
h2 { font-size: 15px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted);
  border-bottom: 1px solid var(--line); padding-bottom: 8px; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 16px; }
.card .name { font-weight: 600; font-size: 16px; }
.card .role { color: var(--muted); font-size: 12px; }
.metrics { display: flex; gap: 16px; margin-top: 12px; }
.metric .n { font-size: 22px; font-weight: 700; }
.metric .l { font-size: 11px; color: var(--muted); text-transform: uppercase; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); }
th { color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; }
.feed { list-style: none; padding: 0; margin: 0; }
.feed li { padding: 10px 0; border-bottom: 1px solid var(--line); }
.tag { display: inline-block; padding: 1px 8px; border-radius: 99px; font-size: 11px;
  font-weight: 600; margin-right: 8px; }
.tag.commit { background: rgba(63,185,80,.15); color: var(--commit); }
.tag.pr { background: rgba(88,166,255,.15); color: var(--pr); }
.tag.issue { background: rgba(210,153,34,.15); color: var(--issue); }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.muted { color: var(--muted); }
code { background: #00000033; padding: 1px 5px; border-radius: 5px; font-size: 13px; }
"""


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""))


# Required keys every renderer indexes directly. A malformed event (hand-edited
# artifact, schema drift) missing one of these used to crash the whole render;
# fail soft instead (house opinion #5) — drop it with a stderr warning, keep going.
_REQUIRED_EVENT_KEYS = ("type", "repo")


def sanitize_events(activity: dict) -> dict:
    events = activity.get("events", [])
    kept = []
    for event in events:
        missing = [k for k in _REQUIRED_EVENT_KEYS if not (isinstance(event, dict) and event.get(k))]
        if missing:
            print(
                f"  skipping malformed event (missing {', '.join(missing)}): {event!r}",
                file=sys.stderr,
            )
            continue
        kept.append(event)
    activity["events"] = kept
    return activity


def counts_by_type(events: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for event in events:
        counts[event["type"]] += 1
    return counts


def name_for(login: str | None, team: list[dict]) -> str:
    if not login:
        return "(unattributed)"
    for member in team:
        if member.get("login") == login:
            return member.get("name") or login
    return login


def people_section(activity: dict) -> str:
    team = activity.get("team", [])
    events = activity.get("events", [])
    by_person: dict[str | None, list[dict]] = defaultdict(list)
    for event in events:
        by_person[event.get("actor")].append(event)

    ordered = [m.get("login") for m in team if m.get("login")]
    for login in by_person:
        if login not in ordered:
            ordered.append(login)

    cards = []
    for login in ordered:
        evs = by_person.get(login, [])
        counts = counts_by_type(evs)
        role = next((m.get("role") for m in team if m.get("login") == login), "") or ""
        cards.append(
            f'<div class="card"><div class="name">{esc(name_for(login, team))}</div>'
            f'<div class="role">{esc(role)}</div>'
            '<div class="metrics">'
            f'<div class="metric"><div class="n">{counts.get("commit", 0)}</div>'
            '<div class="l">commits</div></div>'
            f'<div class="metric"><div class="n">{counts.get("pr", 0)}</div>'
            '<div class="l">PRs</div></div>'
            f'<div class="metric"><div class="n">{counts.get("issue", 0)}</div>'
            '<div class="l">issues</div></div>'
            "</div></div>"
        )
    return '<section><h2>People</h2><div class="cards">' + "".join(cards) + "</div></section>"


def repos_section(activity: dict) -> str:
    events = activity.get("events", [])
    by_repo: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        by_repo[event["repo"]].append(event)
    rows = []
    for repo in sorted(by_repo):
        c = counts_by_type(by_repo[repo])
        rows.append(
            f"<tr><td><code>{esc(repo)}</code></td><td>{c.get('commit', 0)}</td>"
            f"<td>{c.get('pr', 0)}</td><td>{c.get('issue', 0)}</td>"
            f"<td>{len(by_repo[repo])}</td></tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="5" class="muted">No activity.</td></tr>')
    return (
        "<section><h2>Repositories</h2><table><thead><tr>"
        "<th>Repo</th><th>Commits</th><th>PRs</th><th>Issues</th><th>Total</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></section>"
    )


def projects_section(activity: dict) -> str:
    events = activity.get("events", [])
    names = activity.get("projects", [])
    if not names:
        return ""
    buckets: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        if event.get("project"):
            buckets[event["project"]].append(event)
    rows = []
    for name in names:
        evs = buckets.get(name, [])
        repos = sorted({e["repo"] for e in evs})
        open_prs = sum(1 for e in evs if e["type"] == "pr" and e.get("state") == "open")
        merged = sum(1 for e in evs if e["type"] == "pr" and e.get("merged"))
        open_issues = sum(1 for e in evs if e["type"] == "issue" and e.get("state") == "open")
        rows.append(
            f"<tr><td>{esc(name)}</td><td>{len(repos)}</td><td>{open_prs}</td>"
            f"<td>{merged}</td><td>{open_issues}</td><td>{len(evs)}</td></tr>"
        )
    return (
        "<section><h2>Projects (cross-repo)</h2><table><thead><tr>"
        "<th>Project</th><th>Repos</th><th>Open PRs</th><th>Merged PRs</th>"
        "<th>Open issues</th><th>Events</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></section>"
    )


def feed_section(activity: dict, limit: int = 60) -> str:
    team = activity.get("team", [])
    items = []
    for event in activity.get("events", [])[:limit]:
        when = (event.get("updated_at") or event.get("created_at") or "")[:10]
        title = esc(event.get("title") or "(no title)")
        url = event.get("url")
        link = f'<a href="{esc(url)}">{title}</a>' if url else title
        state = "merged" if (event["type"] == "pr" and event.get("merged")) else event.get("state")
        project = event.get("project")
        proj = f' · <span class="muted">{esc(project)}</span>' if project else ""
        items.append(
            f'<li><span class="tag {esc(event["type"])}">{esc(event["type"])}</span>'
            f"{link} <span class=\"muted\">— {esc(name_for(event.get('actor'), team))} · "
            f"<code>{esc(event['repo'])}</code> · {esc(when)} · {esc(state)}</span>{proj}</li>"
        )
    if not items:
        items.append('<li class="muted">No activity in the window.</li>')
    return '<section><h2>Recent activity</h2><ul class="feed">' + "".join(items) + "</ul></section>"


def render(activity: dict) -> str:
    window = activity.get("window", {})
    banners = []
    if not activity.get("authenticated", True):
        banners.append(
            '<div class="banner">Collected unauthenticated — counts may be incomplete.</div>'
        )
    for err in activity.get("errors", []):
        banners.append(f'<div class="banner">Skipped {esc(err)}</div>')
    sub = (
        f"Window {esc(window.get('since'))} → {esc(window.get('until'))} "
        f"({esc(window.get('days'))} days) · {len(activity.get('repos', []))} repos · "
        f"generated {esc(activity.get('generated_at'))}"
    )
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Team Portfolio</title><style>"
        + CSS
        + "</style></head><body><header><h1>Team Portfolio</h1>"
        f'<div class="sub">{sub}</div>'
        + "".join(banners)
        + "</header><main>"
        + people_section(activity)
        + repos_section(activity)
        + projects_section(activity)
        + feed_section(activity)
        + "</main></body></html>\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a self-contained HTML dashboard.")
    parser.add_argument("--activity", default="portfolio-activity.json")
    parser.add_argument("--out", default="portfolio.html")
    args = parser.parse_args(argv)

    try:
        with open(args.activity, encoding="utf-8") as fh:
            activity = json.load(fh)
    except FileNotFoundError:
        print(f"Activity artifact not found: {args.activity}", file=sys.stderr)
        print("Run portfolio-collect.py first.", file=sys.stderr)
        return 2

    activity = sanitize_events(activity)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(render(activity))
    print(f"  wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
