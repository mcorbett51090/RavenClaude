#!/usr/bin/env bash
# test-seat-stderr-capture.sh — Gate 135 (FORGE dashboard-process-hardening, P0).
#
# Proves the ALREADY-COMMITTED P0 seat-error observability work in
# plugins/ravenclaude-core/hooks/thing-orchestrator.sh:
#   - the SERR fixed-slot array + the run_seat `2>"$tmp/$role.err"` capture,
#   - parse_seat's rc→class-label classification + the whitelisted stderr enrichment,
#   - the fail-closed `_on_exit` EXIT trap (_emitted / _tmp_to_clean),
#   - the additive `seat_error` field in the Sága seat-JSON emission.
#
# It drives the REAL orchestrator with mocked seats (THING_SEAT_MOCK_VERDICT) + a
# temp comfort-posture that toggles two reviewed categories on — REUSING the Gate 14
# / Gate 28-D harness pattern. Every case is CI-safe (no live `claude`): a mock
# verdict, or a stub `claude` on PATH that exits non-zero (→ seat exit 5).
#
# Assertions (per the plan's Gate 135 bullet):
#   1. seat_error PRESENT       — a failed seat carries a non-null, known-class
#                                 seat_error in the Sága log (NOT a bare abstain).
#   2. disposition UNCHANGED    — an abstaining high-stakes panel still fails
#                                 closed (deny); the deny does NOT depend on P0.
#   3. FM2 fail-closed trap      — a forced abort with no verdict emits deny (never
#                                 fail-open); the happy path emits exactly one verdict.
#   4. FM7 no-leak               — a secret-shaped token in the seat's stderr NEVER
#                                 reaches the stored seat_error / Sága log.
#
# Must-fail halves (mutations on a TEMP COPY — the real file is never touched):
#   (a) revert `2>"$tmp/$role.err"` → `2>/dev/null`  → the whitelisted enrichment drops.
#   (b) neuter the fail-closed trap                   → the forced abort fails OPEN.
#   (c) store raw stderr instead of the whitelist     → the secret LEAKS.
#   (d) remove the SERR classification store           → seat_error goes null (pre-P0).
#
# Exit 0 iff every assertion AND every must-fail half holds.

set -euo pipefail

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# hooks/tests/ -> hooks/ -> ravenclaude-core/ -> plugins/ -> REPO
REPO="$(cd "$SELF_DIR/../../../.." && pwd)"
PLUGIN="$REPO/plugins/ravenclaude-core"
ORCH="$PLUGIN/hooks/thing-orchestrator.sh"
SECRET='ghp_FAKE1234567890abcdefABCDEF1234567890'   # secret-SHAPED, not a real key

for bin in jq python3; do
  command -v "$bin" >/dev/null 2>&1 || { echo "SKIP: $bin not available"; exit 0; }
done
[ -f "$ORCH" ] || { echo "FAIL: orchestrator not found at $ORCH"; exit 1; }

TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP" 2>/dev/null || true; }
trap cleanup EXIT

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); printf '  PASS  %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  FAIL  %s\n' "$1"; }
check(){ if [ "$2" = "$3" ]; then ok "$1"; else bad "$1 (want [$3] got [$2])"; fi; }

# ── Temp project: two reviewed categories ON. shell_remote_mutate is high-stakes
#    (fail-closed → deny on abstain); shell_local_mutate is medium (used for the
#    below-gate_floor positive control). Mirrors the Gate 14 posture shape.
PROJ="$TMP/proj"
mkdir -p "$PROJ/.ravenclaude"
cat > "$PROJ/.ravenclaude/comfort-posture.yaml" <<'EOF'
schema_version: 5
categories:
  shell_remote_mutate:
    user: ask
    local: ask
    project: inherit
    thing: on
  shell_local_mutate:
    user: allow
    local: allow
    project: inherit
    thing: on
EOF
SAGA="$PROJ/.ravenclaude/runs/thing"

# Stub `claude` that exits non-zero → the real seat wrapper takes its exit-5
# ("claude invocation failed") path. Prepended to PATH, it wins over any real
# claude, so the exit-5 case is deterministic in CI *and* locally.
STUB="$TMP/stubbin"; mkdir -p "$STUB"
printf '#!/usr/bin/env bash\nexit 1\n' > "$STUB/claude"; chmod +x "$STUB/claude"

fresh()   { find "$SAGA" -name '*.json' -delete 2>/dev/null || true; }
payload() { jq -cn --arg c "$1" --arg cwd "$PROJ" \
              '{tool_name:"Bash",tool_input:{command:$c},cwd:$cwd,session_id:"audit"}'; }
saga()    { cat "$(ls -t "$SAGA"/*.json 2>/dev/null | head -1)" 2>/dev/null; }
decision(){ printf '%s' "$1" | jq -r '.hookSpecificOutput.permissionDecision // "none"' 2>/dev/null || echo none; }

# Drive the REAL orchestrator with a mock verdict. The trailing `|| true` swallows
# ONLY the propagated exit status (an abort-mutant aborts non-zero by design);
# stdout — the verdict JSON we assert on — is still captured. Without it `set -e`
# would kill the test on the (intentional) FM2 fault-injection runs.
run_mock() { fresh; payload "$2" | THING_SEAT_MOCK_VERDICT="$1" bash "$ORCH" 2>/dev/null || true; }
# Drive the REAL orchestrator with NO mock but a stub claude (→ real seat exit 5).
run_stub() { fresh; payload "$1" | PATH="$STUB:$PATH" bash "$ORCH" 2>/dev/null || true; }

# Copy the orchestrator to a temp path and apply exact-string mutation pairs.
# `assert n>=1` fails LOUDLY if the P0 code drifts from the byte the mutation
# targets — a shape change in the code under test must break this gate, not slip by.
mk_mutant() { # $1=out-path  then old new [old new ...]
  local out="$1"; shift
  python3 - "$ORCH" "$out" "$@" <<'PY'
import sys
src = open(sys.argv[1]).read()
out = sys.argv[2]
pairs = sys.argv[3:]
for i in range(0, len(pairs), 2):
    old, new = pairs[i], pairs[i+1]
    assert src.count(old) >= 1, f"mutation target NOT FOUND: {old!r}"
    src = src.replace(old, new)
open(out, "w").write(src)
PY
}
# A mutant runs from $TMP, so point it at the real plugin scripts via CLAUDE_PLUGIN_ROOT.
run_mutant() { # $1=mutant $2=mock ($2="" -> stub claude) $3=cmd
  fresh
  if [ -n "$2" ]; then
    payload "$3" | CLAUDE_PLUGIN_ROOT="$PLUGIN" THING_SEAT_MOCK_VERDICT="$2" bash "$1" 2>/dev/null || true
  else
    payload "$3" | CLAUDE_PLUGIN_ROOT="$PLUGIN" PATH="$STUB:$PATH" bash "$1" 2>/dev/null || true
  fi
}
# Same, but ECHO the orchestrator's EXIT CODE — the load-bearing gating signal
# (only exit 2 blocks; a deny JSON on any other non-zero exit is IGNORED and the
# command runs — claude-code-permissions.md:199/207).
run_mutant_ec() { # $1=mutant $2=mock $3=cmd -> the exit code
  fresh
  local ec=0
  payload "$3" | CLAUDE_PLUGIN_ROOT="$PLUGIN" THING_SEAT_MOCK_VERDICT="$2" bash "$1" >/dev/null 2>&1 || ec=$?
  echo "$ec"
}

echo "── Gate 135: seat stderr → Sága seat_error capture (P0, FM2, FM7) ──────────"

# ── 1. seat_error PRESENT (not a bare abstain) ───────────────────────────────
# 1a: a mock timeout → every seat abstains WITH a non-null, known-class seat_error.
out="$(run_mock timeout "git fetch origin")"
check "1a: mock-timeout run fails closed (deny)" "$(decision "$out")" "deny"
n_seats="$(saga | jq -r '.seats | length' 2>/dev/null || echo 0)"
if [ "${n_seats:-0}" -ge 2 ]; then ok "1a: panel convened ($n_seats seats)"; else bad "1a: expected >=2 seats, got $n_seats"; fi
# non-null AND a known class label for every seat (NOT bare null).
n_null="$(saga | jq -r '[.seats[] | select(.seat_error==null)] | length' 2>/dev/null || echo 99)"
check "1a: no seat carries a null seat_error (bare abstain)" "${n_null:-99}" "0"
n_timeout="$(saga | jq -r '[.seats[] | select(.seat_error=="timeout")] | length' 2>/dev/null || echo 0)"
check "1a: every abstaining seat classified 'timeout'" "${n_timeout:-0}" "${n_seats:-0}"

# 1b: a REAL seat failure (stub claude exits 1 → seat exit 5) is classified +
# enriched from the whitelisted stderr — proves the capture path end-to-end.
out="$(run_stub "git fetch origin")"
check "1b: stub-claude (real seat exit 5) fails closed (deny)" "$(decision "$out")" "deny"
se_stub="$(saga | jq -r '.seats[0].seat_error // "null"' 2>/dev/null || echo null)"
case "$se_stub" in
  "claude invocation error (exit 5)"*) ok "1b: seat_error = '$se_stub'" ;;
  *) bad "1b: expected 'claude invocation error (exit 5)…', got [$se_stub]" ;;
esac
case "$se_stub" in
  *"invocation failed"*) ok "1b: whitelisted stderr enrichment present" ;;
  *) bad "1b: expected the '— invocation failed' enrichment, got [$se_stub]" ;;
esac

# ── 2. disposition UNCHANGED by P0 (fail-closed floor is independent of seat_error) ──
# Positive control: the harness is NOT rigged to always deny.
out="$(run_mock allow "git commit -m wip")"
check "2: positive control — below-floor allow resolves to allow" "$(decision "$out")" "allow"
# Equivalence: strip the SERR classification store (simulate PRE-P0) → seat_error
# goes null AND the disposition is STILL deny — the deny comes from the >=2-abstain
# floor, not from seat_error. This is P0's additive-only invariant.
mk_mutant "$TMP/m_noserr.sh" 'SERR[$(_ri "$role")]="$_lbl"' 'SERR[$(_ri "$role")]=""'
out="$(run_mutant "$TMP/m_noserr.sh" timeout "git fetch origin")"
check "2: pre-P0 (no SERR store) still fails closed (deny)" "$(decision "$out")" "deny"
n_null="$(saga | jq -r '[.seats[] | select(.seat_error==null)] | length' 2>/dev/null || echo -1)"
n_seats="$(saga | jq -r '.seats | length' 2>/dev/null || echo 0)"
check "2: pre-P0 (no SERR store) → seat_error null (bare abstain)" "${n_null:-(-1)}" "${n_seats:-0}"

# ── 3. FM2 — fail-closed trap (the security teeth) ───────────────────────────
# 3a: happy path emits EXACTLY ONE verdict (the trap does not double-emit on exit 0).
out="$(run_mock allow "git commit -m wip")"
n_emit="$(printf '%s' "$out" | grep -c 'permissionDecision' 2>/dev/null || true)"
check "3a: happy path emits exactly one verdict JSON" "${n_emit:-0}" "1"

# 3b: force a non-zero-non-2 abort on the seat hot path (no verdict emitted) — the
# REAL fail-closed _on_exit trap must make the orchestrator EXIT 2 (the only blocking
# code; a deny JSON on any other non-zero exit is IGNORED and the command RUNS). Assert
# the EXIT CODE, not stdout — the exit code is what actually gates the tool call.
mk_mutant "$TMP/m_abort.sh" \
  '  _tmp_to_clean="$tmp"' '  _tmp_to_clean="$tmp"
  false  # FM2 forced abort (test injection)'
check "3b: forced seat-path abort → orchestrator exits 2 (blocks, NOT fail-open)" \
  "$(run_mutant_ec "$TMP/m_abort.sh" allow "git fetch origin")" "2"

# 3c: the trap's guard, unit-tested on the REAL function body (extracted verbatim).
# The fail-closed conversion is an EXIT-CODE 2 (the blocking signal); a legit early
# allow (ec=0) or an already-emitted verdict must NOT be turned into a block.
awk '/^_on_exit\(\) \{/{f=1} f{print} f&&/^\}$/{exit}' "$ORCH" > "$TMP/on_exit.snip"
trap_ec() { # $1=_emitted $2=simulated-exit-code -> the trap's resulting exit code
  local ec=0
  bash -c 'source "$1"; _emitted="$2"; _tmp_to_clean=""; ( exit "$3" ); _on_exit' \
    _ "$TMP/on_exit.snip" "$1" "$2" >/dev/null 2>&1 || ec=$?
  echo "$ec"
}
check "3c: trap on abort (ec=1, unemitted) → exits 2 (fail-closed block)" "$(trap_ec 0 1)" "2"
check "3c: trap on ec=0 (legit allow) → does NOT block" "$(trap_ec 0 0)" "0"
check "3c: trap when already emitted → does NOT block" "$(trap_ec 1 1)" "0"
# and the trap emits its reason to STDERR (not stdout — stdout JSON is ignored on exit 2)
stderr_txt="$(bash -c 'source "$1"; _emitted=0; _tmp_to_clean=""; ( exit 1 ); _on_exit' _ "$TMP/on_exit.snip" 2>&1 >/dev/null || true)"
if printf '%s' "$stderr_txt" | grep -qi 'failing closed'; then ok "3c: trap reason goes to stderr"; else bad "3c: trap reason not on stderr"; fi

# ── 4. FM7 — no secret leak ──────────────────────────────────────────────────
# The unknown-mock path echoes the (attacker-controllable) mock value to the seat's
# stderr; drive a secret-shaped value through it. The bounded read + whitelist store
# only known rc-class labels — the raw stderr (with the secret) is NEVER stored.
out="$(run_mock "$SECRET" "git fetch origin")"
check "4: secret-in-stderr run still fails closed (deny)" "$(decision "$out")" "deny"
saga_txt="$(saga)"
if printf '%s' "$saga_txt" | grep -q "$SECRET"; then
  bad "4: SECRET LEAKED into the Sága log"
else
  ok "4: secret NEVER appears in the Sága log (bounded + whitelisted)"
fi
se_sec="$(printf '%s' "$saga_txt" | jq -r '.seats[0].seat_error // "null"' 2>/dev/null || echo null)"
check "4: seat_error is the safe rc-class label, not raw stderr" "$se_sec" "bad payload / mock"

# ── Must-fail halves (each mutation must break exactly the property it targets) ──
echo "── Gate 135: must-fail halves (mutations prove each control has teeth) ──────"

# (a) revert the stderr capture → the whitelisted enrichment suffix drops.
mk_mutant "$TMP/m_redir.sh" '2>"$tmp/$role.err"' '2>/dev/null'
run_mutant "$TMP/m_redir.sh" "" "git fetch origin" >/dev/null
se_rev="$(saga | jq -r '.seats[0].seat_error // "null"' 2>/dev/null || echo null)"
case "$se_rev" in
  *"invocation failed"*) bad "(a) reverting the capture STILL enriched — no teeth [$se_rev]" ;;
  "claude invocation error (exit 5)"*) ok "(a) revert 2>/dev/null → enrichment dropped (capture matters)" ;;
  *) bad "(a) unexpected seat_error under reverted capture: [$se_rev]" ;;
esac

# (b) neuter the fail-closed trap → the same forced abort now fails OPEN. The gating
# signal is the EXIT CODE: the real trap makes the abort exit 2 (blocks); with the
# guard neutered the abort exits its raw non-zero-non-2 code (1), which Claude Code
# treats as non-blocking → the command RUNS (fail-open). Assert the exit code flips.
mk_mutant "$TMP/m_abort_notrap.sh" \
  '  _tmp_to_clean="$tmp"' '  _tmp_to_clean="$tmp"
  false  # FM2 forced abort (test injection)' \
  'if [ "$_emitted" != 1 ] && [ "$_ec" != 0 ] && [ "$_ec" != 2 ]; then' 'if false; then'
ec_notrap="$(run_mutant_ec "$TMP/m_abort_notrap.sh" allow "git fetch origin")"
if [ "$ec_notrap" = "2" ]; then
  bad "(b) trap-removed mutant STILL exits 2 — no teeth (the guard isn't the thing blocking)"
elif [ "$ec_notrap" != "0" ] && [ "$ec_notrap" != "2" ]; then
  ok "(b) trap removed → forced abort exits $ec_notrap (non-2 = fail-OPEN; the real trap's exit-2 is what closes it)"
else
  bad "(b) trap-removed mutant exited $ec_notrap (unexpected)"
fi

# (c) store raw stderr instead of the whitelist → the secret LEAKS.
mk_mutant "$TMP/m_leak.sh" 'SERR[$(_ri "$role")]="$_lbl"' 'SERR[$(_ri "$role")]="$_raw"'
run_mutant "$TMP/m_leak.sh" "$SECRET" "git fetch origin" >/dev/null
if saga | grep -q "$SECRET"; then
  ok "(c) raw-stderr store → secret LEAKS (whitelist store matters)"
else
  bad "(c) raw-stderr mutant did NOT leak — no teeth (FM7 test would be vacuous)"
fi

echo "─────────────────────────────────────────────────────────────────────────────"
printf 'Gate 135: %d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
echo "Gate 135 PASS — P0 seat-error capture: present, fail-closed, no-leak, teeth proven."
