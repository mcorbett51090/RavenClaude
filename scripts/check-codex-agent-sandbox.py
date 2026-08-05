#!/usr/bin/env python3
"""check-codex-agent-sandbox.py — Gate 170.

Holds least privilege for the Codex custom-agent projection.

THE INVARIANT, and why omission is the dangerous case. Codex documents
`sandbox_mode` as a per-agent setting and — the load-bearing sentence — **the
parent turn's permission mode is inherited when it is omitted**
`[docs-verified 2026-07-29 — learn.chatgpt.com/docs/agent-configuration/subagents]`.

So an agent file with no `sandbox_mode` does not fail safe. It runs with whatever
the parent session has. A review-only agent projected without it silently inherits
write access — the identical shape to MH-10, where an omitted Copilot `tools:`
silently granted ALL tools. Two hosts, two different mechanisms, one bug.

Hence: `sandbox_mode` must be present on EVERY file, and must be `read-only` for
every agent whose canonical `tools:` declares no write tool. Both are asserted
against the canonical agents, not against the generator — a gate that asks the
generator what it meant to do proves nothing.

Assertions:
  1. PARSES     — every file is valid TOML, with the three required fields
                  non-empty (`name`, `description`, `developer_instructions`)
  2. PRESENT    — `sandbox_mode` on every file; never left to inheritance
  3. LEAST-PRIV — read-only for every agent declaring no write tool
  4. COVERAGE   — one file per canonical agent, no orphans
  5. INSTRUCTIONS — `developer_instructions` is non-trivial (a projection that
                  silently dropped the body would still satisfy 1-4)

Usage:
    python3 scripts/check-codex-agent-sandbox.py
    python3 scripts/check-codex-agent-sandbox.py --must-fail
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GEN = REPO_ROOT / "scripts" / "generate-codex-agents.py"
AGENTS_DIR = REPO_ROOT / "plugins" / "ravenclaude-core" / "agents"
CODEX_DIR = REPO_ROOT / "plugins" / "ravenclaude-core" / "codex" / "agents"

try:
    import tomllib as _toml  # py3.11+
except ModuleNotFoundError:  # pragma: no cover - stock macOS ships 3.9
    try:
        import tomli as _toml
    except ModuleNotFoundError:
        _toml = None


def load_generator():
    spec = importlib.util.spec_from_file_location("_codex_agents_under_test", GEN)
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
        # A gate that cannot parse TOML cannot assert anything about TOML. Say so
        # loudly rather than passing on a substring scan — this repo's own rule
        # after the network_access-as-a-string bug shipped green.
        bad("no TOML parser available (tomllib/tomli) — cannot verify; install tomli")
        return failures

    if mutate:
        # THE MUTANT: stop emitting sandbox_mode, i.e. let it fall back to the
        # parent's permission mode. This is the exact silent-inheritance bug, and
        # it is what a well-meaning "the default is fine" edit would look like.
        original = mod.build_agent_toml

        def no_sandbox(agent: dict) -> str:
            out = original(agent)
            return "\n".join(
                ln for ln in out.splitlines() if not ln.startswith("sandbox_mode =")
            ) + "\n"

        mod.build_agent_toml = no_sandbox

    canonical = {}
    for path in sorted(AGENTS_DIR.glob("*.md")):
        a = mod.parse_agent(path)
        canonical[a["name"]] = a
    if not canonical:
        bad("no canonical agents found — the gate would pass vacuously")
        return failures

    # Assert against the tree the generator WOULD produce, so a mutated generator
    # is caught before anyone regenerates, and against the committed files, so a
    # hand-edit is caught too.
    generated = {name.removesuffix(".toml"): body for name, body in mod.build_tree().items()}

    for label, source in (("generated", generated), ("committed", None)):
        for name, agent in sorted(canonical.items()):
            if source is None:
                path = CODEX_DIR / f"{name}.toml"
                if not path.is_file():
                    bad(f"committed: no .toml for canonical agent {name!r}")
                    continue
                text = path.read_text(encoding="utf-8")
            else:
                if name not in source:
                    bad(f"generated: no .toml for canonical agent {name!r}")
                    continue
                text = source[name]

            try:
                data = _toml.loads(text)
            except Exception as e:  # noqa: BLE001 - report any parse failure
                bad(f"{label} {name}: not valid TOML — {e}")
                continue

            for req in ("name", "description", "developer_instructions"):
                if not data.get(req):
                    bad(f"{label} {name}: required field {req!r} missing or empty")

            # 5 — the body actually travelled.
            body = data.get("developer_instructions") or ""
            if len(body) < 200:
                bad(f"{label} {name}: developer_instructions is only {len(body)} chars "
                    "— the agent body did not travel")

            # 2 — presence. THE security assertion.
            sandbox = data.get("sandbox_mode")
            if not sandbox:
                bad(f"{label} {name}: NO sandbox_mode — Codex inherits the PARENT "
                    "turn's permissions when it is omitted, so this agent runs with "
                    "whatever the session has")
                continue
            if sandbox not in (mod.SANDBOX_READ_ONLY, mod.SANDBOX_WORKSPACE_WRITE):
                bad(f"{label} {name}: unknown sandbox_mode {sandbox!r}")
                continue

            # 3 — least privilege, derived from the CANONICAL tools.
            expected = mod.sandbox_for(agent["tools"])
            if sandbox != expected:
                bad(f"{label} {name}: sandbox_mode={sandbox!r} but canonical tools "
                    f"{agent['tools']} imply {expected!r}")

    # 4 — no orphans.
    if CODEX_DIR.is_dir():
        for orphan in sorted(CODEX_DIR.glob("*.toml")):
            if orphan.stem not in canonical:
                bad(f"orphan {orphan.name} — no canonical agent of that name")

    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args()
    mod = load_generator()

    if args.must_fail:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            failures = run(mod, mutate=True)
        text = err.getvalue()
        if failures == 0:
            print("MUST-FAIL: dropping sandbox_mode produced NO failures — no teeth",
                  file=sys.stderr)
            return 1
        if "NO sandbox_mode" not in text:
            print("MUST-FAIL: failed, but not on the missing-sandbox assertion",
                  file=sys.stderr)
            print(text, file=sys.stderr)
            return 1
        print(f"  ok: teeth — omitting sandbox_mode (silent parent inheritance) is "
              f"caught ({failures} failure(s))")
        print("Codex agent sandbox: MUST-FAIL half behaved correctly")
        return 0

    failures = run(mod)
    if failures:
        print(f"FAIL: {failures} assertion(s) failed", file=sys.stderr)
        return 1
    n = len(list(AGENTS_DIR.glob("*.md")))
    ro = sum(
        1 for p in CODEX_DIR.glob("*.toml")
        if _toml.loads(p.read_text(encoding="utf-8")).get("sandbox_mode") == "read-only"
    )
    print(f"  ok: {n} agents projected; every file carries an explicit sandbox_mode")
    print(f"  ok: {ro} review-only agent(s) are read-only, derived from canonical tools")
    print("  ok: valid TOML, required fields present, bodies travelled, no orphans")
    print("Codex agent sandbox: ALL ASSERTIONS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
