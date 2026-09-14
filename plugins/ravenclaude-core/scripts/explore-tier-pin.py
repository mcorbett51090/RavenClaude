#!/usr/bin/env python3
"""explore-tier-pin.py — the PREVENTION leg of model-tier delegation.

Called by hooks/explore-tier-pin.sh (PreToolUse on Agent/Task). Reads the
PreToolUse payload on stdin and, when the dispatch is an un-pinned built-in
`Explore`, prints a `hookSpecificOutput.updatedInput` envelope that adds
`model: <tier>` to the tool input. Prints NOTHING otherwise.

WHY A REWRITE AND NOT AN ADVISORY. handoff-tax-meter.sh (PostToolUse) already
flags `frontier_readonly` — but it fires AFTER the Explore has run on the
frontier model, i.e. after the money is spent. The doctrine in
knowledge/model-tier-delegation.md says "pass `model: haiku` per invocation";
the constitution says the same; both are prose, and prose has no gate on the
Agent call. `updatedInput` is the one PreToolUse field that DOES bind here:
`[docs-verified 2026-09-14, hooks reference § "PreToolUse decision control"]`
"Modifies the tool's input parameters before execution. Replaces the entire
input object, so include unchanged fields alongside modified ones." The
envelope is emitted WITHOUT a `permissionDecision`, so the consumer's
comfort-posture `subagent_dispatch` category (allow / ask) still governs the
dispatch exactly as before — this hook changes the model, never the gate.

WHAT IT PINS — deliberately narrow:
  * subagent_type basename == "explore" (the built-in; matched after any
    plugin-scope prefix, case-insensitive). Explore is the ONE built-in whose
    whole job is reading and which, since Claude Code v2.1.198, inherits the
    main conversation's model when un-pinned. `scout` already pins `haiku` via
    frontmatter; `general-purpose` / `Plan` do real work and are left alone.
  * tool_input.model absent or empty. An explicit `model` — including an
    explicit "inherit" — is the Team Lead's decision and is honoured.
  * CLAUDE_CODE_SUBAGENT_MODEL unset. When the consumer already routes every
    sub-agent by env var, a per-invocation pin would OVERRIDE that fleet-wide
    choice (per-invocation wins in the resolution order), so the hook stands
    down.

KNOB (in .ravenclaude/comfort-posture.yaml):
    handoff_tax:
      pin_explore: haiku      # default when the key is absent; sonnet | off
    handoff_tax: off          # disables the meter's advisory AND this pin
Absent posture file -> the calling hook has already no-op'd (opt-in by posture
presence, the same rule as every other advisory/rewrite hook in this plugin).

FAIL-SAFE: every error path prints nothing and exits 0 — the dispatch proceeds
with the input Claude sent. A rewrite that cannot be computed is not applied.

Self-test: `python3 explore-tier-pin.py --self-test` — proves the four
stand-down conditions, the two pin values, the knob parse, the `off` knob, the
envelope shape (every original field preserved), and a must-fail canary (an
un-pinned Explore that MUST be rewritten).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_PIN = "haiku"
ALLOWED_PINS = ("haiku", "sonnet")
PIN_TYPES = frozenset({"explore"})

_MAX_POSTURE_BYTES = 256 * 1024
_POSTURE_OFF = re.compile(r"^[ \t]*handoff_tax[ \t]*:[ \t]*(off|false|no)\b", re.M)
_POSTURE_BLOCK = re.compile(r"^[ \t]*handoff_tax[ \t]*:[ \t]*$", re.M)
_POSTURE_PIN = re.compile(r"^[ \t]+pin_explore[ \t]*:[ \t]*([A-Za-z_-]+)\b", re.M)

DOCTRINE = "plugins/ravenclaude-core/knowledge/model-tier-delegation.md"


def find_project_root(start: Path) -> Path:
    try:
        cur = start.resolve()
    except OSError:
        return start
    for cand in (cur, *cur.parents):
        if (cand / ".ravenclaude").is_dir() or (cand / ".git").exists():
            return cand
    return cur


def read_pin(root: Path) -> str | None:
    """Return the tier to pin, or None when the knob turns the pin off.

    Regex, not YAML: no pyyaml dependency; the knob is one scalar in one block.
    Absent file / absent key -> DEFAULT_PIN. An unrecognised value -> None
    (off): a knob we cannot read must not become a rewrite we did not intend.
    """
    p = root / ".ravenclaude" / "comfort-posture.yaml"
    try:
        if not p.is_file() or p.stat().st_size > _MAX_POSTURE_BYTES:
            return DEFAULT_PIN
        raw = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return DEFAULT_PIN
    if _POSTURE_OFF.search(raw):
        return None
    if _POSTURE_BLOCK.search(raw):
        m = _POSTURE_PIN.search(raw)
        if m:
            val = m.group(1).strip().lower()
            if val in ALLOWED_PINS:
                return val
            return None  # off, false, no, or anything we do not recognise
    return DEFAULT_PIN


def _basename_type(subagent_type: str) -> str:
    return (subagent_type or "").rsplit(":", 1)[-1].strip().lower()


def decide(payload: dict, pin: str | None, env: dict) -> dict | None:
    """Pure: payload + knob + env -> envelope dict, or None (stand down)."""
    if payload.get("tool_name") not in ("Agent", "Task"):
        return None
    if pin is None:
        return None
    if env.get("CLAUDE_CODE_SUBAGENT_MODEL"):
        return None
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    if _basename_type(str(tool_input.get("subagent_type") or "")) not in PIN_TYPES:
        return None
    model = tool_input.get("model")
    if isinstance(model, str) and model.strip():
        return None
    if model is not None and not isinstance(model, str):
        return None
    updated = dict(tool_input)
    updated["model"] = pin
    subagent = str(tool_input.get("subagent_type") or "Explore")
    context = (
        f"[RavenClaude guard notice — explore-tier-pin] `{subagent}` was dispatched "
        f"without `model`, so it would have inherited this conversation's model "
        f"(Claude Code ≥ v2.1.198). Pinned to `{pin}` before it ran — a read-only "
        f"search worker is the 'high volume, low judgment' row of the tier table. "
        f"To run Explore on a stronger tier, pass `model` explicitly; the pin never "
        f"overrides an explicit choice. Knob: `handoff_tax: {{ pin_explore: "
        f"haiku | sonnet | off }}` in .ravenclaude/comfort-posture.yaml. Ref: {DOCTRINE}"
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": updated,
            "additionalContext": context,
        }
    }


# ── self-test ───────────────────────────────────────────────────────────────


def _payload(subagent_type: str = "Explore", model=None, tool_name: str = "Agent") -> dict:
    ti = {"prompt": "find every caller of foo", "description": "t", "subagent_type": subagent_type}
    if model is not None:
        ti["model"] = model
    return {"session_id": "selftest", "tool_name": tool_name, "tool_input": ti}


def self_test() -> int:
    import tempfile

    fails = 0

    def check(name: str, ok: bool) -> None:
        nonlocal fails
        print(("  ✓ " if ok else "  ✗ ") + name)
        if not ok:
            fails += 1

    env: dict = {}
    # must-fail canary: the un-pinned Explore MUST be rewritten.
    env_out = decide(_payload(), DEFAULT_PIN, env)
    check("canary: un-pinned Explore -> envelope", env_out is not None)
    if env_out:
        hso = env_out["hookSpecificOutput"]
        check("envelope: hookEventName PreToolUse", hso.get("hookEventName") == "PreToolUse")
        check("envelope: updatedInput.model == haiku", hso["updatedInput"].get("model") == "haiku")
        check(
            "envelope: original fields preserved",
            hso["updatedInput"].get("prompt") == "find every caller of foo"
            and hso["updatedInput"].get("subagent_type") == "Explore",
        )
        check("envelope: NO permissionDecision (gate untouched)", "permissionDecision" not in hso)
        check(
            "envelope: additionalContext names the knob", "pin_explore" in hso["additionalContext"]
        )
    check(
        "plugin-scoped explore is matched",
        decide(_payload("some-plugin:explore"), DEFAULT_PIN, env) is not None,
    )
    check(
        "Task (legacy tool name) is matched",
        decide(_payload(tool_name="Task"), DEFAULT_PIN, env) is not None,
    )
    check(
        "pin value sonnet honoured",
        (decide(_payload(), "sonnet", env) or {})
        .get("hookSpecificOutput", {})
        .get("updatedInput", {})
        .get("model")
        == "sonnet",
    )
    # stand-downs
    check("stand down: explicit model", decide(_payload(model="opus"), DEFAULT_PIN, env) is None)
    check(
        "stand down: explicit inherit", decide(_payload(model="inherit"), DEFAULT_PIN, env) is None
    )
    check(
        "stand down: scout (pins via frontmatter)",
        decide(_payload("scout"), DEFAULT_PIN, env) is None,
    )
    check(
        "stand down: general-purpose", decide(_payload("general-purpose"), DEFAULT_PIN, env) is None
    )
    check(
        "stand down: non-dispatch tool",
        decide(_payload(tool_name="Bash"), DEFAULT_PIN, env) is None,
    )
    check("stand down: knob off", decide(_payload(), None, env) is None)
    check(
        "stand down: CLAUDE_CODE_SUBAGENT_MODEL set",
        decide(_payload(), DEFAULT_PIN, {"CLAUDE_CODE_SUBAGENT_MODEL": "haiku"}) is None,
    )
    check(
        "stand down: malformed tool_input",
        decide({"tool_name": "Agent", "tool_input": "x"}, DEFAULT_PIN, env) is None,
    )
    check(
        "empty model string counts as un-pinned",
        decide(_payload(model=""), DEFAULT_PIN, env) is not None,
    )

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".ravenclaude").mkdir()
        pf = root / ".ravenclaude" / "comfort-posture.yaml"
        check("knob: no posture file -> default haiku", read_pin(root) == "haiku")
        pf.write_text("schema_version: 5\n", encoding="utf-8")
        check("knob: absent key -> default haiku", read_pin(root) == "haiku")
        pf.write_text("schema_version: 5\nhandoff_tax:\n  pin_explore: sonnet\n", encoding="utf-8")
        check("knob: pin_explore sonnet", read_pin(root) == "sonnet")
        pf.write_text("schema_version: 5\nhandoff_tax:\n  pin_explore: off\n", encoding="utf-8")
        check("knob: pin_explore off -> None", read_pin(root) is None)
        pf.write_text("schema_version: 5\nhandoff_tax:\n  pin_explore: opus\n", encoding="utf-8")
        check(
            "knob: unrecognised value (opus) -> None, never a guessed rewrite",
            read_pin(root) is None,
        )
        pf.write_text("schema_version: 5\nhandoff_tax: off\n", encoding="utf-8")
        check("knob: handoff_tax: off -> None", read_pin(root) is None)
        pf.write_text(
            "schema_version: 5\nhandoff_tax:\n  report_cap_words: 300\n", encoding="utf-8"
        )
        check("knob: block without pin_explore -> default haiku", read_pin(root) == "haiku")

    print(f"explore-tier-pin self-test: {'PASS' if fails == 0 else 'FAIL'} ({fails} failure(s))")
    return 0 if fails == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--project-root", default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            return 0
        start = Path(
            args.project_root
            or os.environ.get("CLAUDE_PROJECT_DIR")
            or payload.get("cwd")
            or os.getcwd()
        )
        root = find_project_root(start)
        envelope = decide(payload, read_pin(root), dict(os.environ))
        if envelope is not None:
            sys.stdout.write(json.dumps(envelope, separators=(",", ":")) + "\n")
    except Exception:  # noqa: BLE001 — a rewrite that cannot be computed is not applied
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
