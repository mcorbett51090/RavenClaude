#!/usr/bin/env python3
"""check-copilot-mcp-optin.py — Gate 169 (audit MH-19, Copilot half).

Holds the consent model for MCP servers on the Copilot host.

THE ASYMMETRY THIS PROTECTS. On Claude Code you receive a plugin's MCP server
*because you installed that plugin* — consent is structural and per-plugin.
Copilot's `~/.copilot/mcp-config.json` is **global**; there is no per-plugin step.
So projecting every declared server wholesale would not restore parity, it would
install third-party software from plugins the user never chose — including a
write-capable one, which `docs/best-practices/bundled-mcp-servers.md` treats as an
Absolute-rule gate. Naming the server on the command line IS the consent step.

That makes "installs nothing unless asked" a **security property**, not a default,
and the tempting refactor ("just wire them all, it is friendlier") is exactly the
regression this gate exists to catch. The teeth half is that refactor.

Assertions:
  1. COMPLETE   — the catalogue lists every server any plugin declares (no drift)
  2. NAMED SAFE — the catalogue is NOT called `.mcp.json`; the installer's legacy
                  auto-merge keys on that name, so the filename is what keeps the
                  catalogue from being swept into a global config by old code
  3. OPT-IN     — installing by name installs THAT server and no other
  4. LOUD       — an unknown name fails non-zero and writes nothing
  5. THIRD-PARTY— every catalogue entry carries its provenance, so the installer
                  can say whose software it is about to run

Usage:
    python3 scripts/check-copilot-mcp-optin.py
    python3 scripts/check-copilot-mcp-optin.py --must-fail
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = REPO_ROOT / "scripts" / "install-copilot-mcp.py"
COPILOT_PKG = REPO_ROOT / "plugins" / "ravenclaude-core" / "copilot"
CATALOG = COPILOT_PKG / "mcp-catalog.json"


def load_installer():
    spec = importlib.util.spec_from_file_location("_mcp_optin_under_test", INSTALLER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def declared_servers() -> set[str]:
    names: set[str] = set()
    for manifest in sorted(REPO_ROOT.glob("plugins/*/.claude-plugin/plugin.json")):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        mcp = data.get("mcpServers")
        if isinstance(mcp, dict):
            names.update(mcp)
    return names


def run(mod, *, mutate: bool = False) -> int:
    failures = 0

    def bad(msg: str) -> None:
        nonlocal failures
        failures += 1
        print(f"  FAIL: {msg}", file=sys.stderr)

    if mutate:
        # THE MUTANT: the "friendlier" refactor — ignore what was asked for and
        # wire the whole catalogue. Reproduces the wholesale merge whose absence
        # is the point of this design.
        def install_everything(catalog, dest, wanted_raw):  # noqa: ARG001
            cur = mod.load_installed(dest)
            cur.setdefault("mcpServers", {}).update(
                {n: e["config"] for n, e in catalog.items()}
            )
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(cur, indent=2) + "\n", encoding="utf-8")
            return 0

        mod.cmd_install = install_everything

    if not CATALOG.is_file():
        bad(f"catalogue missing at {CATALOG} — run generate-copilot-plugin.py")
        return failures

    catalog = mod.load_catalog(CATALOG)

    # 1 — completeness
    missing = declared_servers() - set(catalog)
    if missing:
        bad(f"catalogue is stale — declared but absent: {sorted(missing)}")

    # 2 — the filename IS the safety property
    if (COPILOT_PKG / ".mcp.json").exists():
        bad(".mcp.json exists in the Copilot package — the installer's legacy "
            "auto-merge would sweep it into the GLOBAL config with no consent step")

    # 5 — provenance on every entry
    for name, entry in sorted(catalog.items()):
        if not entry.get("shipped_by"):
            bad(f"{name}: no shipped_by — the installer cannot say whose software this is")
        if not entry.get("party"):
            bad(f"{name}: no party — third-party software must be labelled as such")
        if not entry.get("config"):
            bad(f"{name}: no config — nothing to install")

    with tempfile.TemporaryDirectory() as td:
        dest = Path(td) / "mcp-config.json"

        # 3 — opt-in installs exactly what was named
        target = sorted(catalog)[0]
        rc = mod.cmd_install(catalog, dest, target)
        if rc != 0:
            bad(f"installing {target!r} failed (rc={rc})")
        got = set(mod.load_installed(dest).get("mcpServers") or {})
        if got != {target}:
            bad(f"OPT-IN VIOLATED: asked for {{{target!r}}}, config now holds {sorted(got)}")

        # 4 — an unknown name fails loudly and changes nothing
        before = dest.read_text(encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc2 = mod.cmd_install(catalog, dest, "definitely-not-a-server")
        if rc2 == 0:
            bad("an unknown server name returned success — a silent no-op is the "
                "failure shape this design removes")
        if dest.read_text(encoding="utf-8") != before:
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
            print("MUST-FAIL: the install-everything mutant produced NO failures — no teeth",
                  file=sys.stderr)
            return 1
        if "OPT-IN VIOLATED" not in text:
            print("MUST-FAIL: failed, but not on the opt-in assertion", file=sys.stderr)
            print(text, file=sys.stderr)
            return 1
        print(f"  ok: teeth — a wholesale 'wire them all' refactor is caught "
              f"({failures} failure(s), incl. OPT-IN VIOLATED)")
        print("Copilot MCP opt-in: MUST-FAIL half behaved correctly")
        return 0

    failures = run(mod)
    if failures:
        print(f"FAIL: {failures} assertion(s) failed", file=sys.stderr)
        return 1
    print(f"  ok: catalogue lists all {len(declared_servers())} declared server(s), with provenance")
    print("  ok: not named .mcp.json — the legacy auto-merge cannot sweep it up")
    print("  ok: opting in by name installs THAT server and no other")
    print("  ok: an unknown name fails loudly and writes nothing")
    print("Copilot MCP opt-in: ALL ASSERTIONS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
