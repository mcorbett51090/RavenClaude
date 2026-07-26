#!/usr/bin/env python3
"""Gate 139 — orchestrator absent-vs-`full` doc consistency.

The `orchestrator:` comfort-posture knob defaults to `full` when the key is
ABSENT (only an explicit `off` disables relay eligibility). That default is
stated in three separate places, and they drifted once: `copilot/AGENTS.md`'s
relay-mode condition 3 required the LITERAL key set to `decide`/`full`, so an
absent key silently failed the relay-eligibility check even though `CLAUDE.md`
documents the default as `full`. This gate keeps the three sources honest.

It asserts all three agree that an absent key defaults to `full`:

  (a) CLAUDE.md (root OR plugins/ravenclaude-core/) § "Claude orchestrator knob"
      states a `full` default.
  (b) plugins/ravenclaude-core/skills/spawn-team/SKILL.md says "Absent = `full`".
  (c) scripts/generate-copilot-plugin.py's relay condition 3 template carries an
      "or absent" / absent-defaults qualifier (so the GENERATED copilot/AGENTS.md
      does not re-drift into the literal-key-only requirement).

Fails if ANY source is silent on the absent-key case.

Usage:
  check-orchestrator-doc-consistency.py              # run the gate (exit 0 = consistent)
  check-orchestrator-doc-consistency.py --self-test  # prove teeth: each absent-key
                                                     # clause, when stripped, is caught
  (--must-fail is an alias for --self-test.)
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD_ROOT = REPO_ROOT / "CLAUDE.md"
CLAUDE_MD_PLUGIN = REPO_ROOT / "plugins" / "ravenclaude-core" / "CLAUDE.md"
SPAWN_TEAM = REPO_ROOT / "plugins" / "ravenclaude-core" / "skills" / "spawn-team" / "SKILL.md"
GENERATOR = REPO_ROOT / "scripts" / "generate-copilot-plugin.py"

# "## Claude orchestrator knob ..." section, up to the next heading (or EOF).
_KNOB_SECTION_RE = re.compile(r"(?ims)^#{1,6}[^\n]*orchestrator knob[^\n]*\n(.*?)(?=^#{1,6}\s|\Z)")
# A "`full` default" statement in either direction ("Default: `full`" / "full ... default").
_FULL_DEFAULT_RE = re.compile(r"default[^\n]{0,20}`?full`?", re.IGNORECASE)
_FULL_DEFAULT_REV_RE = re.compile(r"`?full`?[^\n]{0,20}default", re.IGNORECASE)
# spawn-team's "Absent = `full`" (formatting-tolerant).
_ABSENT_FULL_RE = re.compile(r"absent[^\n]{0,15}\bfull\b", re.IGNORECASE)
# The generator's relay condition-3 list item (may span multiple physical lines).
_COND3_RE = re.compile(r"3\.\s*`orchestrator:`.*?(?=\n\n)", re.DOTALL)


def _knob_states_full_default(text):
    """True if any "orchestrator knob" section in `text` states a `full` default."""
    for match in _KNOB_SECTION_RE.finditer(text):
        section = match.group(1)
        if _FULL_DEFAULT_RE.search(section) or _FULL_DEFAULT_REV_RE.search(section):
            return True
    return False


def check_claude_md(root_text, plugin_text):
    """(a) root OR plugin CLAUDE.md § orchestrator knob states a `full` default."""
    return _knob_states_full_default(root_text) or _knob_states_full_default(plugin_text)


def check_spawn_team(text):
    """(b) spawn-team/SKILL.md says the absent knob defaults to `full`."""
    return bool(_ABSENT_FULL_RE.search(text))


def _cond3_text(generator_text):
    match = _COND3_RE.search(generator_text)
    return match.group(0) if match else ""


def check_generator(text):
    """(c) generate-copilot-plugin.py's relay condition 3 carries an absent qualifier."""
    return "absent" in _cond3_text(text).lower()


def _read(path):
    return path.read_text(encoding="utf-8")


def run_gate():
    root_text = _read(CLAUDE_MD_ROOT)
    plugin_text = _read(CLAUDE_MD_PLUGIN)
    skill_text = _read(SPAWN_TEAM)
    generator_text = _read(GENERATOR)

    checks = [
        ("(a) CLAUDE.md (root OR plugin) states a `full` default", check_claude_md(root_text, plugin_text)),
        ("(b) spawn-team/SKILL.md says absent = `full`", check_spawn_team(skill_text)),
        ("(c) generate-copilot-plugin.py cond-3 carries the 'or absent' qualifier", check_generator(generator_text)),
    ]

    all_ok = True
    for label, passed in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {label}")
        all_ok = all_ok and passed

    if all_ok:
        print("Gate 139 PASS — three sources agree that an absent `orchestrator:` key defaults to `full`.")
        return 0
    print(
        "Gate 139 FAIL — a source is silent on the absent-key case; absent must default to `full`.",
        file=sys.stderr,
    )
    return 1


def self_test():
    """Prove the gate has teeth: strip each source's absent-key clause and confirm
    the corresponding check flips to FAIL. The headline case (plan §8) is (c) —
    reintroducing the literal-key-only condition 3 must be caught."""
    root_text = _read(CLAUDE_MD_ROOT)
    plugin_text = _read(CLAUDE_MD_PLUGIN)
    skill_text = _read(SPAWN_TEAM)
    generator_text = _read(GENERATOR)

    # Sanity: the real tree must pass every check before teeth mean anything.
    for label, passed in (
        ("(a) CLAUDE.md", check_claude_md(root_text, plugin_text)),
        ("(b) spawn-team", check_spawn_team(skill_text)),
        ("(c) generator", check_generator(generator_text)),
    ):
        if not passed:
            print(f"self-test SETUP FAIL: {label} does not pass on the real tree", file=sys.stderr)
            return 1

    # Teeth (c): revert condition 3 to the pre-fix literal-key form (no "absent").
    generator_stripped = _COND3_RE.sub(
        "3. `orchestrator:` is `decide` or `full` (not `off`).", generator_text
    )
    if check_generator(generator_stripped):
        print("TEETH FAIL (c): stripped 'or absent' clause was NOT caught", file=sys.stderr)
        return 1

    # Teeth (a): remove the `full` default statement from the plugin milestone.
    plugin_stripped = plugin_text.replace(
        "**Default: `full`**", "The default is resolved at runtime"
    )
    if check_claude_md(root_text, plugin_stripped):
        print("TEETH FAIL (a): stripped `full` default was NOT caught", file=sys.stderr)
        return 1

    # Teeth (b): remove the "Absent = `full`" statement from spawn-team.
    skill_stripped = skill_text.replace("Absent = `full`", "The knob is required")
    if check_spawn_team(skill_stripped):
        print("TEETH FAIL (b): stripped 'Absent = full' was NOT caught", file=sys.stderr)
        return 1

    print(
        "Gate 139 self-test PASS — all three checks pass on the real tree AND each is "
        "caught when its absent-key clause is stripped (teeth verified)."
    )
    return 0


def main():
    parser = argparse.ArgumentParser(description="Gate 139 — orchestrator absent-vs-full doc consistency.")
    parser.add_argument(
        "--self-test",
        "--must-fail",
        dest="self_test",
        action="store_true",
        help="prove teeth: strip each absent-key clause and confirm the gate catches it",
    )
    args = parser.parse_args()
    return self_test() if args.self_test else run_gate()


if __name__ == "__main__":
    sys.exit(main())
