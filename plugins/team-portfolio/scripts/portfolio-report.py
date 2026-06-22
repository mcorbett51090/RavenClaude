#!/usr/bin/env python3
"""portfolio-report.py — render markdown roll-ups from portfolio-activity.json.

Consumes the normalized artifact written by portfolio-collect.py and emits two
committed, diffable markdown reports plus a per-project status section:

  * weekly-tracker.md   — per-person, per-repo summary for the window. The
                          supervisor's "manage the team" view.
  * activity-rollup.md  — a chronological, newest-first feed of every event
                          (the cross-repo replacement for a single-repo
                          activity log).

Both are plain markdown so they live in the hub repo, review in PRs, and diff
cleanly week over week. Pure standard library.

Optional narrative layer: if the config enables it (`narrative.enabled: true`),
any `*.md` files in the narrative dir are appended verbatim under a "Notes"
heading — the hand-maintained context the commits can't capture.

Usage:
    python3 portfolio-report.py --activity portfolio-activity.json --out-dir reports
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

TYPE_LABEL = {"commit": "commits", "pr": "pull requests", "issue": "issues"}
TYPE_LABEL_SINGULAR = {"commit": "commit", "pr": "pull request", "issue": "issue"}


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# Required keys every renderer indexes directly. A malformed event (hand-edited
# artifact, schema drift) missing one used to crash the whole render; fail soft
# instead (house opinion #5) — drop it with a stderr warning, keep going.
_REQUIRED_EVENT_KEYS = ("type", "repo")


def sanitize_events(activity: dict) -> dict:
    kept = []
    for event in activity.get("events", []):
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


def display_name(login: str | None, team: list[dict]) -> str:
    if not login:
        return "(unattributed)"
    for member in team:
        if member.get("login") == login:
            return member.get("name") or login
    return login


def _counts_by_type(events: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for event in events:
        counts[event["type"]] += 1
    return counts


def _fmt_counts(counts: dict[str, int]) -> str:
    parts = []
    for kind in ("commit", "pr", "issue"):
        n = counts.get(kind)
        if n:
            label = TYPE_LABEL_SINGULAR[kind] if n == 1 else TYPE_LABEL[kind]
            parts.append(f"{n} {label}")
    return ", ".join(parts) if parts else "no activity"


def render_weekly_tracker(activity: dict) -> str:
    team = activity.get("team", [])
    window = activity.get("window", {})
    events = activity.get("events", [])

    by_person: dict[str | None, list[dict]] = defaultdict(list)
    for event in events:
        by_person[event.get("actor")].append(event)

    lines = [
        "# Weekly tracker",
        "",
        f"> Generated {activity.get('generated_at', '?')} · "
        f"window {window.get('since', '?')} → {window.get('until', '?')} "
        f"({window.get('days', '?')} days) · {len(activity.get('repos', []))} repos.",
        "",
        "Cross-repo activity rolled up per person. Newest first within each person.",
        "",
    ]

    if not activity.get("authenticated", True):
        lines += ["> ⚠️ Collected **unauthenticated** — counts may be incomplete.", ""]
    for err in activity.get("errors", []):
        lines.append(f"> ⚠️ Skipped {err}")
    if activity.get("errors"):
        lines.append("")

    # Order people by the configured roster first, then any extras seen.
    ordered_logins = [m.get("login") for m in team if m.get("login")]
    for login in by_person:
        if login not in ordered_logins:
            ordered_logins.append(login)

    for login in ordered_logins:
        person_events = by_person.get(login, [])
        name = display_name(login, team)
        role = next(
            (m.get("role") for m in team if m.get("login") == login and m.get("role")), None
        )
        heading = f"## {name}" + (f" — _{role}_" if role else "")
        lines += [heading, "", f"**Summary:** {_fmt_counts(_counts_by_type(person_events))}.", ""]

        # Per-repo breakdown table.
        by_repo: dict[str, list[dict]] = defaultdict(list)
        for event in person_events:
            by_repo[event["repo"]].append(event)
        if by_repo:
            lines += ["| Repo | Commits | PRs | Issues |", "| --- | --- | --- | --- |"]
            for repo in sorted(by_repo):
                c = _counts_by_type(by_repo[repo])
                lines.append(
                    f"| `{repo}` | {c.get('commit', 0)} | {c.get('pr', 0)} | {c.get('issue', 0)} |"
                )
            lines.append("")

        # Notable PRs / issues (not commits — too noisy) as bullets.
        notable = [e for e in person_events if e["type"] in ("pr", "issue")][:10]
        if notable:
            lines.append("**Pull requests & issues:**")
            lines.append("")
            for event in notable:
                lines.append(f"- {_event_bullet(event)}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _event_bullet(event: dict) -> str:
    state = event.get("state") or ""
    if event["type"] == "pr" and event.get("merged"):
        state = "merged"
    badge = f"`{event['type']}`"
    state_txt = f" _({state})_" if state else ""
    repo = event["repo"]
    title = event.get("title") or "(no title)"
    url = event.get("url")
    link = f"[{title}]({url})" if url else title
    project = event.get("project")
    proj_txt = f" · project: **{project}**" if project else ""
    return f"{badge} {link}{state_txt} — `{repo}`{proj_txt}"


def render_rollup(activity: dict) -> str:
    team = activity.get("team", [])
    events = activity.get("events", [])
    lines = [
        "# Activity roll-up",
        "",
        f"> Generated {activity.get('generated_at', '?')}. "
        "Every commit, pull request, and issue across all tracked repos, newest first.",
        "",
    ]
    for event in events:
        when = (event.get("updated_at") or event.get("created_at") or "")[:10]
        who = display_name(event.get("actor"), team)
        lines.append(f"- `{when}` **{who}** — {_event_bullet(event)}")
    if not events:
        lines.append("- _No activity in the window._")
    return "\n".join(lines).rstrip() + "\n"


def render_projects(activity: dict) -> str:
    events = activity.get("events", [])
    project_names = activity.get("projects", [])
    lines = ["# Project status (cross-repo)", "", f"> Generated {activity.get('generated_at', '?')}."]
    lines.append("")

    buckets: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        if event.get("project"):
            buckets[event["project"]].append(event)

    if not project_names:
        return "\n".join(lines + ["_No projects defined in the config._"]) + "\n"

    for name in project_names:
        proj_events = buckets.get(name, [])
        repos = sorted({e["repo"] for e in proj_events})
        open_prs = sum(1 for e in proj_events if e["type"] == "pr" and e.get("state") == "open")
        merged_prs = sum(1 for e in proj_events if e["type"] == "pr" and e.get("merged"))
        open_issues = sum(
            1 for e in proj_events if e["type"] == "issue" and e.get("state") == "open"
        )
        lines += [
            f"## {name}",
            "",
            f"- Repos with activity: {', '.join(f'`{r}`' for r in repos) or '_none_'}",
            f"- Open PRs: {open_prs} · Merged PRs: {merged_prs} · Open issues: {open_issues}",
            f"- Total events in window: {len(proj_events)}",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def append_narrative(config: dict | None) -> str:
    if not config:
        return ""
    narrative = config.get("narrative", {})
    if not narrative.get("enabled"):
        return ""
    directory = narrative.get("dir", "portfolio/narrative")
    if not os.path.isdir(directory):
        return ""
    chunks = ["", "## Notes (hand-maintained)", ""]
    for fname in sorted(os.listdir(directory)):
        if fname.endswith(".md"):
            with open(os.path.join(directory, fname), encoding="utf-8") as fh:
                chunks += [f"### {fname}", "", fh.read().rstrip(), ""]
    return "\n".join(chunks)


def write(out_dir: str, name: str, content: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"  wrote {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render markdown roll-ups from activity JSON.")
    parser.add_argument("--activity", default="portfolio-activity.json")
    parser.add_argument("--out-dir", default="reports")
    parser.add_argument("--config", default=None, help="Config (only needed for the narrative layer).")
    args = parser.parse_args(argv)

    try:
        activity = load(args.activity)
    except FileNotFoundError:
        print(f"Activity artifact not found: {args.activity}", file=sys.stderr)
        print("Run portfolio-collect.py first.", file=sys.stderr)
        return 2

    activity = sanitize_events(activity)
    config = None
    if args.config and os.path.isfile(args.config):
        config = json.loads(open(args.config, encoding="utf-8").read())

    narrative = append_narrative(config)
    write(args.out_dir, "weekly-tracker.md", render_weekly_tracker(activity) + narrative)
    write(args.out_dir, "activity-rollup.md", render_rollup(activity))
    write(args.out_dir, "project-status.md", render_projects(activity))
    return 0


if __name__ == "__main__":
    sys.exit(main())
