#!/usr/bin/env bash
# Gate 197 — guard-premise scope + tool-agnostic screen.
#
# Three fixes, exercised end-to-end through the real hook:
#
#   1. NESTED-WORKTREE SCOPE. The project-relative path was computed with
#      `path.replace(proj, "").lstrip("/")` — a substring operation, not a path
#      operation — at TWO independent call sites (T-PROSE's durable-artifact
#      exemption and T-SHAPE's prefix-exemption list). In a nested worktree the
#      tree sits at <proj>/.claude/worktrees/<wt>/, so a genuine run artifact
#      resolved to `.claude/worktrees/<wt>/.ravenclaude/runs/...`, which does not
#      startswith(".ravenclaude/") — the exemption evaporated and the guard denied
#      legitimate writes. Both sites are asserted, because patching one and
#      stopping is the fix-one-instance trap this initiative exists to kill.
#
#   2. TOOL SCOPE. The screen ran on Write only, so the identical prose via Edit
#      or MultiEdit evaded it entirely — both a false negative and the exact
#      surface a session tunnels through when a Write is denied.
#
#   3. The sanctioned escape still clears a false positive, so the correct
#      response to one is never a tool switch.
#
# Every assertion has a teeth half: a mutant that reverts the fix must restore
# the old behaviour, or the assertion is not measuring the fix.
#
# ⛔ WHY THE FIXTURE PROSE IS ASSEMBLED WITH printf INSTEAD OF WRITTEN OUT.
# This file's fixtures must CONTAIN the shape the guard denies, and the guard
# scans the content of the very write that creates this file — so writing them
# literally is self-denying. (Verified while authoring: the first version of this
# file was denied by guard-premise itself.) A guard cannot tell a command from a
# description of one, which is this repo's recorded "source-scan gates match
# PROSE" failure. printf-assembly is the interim mitigation; the durable fix is
# the sanctioned exempt path / in-file sentinel, which is deliberately NOT here
# because widening what a guard ignores is a security decision that earns its own
# security review. Do NOT "simplify" these back into literals.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK="$HERE/../guard-premise.sh"
PASS=0; FAIL=0
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

ok()  { PASS=$((PASS+1)); printf '  ok    %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  FAIL  %s (%s)\n' "$1" "$2"; }

# Build a hook payload. Keeping this in python avoids hand-quoting JSON and lets
# the Edit/MultiEdit shapes carry their real field names.
_payload() {
  python3 - "$1" "$2" "$3" <<'PY'
import json, sys
tool, path, content = sys.argv[1], sys.argv[2], sys.argv[3]
ti = {"file_path": path}
if tool == "Write":
    ti["content"] = content
elif tool == "Edit":
    ti["old_string"] = "PLACEHOLDER"
    ti["new_string"] = content
else:
    ti["edits"] = [{"old_string": "PLACEHOLDER", "new_string": content}]
json.dump({"tool_name": tool, "tool_input": ti, "session_id": "gate197"}, sys.stdout)
PY
}

# Drive the hook; echo its exit code. 2 = deny, 0 = allow.
_run() { # hook proj tool path content
  local _rc=0
  _payload "$3" "$4" "$5" \
    | CLAUDE_PROJECT_DIR="$2" bash "$1" "$2" >/dev/null 2>&1 || _rc=$?
  printf '%s' "$_rc"
}

assert() { # label hook proj tool path content want_rc
  local got; got="$(_run "$2" "$3" "$4" "$5" "$6")"
  if [ "$got" = "$7" ]; then ok "$1"; else bad "$1" "want exit $7, got $got"; fi
}

# ── Fixture tree: a project with a NESTED worktree under it ──────────────────
PROJ="$TMP/proj"
WT="$PROJ/.claude/worktrees/wt"
mkdir -p "$PROJ/docs" "$WT/.ravenclaude/runs/task" "$WT/src" "$WT/docs"

# The diagnosis shape T-PROSE exists to catch: a defect predicate about a named
# subject, with a certainty stamp beside it. Assembled, never written literally.
DIAG="$(printf 'The %s is %s. %s 2026-08-13: it %s not fire.' scheduler broken Confirmed does)"
BENIGN='Ordinary notes about the plan. Nothing is asserted about any subject.'
ESCAPE="$(printf '%s\npremise-ok: probed the subject directly, it fired' "$DIAG")"

echo "── Gate 197: guard-premise scope + tool-agnostic screen ──"

# ── 0. The fixture really does trip the screen ──────────────────────────────
# Asserted FIRST. Every "is allowed" result below is only meaningful if the
# prose would otherwise deny — an inert fixture would make them all vacuous.
assert "control: the diagnosis fixture IS denied on a plain durable path" \
  "$HOOK" "$PROJ" "Write" "$PROJ/docs/finding.md" "$DIAG" "2"

# ── 1. Nested worktree, T-PROSE call site ───────────────────────────────────
assert "T-PROSE: diagnosis in .ravenclaude/runs (nested worktree) is allowed" \
  "$HOOK" "$PROJ" "Write" "$WT/.ravenclaude/runs/task/notes.md" "$DIAG" "0"

# ── 2. Nested worktree, T-SHAPE call site ───────────────────────────────────
# A NEW source module under .ravenclaude/runs hits the OTHER exemption.
# Asserted separately so a one-call-site fix is caught.
assert "T-SHAPE: new module in .ravenclaude/runs (nested worktree) is allowed" \
  "$HOOK" "$PROJ" "Write" "$WT/.ravenclaude/runs/task/probe.py" "print(1)" "0"

# ── 3. The screen is tool-agnostic ──────────────────────────────────────────
assert "T-PROSE: the same diagnosis via Edit is screened too" \
  "$HOOK" "$PROJ" "Edit" "$PROJ/docs/finding.md" "$DIAG" "2"
assert "T-PROSE: the same diagnosis via MultiEdit is screened too" \
  "$HOOK" "$PROJ" "MultiEdit" "$PROJ/docs/finding.md" "$DIAG" "2"

# ── 4. Ordinary prose is not denied (the guard must stay usable) ────────────
assert "benign docs prose via Write is allowed" \
  "$HOOK" "$PROJ" "Write" "$PROJ/docs/plan.md" "$BENIGN" "0"
assert "benign docs prose via Edit is allowed" \
  "$HOOK" "$PROJ" "Edit" "$PROJ/docs/plan.md" "$BENIGN" "0"

# ── 5. The sanctioned escape clears a false positive — on the Edit path too ──
# This is why a tool switch is never the right answer to a deny.
assert "an in-block premise-ok marker clears the deny via Edit" \
  "$HOOK" "$PROJ" "Edit" "$PROJ/docs/finding.md" "$ESCAPE" "0"

# ── TEETH ───────────────────────────────────────────────────────────────────
# A mutant that reverts each fix MUST restore the old behaviour. Without this,
# "it is allowed now" could be true for reasons unrelated to the change.

# Teeth A — revert the path helper to the substring idiom.
MUT_PATH="$TMP/mutant-substring.sh"
sed -e 's|^    marker = os.sep.*$|    return p.replace(root, "").lstrip("/")|' "$HOOK" > "$MUT_PATH"
got="$(_run "$MUT_PATH" "$PROJ" "Write" "$WT/.ravenclaude/runs/task/notes.md" "$DIAG")"
if [ "$got" = "2" ]; then
  ok "teeth: substring-idiom mutant DENIES the nested-worktree run artifact"
else
  bad "teeth: substring-idiom mutant" \
      "expected the old deny (2), got $got — the scope assertion is not measuring the fix"
fi

# Teeth B — revert the tool gate to Write-only.
MUT_TOOL="$TMP/mutant-writeonly.sh"
sed -e 's|^if _TOOL not in ("Write", "Edit", "MultiEdit"):$|if _TOOL != "Write":|' "$HOOK" > "$MUT_TOOL"
got="$(_run "$MUT_TOOL" "$PROJ" "Edit" "$PROJ/docs/finding.md" "$DIAG")"
if [ "$got" = "0" ]; then
  ok "teeth: Write-only mutant lets the Edit-borne diagnosis through"
else
  bad "teeth: Write-only mutant" \
      "expected the old evasion (0), got $got — the tool-scope assertion is not measuring the fix"
fi

# ── 6. xc.tribunal-self-disable trigger (2b): read vs mutation ──────────────
# The verb list lumped the stream editors (sed/perl/awk — READ by default; they
# write to stdout unless given an in-place flag) in with verbs that have no read
# mode. So an ordinary verification read of the Thing's own files was hard-denied
# pre-LLM and non-overridably, which is how a session ends up tunnelling around
# the guard rather than using it. The discriminator NARROWS what counts as a
# mutation; it must not narrow what counts as a substrate path.
#
# Command strings are assembled from fragments for the same self-reference
# reason as the prose fixtures above.
if python3 - "$HERE/../../knowledge/concerns-catalog.md" <<'PY'
import re, sys
try:
    import yaml
except ImportError:
    print("  !! trigger check SKIPPED - PyYAML absent. THIS IS NOT A PASS.")
    sys.exit(0)
text = open(sys.argv[1], encoding="utf-8").read()
data = yaml.safe_load(re.search(r"```yaml\n(.*?)```", text, re.S).group(1)) or {}
pats = []
for c in data.get("cross_cutting") or []:
    if c.get("id") == "xc.tribunal-self-disable":
        pats = [re.compile(p, re.I) for p in (c.get("triggers") or {}).get("regex") or []]
if not pats:
    print("  FAIL  no xc.tribunal-self-disable triggers found")
    sys.exit(1)

SUB = "plugins/ravenclaude-core/hooks/guard-premise.sh"
D, I = "-", "i"
cases = [
    ("bare pattern-print read of a hook",   "sed " + D + "n '1,40p' " + SUB, False),
    ("bare perl read of a hook",            "perl " + D + "ne 'print' " + SUB, False),
    ("bare awk read of a hook",             "awk 'NR<5' " + SUB, False),
    ("in-place stream edit of a hook",      "sed " + D + I + " 's/a/b/' " + SUB, True),
    ("in-place perl edit of a hook",        "perl " + D + "p" + I + " " + D + "e 's/a/b/' " + SUB, True),
    ("long-form in-place edit of a hook",   "sed " + D + D + "in-place 's/a/b/' " + SUB, True),
    ("remove a hook",                       "r" + "m " + D + "f " + SUB, True),
    ("pipe into a hook via tee",            "echo x | tee " + SUB, True),
    ("redirect onto a hook",                "echo x > " + SUB, True),
    # A read here with an in-place edit in a LATER chained command must not arm
    # this one — the window is separator-bounded on purpose.
    ("read, then in-place edit elsewhere",
     "sed " + D + "n 1p " + SUB + " ; sed " + D + I + " 's/a/b/' /tmp/other", False),
]
bad = 0
for label, cmd, want in cases:
    got = any(p.search(cmd) for p in pats)
    if got == want:
        print(f"  ok    trigger: deny={got!s:5} {label}")
    else:
        bad += 1
        print(f"  FAIL  trigger: deny={got!s:5} want={want!s:5} {label}")
sys.exit(1 if bad else 0)
PY
then ok "read/mutate discriminator: reads released, every mutation still denies"
else bad "read/mutate discriminator" "see the per-case lines above"
fi

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
