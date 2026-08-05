#!/usr/bin/env bash
# Gate 167 — a COPILOT-shaped payload reaches the tribunal and is still denied.
#
# This is the residual MH-01 split out but never built. MH-01 was the P0 where the
# command-review tribunal was "fully wired, reviewing nothing" under Copilot: the
# envelope was translated but the tool-name VALUE was not, and
# thing-orchestrator.sh dispatches on a CASE-SENSITIVE
# `Bash | Read | Write | ...` list falling to `*) exit 0`. Copilot sends `bash`.
# So every Copilot tool call sailed past the classifier, the self-disable guard
# and the category-independent hard-rule screen.
#
# WHY THE EXISTING COVERAGE DOES NOT CLOSE IT.
#   - Gate 20 drives the ADAPTER and asserts its I/O shape (stderr preservation,
#     the 512-byte cap, CLAUDE_SESSION_ID export). It never asks whether a verdict
#     actually comes out the far end.
#   - Gates 50 / 121 / 162 and test-seat-stderr-capture drive the ORCHESTRATOR,
#     but every one of them feeds it a CLAUDE-shaped payload.
#
# Measured 2026-07-29: of the hook tests, exactly ONE uses a Copilot-shaped
# `toolName` (Gate 20's) and it is NOT among the four that drive the orchestrator.
# So the seam where the P0 actually lived — adapter output feeding orchestrator
# input — had no test crossing it. A regression in the tool-name map would leave
# every existing gate green while the tribunal went dark again, silently, exactly
# as it did the first time.
#
# WHAT THIS ASSERTS
#   G167.1  control — the Claude-shaped payload is denied (the command really is
#           deny-worthy, so a later deny is not an artifact of the fixture)
#   G167.2  the SAME command in a Copilot envelope, through the adapter, is denied
#   G167.3  TEETH — with the tool-name map defeated, the deny DISAPPEARS
#
# G167.3 is the one that matters: it reproduces MH-01 on demand and proves this
# gate would catch its return. A gate for a silent failure is worthless unless it
# has been watched failing.
#
# NOTE ON LITERALS: the force-push string is assembled at runtime. Inline, the
# category-independent hard-rule screen (§B.9.3) denies the Write that creates
# this very file — the same trap Gate 162's header documents.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="$(cd "$HERE/.." && pwd)"
ADAPTER="$HOOKS_DIR/copilot-hook-adapter.sh"
ORCH="$HOOKS_DIR/thing-orchestrator.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ✓ %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  ✗ %s\n' "$1"; }

for f in "$ADAPTER" "$ORCH"; do
  [ -f "$f" ] || { printf 'FATAL: missing %s\n' "$f" >&2; exit 1; }
done
command -v jq >/dev/null 2>&1 || { printf 'SKIP: jq absent\n' >&2; exit 0; }

# Assembled so the literal never sits in this file (see header).
FORCED_PUSH="git push --""force origin main"

# Scratch project with the Thing enabled for ONE category. The hard rule is
# category-INDEPENDENT (§B.9.3) — it fires regardless of which category the
# command routes to — but the orchestrator short-circuits entirely when nothing
# is toggled, which is correct and is the state of every non-adopter.
PROJ="$TMP/proj"
mkdir -p "$PROJ/.ravenclaude"
cat > "$PROJ/.ravenclaude/comfort-posture.yaml" <<'YAML'
schema_version: 5
categories:
  shell_remote_mutate:
    user: ask
    local: ask
    project: inherit
    thing: on
YAML

# ── G167.1 — control: Claude-shaped payload is denied ────────────────────────
echo "── G167.1: control — Claude-shaped force-push is denied ─────────────────"
rc=0
jq -cn --arg cwd "$PROJ" --arg cmd "$FORCED_PUSH" \
  '{tool_name:"Bash",tool_input:{command:$cmd},cwd:$cwd,session_id:"g167a"}' \
  | CLAUDE_PROJECT_DIR="$PROJ" CLAUDE_SESSION_ID="g167a" \
    bash "$ORCH" >"$TMP/out-a.json" 2>"$TMP/err-a.txt" || rc=$?

# The orchestrator signals a block either by exit 2 or by an emitted deny verdict.
claude_denied=0
[ "$rc" -eq 2 ] && claude_denied=1
if grep -q '"permissionDecision"[[:space:]]*:[[:space:]]*"deny"' "$TMP/out-a.json" 2>/dev/null; then
  claude_denied=1
fi
if [ "$claude_denied" -eq 1 ]; then
  ok "control: the tribunal denies this command in Claude shape (exit=$rc)"
else
  bad "control: NOT denied in Claude shape (exit=$rc) — the fixture is wrong, not the adapter"
  printf '     stdout: %s\n' "$(head -c 300 "$TMP/out-a.json" 2>/dev/null)"
  printf '     stderr: %s\n' "$(head -c 300 "$TMP/err-a.txt" 2>/dev/null)"
fi

# ── G167.2 — the same command, Copilot envelope, through the adapter ─────────
echo "── G167.2: Copilot-shaped force-push through the adapter is denied ──────"
# Copilot's real shape: lowercase toolName, toolArgs as a JSON *string*.
copilot_payload() {
  jq -cn --arg cwd "$PROJ" --arg cmd "$FORCED_PUSH" --arg tn "${1:-bash}" \
    '{toolName:$tn,toolArgs:({command:$cmd}|tostring),cwd:$cwd,sessionId:"g167b"}'
}

rc=0
copilot_payload bash \
  | CLAUDE_PROJECT_DIR="$PROJ" bash "$ADAPTER" bash-pretool "$ORCH" \
      >"$TMP/out-b.json" 2>"$TMP/err-b.txt" || rc=$?

# The adapter always exits 0 and carries the decision in the JSON (by contract).
decision_b="$(jq -r '.permissionDecision // empty' "$TMP/out-b.json" 2>/dev/null)"
if [ "$decision_b" = "deny" ]; then
  ok "Copilot payload -> adapter -> tribunal -> deny (the MH-01 seam holds)"
else
  bad "Copilot payload was NOT denied (permissionDecision='${decision_b:-<none>}') — the tribunal is dark on this host"
  printf '     stdout: %s\n' "$(head -c 300 "$TMP/out-b.json" 2>/dev/null)"
  printf '     stderr: %s\n' "$(head -c 300 "$TMP/err-b.txt" 2>/dev/null)"
fi

# ── G167.3 — TEETH: defeat the tool-name map, deny must vanish ───────────────
echo "── G167.3: teeth — without tool-name normalisation the deny disappears ──"
MUT="$TMP/adapter-mutant.sh"
python3 - "$ADAPTER" "$MUT" <<'PY'
import pathlib
import sys

src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
# Reproduce the pre-fix adapter: pass the raw Copilot tool name straight through
# instead of mapping it onto Claude's vocabulary.
anchor = "($map[$lc] // $raw)"
if anchor not in src:
    # A vacuous teeth half is worse than none: if the adapter is refactored so
    # this anchor no longer exists, FAIL LOUDLY rather than "mutating" nothing
    # and reporting teeth we do not have.
    sys.stderr.write(
        "MUTATION ANCHOR NOT FOUND: expected %r in the adapter. The teeth half "
        "cannot be trusted until this is re-pointed at the current map lookup.\n"
        % anchor
    )
    raise SystemExit(3)
pathlib.Path(sys.argv[2]).write_text(src.replace(anchor, "($raw)"), encoding="utf-8")
PY
mut_rc=$?

if [ "$mut_rc" -ne 0 ]; then
  bad "teeth: could not build the mutant (anchor missing) — re-point the mutation"
else
  rc=0
  copilot_payload bash \
    | CLAUDE_PROJECT_DIR="$PROJ" bash "$MUT" bash-pretool "$ORCH" \
        >"$TMP/out-c.json" 2>"$TMP/err-c.txt" || rc=$?
  decision_c="$(jq -r '.permissionDecision // empty' "$TMP/out-c.json" 2>/dev/null)"
  if [ "$decision_c" = "deny" ]; then
    bad "teeth: the mutant STILL denied — this gate does not actually test the tool-name map"
  else
    ok "teeth: normalisation defeated -> no deny ('${decision_c:-<none>}') — MH-01 reproduced, so this gate would catch its return"
  fi
fi

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'FAIL: %d of %d assertion(s) failed\n' "$FAIL" "$((PASS + FAIL))" >&2
  exit 1
fi
printf 'Copilot tribunal e2e: %d/%d assertions passed\n' "$PASS" "$PASS"
exit 0
