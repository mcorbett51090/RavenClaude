#!/usr/bin/env python3
"""check-copilot-agent-tools.py — Gate 166 (audit MH-10).

Asserts that the least-privilege `tools:` allowlist survives projection into the
Copilot `.agent.md` package, and — the part that actually needs a machine — that
the translation can never GRANT MORE than the canonical agent intended.

Why a gate rather than review. The projection is safe today because GitHub
documents that "All unrecognized tool names are ignored", so a wrong name is
dropped rather than widened. That makes it cheap to list several equal-privilege
spellings per Claude tool (belt and braces against silent capability loss on a
host we cannot execute in CI). The cost of that cheapness is that the map is
*inviting* to edit — and one execute-class name added to a read-only row would
hand arbitrary shell to `security-reviewer` while every other check stayed green.
That is precisely the P0 MH-10 closed, reopened from the inside. So the invariant
is checked by class, not trusted to care.

Four assertions:

  1. PROJECTED — every agent in the generated package carries a `tools:` line
     (unless canonically `*`), so the field cannot silently vanish again.
  2. FAITHFUL  — the projected set equals project_tools(canonical tools) exactly.
  3. NO ESCALATION (the security floor) — no projected name outranks the highest
     privilege class the canonical agent declared. An agent with no Bash may not
     receive an execute-class name; an agent with no Edit/Write may not receive a
     write-class name.
  4. THE P0 CASE, NAMED — `security-reviewer` specifically must not receive
     `edit`. Written as its own assertion because it is the finding's worked
     example and deserves to fail by name, not as one row of a loop.

Usage:
    python3 scripts/check-copilot-agent-tools.py
    python3 scripts/check-copilot-agent-tools.py --must-fail   # teeth self-test
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GEN = REPO_ROOT / "scripts" / "generate-copilot-plugin.py"
CANON_AGENTS = REPO_ROOT / "plugins" / "ravenclaude-core" / "agents"
PROJECTED = REPO_ROOT / "plugins" / "ravenclaude-core" / "copilot" / "agents"

_TOOLS_RE = re.compile(r"^tools:\s*(.+)$", re.M)
_FLOW_RE = re.compile(r'"([^"]+)"')


def load_generator():
    spec = importlib.util.spec_from_file_location("_copilot_gen_under_test", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def canonical_tools(path: Path) -> list[str]:
    m = _TOOLS_RE.search(path.read_text(encoding="utf-8"))
    if not m:
        return []
    raw = m.group(1).strip().strip('"').strip("'")
    return [t.strip() for t in raw.split(",") if t.strip()]


def projected_tools(path: Path) -> list[str] | None:
    """Return the emitted tool list, or None if the file carries no `tools:`."""
    m = _TOOLS_RE.search(path.read_text(encoding="utf-8"))
    if not m:
        return None
    return _FLOW_RE.findall(m.group(1))


def run(mod, *, mutate_map: bool = False) -> int:
    """Return the number of failures. `mutate_map` is the teeth half: it widens a
    read-only row with an execute-class name, exactly the edit assertion 3 exists
    to catch."""
    if mutate_map:
        # Put a WRITE-class name on a read-only row. This is the realistic shape
        # of the regression — someone adds a spelling without checking its class —
        # and it reproduces MH-10 exactly: every agent declaring Grep but not
        # Edit/Write (security-reviewer, code-reviewer, architect, …) silently
        # regains write.
        #
        # Note an execute-class mutant would NOT do: all 15 agents declare Bash,
        # so exec is already in every declared set and nothing would escalate.
        # The mutant has to grant a class no agent declared.
        mod._AGENT_TOOL_MAP = dict(mod._AGENT_TOOL_MAP)
        mod._AGENT_TOOL_MAP["Grep"] = ("grep", "search", "edit")

    failures = 0

    def bad(msg: str) -> None:
        nonlocal failures
        failures += 1
        print(f"  FAIL: {msg}", file=sys.stderr)

    agents = sorted(CANON_AGENTS.glob("*.md"))
    if not agents:
        bad("no canonical agents found — the gate would pass vacuously")
        return failures

    for canon in agents:
        proj = PROJECTED / f"{canon.stem}.agent.md"
        if not proj.is_file():
            bad(f"{canon.stem}: no projected .agent.md")
            continue

        declared = canonical_tools(canon)
        expected = mod.project_tools(declared)
        actual = projected_tools(proj)

        # 1 — the field must be present whenever a restriction was intended.
        if expected and actual is None:
            bad(f"{canon.stem}: canonical tools {declared} but projection has NO "
                f"tools: line — agent runs fully privileged")
            continue

        # 2 — faithful translation.
        if expected and actual != expected:
            bad(f"{canon.stem}: projected {actual} != expected {expected}")

        # 3 — the security floor: the projected classes must be a SUBSET of the
        # declared classes.
        #
        # Set membership, deliberately NOT a max-privilege ceiling. A ceiling is
        # the intuitive rule and it is wrong here: `security-reviewer` declares
        # Bash, so its ceiling would be execute-class, which would then license
        # `edit` — the very grant it deliberately withholds. Its declared classes
        # are {read, exec} and write is simply not among them. The first version
        # of this gate used the ceiling and could not fail on the finding it
        # exists to guard.
        #
        # Checked against BOTH the generated `expected` and the committed
        # `actual`: the first catches a widened map before anyone regenerates,
        # the second catches a hand-edited package.
        declared_classes = {
            mod._CLAUDE_TOOL_CLASS[t] for t in declared if t in mod._CLAUDE_TOOL_CLASS
        }
        for label, names in (("map", expected), ("package", actual or [])):
            for name in names:
                cls = mod._COPILOT_TOOL_CLASS.get(name)
                if cls is None:
                    bad(f"{canon.stem}: projected unknown-class name {name!r} — add "
                        f"it to _COPILOT_TOOL_CLASS with its privilege class")
                    continue
                if cls not in declared_classes:
                    bad(f"{canon.stem}: ESCALATION in {label} — {name!r} is "
                        f"{cls}-class but the canonical agent declares only "
                        f"{sorted(declared_classes)}. Canonical: {declared}")

    # 4 — the worked example, by name.
    sec = PROJECTED / "security-reviewer.agent.md"
    if sec.is_file():
        got = projected_tools(sec) or []
        if "edit" in got:
            bad("security-reviewer: projection grants 'edit' — the exact P0 MH-10 "
                "closed (canonically Read/Grep/Glob/Bash/WebFetch, no Write/Edit)")
        if not got:
            bad("security-reviewer: no projected tools at all — least-privilege lost")
    else:
        bad("security-reviewer.agent.md missing from the projected package")

    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--must-fail", action="store_true",
                    help="teeth: widen a read-only row and assert this gate catches it")
    args = ap.parse_args()

    mod = load_generator()

    if args.must_fail:
        # The teeth half must fail for the RIGHT reason. A mutant that merely
        # made the projection stale would also produce failures, so require the
        # escalation assertion itself to be among them.
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            failures = run(mod, mutate_map=True)
        text = err.getvalue()
        if failures == 0:
            print("MUST-FAIL: mutant produced NO failures — the gate has no teeth",
                  file=sys.stderr)
            return 1
        if "ESCALATION" not in text:
            print("MUST-FAIL: mutant failed, but not on the escalation assertion — "
                  "the class check is not what caught it", file=sys.stderr)
            print(text, file=sys.stderr)
            return 1
        print(f"  ok: teeth — a write-class name on a read-only row is caught "
              f"({failures} failure(s), incl. ESCALATION)")
        print("Copilot agent tools: MUST-FAIL half behaved correctly")
        return 0

    failures = run(mod)
    if failures:
        print(f"FAIL: {failures} assertion(s) failed", file=sys.stderr)
        return 1
    n = len(sorted(CANON_AGENTS.glob("*.md")))
    print(f"  ok: {n} agents project their least-privilege tools with no class escalation")
    print("  ok: security-reviewer does NOT receive 'edit'")
    print("Copilot agent tools: ALL ASSERTIONS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
