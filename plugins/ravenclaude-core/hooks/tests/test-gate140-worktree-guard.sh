#!/usr/bin/env bash
# test-gate140-worktree-guard.sh — Gate 140 audit fixture for the worktree-hygiene
# guard (hooks/worktree-guard.sh), per the FORGE plan §6.
#
# Drives the REAL script to prove its BLOCK-mode teeth are bidirectional:
#   MUST-FAIL  (the guard DENIES a mutating op → exit 2):
#     F1  block + a live sibling session (contention, latecomer) + a mutating op
#     F2  block + anchor checkout (worktrees present, HEAD on the anchor branch)
#         + a mutating op
#   MUST-PASS  (the guard ALLOWS → exit 0):
#     P1  a lone checkout (no contention, not anchor) + a mutating op  [solo silence]
#     P2  block + contention + a READ op (git status — never a mutation)
#     P3  block + contention + a mutating op + RC_WORKTREE_GUARD_ACK=1  [escape hatch]
#   MF  teeth half — neuter the mutating-op classifier and assert F1's deny
#       disappears, proving the exit-2 is produced by the mutating detector and
#       is not a vacuous pass.
#
# Self-contained: every fixture is a throwaway `git init` under mktemp and the
# registry is redirected to a scratch RC_WORKTREE_GUARD_HOME, so the real
# $HOME/.ravenclaude registry is NEVER touched (follows the test-gate*.sh +
# test-worktree-guard-core.sh convention).
#
# Run directly:  bash plugins/ravenclaude-core/hooks/tests/test-gate140-worktree-guard.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$(cd "$SCRIPT_DIR/.." && pwd)/worktree-guard.sh"

# The payload's `.session_id` is how each simulated session is told apart; an
# ambient CLAUDE_SESSION_ID would override it (every session collides → no
# contention). CLAUDE_PROJECT_DIR is cleared so a deny's audit emit no-ops
# instead of writing a stray hook-events.jsonl into the real project.
unset CLAUDE_SESSION_ID 2>/dev/null || true
unset CLAUDE_PROJECT_DIR 2>/dev/null || true

PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

if ! command -v jq >/dev/null 2>&1; then
  echo "SKIP: jq not available — the block-mode fixtures need it to build payloads and let the guard classify the op"
  exit 0
fi
if ! command -v git >/dev/null 2>&1; then
  echo "SKIP: git not available — the worktree-guard fixtures need a git working tree"
  exit 0
fi

# ── fixture helpers (mirrors test-worktree-guard-core.sh) ─────────────────────

# mk_repo <dir> [posture-mode] — a git repo on `main` with one commit + a posture.
mk_repo() {
  local d="$1" mode="${2:-}"
  git init -q "$d"
  git -C "$d" config user.email t@example.com
  git -C "$d" config user.name test
  git -C "$d" commit --allow-empty -q -m init
  git -C "$d" branch -M main
  mkdir -p "$d/.ravenclaude"
  [ -n "$mode" ] && printf 'worktree_guard: %s\n' "$mode" > "$d/.ravenclaude/comfort-posture.yaml"
}

# path_key <dir> — the sha256(realpath) registry key the hook computes.
path_key() {
  local rt; rt="$(cd "$1" 2>/dev/null && pwd -P)"
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$rt" | sha256sum | cut -d' ' -f1
  else
    printf '%s' "$rt" | shasum -a 256 | cut -d' ' -f1
  fi
}

# seed_record <bucket-dir> <sid> <pid> <started_at> — write a registry record.
seed_record() {
  mkdir -p "$1"
  printf '{"session_id":"%s","pid":%s,"ppid":0,"host":"h","branch":"main","started_at":%s}\n' \
    "$2" "$3" "$4" > "$1/$2.json"
}

# mk_payload <cwd> <sid> <tool_name> <tool_input-json>
mk_payload() {
  jq -cn --arg cwd "$1" --arg sid "$2" --arg tn "$3" --argjson ti "$4" \
    '{cwd:$cwd, session_id:$sid, tool_name:$tn, tool_input:$ti}'
}

# run_check <repo> <sid> <tool> <input-json> [ack] — echo the guard's exit code.
run_check() {
  local repo="$1" sid="$2" tool="$3" tin="$4" ack="${5:-}" _rc
  if [ "$ack" = "ack" ]; then
    mk_payload "$repo" "$sid" "$tool" "$tin" | RC_WORKTREE_GUARD_ACK=1 bash "$HOOK" check >/dev/null 2>&1
    _rc=$?
  else
    mk_payload "$repo" "$sid" "$tool" "$tin" | bash "$HOOK" check >/dev/null 2>&1
    _rc=$?
  fi
  printf '%s' "$_rc"
}

MUT='{"command":"git commit -m x"}'   # a mutating op the guard denies in block mode
READ='{"command":"git status"}'       # a read the guard never denies

echo
echo "── F1: MUST-FAIL — block + contention (latecomer) + mutating -> exit 2 ────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" block
BUCKET="$SB/guard/sessions/$(path_key "$R")"
sleep 300 & INC=$!; disown 2>/dev/null || true
seed_record "$BUCKET" incumbent "$INC" "$(( $(date +%s) - 100 ))"
RC="$(run_check "$R" latecomer Bash "$MUT")"
kill "$INC" 2>/dev/null || true
if [ "$RC" = "2" ]; then
  pass "F1: block + a live incumbent + a mutating op -> exit 2 DENY"
else
  fail "F1: expected exit 2 DENY, got '$RC'"
fi
rm -rf "$SB"

echo
echo "── F2: MUST-FAIL — block + anchor checkout + mutating -> exit 2 ───────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" block
git -C "$R" worktree add -q -b sib "$SB/sibling"   # worktrees present + HEAD on main -> anchor
RC="$(run_check "$R" solo Bash "$MUT")"
if [ "$RC" = "2" ]; then
  pass "F2: block + anchor (worktrees present, on the anchor branch) + a mutating op -> exit 2 DENY"
else
  fail "F2: expected exit 2 DENY, got '$RC'"
fi
rm -rf "$SB"

echo
echo "── P1: MUST-PASS — lone checkout + mutating -> exit 0 (solo silence) ──────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" block
RC="$(run_check "$R" solo Bash "$MUT")"
if [ "$RC" = "0" ]; then
  pass "P1: a lone checkout (no contention, not anchor) + a mutating op -> exit 0 allow"
else
  fail "P1: expected exit 0 allow, got '$RC'"
fi
rm -rf "$SB"

echo
echo "── P2: MUST-PASS — block + contention + a READ op -> exit 0 ──────────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" block
BUCKET="$SB/guard/sessions/$(path_key "$R")"
sleep 300 & INC=$!; disown 2>/dev/null || true
seed_record "$BUCKET" incumbent "$INC" "$(( $(date +%s) - 100 ))"
RC="$(run_check "$R" latecomer Bash "$READ")"
kill "$INC" 2>/dev/null || true
if [ "$RC" = "0" ]; then
  pass "P2: block + contention + a READ op (git status) -> exit 0 allow (never denies a read)"
else
  fail "P2: expected exit 0 allow, got '$RC'"
fi
rm -rf "$SB"

echo
echo "── P3: MUST-PASS — block + contention + mutating + ACK=1 -> exit 0 ────────"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" block
BUCKET="$SB/guard/sessions/$(path_key "$R")"
sleep 300 & INC=$!; disown 2>/dev/null || true
seed_record "$BUCKET" incumbent "$INC" "$(( $(date +%s) - 100 ))"
RC="$(run_check "$R" latecomer Bash "$MUT" ack)"
kill "$INC" 2>/dev/null || true
if [ "$RC" = "0" ]; then
  pass "P3: block + contention + a mutating op + RC_WORKTREE_GUARD_ACK=1 -> exit 0 (escape hatch)"
else
  fail "P3: expected exit 0 allow, got '$RC'"
fi
rm -rf "$SB"

echo
echo "── MF: teeth — neuter the mutating classifier, F1's deny must disappear ───"
# Neutralize the check subcommand's mutating branch so nothing is classified as a
# mutation; F1's exact scenario must then NO LONGER deny (exit 0), proving the
# exit-2 in F1 is produced by the mutating detector and is not a vacuous pass.
PATCH_TMP="$(mktemp -d)"; PATCH_HOOK="$PATCH_TMP/worktree-guard-nomut.sh"
python3 - "$HOOK" "$PATCH_HOOK" <<'PY'
import sys
src = open(sys.argv[1]).read()
needle = "if _wg_is_mutating; then"
repl = "if false; then  # MF: mutating classification neutered"
assert needle in src, "MF anchor drift: the '_wg_is_mutating' call site was not found"
open(sys.argv[2], "w").write(src.replace(needle, repl, 1))
PY
chmod +x "$PATCH_HOOK"
SB="$(mktemp -d)"; export RC_WORKTREE_GUARD_HOME="$SB/guard"
R="$SB/repo"; mk_repo "$R" block
BUCKET="$SB/guard/sessions/$(path_key "$R")"
sleep 300 & INC=$!; disown 2>/dev/null || true
seed_record "$BUCKET" incumbent "$INC" "$(( $(date +%s) - 100 ))"
mk_payload "$R" latecomer Bash "$MUT" | bash "$PATCH_HOOK" check >/dev/null 2>&1
RC=$?
kill "$INC" 2>/dev/null || true
rm -rf "$SB" "$PATCH_TMP"
if [ "$RC" = "0" ]; then
  pass "MF: with the mutating classifier neutered, F1's deny disappears (exit 0) — the exit-2 has teeth"
else
  fail "MF: the neutered hook still returned '$RC' (expected 0) — the must-fail patch missed its target"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "Gate 140 (worktree-guard block-mode teeth): ALL ASSERTIONS PASS"
  exit 0
else
  echo "Gate 140 (worktree-guard block-mode teeth): $FAIL assertion(s) FAILED"
  exit 1
fi
