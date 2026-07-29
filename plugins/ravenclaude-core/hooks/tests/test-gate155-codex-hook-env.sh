#!/usr/bin/env bash
# Gate 155 — the Codex env shim (hooks/codex-hook-env.sh) keeps its four invariants.
#
# WHY THIS GATE EXISTS, and why each half has real teeth:
#
# The shim sits in front of EVERY RavenClaude guardrail under Codex. If it drops a
# stdin byte, swallows an exit code, or dies on a malformed payload, it does not
# fail loudly — it silently disarms the enforcement layer for that host, which is
# precisely the failure class the multi-host audit exists to close (MH-05/MH-07).
# So each invariant is asserted directly, and the exit-code one carries a must-fail
# half, because "exit 2 propagates" is the single assertion whose regression would
# turn every block into a silent allow.
#
# Driven through the REAL shim against recording stubs — never a reimplementation.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHIM="$HERE/../codex-hook-env.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); printf '  ✓ %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  ✗ %s\n' "$1"; }
check(){ if [ "$2" = "$3" ]; then ok "$1"; else bad "$1 (want [$3], got [$2])"; fi; }

if [ ! -f "$SHIM" ]; then
  printf 'FATAL: shim not found at %s\n' "$SHIM" >&2
  exit 1
fi

# A recording stub standing in for a real hook: dumps its stdin and the two
# variables the shim is supposed to fill, then exits with a code we control.
cat >"$TMP/stub.sh" <<'STUB'
#!/usr/bin/env bash
{ cat; } >"$RC_TEST_OUT/stdin.txt"
{
  printf 'PROJECT_DIR=%s\n' "${CLAUDE_PROJECT_DIR:-}"
  printf 'SESSION_ID=%s\n'  "${CLAUDE_SESSION_ID:-}"
  printf 'THING_HOST=%s\n'  "${THING_HOST:-}"
} >"$RC_TEST_OUT/env.txt"
exit "${RC_TEST_EXIT:-0}"
STUB
chmod +x "$TMP/stub.sh"

export RC_TEST_OUT="$TMP"
PAYLOAD='{"session_id":"sess-abc123","cwd":"/tmp/proj","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"echo hi"}}'

printf '── Gate 155: Codex env shim invariants ──\n'

# ---------------------------------------------------------------- invariant 1
# stdin passes through BYTE-IDENTICAL. A hook re-parsing the payload must see
# exactly what Codex sent — the shim adds no field and drops none.
env -u CLAUDE_PROJECT_DIR -u CLAUDE_SESSION_ID -u THING_HOST \
  RC_TEST_OUT="$TMP" bash "$SHIM" "$TMP/stub.sh" <<<"$PAYLOAD" >/dev/null 2>&1
got="$(cat "$TMP/stdin.txt" 2>/dev/null || echo MISSING)"
check "invariant 1: stdin passed through byte-identical" "$got" "$PAYLOAD"

# ---------------------------------------------------------------- invariant 2a
# Fills the two genuinely-absent vars FROM STDIN — the documented-reliable source.
# (_portable.sh's CODEX_PROJECT_ROOT/SESSION_ID fallbacks are speculative names
# that are NOT in Codex's documented environment, which is why this exists.)
grep -q '^PROJECT_DIR=/tmp/proj$'      "$TMP/env.txt" && ok "invariant 2a: CLAUDE_PROJECT_DIR lifted from payload .cwd" \
  || bad "invariant 2a: CLAUDE_PROJECT_DIR not lifted ($(grep '^PROJECT_DIR=' "$TMP/env.txt" || true))"
grep -q '^SESSION_ID=sess-abc123$'     "$TMP/env.txt" && ok "invariant 2a: CLAUDE_SESSION_ID lifted from payload .session_id" \
  || bad "invariant 2a: CLAUDE_SESSION_ID not lifted"
grep -q '^THING_HOST=codex$'           "$TMP/env.txt" && ok "invariant 2a: THING_HOST asserted as codex" \
  || bad "invariant 2a: THING_HOST not set to codex"

# ---------------------------------------------------------------- invariant 2b
# BLANKS ONLY. A value the host already set must survive untouched — Claude Code
# is authoritative about its own vocabulary, and clobbering it would corrupt a
# correctly-configured session.
CLAUDE_PROJECT_DIR=/real/host/dir CLAUDE_SESSION_ID=host-sid THING_HOST=claude-code \
  RC_TEST_OUT="$TMP" bash "$SHIM" "$TMP/stub.sh" <<<"$PAYLOAD" >/dev/null 2>&1
grep -q '^PROJECT_DIR=/real/host/dir$' "$TMP/env.txt" && ok "invariant 2b: preset CLAUDE_PROJECT_DIR NOT overwritten" \
  || bad "invariant 2b: preset CLAUDE_PROJECT_DIR was clobbered"
grep -q '^SESSION_ID=host-sid$'        "$TMP/env.txt" && ok "invariant 2b: preset CLAUDE_SESSION_ID NOT overwritten" \
  || bad "invariant 2b: preset CLAUDE_SESSION_ID was clobbered"
grep -q '^THING_HOST=claude-code$'     "$TMP/env.txt" && ok "invariant 2b: preset THING_HOST NOT overwritten" \
  || bad "invariant 2b: preset THING_HOST was clobbered"

# ---------------------------------------------------------------- invariant 3
# EXIT CODE propagates verbatim. exit 2 is how every guardrail here blocks;
# swallowing it converts every deny into a silent allow.
env -u CLAUDE_PROJECT_DIR RC_TEST_OUT="$TMP" RC_TEST_EXIT=2 \
  bash "$SHIM" "$TMP/stub.sh" <<<"$PAYLOAD" >/dev/null 2>&1
check "invariant 3: exit 2 (block) propagates" "$?" "2"

env -u CLAUDE_PROJECT_DIR RC_TEST_OUT="$TMP" RC_TEST_EXIT=0 \
  bash "$SHIM" "$TMP/stub.sh" <<<"$PAYLOAD" >/dev/null 2>&1
check "invariant 3: exit 0 (allow) propagates" "$?" "0"

# ---------------------------------------------------------------- invariant 4
# NEVER fails the hook. A malformed payload, or an empty one, must still run the
# hook — a telemetry convenience must not become a new way for a guardrail to die.
env -u CLAUDE_PROJECT_DIR RC_TEST_OUT="$TMP" \
  bash "$SHIM" "$TMP/stub.sh" <<<'not json at all {{{' >/dev/null 2>&1
check "invariant 4: malformed payload still runs the hook" "$?" "0"
got="$(cat "$TMP/stdin.txt" 2>/dev/null || echo MISSING)"
check "invariant 4: malformed payload still passed through verbatim" "$got" "not json at all {{{"

printf '' | env -u CLAUDE_PROJECT_DIR RC_TEST_OUT="$TMP" \
  bash "$SHIM" "$TMP/stub.sh" >/dev/null 2>&1
check "invariant 4: empty stdin still runs the hook" "$?" "0"

# ---------------------------------------------------------------- must-fail half
# TEETH: mutate the shim so it swallows the hook's exit code, and prove the
# invariant-3 assertion above would have caught it. Without this, "exit 2
# propagates" is an assertion nobody has ever seen fail.
sed 's/^exit \$?$/exit 0/' "$SHIM" >"$TMP/mutant.sh"
if ! grep -q '^exit 0$' "$TMP/mutant.sh"; then
  bad "teeth: could not build the exit-swallowing mutant (shim tail changed?)"
else
  env -u CLAUDE_PROJECT_DIR RC_TEST_OUT="$TMP" RC_TEST_EXIT=2 \
    bash "$TMP/mutant.sh" "$TMP/stub.sh" <<<"$PAYLOAD" >/dev/null 2>&1
  mrc=$?
  if [ "$mrc" -eq 0 ]; then
    ok "teeth: exit-swallowing mutant returns 0 — invariant 3 has real teeth"
  else
    bad "teeth: mutant still returned $mrc — invariant 3 may be vacuous"
  fi
fi

# TEETH 2: a mutant that drops the blanks-only guard must clobber a preset value.
sed 's/^if \[ -z "${CLAUDE_PROJECT_DIR:-}" \]; then$/if true; then/' "$SHIM" >"$TMP/mutant2.sh"
CLAUDE_PROJECT_DIR=/real/host/dir RC_TEST_OUT="$TMP" \
  bash "$TMP/mutant2.sh" "$TMP/stub.sh" <<<"$PAYLOAD" >/dev/null 2>&1
if grep -q '^PROJECT_DIR=/tmp/proj$' "$TMP/env.txt"; then
  ok "teeth: blanks-only mutant DOES clobber — invariant 2b has real teeth"
else
  bad "teeth: blanks-only mutant did not clobber — invariant 2b may be vacuous"
fi

printf '\n  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
