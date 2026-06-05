#!/usr/bin/env python3
"""portfolio-config-check.py — validate team-portfolio.json before a collection run.

A static, offline linter for the portfolio config. It makes **no** network calls
(it cannot tell whether a repo exists on GitHub — that is the collector's fail-soft
job); it checks the config against the exact shape `portfolio-collect.py` reads, so
that the drift classes the scenarios bank documents are caught before they silently
distort a run:

  * a token accidentally committed into the config           (security — CLAUDE.md §4 #2)
  * a duplicate or malformed "owner/name" repo entry         (config drift)
  * the hub repo listed among the repos it is supposed to    (self-tracking —
    track                                                      best-practices)
  * a project whose match block can never match (no rules)   (silent under-match)
  * a project rule referencing a repo not in repos[]         (likely typo / dead rule)
  * a team entry missing a login, or a non-string repo       (schema)
  * narrative.enabled true but no dir set                    (config)

Exit codes:
    0  — no errors (warnings may still print)
    1  — at least one ERROR (the config would distort or fail a run)
    2  — the config file is missing or not valid JSON

Usage:
    python3 portfolio-config-check.py --config team-portfolio.json
    python3 portfolio-config-check.py --config team-portfolio.json --strict   # warnings fail too
"""

from __future__ import annotations

import argparse
import json
import re
import sys

REPO_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*)/[A-Za-z0-9._-]+$")
# A token committed into the config is a security issue (CLAUDE.md §4 #2). These are
# the well-known GitHub token prefixes; the check is heuristic, not exhaustive.
TOKEN_PREFIXES = ("ghp_", "gho_", "ghu_", "ghs_", "ghr_", "github_pat_")


class Findings:
    """Accumulates errors and warnings with a deterministic print order."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def _looks_like_token(value: str) -> bool:
    return any(value.startswith(p) for p in TOKEN_PREFIXES)


def _scan_for_tokens(node: object, path: str, found: Findings) -> None:
    """Walk the config recursively; flag any string value that looks like a token."""
    if isinstance(node, dict):
        for key, val in node.items():
            _scan_for_tokens(val, f"{path}.{key}", found)
    elif isinstance(node, list):
        for i, val in enumerate(node):
            _scan_for_tokens(val, f"{path}[{i}]", found)
    elif isinstance(node, str) and _looks_like_token(node):
        found.error(
            f"{path}: value looks like a GitHub token — secrets must live in the "
            "environment (PORTFOLIO_TOKEN / GITHUB_TOKEN / GH_TOKEN), never in the config."
        )


def check_window(config: dict, found: Findings) -> None:
    window = config.get("window_days", 7)
    if not isinstance(window, int) or isinstance(window, bool) or window <= 0:
        found.error(f"window_days must be a positive integer, got {window!r}.")


def check_repos(config: dict, found: Findings) -> list[str]:
    repos = config.get("repos", [])
    if not isinstance(repos, list) or not repos:
        found.error("repos[] must be a non-empty list of \"owner/name\" strings.")
        return []
    seen: set[str] = set()
    valid: list[str] = []
    for i, repo in enumerate(repos):
        if not isinstance(repo, str):
            found.error(f"repos[{i}] must be a string, got {type(repo).__name__}.")
            continue
        if not REPO_RE.match(repo):
            found.error(f'repos[{i}] = "{repo}" is not a valid "owner/name" path.')
            continue
        if repo in seen:
            found.error(f'repos[{i}] = "{repo}" is a duplicate entry.')
            continue
        seen.add(repo)
        valid.append(repo)
    return valid


def check_hub_not_self_tracked(config: dict, valid_repos: list[str], found: Findings) -> None:
    """If the config names its own hub repo, flag it (a hub tracking itself is noise)."""
    hub = config.get("hub_repo")
    if isinstance(hub, str) and hub in valid_repos:
        found.warn(
            f'hub_repo "{hub}" is also listed in repos[] — a hub repo tracking itself '
            "re-imports its own bot refresh commits as activity. Remove it from repos[]."
        )


def check_team(config: dict, found: Findings) -> None:
    team = config.get("team", [])
    if not isinstance(team, list):
        found.error("team must be a list of { login, name, role } objects.")
        return
    if not team:
        found.warn(
            "team[] is empty — the collector will then count EVERY author in each repo, "
            "not just your roster. Add team logins to scope the report."
        )
    seen: set[str] = set()
    for i, member in enumerate(team):
        if not isinstance(member, dict):
            found.error(f"team[{i}] must be an object, got {type(member).__name__}.")
            continue
        login = member.get("login")
        if not login or not isinstance(login, str):
            found.error(f"team[{i}] is missing a string 'login' (the GitHub username).")
            continue
        if login in seen:
            found.warn(f'team[{i}] login "{login}" is a duplicate.')
        seen.add(login)


def check_projects(config: dict, valid_repos: list[str], found: Findings) -> None:
    projects = config.get("projects", [])
    if not isinstance(projects, list):
        found.error("projects must be a list of { name, match } objects.")
        return
    repo_set = set(valid_repos)
    seen_names: set[str] = set()
    for i, project in enumerate(projects):
        if not isinstance(project, dict):
            found.error(f"projects[{i}] must be an object.")
            continue
        name = project.get("name")
        if not name or not isinstance(name, str):
            found.error(f"projects[{i}] is missing a string 'name'.")
            name = f"<index {i}>"
        elif name in seen_names:
            found.warn(f'projects[{i}] name "{name}" is a duplicate — first match wins.')
        else:
            seen_names.add(name)
        match = project.get("match", {})
        if not isinstance(match, dict):
            found.error(f'project "{name}" has a non-object match block.')
            continue
        rule_repos = match.get("repos", []) or []
        labels = match.get("labels", []) or []
        prefixes = match.get("title_prefixes", []) or []
        if not (rule_repos or labels or prefixes):
            found.error(
                f'project "{name}" has no match rules (repos / labels / title_prefixes) '
                "— it can never match an event and will always be empty."
            )
        for rr in rule_repos:
            if isinstance(rr, str) and rr not in repo_set:
                found.warn(
                    f'project "{name}" match.repos references "{rr}", which is not in '
                    "repos[] — that rule is dead unless the repo is also collected."
                )


def check_narrative(config: dict, found: Findings) -> None:
    narrative = config.get("narrative")
    if isinstance(narrative, dict) and narrative.get("enabled") and not narrative.get("dir"):
        found.error("narrative.enabled is true but narrative.dir is not set.")


def validate(config: dict) -> Findings:
    found = Findings()
    _scan_for_tokens(config, "config", found)
    check_window(config, found)
    valid_repos = check_repos(config, found)
    check_hub_not_self_tracked(config, valid_repos, found)
    check_team(config, found)
    check_projects(config, valid_repos, found)
    check_narrative(config, found)
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate team-portfolio.json before a collection run (offline, no network)."
    )
    parser.add_argument("--config", default="team-portfolio.json", help="Path to the JSON config.")
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as failures (exit 1)."
    )
    args = parser.parse_args(argv)

    try:
        with open(args.config, encoding="utf-8") as fh:
            config = json.load(fh)
    except FileNotFoundError:
        print(f"Config not found: {args.config}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Config is not valid JSON ({args.config}): {exc}", file=sys.stderr)
        return 2

    if not isinstance(config, dict):
        print("Config root must be a JSON object.", file=sys.stderr)
        return 2

    found = validate(config)

    for warning in found.warnings:
        print(f"  WARN  {warning}")
    for error in found.errors:
        print(f"  ERROR {error}", file=sys.stderr)

    if found.errors:
        print(
            f"\n{len(found.errors)} error(s), {len(found.warnings)} warning(s) — fix errors before collecting.",
            file=sys.stderr,
        )
        return 1
    if found.warnings and args.strict:
        print(f"\n{len(found.warnings)} warning(s) and --strict set — failing.", file=sys.stderr)
        return 1
    print(f"Config OK — 0 errors, {len(found.warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
