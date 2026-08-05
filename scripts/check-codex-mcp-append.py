#!/usr/bin/env python3
"""check-codex-mcp-append.py — Gate 171 (audit MH-19, Codex half).

Holds the property that made this safe to build at all.

THE HISTORY. Wiring MCP into `.codex/config.toml` was deferred for a stated
reason: *"a bad TOML merge would clobber a hand-tuned config."* The concern was
sound — v0.216.0 records the sharper version of it, where appending a BARE KEY
attaches it to the most recent table, so `sandbox_mode` appended to a file
containing `[mcp_servers.github]` silently became
`mcp_servers.github.sandbox_mode`: valid TOML, wrong meaning, invisible in a diff.

THE INSIGHT THAT RETIRED IT. Bare keys and table headers are opposites here:

    a bare key       is POSITION-DEPENDENT   -> appending is dangerous
    a [table] header is POSITION-INDEPENDENT -> appending is safe

An MCP server is a `[mcp_servers.<name>]` table, so it can be added by pure
append — and a pure append cannot clobber, because it never rewrites an existing
byte. That turns "be careful with the merge" into a checkable invariant, which is
what this gate checks. A property nobody asserts is a promise, not a guarantee.

Assertions:
  1. APPEND-ONLY  — after installing, the new file STARTS WITH the old file,
                    byte for byte. This is the whole safety argument.
  2. PRESERVES    — a hand-tuned `[mcp_servers.*]` table and root keys survive
                    unchanged, verified by PARSING both sides (not by eye — the
                    lesson from `network_access` shipping as a quoted string).
  3. IDEMPOTENT   — re-installing the same server changes nothing and never
                    duplicates a table (a duplicate table is a TOML error).
  4. PARSES       — the result is valid TOML.
  5. LOUD         — an unknown server name fails non-zero and writes nothing.

Usage:
    python3 scripts/check-codex-mcp-append.py
    python3 scripts/check-codex-mcp-append.py --must-fail
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = REPO_ROOT / "scripts" / "install-codex-mcp.py"
CATALOG = REPO_ROOT / "plugins" / "ravenclaude-core" / "copilot" / "mcp-catalog.json"

try:
    import tomllib as _toml
except ModuleNotFoundError:  # pragma: no cover
    try:
        import tomli as _toml
    except ModuleNotFoundError:
        _toml = None

HAND_TUNED = """\
# my hand-tuned config
sandbox_mode = "read-only"
approval_policy = "untrusted"

[mcp_servers.my-own-server]
command = "my-tool"
args = ["--flag"]

[sandbox_workspace_write]
network_access = false
"""


def load_installer():
    spec = importlib.util.spec_from_file_location("_codex_mcp_under_test", INSTALLER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(mod, *, mutate: bool = False) -> int:
    failures = 0

    def bad(msg: str) -> None:
        nonlocal failures
        failures += 1
        print(f"  FAIL: {msg}", file=sys.stderr)

    if _toml is None:
        bad("no TOML parser available (tomllib/tomli) — cannot verify")
        return failures

    if mutate:
        # THE MUTANT: a "tidier" implementation that REWRITES the file from a
        # parsed model instead of appending. It round-trips through a parser and
        # re-emits, which looks clean and silently discards every comment and any
        # ordering the user cared about — the clobber this design forbids.
        def rewrite(catalog, config, wanted_raw):
            wanted = [w.strip() for w in wanted_raw.split(",") if w.strip()]
            data = _toml.loads(config.read_text(encoding="utf-8")) if config.is_file() else {}
            servers = data.setdefault("mcp_servers", {})
            for n in wanted:
                if n in catalog:
                    servers[n] = catalog[n]["config"]
            out = []
            for k, v in data.items():
                if k == "mcp_servers":
                    continue
                if isinstance(v, str):
                    out.append(f'{k} = "{v}"')
            for n, cfg in servers.items():
                out.append(f"\n[mcp_servers.{n}]")
                if isinstance(cfg.get("command"), str):
                    out.append(f'command = "{cfg["command"]}"')
            config.write_text("\n".join(out) + "\n", encoding="utf-8")
            return 0

        mod.install = rewrite

    catalog = mod.load_catalog(CATALOG)
    if not catalog:
        bad("empty catalogue — the gate would pass vacuously")
        return failures
    target = sorted(catalog)[0]

    with tempfile.TemporaryDirectory() as td:
        cfg = Path(td) / "config.toml"
        cfg.write_text(HAND_TUNED, encoding="utf-8")
        before = cfg.read_text(encoding="utf-8")
        before_parsed = _toml.loads(before)

        rc = mod.install(catalog, cfg, target)
        if rc != 0:
            bad(f"installing {target!r} failed (rc={rc})")
        after = cfg.read_text(encoding="utf-8")

        # 1 — the safety argument, as an assertion.
        if not after.startswith(before):
            bad("NOT APPEND-ONLY: the original bytes were rewritten — this is the "
                "clobber the design forbids")

        # 4 — parses.
        try:
            after_parsed = _toml.loads(after)
        except Exception as e:  # noqa: BLE001
            bad(f"result does not parse as TOML — {e}")
            return failures

        # 2 — the hand-tuned content survived, verified by parse.
        for key in ("sandbox_mode", "approval_policy"):
            if after_parsed.get(key) != before_parsed.get(key):
                bad(f"root key {key!r} changed: "
                    f"{before_parsed.get(key)!r} -> {after_parsed.get(key)!r}")
        own_before = before_parsed["mcp_servers"]["my-own-server"]
        own_after = (after_parsed.get("mcp_servers") or {}).get("my-own-server")
        if own_after != own_before:
            bad(f"hand-tuned server changed: {own_before!r} -> {own_after!r}")
        if "# my hand-tuned config" not in after:
            bad("the user's comments were discarded")
        if target not in (after_parsed.get("mcp_servers") or {}):
            bad(f"{target!r} was not actually added")

        # 3 — idempotent, and never a duplicate table.
        mid = cfg.read_text(encoding="utf-8")
        mod.install(catalog, cfg, target)
        if cfg.read_text(encoding="utf-8") != mid:
            bad("re-installing the same server changed the file — not idempotent")
        headers = mod.existing_servers(cfg.read_text(encoding="utf-8"))
        if len(headers) != len(set(headers)):
            bad("duplicate [mcp_servers.*] table emitted — that is a TOML error")

        # 5 — loud on unknown.
        before_unknown = cfg.read_text(encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc2 = mod.install(catalog, cfg, "definitely-not-a-server")
        if rc2 == 0:
            bad("an unknown server name returned success")
        if cfg.read_text(encoding="utf-8") != before_unknown:
            bad("an unknown server name mutated the config")

    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args()
    mod = load_installer()

    if args.must_fail:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            failures = run(mod, mutate=True)
        text = err.getvalue()
        if failures == 0:
            print("MUST-FAIL: the rewrite-the-file mutant produced NO failures — no teeth",
                  file=sys.stderr)
            return 1
        if "NOT APPEND-ONLY" not in text:
            print("MUST-FAIL: failed, but not on the append-only assertion",
                  file=sys.stderr)
            print(text, file=sys.stderr)
            return 1
        print(f"  ok: teeth — a parse-and-re-emit 'tidier' implementation is caught "
              f"({failures} failure(s), incl. NOT APPEND-ONLY)")
        print("Codex MCP append: MUST-FAIL half behaved correctly")
        return 0

    failures = run(mod)
    if failures:
        print(f"FAIL: {failures} assertion(s) failed", file=sys.stderr)
        return 1
    print("  ok: append-only — the new file starts with the old file, byte for byte")
    print("  ok: hand-tuned tables, root keys and comments all survive")
    print("  ok: idempotent; never emits a duplicate table")
    print("  ok: result parses as TOML; unknown names fail without writing")
    print("Codex MCP append: ALL ASSERTIONS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
