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

Pin rule (added 2026-10-19 repo review): a server launched by a package runner
(`uvx`, `npx`, `bunx`, `pipx run`) must name an exact version — `pkg==1.2.3` or
`pkg@1.2.3` (scoped npm: `@scope/pkg@1.2.3`). `@latest` or a bare package name is
a violation: the runner would fetch whatever release is newest at each MCP start
and run it with the user's privileges (bundled-mcp-servers.md requires "a pinned
published artifact"). URL (`http`) servers and bare installed commands are not
package-runner launches and are not checked.

Exit 0 if all bundled servers are attributed and pinned; exit 1 (listing
violations) otherwise. `--root DIR` scans an alternate tree (used by
audit-gates.sh fixtures); default is the repo root. `--self-test` runs the
built-in fixtures.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import tempfile

# Package runners whose first positional argument is a package spec, with the
# flags that carry the spec themselves and the flags that take a (non-spec) value.
_RUNNERS = {
    "uvx": (
        {"--from"},
        {
            "--python",
            "-p",
            "--with",
            "--with-editable",
            "--with-requirements",
            "--index",
            "--index-url",
            "--extra-index-url",
            "-c",
            "--constraints",
        },
    ),
    "npx": ({"-p", "--package"}, {"--registry", "--cache", "-c", "--call"}),
    "bunx": ({"-p", "--package"}, set()),
    "pipx": ({"--spec"}, {"--python", "--index-url", "--pip-args"}),
}
_VERSION = re.compile(r"\d+(?:\.\d+){0,3}(?:[-+.]?[0-9A-Za-z][0-9A-Za-z.+-]*)?")


def package_spec(command: str, args: list) -> str | None:
    """The package spec a runner launch names, or None when `command` is not a runner."""
    base = os.path.basename(str(command))
    if base not in _RUNNERS:
        return None
    spec_flags, value_flags = _RUNNERS[base]
    toks = [str(a) for a in (args or [])]
    if base == "pipx" and toks and toks[0] == "run":
        toks = toks[1:]
    i = 0
    while i < len(toks):
        tok = toks[i]
        if tok in spec_flags:
            return toks[i + 1] if i + 1 < len(toks) else ""
        if tok in value_flags:
            i += 2
            continue
        if tok.startswith("-"):
            i += 1
            continue
        return tok
    return ""


def is_pinned(spec: str) -> bool:
    """True for `name==1.2.3` or `name@1.2.3` (incl. scoped `@scope/name@1.2.3`)."""
    if "==" in spec:
        name, ver = spec.split("==", 1)
        return bool(name) and _VERSION.fullmatch(ver) is not None
    at = spec.rfind("@")
    if at > 0:
        return _VERSION.fullmatch(spec[at + 1 :]) is not None
    return False


def check_pins(name: str, servers: dict) -> list[str]:
    errs: list[str] = []
    for server, cfg in servers.items():
        if not isinstance(cfg, dict):
            continue
        spec = package_spec(cfg.get("command", ""), cfg.get("args", []))
        if spec is None or is_pinned(spec):
            continue
        runner = os.path.basename(str(cfg.get("command", "")))
        errs.append(
            f"{name}: mcpServers['{server}'] launches `{runner} {spec or '<no package>'}` "
            f"without an exact version — pin it as ==<version> or @<version> (never "
            f"@latest); see docs/best-practices/bundled-mcp-servers.md"
        )
    return errs


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
    if isinstance(servers, dict):
        errs += check_pins(name, servers)
    attr = data.get("x-mcpAttribution", {})
    if not isinstance(attr, dict):
        return errs + [
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
                # Word/token-boundary match, not a bare substring: a NOTICE that
                # names a LONGER server (e.g. 'postman-enterprise') must not
                # spuriously satisfy attribution for a shorter one ('postman'),
                # nor 'dbeaver' satisfy 'db'. `-`/`_`/word-chars are treated as
                # part of a token so a server name embedded in a longer id fails.
                if not re.search(r"(?<![\w-])" + re.escape(server) + r"(?![\w-])", nf.read()):
                    errs.append(
                        f"{name}: {notice} does not mention server '{server}' "
                        f"(attribution must name the server it covers)"
                    )
    return errs


def _self_test() -> int:
    """Fixtures for the pin rule (attributed, so only the pin decides the verdict)."""

    def verdict(server_cfg: dict) -> bool:
        with tempfile.TemporaryDirectory() as d:
            root = os.path.join(d, "plugins", "sample")
            os.makedirs(os.path.join(root, ".claude-plugin"))
            manifest = {
                "name": "sample",
                "version": "0.0.1",
                "mcpServers": {"acme": server_cfg},
                "x-mcpAttribution": {
                    "acme": {"party": "third-party", "source": "s", "license": "MIT"}
                },
            }
            with open(os.path.join(root, ".claude-plugin", "plugin.json"), "w") as fh:
                json.dump(manifest, fh)
            with open(os.path.join(root, "NOTICE.md"), "w") as fh:
                fh.write("acme attribution\n")
            return not check_plugin(os.path.join(root, ".claude-plugin", "plugin.json"))

    cases = [
        ("uvx pkg@latest fails", {"command": "uvx", "args": ["acme-mcp@latest"]}, False),
        ("uvx unversioned fails", {"command": "uvx", "args": ["acme-mcp"]}, False),
        ("npx -y unversioned fails", {"command": "npx", "args": ["-y", "@acme/mcp"]}, False),
        ("pipx run unversioned fails", {"command": "pipx", "args": ["run", "acme-mcp"]}, False),
        ("uvx pkg==1.2.3 passes", {"command": "uvx", "args": ["acme-mcp==1.2.3"]}, True),
        (
            "uvx --from pkg==1.2.3 passes",
            {"command": "uvx", "args": ["--from", "acme==1.2.3", "acme"]},
            True,
        ),
        (
            "npx -y @scope/pkg@1.2.3 passes",
            {"command": "npx", "args": ["-y", "@acme/mcp@1.2.3"]},
            True,
        ),
        (
            "absolute-path uvx is still checked",
            {"command": "/home/u/.local/bin/uvx", "args": ["acme"]},
            False,
        ),
        ("bare installed command is not a runner", {"command": "acme-mcp-server"}, True),
        ("url server is not a runner", {"type": "http", "url": "https://example.com/mcp"}, True),
    ]
    failed = 0
    for label, cfg, want_ok in cases:
        ok = verdict(cfg) == want_ok
        failed += not ok
        print(("  PASS " if ok else "  FAIL ") + label)
    print(f"check-mcp-attribution self-test: {len(cases) - failed}/{len(cases)} passed.")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="repo root to scan (default: .)")
    ap.add_argument("--self-test", action="store_true", help="run the built-in pin fixtures")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()

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
