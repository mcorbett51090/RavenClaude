#!/usr/bin/env python3
"""generate-codex-agents.py — project the canonical agents into Codex custom agents.

Sibling of `generate-copilot-plugin.py`. The canonical `plugins/ravenclaude-core/
agents/*.md` are the single source of truth; this emits one `.toml` per agent
into `plugins/ravenclaude-core/codex/agents/`, which the installer copies into a
consumer's `.codex/agents/`.

WHY THIS EXISTS, AND WHY IT IS A SECURITY FIX, NOT A CONVENIENCE
---------------------------------------------------------------
Codex documents a **per-agent `sandbox_mode`**, and — the load-bearing sentence —
**"the parent turn's permission mode is inherited when omitted"**. So an agent
file with no `sandbox_mode` does not run "safely by default": it runs with
whatever the parent session has. A review-only agent projected without it would
silently inherit write access.

That is the same shape as MH-10 on Copilot, where an omitted `tools:` silently
granted ALL tools. Hence the invariant here: **`sandbox_mode` is ALWAYS emitted,
never left to inheritance.** Gate 170 asserts it.

VERIFIED CONTRACT `[docs-verified 2026-07-29 —
https://learn.chatgpt.com/docs/agent-configuration/subagents]`:
  * location : `.codex/agents/*.toml` (project) or `~/.codex/agents/` (personal)
  * required : `name`, `description`, `developer_instructions`
  * optional : `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`,
               `skills.config`
  * `sandbox_mode` values seen in the docs' examples: "read-only",
    "workspace-write"; omitted ⇒ inherits the parent turn
  * applies to local Codex clients, the CLI among them

This projection deliberately emits only `name`, `description`, `sandbox_mode` and
`developer_instructions`:
  * `model` / `model_reasoning_effort` — the canonical agents pin no Codex model,
    and inventing one would silently override the consumer's own default.
  * `mcp_servers` — MCP on Codex is a separate, deliberately-deferred piece (the
    TOML merge risk); wiring it here would smuggle it in.

`[unverified — no Codex CLI on this machine]` Two things could not be checked by
execution, only by documentation, and both are named rather than assumed:
  1. Whether a kebab-case `name` (our canonical form) is accepted. The docs' one
     example uses `pr_explorer` in a file called `pr-explorer.toml`, so filename
     and name may differ — but nothing states a charset rule. We keep the
     canonical kebab name so an agent is called the same thing on every host; a
     mismatch would fail LOUDLY (agent not found), never silently widen privilege.
  2. openai/codex#26868 reports custom subagents in `~/.codex/agents/*.toml` not
     always being applied on spawn. That is an upstream defect, not a reason to
     emit a wrong file — but a consumer seeing an agent ignored should read that
     issue before assuming this projection is at fault.
Settle both by running Codex and spawning a projected agent.

Byte-deterministic: sorted iteration, `\\n` only, no timestamps. `--check` exits 1
if the committed tree differs from what would be generated.

Usage:
    python3 scripts/generate-codex-agents.py           # write the tree
    python3 scripts/generate-codex-agents.py --check   # exit 1 if stale
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_DIR = REPO_ROOT / "plugins" / "ravenclaude-core"
AGENTS_DIR = CORE_DIR / "agents"
OUTPUT_DIR = CORE_DIR / "codex" / "agents"

_FM_RE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.S)
_KV_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")

# A Claude tool that implies the agent may CHANGE the workspace. An agent
# declaring none of these is review-only and gets the read-only sandbox.
_WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

SANDBOX_READ_ONLY = "read-only"
SANDBOX_WORKSPACE_WRITE = "workspace-write"


def split_frontmatter(text: str) -> tuple[str, str]:
    m = _FM_RE.match(text)
    return (m.group(1), m.group(2)) if m else ("", text)


def scalar(raw: str) -> str:
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def parse_agent(path: Path) -> dict:
    fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    name = description = ""
    tools: list[str] = []
    for line in fm.splitlines():
        kv = _KV_RE.match(line)
        if not kv:
            continue
        key, raw = kv.group(1), kv.group(2)
        if key == "name" and not name:
            name = scalar(raw)
        elif key == "description" and not description:
            description = scalar(raw)
        elif key == "tools" and not tools:
            tools = [t.strip() for t in scalar(raw).split(",") if t.strip()]
    return {
        "name": name or path.stem,
        "description": description,
        "tools": tools,
        "body": body.strip(),
    }


def sandbox_for(tools: list[str]) -> str:
    """Least privilege: read-only unless the agent declares a write tool.

    `*` (all tools) means the agent is explicitly unrestricted, so it maps to
    workspace-write. An EMPTY tools list is treated as write-capable too — not
    as "no privileges" — because an agent with no declared tools is a malformed
    agent (check-frontmatter.py gates the field), and guessing "read-only" there
    would look like a working restriction while actually being a parse failure.
    Fail toward the honest value and let the frontmatter gate catch the real bug.
    """
    if not tools or "*" in tools:
        return SANDBOX_WORKSPACE_WRITE
    return (
        SANDBOX_WORKSPACE_WRITE
        if any(t in _WRITE_TOOLS for t in tools)
        else SANDBOX_READ_ONLY
    )


def toml_basic(value: str) -> str:
    """A TOML basic string (single line)."""
    out = value.replace("\\", "\\\\").replace('"', '\\"')
    out = out.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    return f'"{out}"'


def toml_literal_block(value: str) -> str:
    """A TOML multi-line LITERAL string — no escape processing at all.

    Chosen over a basic (\"\"\") block deliberately: agent bodies are markdown
    full of backslashes and quotes, and every one of those would need escaping in
    a basic string. A literal block needs none. Its only hazard is the terminator
    itself, which cannot be escaped inside a literal string — so if a body ever
    contains it we RAISE rather than emit a corrupt file.
    """
    if "'''" in value:
        raise ValueError(
            "agent body contains a TOML literal-string terminator (''') — emit "
            "this one as an escaped basic string instead of corrupting the file"
        )
    # A leading newline immediately after the opening delimiter is trimmed by
    # TOML, which is exactly the formatting we want.
    return "'''\n" + value + "\n'''"


def build_agent_toml(agent: dict) -> str:
    sandbox = sandbox_for(agent["tools"])
    header = (
        "# GENERATED by scripts/generate-codex-agents.py — do not edit by hand.\n"
        f"# Source: plugins/ravenclaude-core/agents/{agent['name']}.md\n"
        "#\n"
        "# sandbox_mode is ALWAYS emitted. Codex inherits the PARENT turn's\n"
        "# permission mode when it is omitted, so leaving it out would give a\n"
        "# review-only agent whatever the main session has — the same silent\n"
        "# privilege grant that MH-10 fixed on Copilot.\n"
        f"# Derived from the canonical tools: {', '.join(agent['tools']) or '(none)'}\n"
    )
    return (
        header
        + f"name = {toml_basic(agent['name'])}\n"
        + f"description = {toml_basic(agent['description'])}\n"
        + f"sandbox_mode = {toml_basic(sandbox)}\n"
        + f"developer_instructions = {toml_literal_block(agent['body'])}\n"
    )


def build_tree() -> dict[str, str]:
    tree: dict[str, str] = {}
    for path in sorted(AGENTS_DIR.glob("*.md")):
        agent = parse_agent(path)
        tree[f"{agent['name']}.toml"] = build_agent_toml(agent)
    return tree


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 if the tree is stale")
    args = ap.parse_args()

    tree = build_tree()
    if not tree:
        print("FATAL: no canonical agents found", file=sys.stderr)
        return 1

    if args.check:
        stale = []
        existing = {p.name for p in OUTPUT_DIR.glob("*.toml")} if OUTPUT_DIR.is_dir() else set()
        for rel, content in sorted(tree.items()):
            dest = OUTPUT_DIR / rel
            if not dest.is_file() or dest.read_text(encoding="utf-8") != content:
                stale.append(rel)
        for orphan in sorted(existing - set(tree)):
            stale.append(f"{orphan} (orphan — no canonical agent)")
        if stale:
            for rel in stale:
                print(f"STALE: {OUTPUT_DIR.relative_to(REPO_ROOT)}/{rel}", file=sys.stderr)
            return 1
        print(f"codex agents fresh ({len(tree)} file(s))")
        return 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for rel, content in sorted(tree.items()):
        dest = OUTPUT_DIR / rel
        dest.write_text(content, encoding="utf-8")
        print(f"wrote {dest.relative_to(REPO_ROOT)} ({len(content):,} bytes)")
    for orphan in sorted(p for p in OUTPUT_DIR.glob("*.toml") if p.name not in tree):
        orphan.unlink()
        print(f"removed orphan {orphan.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
