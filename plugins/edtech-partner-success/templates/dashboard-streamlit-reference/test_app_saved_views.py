#!/usr/bin/env python3
"""Regression test: app.py binds saved-view SQL values instead of interpolating them.

repo-review 2026-10-19 (domainplugins-14). Stdlib only; no Snowflake or Streamlit
needed. app.py runs Streamlit calls at import time, so the saved-view helpers are
lifted out of its source with `ast` and run against a recording fake session.
Run:  python3 test_app_saved_views.py   (exit 0 = all pass)
"""

from __future__ import annotations

import ast
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, "app.py")
HELPERS = {"_VIEW_NAME_RE", "_SAVE_VIEW_SQL", "_LOAD_VIEW_SQL"}
FUNCS = {"is_valid_view_name", "save_view", "load_view_state"}
results: list[tuple[str, bool]] = []


def check(name: str, ok: bool) -> None:
    results.append((name, bool(ok)))
    print(("  PASS " if ok else "  FAIL ") + name)


def load_helpers() -> dict:
    tree = ast.parse(open(APP, encoding="utf-8").read())
    keep = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in FUNCS:
            keep.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id in HELPERS for t in node.targets
        ):
            keep.append(node)
    ns: dict = {"json": json, "re": re}
    exec(compile(ast.Module(body=keep, type_ignores=[]), APP, "exec"), ns)  # noqa: S102
    missing = (HELPERS | FUNCS) - set(ns)
    if missing:
        raise SystemExit(f"app.py is missing the saved-view helpers: {sorted(missing)}")
    return ns


class _Column:
    def __init__(self, value):
        self.iloc = [value]


class _Frame:
    def __init__(self, value):
        self._value = value

    def __getitem__(self, key):
        return _Column(self._value)


class _Result:
    def __init__(self, value):
        self._value = value

    def collect(self):
        return []

    def to_pandas(self):
        return _Frame(self._value)


class FakeSession:
    def __init__(self, stored: str = "{}"):
        self.calls: list[tuple[str, list | None]] = []
        self.stored = stored

    def sql(self, query, params=None):
        self.calls.append((query, params))
        return _Result(self.stored)


def main() -> int:
    ns = load_helpers()
    filters = {"school": "O'Brien Academy", "segment": "renewal"}

    print("save_view — values are bound, never interpolated")
    s = FakeSession()
    ns["save_view"](s, "Morning view", filters)
    query, params = s.calls[0]
    check("one statement issued", len(s.calls) == 1)
    check(
        "the apostrophe-bearing filter JSON is a bind value",
        params == ["Morning view", json.dumps(filters)],
    )
    check(
        "the SQL text carries no user value", "O'Brien" not in query and "Morning view" not in query
    )
    check("the SQL text uses qmark binds", query.count("?") == 2)

    print("save_view — an invalid name is refused before any SQL")
    injection = "x' || (SELECT LISTAGG(email, ',') FROM core.partner_contacts) || '"
    s = FakeSession()
    try:
        ns["save_view"](s, injection, filters)
        refused = False
    except ValueError:
        refused = True
    check("an injection-shaped name raises ValueError", refused)
    check("no SQL was sent for it", s.calls == [])
    check("an over-long name is invalid", not ns["is_valid_view_name"]("v" * 65))
    check("an ordinary name is valid", ns["is_valid_view_name"]("Pre-standup view_2"))

    print("load_view_state — the chosen name is bound")
    s = FakeSession(stored=json.dumps(filters))
    got = ns["load_view_state"](s, "Morning view")
    query, params = s.calls[0]
    check("returns the stored filters", got == filters)
    check("the name is a bind value", params == ["Morning view"] and "Morning view" not in query)

    print("app.py — no f-string SQL left on the saved-view path")
    src = open(APP, encoding="utf-8").read()
    sql_fstrings = [
        line.strip()
        for line in src.splitlines()
        if line.strip().startswith('f"')
        and any(k in line for k in ("view_name", "view_state", "PARSE_JSON", "psm_saved_view"))
    ]
    check("no f-string builds saved-view SQL", sql_fstrings == [])
    check("no PARSE_JSON('{...}') interpolation", "PARSE_JSON('{" not in src)

    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} checks passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
