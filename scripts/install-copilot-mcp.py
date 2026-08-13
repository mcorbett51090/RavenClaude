#!/usr/bin/env python3
"""install-copilot-mcp.py — opt-in MCP installation for the Copilot host (MH-19).

WHY OPT-IN, and why this is not merely a convenience knob.

On Claude Code you receive a plugin's MCP server *because you installed that
plugin*. The consent is structural: per-plugin, by construction. Copilot's
`~/.copilot/mcp-config.json` is **global** — there is no per-plugin step to hang
consent on. So projecting every declared server wholesale would not "restore
parity", it would silently install third-party software from plugins the user
never chose, including a write-capable one, which
`docs/best-practices/bundled-mcp-servers.md` treats as an Absolute-rule gate.

Naming the server on the command line IS the consent step, standing in for the
per-plugin choice the host does not offer.

WHAT THE OLD CODE ACTUALLY DID, stated accurately: `scripts/ravenclaude` merged
`<copilot-pkg>/.mcp.json` into the global config, and nothing ever generated that
file. Read correctly that step was **not a bug** — it was written for
ravenclaude-core's own servers and core ships none, so it was correctly inert.
The defect was that it *looked* broken: `status` printed "mcp: not configured",
which reads as "you have not set it up" rather than "there is nothing to set."

Two modes:
    --servers a,b   install exactly those, or FAIL (an unknown name is never a
                    silent no-op — asking for a server, getting nothing, and
                    being told "ok" is the failure shape this file removes)
    --status        report what is available and what is currently installed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_catalog(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {s["name"]: s for s in data.get("servers", []) if isinstance(s, dict)}


class UnreadableConfig(Exception):
    """The destination exists but cannot be understood."""


def load_installed(dest: Path) -> dict:
    """Absent -> {}. Present-but-unparseable -> RAISE, never silently replace.

    The first version returned {} for BOTH cases, so a hand-broken or
    half-written ~/.copilot/mcp-config.json was overwritten and every server the
    user had configured by hand was destroyed — in their GLOBAL config, with a
    success message. The Codex sibling is structurally immune (it appends and
    asserts the prefix survives); this is the JSON equivalent of that promise:
    a file we cannot read is a file we must not rewrite.
    """
    if not dest.exists():
        return {}
    try:
        cur = json.loads(dest.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError) as e:
        raise UnreadableConfig(
            f"{dest} exists but is not valid JSON ({e}). Refusing to overwrite it — "
            "fix or move the file, then re-run."
        ) from e
    except OSError as e:
        raise UnreadableConfig(f"cannot read {dest}: {e}") from e
    if not isinstance(cur, dict):
        raise UnreadableConfig(f"{dest} is valid JSON but not an object — refusing to overwrite")
    return cur


def cmd_status(catalog: dict[str, dict], dest: Path) -> int:
    try:
        installed = set(load_installed(dest).get("mcpServers") or {})
    except UnreadableConfig as e:
        print(f"  {e}", file=sys.stderr)
        return 1
    if not catalog:
        print("mcp:     no servers in the catalogue")
        return 0
    # The headline correction: name the reason, not a bare "not configured".
    print("mcp:     ravenclaude-core ships NO MCP servers of its own.")
    print("         These come from other plugins and are OPT-IN on this host:")
    for name in sorted(catalog):
        entry = catalog[name]
        mark = "installed" if name in installed else "available"
        by = ", ".join(entry.get("shipped_by") or []) or "?"
        party = entry.get("party") or "unstated"
        print(f"           [{mark:9}] {name}  ({party}; from {by})")
    if not installed:
        print("         install one with: ravenclaude install --host copilot --with-mcp <name>")
    return 0


def cmd_install(catalog: dict[str, dict], dest: Path, wanted_raw: str) -> int:
    wanted = [w.strip() for w in wanted_raw.split(",") if w.strip()]
    if not wanted:
        print("  no server names given", file=sys.stderr)
        return 1
    unknown = [w for w in wanted if w not in catalog]
    if unknown:
        # Fail loudly. A silently-ignored name would leave the user believing a
        # server is wired when nothing is.
        print(f"  unknown MCP server(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"  available: {', '.join(sorted(catalog))}", file=sys.stderr)
        return 1
    try:
        cur = load_installed(dest)
    except UnreadableConfig as e:
        print(f"  {e}", file=sys.stderr)
        return 1
    servers = cur.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        print(
            "  existing mcp-config.json has a non-object mcpServers — refusing to overwrite",
            file=sys.stderr,
        )
        return 1
    added = []
    for name in wanted:
        if name in servers:
            # Never rewrite an existing entry: it may be the user's own tuning
            # (a hand-edited env var, different args). Mirror install-codex-mcp.py,
            # which already protects hand-tuning this way.
            print(f"  = {name} already configured — left untouched")
            continue
        servers[name] = catalog[name]["config"]
        added.append(name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(cur, indent=2) + "\n", encoding="utf-8")
    for name in added:
        by = ", ".join(catalog[name].get("shipped_by") or []) or "?"
        print(f"  + {name} ({catalog[name].get('party', 'unstated')}, from {by})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", required=True, type=Path)
    ap.add_argument("--dest", required=True, type=Path)
    ap.add_argument("--servers")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    try:
        catalog = load_catalog(args.catalog)
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"  cannot read the MCP catalogue: {e}", file=sys.stderr)
        return 1

    if args.status:
        return cmd_status(catalog, args.dest)
    if args.servers:
        return cmd_install(catalog, args.dest, args.servers)
    ap.error("one of --servers or --status is required")
    return 2


if __name__ == "__main__":
    sys.exit(main())
