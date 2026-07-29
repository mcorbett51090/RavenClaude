#!/usr/bin/env python3
"""install-codex-mcp.py — opt-in MCP wiring for the Codex host (MH-19, Codex half).

THE RISK THAT DEFERRED THIS, AND THE PROPERTY THAT RETIRES IT
-------------------------------------------------------------
The recorded reason for not building this was: *"a bad TOML merge would clobber a
hand-tuned config."* That is a real risk and this repo has already been bitten by
its sharper cousin — v0.216.0 records that appending a BARE KEY to
`.codex/config.toml` attaches it to the most recent table, so appending
`sandbox_mode` to a file containing `[mcp_servers.github]` silently sets
`mcp_servers.github.sandbox_mode`: valid TOML, wrong meaning, invisible in a diff.

But bare keys and table headers are opposites in exactly this respect:

    a bare key      is POSITION-DEPENDENT  -> appending is dangerous
    a [table] header is POSITION-INDEPENDENT -> appending is safe

An MCP server is a `[mcp_servers.<name>]` **table**. So it can be added by pure
APPEND, and pure append cannot clobber anything, because it never rewrites an
existing byte. That is not a promise to be careful — it is a property, asserted
on every write:

    assert new_text.startswith(original_text)

Three further rules make it total:
  * A server whose table ALREADY EXISTS is skipped, never rewritten. Duplicate
    tables are a TOML error, and more importantly the existing one may be the
    user's own tuning.
  * The result is PARSED before it is written. If it does not parse, nothing is
    written. (The lesson from `network_access` shipping as a quoted string in
    0.216.0: verify with a parser, never by eye.)
  * Only the shapes we can emit correctly are emitted — string, list-of-strings,
    dict-of-string. Anything else RAISES rather than guessing.

CONSENT, carried over from the Copilot half: nothing is installed unless named.
`~/.codex/config.toml` is global and a project `.codex/config.toml` loads **only
in trusted projects** `[docs-verified 2026-07-29 —
learn.chatgpt.com/docs/extend/mcp]`, so neither location offers a per-plugin
consent step. Naming the server IS the consent.

VERIFIED CONTRACT `[docs-verified 2026-07-29]`: `[mcp_servers.<server-name>]`
with `command` (required), `args`, `env`, `env_vars`, `cwd`, `enabled`,
`startup_timeout_sec`, `tool_timeout_sec` and others optional; the docs' example
renders `env` as a sub-table `[mcp_servers.<name>.env]`, which is what is emitted.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib as _toml  # py3.11+
except ModuleNotFoundError:  # pragma: no cover - stock macOS ships 3.9
    try:
        import tomli as _toml
    except ModuleNotFoundError:
        _toml = None

_HEADER_RE = re.compile(r"^\s*\[\s*mcp_servers\s*\.\s*([A-Za-z0-9_.-]+)", re.M)


def toml_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_server(name: str, cfg: dict) -> str:
    """Render one [mcp_servers.<name>] table.

    Emits only shapes we can render correctly; anything else raises. Guessing at
    an unknown shape is how you produce valid TOML with the wrong meaning.
    """
    lines = [f"[mcp_servers.{name}]"]
    env: dict = {}
    for key in sorted(cfg):
        val = cfg[key]
        if key == "env":
            if not isinstance(val, dict):
                raise ValueError(f"{name}: env must be a table, got {type(val).__name__}")
            env = val
            continue
        if isinstance(val, str):
            lines.append(f"{key} = {toml_str(val)}")
        elif isinstance(val, bool):
            lines.append(f"{key} = {'true' if val else 'false'}")
        elif isinstance(val, int):
            lines.append(f"{key} = {val}")
        elif isinstance(val, list) and all(isinstance(x, str) for x in val):
            rendered = ", ".join(toml_str(x) for x in val)
            lines.append(f"{key} = [{rendered}]")
        else:
            raise ValueError(
                f"{name}: cannot render key {key!r} of type {type(val).__name__} — "
                "add explicit support rather than guessing at the TOML shape"
            )
    if env:
        lines.append("")
        lines.append(f"[mcp_servers.{name}.env]")
        for k in sorted(env):
            v = env[k]
            if not isinstance(v, str):
                raise ValueError(f"{name}: env.{k} must be a string")
            lines.append(f"{k} = {toml_str(v)}")
    return "\n".join(lines) + "\n"


def existing_servers(text: str) -> set[str]:
    return {m.group(1).split(".")[0] for m in _HEADER_RE.finditer(text)}


def load_catalog(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {s["name"]: s for s in data.get("servers", []) if isinstance(s, dict)}


def install(catalog: dict[str, dict], config: Path, wanted_raw: str) -> int:
    wanted = [w.strip() for w in wanted_raw.split(",") if w.strip()]
    if not wanted:
        print("  no server names given", file=sys.stderr)
        return 1
    unknown = [w for w in wanted if w not in catalog]
    if unknown:
        print(f"  unknown MCP server(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"  available: {', '.join(sorted(catalog))}", file=sys.stderr)
        return 1

    original = config.read_text(encoding="utf-8") if config.is_file() else ""
    present = existing_servers(original)

    blocks: list[str] = []
    added: list[str] = []
    for name in wanted:
        if name in present:
            # Never rewrite an existing table: it may be the user's own tuning,
            # and a duplicate table is a TOML error besides.
            print(f"  = {name} already configured — left untouched")
            continue
        try:
            blocks.append(render_server(name, catalog[name]["config"]))
        except ValueError as e:
            print(f"  {e}", file=sys.stderr)
            return 1
        added.append(name)

    if not blocks:
        return 0

    banner = (
        "\n# ── RavenClaude: MCP servers you opted into with --with-mcp ──────────\n"
        "# APPEND-ONLY. Nothing above this line was modified. Each block is a\n"
        "# [mcp_servers.*] TABLE, which is position-independent in TOML, so adding\n"
        "# one cannot change the meaning of anything already in this file.\n"
        "# These are THIRD-PARTY servers; remove a block to uninstall it.\n"
    )
    new_text = original
    if new_text and not new_text.endswith("\n"):
        new_text += "\n"
    new_text += banner + "\n" + "\n".join(blocks)

    # THE SAFETY PROPERTY, asserted rather than promised.
    if not new_text.startswith(original):
        print("  refusing to write: the result is not a pure append", file=sys.stderr)
        return 1

    # Parse before writing. A file we cannot parse is a file we must not ship.
    if _toml is not None:
        try:
            _toml.loads(new_text)
        except Exception as e:  # noqa: BLE001
            print(f"  refusing to write: result does not parse as TOML — {e}", file=sys.stderr)
            return 1
    else:
        print("  WARNING: no TOML parser available; wrote without verification",
              file=sys.stderr)

    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(new_text, encoding="utf-8")
    for name in added:
        by = ", ".join(catalog[name].get("shipped_by") or []) or "?"
        print(f"  + {name} ({catalog[name].get('party', 'unstated')}, from {by})")
    return 0


def status(catalog: dict[str, dict], config: Path) -> int:
    text = config.read_text(encoding="utf-8") if config.is_file() else ""
    present = existing_servers(text)
    print("mcp:     ravenclaude-core ships NO MCP servers of its own.")
    print("         These come from other plugins and are OPT-IN on this host:")
    for name in sorted(catalog):
        mark = "configured" if name in present else "available"
        e = catalog[name]
        by = ", ".join(e.get("shipped_by") or []) or "?"
        print(f"           [{mark:10}] {name}  ({e.get('party', 'unstated')}; from {by})")
    print("         a project .codex/config.toml is read ONLY IN TRUSTED PROJECTS —")
    print("         writing it is not the same as Codex loading it.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", required=True, type=Path)
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--servers")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    try:
        catalog = load_catalog(args.catalog)
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"  cannot read the MCP catalogue: {e}", file=sys.stderr)
        return 1

    if args.status:
        return status(catalog, args.config)
    if args.servers:
        return install(catalog, args.config, args.servers)
    ap.error("one of --servers or --status is required")
    return 2


if __name__ == "__main__":
    sys.exit(main())
