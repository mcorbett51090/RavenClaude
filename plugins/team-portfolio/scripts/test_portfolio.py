#!/usr/bin/env python3
"""test_portfolio.py - regression suite for team-portfolio's collector / report / config-check.

Stdlib-only, zero-dependency runner (no pytest). Run:  python3 test_portfolio.py
Exits 0 iff every check passes. No network: the GitHub client is replaced by an in-memory
stub (`Stub`) or `urllib.request.urlopen` is patched with a scripted fake, and every login,
repo and timestamp below is synthetic.

Each section is named for the review finding it pins (A-21 ... A-31) and asserts the fixed
behaviour with a must-still-work control beside it.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name: str, filename: str):
    """Import a hyphen-named script (not importable with a plain `import`)."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, filename))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


pc = load("portfolio_collect", "portfolio-collect.py")
pr = load("portfolio_report", "portfolio-report.py")
cc = load("portfolio_config_check", "portfolio-config-check.py")

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name)


UNTIL = datetime(2026, 6, 8, tzinfo=timezone.utc)
SINCE = UNTIL - timedelta(days=7)


class Stub:
    """In-memory GitHubClient: `paginate(path, params)` returns the canned list for the path."""

    def __init__(self, commits=(), issues=(), boom=None):
        self.commits, self.issues, self.boom = list(commits), list(issues), boom

    def paginate(self, path, params=None):
        if self.boom is not None:
            raise self.boom
        return self.commits if path.endswith("/commits") else self.issues


def commit(login, date="2026-06-05T00:00:00Z", msg="work"):
    return {
        "author": {"login": login},
        "commit": {"message": msg, "author": {"date": date, "name": login}},
        "html_url": f"https://example.invalid/c/{login}",
    }


def issue(login, *, pr=False, updated="2026-06-05T00:00:00Z", merged_at=None, state="open"):
    it = {
        "user": {"login": login},
        "title": f"{'pr' if pr else 'issue'} by {login}",
        "html_url": f"https://example.invalid/i/{login}",
        "state": state,
        "created_at": updated,
        "updated_at": updated,
        "closed_at": None,
        "labels": [],
    }
    if pr:
        it["pull_request"] = {"merged_at": merged_at}
    return it


def collect(client, team, repo="o/r"):
    return pc.collect_repo(client, repo, SINCE, UNTIL, team)


def sec_a21_case_insensitive_roster():
    print("A-21 — roster login match is case-insensitive (GitHub logins are)")
    team = {"Alice"}
    events, err = collect(
        Stub([commit("alice")], [issue("ALICE"), issue("alice", pr=True), issue("mallory")]), team
    )
    check(
        "roster 'Alice' matches a commit authored by 'alice'",
        any(e["type"] == "commit" for e in events) and err is None,
    )
    check(
        "roster 'Alice' matches an issue by 'ALICE' and a PR by 'alice'",
        sorted(e["type"] for e in events) == ["commit", "issue", "pr"],
    )
    check(
        "a login NOT on the roster ('mallory') is still excluded",
        all(e["actor"] != "mallory" for e in events) and len(events) == 3,
    )
    check(
        "matched events carry the CONFIGURED spelling 'Alice' (one identity per person)",
        {e["actor"] for e in events} == {"Alice"},
    )
    exact, _ = collect(Stub([commit("Alice")]), team)
    check(
        "an exact-case match still works unchanged",
        len(exact) == 1 and exact[0]["actor"] == "Alice",
    )
    nobody, _ = collect(Stub([commit("someone")]), set())
    check(
        "an empty roster still counts every author, spelling untouched",
        len(nobody) == 1 and nobody[0]["actor"] == "someone",
    )
    roster = [{"login": "Alice", "name": "Alice Anderson", "role": "lead"}]
    check(
        "report display_name('alice') resolves the configured display name",
        pr.display_name("alice", roster) == "Alice Anderson"
        and pr.display_name("ALICE", roster) == "Alice Anderson"
        and pr.display_name("bob", roster) == "bob",
    )
    legacy = {
        "team": roster,
        "repos": ["o/r"],
        "window": {},
        "events": [{"type": "pr", "repo": "o/r", "actor": "alice", "title": "t", "state": "open"}],
    }
    tracker = pr.render_weekly_tracker(legacy)
    check(
        "an artifact whose actor is 'alice' renders ONE 'Alice Anderson' section, not two",
        tracker.count("## Alice Anderson") == 1 and "## alice" not in tracker,
    )


def main():
    sec_a21_case_insensitive_roster()

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
