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

import contextlib
import http.client
import importlib.util
import json
import os
import sys
import urllib.error
import urllib.request
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

    def paginate_ex(self, path, params=None):
        return self.paginate(path, params), False


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
    """(events, error) - collect_repo may also return a trailing `truncated` list."""
    res = pc.collect_repo(client, repo, SINCE, UNTIL, team)
    return res[0], res[1]


class FakeResp:
    """What `urllib.request.urlopen` returns, as far as GitHubClient.get uses it."""

    def __init__(self, body: bytes, headers: dict | None = None):
        self._body = body
        self.headers = dict(headers or {})

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@contextlib.contextmanager
def patched_urlopen(fn):
    orig = urllib.request.urlopen
    urllib.request.urlopen = fn
    try:
        yield
    finally:
        urllib.request.urlopen = orig


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


def sec_a22_transport_errors_fail_soft():
    print("A-22 — a truncated/reset/timed-out/non-JSON response fails soft per repo")
    boom = {
        "o/trunc": http.client.IncompleteRead(b"par"),
        "o/reset": ConnectionResetError("reset by peer"),
        "o/slow": TimeoutError("timed out"),
        "o/http404": urllib.error.HTTPError("u", 404, "Not Found", {}, None),
    }
    one_commit = [commit("alice")]

    def fake(req, timeout=0):
        url = req.full_url
        for repo, exc in boom.items():
            if f"/repos/{repo}/" in url:
                raise exc
        if "/repos/o/garbage/" in url:
            return FakeResp(b"<html>not json</html>")
        return FakeResp(
            json.dumps(one_commit if url.split("?")[0].endswith("/commits") else []).encode()
        )

    config = {
        "repos": [*boom, "o/garbage", "o/good"],
        "team": [{"login": "alice"}],
        "window_days": 7,
    }
    try:
        with patched_urlopen(fake):
            activity = pc.build_activity(config, None, "tok")
        crashed = None
    except Exception as exc:  # the pre-fix behaviour: the first bad repo sinks the run
        activity, crashed = {"errors": [], "events": []}, exc
    check("the run completes despite a bad repo (no exception)", crashed is None)
    errs = activity["errors"]
    check("every failing repo is listed in errors (5 of 5)", len(errs) == 5)
    check(
        "a truncated response (IncompleteRead) is reported for ITS repo",
        any(e.startswith("o/trunc:") and "IncompleteRead" in e for e in errs),
    )
    check(
        "a reset connection, a read timeout and a non-JSON 200 are each reported",
        all(any(e.startswith(f"{r}:") for e in errs) for r in ("o/reset", "o/slow", "o/garbage")),
    )
    check(
        "the pre-existing HTTPError path is unchanged ('o/http404: HTTP 404')",
        any(e.startswith("o/http404: HTTP 404") for e in errs),
    )
    check(
        "the OTHER repo is still collected (fail soft per repo)",
        any(e["repo"] == "o/good" for e in activity["events"]),
    )
    events, err = collect(Stub([commit("alice")], boom=http.client.IncompleteRead(b"x")), {"alice"})
    check(
        "collect_repo itself returns (events, error) instead of raising",
        events == [] and err is not None and "IncompleteRead" in err,
    )


def paged_urlopen(commit_pages, issue_pages=1):
    """A urlopen fake serving `commit_pages` pages of commits (each with a Link rel=next except
    the last) and `issue_pages` pages of issues, one item per page."""
    served = {"commits": 0, "issues": 0}

    def fake(req, timeout=0):
        base = req.full_url.split("?")[0]
        kind = "commits" if base.endswith("/commits") else "issues"
        total = commit_pages if kind == "commits" else issue_pages
        served[kind] += 1
        page = served[kind]
        headers = {}
        if page < total:
            headers["Link"] = f'<{base}?page={page + 1}>; rel="next"'
        body = [commit("alice")] if kind == "commits" else [issue("alice")]
        return FakeResp(json.dumps(body).encode(), headers)

    return fake, served


def sec_a29_truncation_is_reported():
    print("A-29 — hitting the MAX_PAGES ceiling is reported, not silent")
    config = {"repos": ["o/big"], "team": [{"login": "alice"}], "window_days": 7}
    fake, served = paged_urlopen(commit_pages=pc.MAX_PAGES + 1)
    with patched_urlopen(fake):
        activity = build_quiet(config)
    check(
        "the 20-page ceiling still bounds the walk (20 requests, not 21)",
        served["commits"] == pc.MAX_PAGES,
    )
    check(
        "a 21-page commits stream puts 'o/big: truncated at 20 pages (commits)' in errors",
        "o/big: truncated at 20 pages (commits)" in activity["errors"],
    )
    check(
        "the events fetched before the ceiling are kept (20 commits)",
        sum(1 for e in activity["events"] if e["type"] == "commit") == pc.MAX_PAGES,
    )
    check(
        "the issues endpoint is not blamed when only commits overran",
        not any("(issues)" in e for e in activity["errors"]),
    )
    fake, _ = paged_urlopen(commit_pages=1, issue_pages=pc.MAX_PAGES + 1)
    with patched_urlopen(fake):
        activity = build_quiet(config)
    check(
        "an over-long issues stream is reported with the (issues) kind",
        "o/big: truncated at 20 pages (issues)" in activity["errors"],
    )
    fake, _ = paged_urlopen(commit_pages=pc.MAX_PAGES, issue_pages=3)
    with patched_urlopen(fake):
        activity = build_quiet(config)
    check(
        "control: EXACTLY 20 pages with no further page is not 'truncated'",
        activity["errors"] == [],
    )
    client = pc.GitHubClient(None)
    fake, _ = paged_urlopen(commit_pages=pc.MAX_PAGES + 1)
    ex = getattr(client, "paginate_ex", None)
    with patched_urlopen(fake):
        items, cut = ex("/repos/o/big/commits") if ex else ([], None)
        plain = client.paginate("/repos/o/big/commits")
    check(
        "paginate_ex returns (items, truncated=True); paginate still returns the plain list",
        cut is True and len(items) == pc.MAX_PAGES and isinstance(plain, list),
    )
    banner = pr.render_weekly_tracker(
        {
            "team": [],
            "repos": ["o/big"],
            "window": {},
            "events": [],
            "errors": ["o/big: truncated at 20 pages (commits)"],
        }
    )
    check(
        "the weekly-tracker banner surfaces the truncation entry",
        "truncated at 20 pages (commits)" in banner,
    )


def build_quiet(config):
    return pc.build_activity(config, None, "tok")


def main():
    sec_a21_case_insensitive_roster()
    sec_a22_transport_errors_fail_soft()
    sec_a29_truncation_is_reported()

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
