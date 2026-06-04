#!/usr/bin/env python3
"""portfolio-collect.py — pull cross-repo, multi-person activity from the GitHub API.

This is the ingest stage of the team-portfolio plugin. It reads a JSON config
(repos + team roster + projects), queries the GitHub REST API for commits, pull
requests, and issues across EVERY configured repo within a lookback window, and
writes a single normalized `portfolio-activity.json` artifact that the report and
dashboard generators consume.

Why GitHub-as-source: it is the only place that already sees every repo AND every
person. A per-repo activity log can't see the repo next door; GitHub already
attributes every commit/PR/issue to a user across all of them.

Design constraints (deliberate):
  * Pure standard library — no PyYAML, no `requests`, no pip install. Runs in a
    bare GitHub Action and in a plain `python3` session unchanged.
  * Secrets never live in the config. The token is read from the environment
    (GITHUB_TOKEN / GH_TOKEN / PORTFOLIO_TOKEN) only.
  * Fail soft per repo: a 404/403 on one repo (e.g. a private repo the token
    can't see) is reported and skipped, never fatal for the whole run.

Usage:
    python3 portfolio-collect.py --config team-portfolio.json --out portfolio-activity.json
    python3 portfolio-collect.py --days 14            # override the window
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API_ROOT = "https://api.github.com"
USER_AGENT = "ravenclaude-team-portfolio"
TOKEN_ENV_VARS = ("PORTFOLIO_TOKEN", "GITHUB_TOKEN", "GH_TOKEN")
MAX_PAGES = 20  # hard ceiling per endpoint so one busy repo can't run away


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def resolve_token(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for name in TOKEN_ENV_VARS:
        val = os.environ.get(name)
        if val:
            return val
    return None


class GitHubClient:
    """Minimal paginating GitHub REST client over urllib."""

    def __init__(self, token: str | None):
        self.token = token

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get(self, path: str, params: dict[str, str] | None = None) -> tuple[object, dict[str, str]]:
        url = path if path.startswith("http") else f"{API_ROOT}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers=self._headers())
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (api.github.com)
            body = resp.read().decode("utf-8")
            headers = {k.lower(): v for k, v in resp.headers.items()}
        return json.loads(body) if body else None, headers

    def paginate(self, path: str, params: dict[str, str] | None = None) -> list[dict]:
        """Follow Link rel=next up to MAX_PAGES; return the concatenated items."""
        items: list[dict] = []
        page_params = dict(params or {})
        page_params.setdefault("per_page", "100")
        next_url: str | None = path
        next_params: dict[str, str] | None = page_params
        pages = 0
        while next_url and pages < MAX_PAGES:
            data, headers = self.get(next_url, next_params)
            pages += 1
            if isinstance(data, list):
                items.extend(data)
            elif isinstance(data, dict) and "items" in data:
                items.extend(data["items"])
            next_url = _next_link(headers.get("link", ""))
            next_params = None  # the Link URL already carries the query string
            _respect_rate_limit(headers)
        return items


def _next_link(link_header: str) -> str | None:
    for part in link_header.split(","):
        segments = part.split(";")
        if len(segments) < 2:
            continue
        url = segments[0].strip().strip("<>")
        rel = segments[1].strip()
        if rel == 'rel="next"':
            return url
    return None


def _respect_rate_limit(headers: dict[str, str]) -> None:
    """If we're about to hit the secondary rate limit, pause briefly."""
    remaining = headers.get("x-ratelimit-remaining")
    if remaining is not None and remaining.isdigit() and int(remaining) <= 1:
        reset = headers.get("x-ratelimit-reset")
        if reset and reset.isdigit():
            wait = max(0, int(reset) - int(time.time())) + 1
            if 0 < wait <= 60:
                time.sleep(wait)


def classify_project(event: dict, projects: list[dict]) -> str | None:
    """Return the FIRST project whose match rules cover this event, else None.

    A project matches if ANY of: the event's repo is listed, OR any of the
    event's labels is listed, OR the title starts with a listed prefix.
    """
    repo = event.get("repo")
    labels = {label.lower() for label in event.get("labels", [])}
    title = (event.get("title") or "").lower()
    for project in projects:
        rules = project.get("match", {})
        if repo and repo in rules.get("repos", []):
            return project["name"]
        rule_labels = {label.lower() for label in rules.get("labels", [])}
        if labels & rule_labels:
            return project["name"]
        for prefix in rules.get("title_prefixes", []):
            if title.startswith(prefix.lower()):
                return project["name"]
    return None


def collect_repo(
    client: GitHubClient, repo: str, since: datetime, until: datetime, team: set[str]
) -> tuple[list[dict], str | None]:
    """Collect commits + issues + PRs for one `owner/name` repo. Returns (events, error)."""
    events: list[dict] = []
    try:
        commits = client.paginate(
            f"/repos/{repo}/commits",
            {"since": iso(since), "until": iso(until)},
        )
        for c in commits:
            actor = (c.get("author") or {}).get("login") or (
                (c.get("commit", {}).get("author") or {}).get("name")
            )
            if team and actor not in team:
                continue
            commit_info = c.get("commit", {})
            events.append(
                {
                    "type": "commit",
                    "repo": repo,
                    "actor": actor,
                    "title": (commit_info.get("message") or "").splitlines()[0][:140],
                    "url": c.get("html_url"),
                    "state": "committed",
                    "created_at": (commit_info.get("author") or {}).get("date"),
                    "updated_at": (commit_info.get("author") or {}).get("date"),
                    "closed_at": None,
                    "labels": [],
                }
            )

        # The issues endpoint returns BOTH issues and PRs (PRs carry a
        # `pull_request` key), each attributed to `user.login` with timestamps
        # and labels — one call covers two event types.
        issues = client.paginate(
            f"/repos/{repo}/issues",
            {"since": iso(since), "state": "all", "filter": "all"},
        )
        for it in issues:
            updated = parse_iso(it.get("updated_at"))
            if updated and updated < since:
                continue
            actor = (it.get("user") or {}).get("login")
            if team and actor not in team:
                continue
            is_pr = "pull_request" in it
            events.append(
                {
                    "type": "pr" if is_pr else "issue",
                    "repo": repo,
                    "actor": actor,
                    "title": (it.get("title") or "")[:140],
                    "url": it.get("html_url"),
                    "state": it.get("state"),
                    "merged": bool((it.get("pull_request") or {}).get("merged_at"))
                    if is_pr
                    else None,
                    "created_at": it.get("created_at"),
                    "updated_at": it.get("updated_at"),
                    "closed_at": it.get("closed_at"),
                    "labels": [
                        (label.get("name") if isinstance(label, dict) else label)
                        for label in it.get("labels", [])
                    ],
                }
            )
    except urllib.error.HTTPError as exc:
        return events, f"{repo}: HTTP {exc.code} ({exc.reason})"
    except urllib.error.URLError as exc:
        return events, f"{repo}: network error ({exc.reason})"
    return events, None


def build_activity(config: dict, days: int | None, token: str | None) -> dict:
    window_days = days or int(config.get("window_days", 7))
    until = utcnow()
    since = until - timedelta(days=window_days)
    repos = config.get("repos", [])
    team_entries = config.get("team", [])
    team_logins = {m["login"] for m in team_entries if m.get("login")}
    projects = config.get("projects", [])

    client = GitHubClient(token)
    all_events: list[dict] = []
    errors: list[str] = []
    for repo in repos:
        events, error = collect_repo(client, repo, since, until, team_logins)
        if error:
            errors.append(error)
        all_events.extend(events)

    for event in all_events:
        event["project"] = classify_project(event, projects)

    all_events.sort(key=lambda e: e.get("updated_at") or "", reverse=True)

    return {
        "schema_version": 1,
        "generated_at": iso(until),
        "window": {"since": iso(since), "until": iso(until), "days": window_days},
        "repos": repos,
        "team": team_entries,
        "supervisor": config.get("supervisor"),
        "projects": [p.get("name") for p in projects],
        "events": all_events,
        "errors": errors,
        "authenticated": bool(token),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect cross-repo GitHub activity.")
    parser.add_argument("--config", default="team-portfolio.json", help="Path to the JSON config.")
    parser.add_argument("--out", default="portfolio-activity.json", help="Output artifact path.")
    parser.add_argument("--days", type=int, default=None, help="Override window_days.")
    parser.add_argument("--token", default=None, help="GitHub token (else read from env).")
    args = parser.parse_args(argv)

    try:
        config = json.loads(open(args.config, encoding="utf-8").read())
    except FileNotFoundError:
        print(f"Config not found: {args.config}", file=sys.stderr)
        print("Copy templates/team-portfolio.json to your hub repo and edit it.", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Config is not valid JSON ({args.config}): {exc}", file=sys.stderr)
        return 2

    token = resolve_token(args.token)
    if not token:
        print(
            "Warning: no token in PORTFOLIO_TOKEN / GITHUB_TOKEN / GH_TOKEN. "
            "Unauthenticated requests are heavily rate-limited and cannot see "
            "private repos.",
            file=sys.stderr,
        )

    activity = build_activity(config, args.days, token)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(activity, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(
        f"Collected {len(activity['events'])} events across {len(activity['repos'])} repos "
        f"({activity['window']['days']}d window) -> {args.out}"
    )
    for err in activity["errors"]:
        print(f"  skipped {err}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
