#!/usr/bin/env python3
"""Verify every bundled MCP server in a plugin is attributed.

Rule: docs/best-practices/bundled-mcp-servers.md

For each `plugins/*/.claude-plugin/plugin.json` that declares an `mcpServers`
block, the manifest must carry a top-level `x-mcpAttribution` map with one
entry per server name. (Top-level placement is the Claude-Code-blessed spot for
ecosystem-agnostic metadata — unrecognized top-level keys are ignored by the
loader and reported only as warnings by `claude plugin validate`, so the field
never affects plugin loading or MCP-server launch.)

Each `x-mcpAttribution["<server>"]` entry must declare:
  - party: "first-party" | "third-party"   (required)
  - for third-party servers also:
      - source:  non-empty (repo/package URL or description)
      - license: non-empty (SPDX id or short name)
      - notice:  a file (default "NOTICE.md") that EXISTS in the plugin root
                 AND mentions the server name (so the attribution is real, not
                 just a declared filename).

This turns "is this server attributed?" into a mechanically-decidable check —
"is third-party" is author-declared, not heuristically guessed from the command.

Exit 0 if all bundled servers are attributed; exit 1 (listing violations)
otherwise. `--root DIR` scans an alternate tree (used by audit-gates.sh
fixtures); default is the repo root.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys


def check_plugin(manifest_path: str) -> list[str]:
    errs: list[str] = []
    try:
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"{manifest_path}: invalid JSON ({e})"]

    servers = data.get("mcpServers")
    if not servers:
        return []  # no bundled servers -> nothing to attribute

    plugin_root = os.path.dirname(os.path.dirname(manifest_path))  # .../<plugin>/
    name = data.get("name") or os.path.basename(plugin_root)
    attr = data.get("x-mcpAttribution", {})
    if not isinstance(attr, dict):
        return [
            f"{name}: x-mcpAttribution must be an object keyed by server name "
            f"(found {type(attr).__name__})"
        ]

    for server in servers:
        entry = attr.get(server)
        if entry is None:
            errs.append(
                f"{name}: mcpServers['{server}'] has no x-mcpAttribution entry "
                f"(see docs/best-practices/bundled-mcp-servers.md)"
            )
            continue
        if not isinstance(entry, dict):
            errs.append(f"{name}: x-mcpAttribution['{server}'] must be an object")
            continue
        party = entry.get("party")
        if party not in ("first-party", "third-party"):
            errs.append(
                f"{name}: x-mcpAttribution['{server}'].party must be "
                f"'first-party' or 'third-party' (found {party!r})"
            )
            continue
        if party == "first-party":
            continue
        # third-party: stronger requirements
        for req in ("source", "license"):
            if not entry.get(req):
                errs.append(
                    f"{name}: third-party server '{server}' missing "
                    f"x-mcpAttribution['{server}'].{req}"
                )
        notice = entry.get("notice", "NOTICE.md")
        notice_path = os.path.join(plugin_root, notice)
        if not os.path.isfile(notice_path):
            errs.append(
                f"{name}: third-party server '{server}' declares notice "
                f"'{notice}' but {notice_path} does not exist"
            )
        else:
            with open(notice_path, encoding="utf-8") as nf:
                if server not in nf.read():
                    errs.append(
                        f"{name}: {notice} does not mention server '{server}' "
                        f"(attribution must name the server it covers)"
                    )
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="repo root to scan (default: .)")
    args = ap.parse_args()

    pattern = os.path.join(args.root, "plugins", "*", ".claude-plugin", "plugin.json")
    manifests = sorted(glob.glob(pattern))

    all_errs: list[str] = []
    for m in manifests:
        all_errs += check_plugin(m)

    if all_errs:
        print("MCP attribution violations:")
        for e in all_errs:
            print(f"  - {e}")
        return 1

    print(f"MCP attribution OK — checked {len(manifests)} plugin manifest(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
