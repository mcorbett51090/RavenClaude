#!/usr/bin/env python3
"""check-nested-dispatch.py — no shipped agent may be able to call agents unless it says so.

WHY THIS GATE. "Sub-agents do not spawn other sub-agents" is a house rule in
rules/agent-collaboration.md and in 180+ plugin constitutions. It is NOT a
platform limit: Claude Code lets a subagent spawn its own, three layers deep by
default (v2.1.219; CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH). The thing that
actually keeps a RavenClaude agent from nesting is its `tools:` allow-list —
the sub-agents reference is explicit: *"To keep one subagent from spawning
while nesting is on ... omit `Agent` from its `tools` list or add it to
`disallowedTools`"* [docs-verified 2026-09-14]. On 2026-09-14 every one of the
623 roster agents omitted `Agent`, so the rule held — by coincidence of
authoring, not by anything that would notice if one file changed. The only
guard was guard-recursive-spawn.sh, a PostToolUse grep over PROSE that warns
and cannot block. This file gates the DECLARATION, which is the layer that
binds.

Two platform facts make the allow-list the right place to gate, not the prose:

  1. In a SUBAGENT definition the `Agent(type)` allow-list syntax is IGNORED —
     "listing `Agent` in `tools` lets that subagent spawn subagents of its own
     while the depth limit allows it, but any type list inside the parentheses
     is ignored" [sub-agents reference, 2026-09-14]. So `Agent(scout)` does not
     mean "may dispatch scout only"; it means "may dispatch anything at any
     tier". A declaration cannot scope nested dispatch; only a PreToolUse hook
     keyed on the `agent_id` input field could. Until such a hook ships, an
     agent that lists `Agent` in any form has unscoped, un-tiered dispatch.
  2. `tools: "*"` inherits every tool available to subagents, `Agent` included.

WHAT IT FAILS ON: an `agents/*.md` whose frontmatter `tools:` grants dispatch —
`Agent`, `Agent(...)`, the historical alias `Task`, or the wildcard `*` — with
no reasoned exemption in tests/fixtures/nested-dispatch-exemptions.json
({"<agent-name>": "<reason>"}). A stale exemption (no such agent) fails; a
reasonless one fails. `TaskOutput` / `TaskStop` are different tools and pass.
A `disallowedTools:` entry is not a grant. An empty roster is not a pass.

WHAT IT DOES NOT DO: read `hooks.json`, run anything, or judge whether nesting
SHOULD be allowed for an exempt agent — the exemption reason is where that
judgment is recorded, and docs/decisions/2026-09-14-nested-dispatch-determination.md
is where the house verdict lives.

Exit codes: --check -> 0 clean / 1 violation. --must-fail -> 3 (declared teeth).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

EXEMPTIONS = "tests/fixtures/nested-dispatch-exemptions.json"
AGENT_GLOB = "plugins/*/agents/**/*.md"
RULE = "plugins/ravenclaude-core/rules/agent-collaboration.md"
DECISION = "docs/decisions/2026-09-14-nested-dispatch-determination.md"

_FM = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
_NAME = re.compile(r"^name:[ \t]*[\"']?([A-Za-z0-9][\w-]*)", re.M)
_TOOLS_INLINE = re.compile(r"^tools:[ \t]*(.*?)[ \t]*$", re.M)
_BLOCK_ITEM = re.compile(r"^[ \t]+-[ \t]*(.+?)[ \t]*$")
_NON_DEFINITION_DOCS = frozenset({"readme.md", "changelog.md", "notes.md"})

# The tool names that grant dispatch. Exact base-name match (before any "(")
# so `TaskOutput` / `TaskStop` / `AgentMap` never trip it.
DISPATCH_TOOLS = frozenset({"agent", "task"})


def _strip(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1].strip()
    return s


def _split_top_level(s: str) -> list[str]:
    """Split on commas that are not inside parentheses (`Bash(git a, b)` stays whole)."""
    out: list[str] = []
    depth = 0
    cur: list[str] = []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return [t for t in (x.strip() for x in out) if t]


def tools_of(frontmatter: str) -> list[str] | None:
    """-> the `tools:` entries, or None when no `tools:` line exists (check-frontmatter's job)."""
    m = _TOOLS_INLINE.search(frontmatter)
    if not m:
        return None
    raw = _strip(m.group(1))
    if raw:
        if raw.startswith("[") and raw.endswith("]"):
            raw = raw[1:-1]
        return [_strip(t) for t in _split_top_level(raw)]
    # block form: the entries are the indented `- X` lines that follow
    items: list[str] = []
    lines = frontmatter[m.end() :].splitlines()
    for ln in lines[1:] if lines and lines[0] == "" else lines:
        bm = _BLOCK_ITEM.match(ln)
        if bm:
            items.append(_strip(bm.group(1)))
        elif ln.strip():
            break
    return items


def grants_dispatch(entry: str) -> str:
    """Pure: one `tools:` entry -> the grant it carries ('' when none)."""
    e = entry.strip()
    if e == "*":
        return "*"
    base = e.split("(", 1)[0].strip()
    if base.lower() in DISPATCH_TOOLS:
        return e
    return ""


def measure(root: Path) -> list[dict]:
    rows: list[dict] = []
    for f in sorted(glob.glob(str(root / AGENT_GLOB), recursive=True)):
        p = Path(f)
        if p.name.casefold() in _NON_DEFINITION_DOCS:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = _FM.match(text)
        if not m:
            continue
        fm = m.group(1)
        tools = tools_of(fm)
        if tools is None:
            continue
        rel = p.relative_to(root)
        plugin = rel.parts[1] if len(rel.parts) > 1 else ""
        nm = _NAME.search(fm)
        name = nm.group(1) if nm else p.stem
        grants = [g for g in (grants_dispatch(t) for t in tools) if g]
        rows.append(
            {"path": str(rel), "plugin": plugin, "name": name, "tools": tools, "grants": grants}
        )
    return rows


def _load_exemptions(root: Path) -> tuple[dict[str, str], list[str]]:
    fp = root / EXEMPTIONS
    if not fp.is_file():
        return {}, []
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"{EXEMPTIONS} does not parse as JSON ({exc}) — UNKNOWN, not clean"]
    if not isinstance(data, dict):
        return {}, [f"{EXEMPTIONS} must be an object of {{agent-name: reason}}"]
    out: dict[str, str] = {}
    problems: list[str] = []
    for k, v in data.items():
        if k.startswith("_"):
            continue
        if not isinstance(v, str) or not v.strip():
            problems.append(
                f"{EXEMPTIONS}: exemption for `{k}` has no reason — a bare name is not an exemption"
            )
            continue
        out[k] = v
    return out, problems


def evaluate(rows: list[dict], exemptions: dict[str, str]) -> tuple[int, list[str], dict]:
    """Pure: (measurement, exemptions) -> (rc, lines, counts)."""
    lines: list[str] = []
    counts = {
        "agents_with_tools": len(rows),
        "granting": 0,
        "granting_exempt": 0,
        "stale_exemptions": 0,
    }
    if not rows:
        lines.append(
            "  ✗ no agents with a `tools:` line were found — an EMPTY measurement is not a pass"
        )
        return 1, lines, counts
    rc = 0
    names = {r["name"] for r in rows}
    for ex in sorted(exemptions):
        if ex not in names:
            counts["stale_exemptions"] += 1
            lines.append(
                f"  ✗ {EXEMPTIONS} exempts `{ex}`, which is not an agent on this roster — a stale"
                " exemption is how an allow-list rots; delete the row"
            )
            rc = 1
    for r in rows:
        if not r["grants"]:
            continue
        counts["granting"] += 1
        shown = ", ".join(f"`{g}`" for g in r["grants"])
        if r["name"] in exemptions:
            counts["granting_exempt"] += 1
            lines.append(
                f"  ⚠ {r['plugin']}/{r['name']}: tools grants {shown} — EXEMPT: {exemptions[r['name']]}"
            )
            continue
        why = (
            "the wildcard inherits `Agent`"
            if "*" in r["grants"]
            else "a type list in `Agent(...)` is IGNORED in a subagent definition, so this is unscoped"
            if any("(" in g for g in r["grants"])
            else "a called agent that can call agents"
        )
        lines.append(
            f"  ✗ {r['plugin']}/{r['name']}: tools grants {shown} — {why}; the house rule is"
            " single-orchestrator (sub-agents surface needs to the Team Lead). Omit it, or exempt"
            f" the agent BY NAME with a reason in {EXEMPTIONS}"
        )
        rc = 1
    return rc, lines, counts


def report(counts: dict, exemptions: dict[str, str]) -> None:
    print(
        f"  agents with tools: {counts['agents_with_tools']}   granting dispatch: {counts['granting']}"
        f" (exempt {counts['granting_exempt']})   exemptions on file: {len(exemptions)}"
    )


def _fake_roster(root: Path, plugin: str, agents: list[tuple[str, str]]) -> None:
    """agents: [(name, tools-frontmatter-fragment)] — the fragment is the raw `tools:` block."""
    d = root / "plugins" / plugin / "agents"
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.md"):
        old.unlink()
    for name, tools_fragment in agents:
        (d / f"{name}.md").write_text(
            f"---\nname: {name}\ndescription: t\n{tools_fragment}\nmodel: sonnet\n---\n\nbody\n",
            encoding="utf-8",
        )


def must_fail() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        fake = Path(td)
        (fake / "tests" / "fixtures").mkdir(parents=True)
        no_ex: dict[str, str] = {}

        # 1. `Agent` in an inline list -> MUST FAIL
        _fake_roster(fake, "p", [("a", "tools: Read, Grep, Agent")])
        rc, _, _ = evaluate(measure(fake), no_ex)
        if rc == 0:
            print("✗ must-fail: `Agent` in tools was accepted.")
            return 0
        # 1b. the historical alias `Task` -> MUST FAIL
        _fake_roster(fake, "p", [("a", "tools: Read, Task")])
        rc, _, _ = evaluate(measure(fake), no_ex)
        if rc == 0:
            print("✗ must-fail: `Task` in tools was accepted.")
            return 0
        # 1c. the wildcard -> MUST FAIL (it inherits Agent)
        _fake_roster(fake, "p", [("a", 'tools: "*"')])
        rc, lines, _ = evaluate(measure(fake), no_ex)
        if rc == 0 or not any("wildcard" in ln for ln in lines):
            print('✗ must-fail: `tools: "*"` was accepted or not named as the wildcard grant.')
            return 0
        # 1d. `Agent(scout)` -> MUST FAIL and must say the type list is ignored
        _fake_roster(fake, "p", [("a", "tools: Read, Agent(scout)")])
        rc, lines, _ = evaluate(measure(fake), no_ex)
        if rc == 0 or not any("IGNORED" in ln for ln in lines):
            print("✗ must-fail: `Agent(scout)` was accepted or not flagged as unscoped.")
            return 0
        # 1e. block-list form -> MUST FAIL
        _fake_roster(fake, "p", [("a", "tools:\n  - Read\n  - Agent")])
        rc, _, _ = evaluate(measure(fake), no_ex)
        if rc == 0:
            print("✗ must-fail: block-form `- Agent` was accepted.")
            return 0
        # 1f. flow-sequence form `[Read, Agent]` -> MUST FAIL
        _fake_roster(fake, "p", [("a", "tools: [Read, Agent]")])
        rc, _, _ = evaluate(measure(fake), no_ex)
        if rc == 0:
            print("✗ must-fail: flow-sequence `[Read, Agent]` was accepted.")
            return 0
        # 2. an exemption WITH a reason -> passes, with the advisory line
        _fake_roster(fake, "p", [("a", "tools: Read, Agent")])
        rc, lines, counts = evaluate(measure(fake), {"a": "orchestrator persona; see decision"})
        if rc != 0 or counts["granting_exempt"] != 1 or not any("EXEMPT" in ln for ln in lines):
            print("✗ must-fail control: a reasoned exemption did not pass with an advisory.")
            return 0
        # 2b. an exemption WITHOUT a reason -> the loader reports it, and the grant still fails
        (fake / EXEMPTIONS).write_text(json.dumps({"a": ""}), encoding="utf-8")
        ex, problems = _load_exemptions(fake)
        rc, _, _ = evaluate(measure(fake), ex)
        if not problems or rc == 0:
            print("✗ must-fail: a reasonless exemption was honoured.")
            return 0
        # 3. a stale exemption -> MUST FAIL
        _fake_roster(fake, "p", [("a", "tools: Read")])
        rc, _, counts = evaluate(measure(fake), {"ghost": "was removed"})
        if rc == 0 or counts["stale_exemptions"] != 1:
            print("✗ must-fail: a stale exemption was accepted.")
            return 0
        # 4. CONTROL — a normal allow-list passes clean, including `Bash(git a, b)` with a
        #    comma inside the parentheses and the look-alikes TaskOutput / TaskStop / AgentMap
        _fake_roster(
            fake,
            "p",
            [
                ("a", "tools: Read, Grep, Glob, Bash(git log, git show), WebFetch"),
                ("b", "tools: Read, TaskOutput, TaskStop, AgentMap"),
                ("c", "tools: Read, Edit\ndisallowedTools: Agent"),
            ],
        )
        rows = measure(fake)
        rc, lines, counts = evaluate(rows, no_ex)
        if rc != 0 or counts["granting"] != 0 or any("✗" in ln or "⚠" in ln for ln in lines):
            print("✗ must-fail control: a clean roster did not pass clean.")
            return 0
        if [r["tools"] for r in rows if r["name"] == "a"][0] != [
            "Read",
            "Grep",
            "Glob",
            "Bash(git log, git show)",
            "WebFetch",
        ]:
            print("✗ must-fail control: the comma inside `Bash(...)` split the entry.")
            return 0
        # 5. empty roster -> rc 1, never a pass
        _fake_roster(fake, "p", [])
        rc, _, _ = evaluate(measure(fake), no_ex)
        if rc == 0:
            print("✗ must-fail: an empty roster was reported as clean.")
            return 0
    print('✓ must-fail: `Agent`, `Task`, `"*"`, `Agent(scout)`, block-form and flow-form grants')
    print("  all fail; a stale or reasonless exemption fails; a reasoned exemption passes with an")
    print("  advisory; a normal allow-list (incl. `Bash(a, b)`, TaskOutput/TaskStop/AgentMap and a")
    print("  `disallowedTools: Agent`) passes clean; an empty roster is not a pass.")
    print("  Exiting 3, the DECLARED teeth code.")
    return 3


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", default=".")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 3")
        return 0
    if args.must_fail:
        return must_fail()

    root = Path(os.path.abspath(args.root))
    rows = measure(root)
    exemptions, problems = _load_exemptions(root)
    rc, lines, counts = evaluate(rows, exemptions)
    report(counts, exemptions)
    for pr in problems:
        print(f"  ✗ {pr}")
        rc = 1
    for ln in lines:
        print(ln)
    if rc == 0 and counts["granting"] == 0:
        print(
            "  ✓ no shipped agent can call agents: every `tools:` allow-list omits `Agent` / `Task` /"
            " `*` — the single-orchestrator rule is declared, not assumed"
        )
    elif rc == 0:
        print("  ✓ no unexempted grant (exempt agents listed above)")
    print(f"  ref: {RULE} · {DECISION}")
    return rc if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
