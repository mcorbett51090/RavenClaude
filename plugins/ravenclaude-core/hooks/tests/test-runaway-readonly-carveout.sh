#!/usr/bin/env bash
# test-runaway-readonly-carveout.sh — Gate 53 fixture for the runaway-brake
# read-only carve-out (v0.131.2).
#
# Proves the read-only carve-out added to hooks/runaway-brake.sh: a legitimate
# burst of read-only startup commands no longer trips the consecutive-LOOP brake,
# while every real protection is preserved.
#
# Seven subtests:
#   R1  N (=12) identical READ-ONLY calls (repeated `git log`) do NOT trip
#       max_consecutive (the consec counter never advances for them).
#   R2  N (=10) identical MUTATING calls (repeated `rm x`) DO trip
#       max_consecutive (unchanged behavior).
#   R2b N (=10) identical Write calls (a mutating non-Bash tool) DO trip
#       max_consecutive (unchanged behavior).
#   R3  `total` still accumulates for read-only calls AND the max_total ceiling
#       still trips on a read-only-only session.
#   R4  A read-only command with an appended mutating clause (`git log && rm x`)
#       is classified NOT read-only — it counts toward consec and trips.
#   R6  Allowlist-leak classes (find -delete, git branch <name>, git remote add,
#       git log --output=f) are classified NOT read-only — each counts and trips
#       (closes the PR #354 security-review findings).
#   R5  Must-fail half — patch the hook to drop the read-only carve-out (count
#       every call) and assert R1 now TRIPS, proving the carve-out has teeth.
#
# Run directly:   bash plugins/ravenclaude-core/hooks/tests/test-runaway-readonly-carveout.sh
# Run via gate:   bash scripts/audit-gates.sh --check 53

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

HOOK="$REPO_ROOT/plugins/ravenclaude-core/hooks/runaway-brake.sh"
PASS=0
FAIL=0

pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

# Build a PreToolUse payload for a given tool_name + JSON tool_input, scoped to a
# tmp cwd (with a comfort-posture.yaml so the hook is opted in) and a session id.
mk_payload() {
  # $1 cwd  $2 session_id  $3 tool_name  $4 tool_input(JSON)
  python3 - "$1" "$2" "$3" "$4" <<'PY'
import json, sys
cwd, sid, tn, ti = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
print(json.dumps({"cwd": cwd, "session_id": sid, "tool_name": tn,
                  "tool_input": json.loads(ti)}))
PY
}

# Fire the hook N times with the same payload against a fresh tmp session.
# Echoes the exit code of EACH call, one per line. Uses the hook at $HOOK unless
# $2 overrides it (for the must-fail half).
fire_n() {
  # $1 N  $2 hook-path  $3 tool_name  $4 tool_input(JSON)  $5 posture-extra(yaml)
  local n="$1" hook="$2" tn="$3" ti="$4" extra="${5:-}"
  local root sid payload rc
  root="$(mktemp -d)"
  mkdir -p "$root/.ravenclaude"
  {
    printf 'categories:\n  shell_readonly: allow\n'
    [ -n "$extra" ] && printf '%s\n' "$extra"
  } > "$root/.ravenclaude/comfort-posture.yaml"
  sid="sess-$RANDOM$RANDOM"
  payload="$(mk_payload "$root" "$sid" "$tn" "$ti")"
  for _ in $(seq 1 "$n"); do
    printf '%s' "$payload" | bash "$hook" >/dev/null 2>&1
    printf '%s\n' "$?"
  done
  rm -rf "$root"
}

# Did ANY of the N invocations trip (exit 2)?
any_trip() { grep -q '^2$' <<<"$1"; }

echo
echo "── R1: 12 identical READ-ONLY calls (git log) → NO trip ──────────────────"
OUT="$(fire_n 12 "$HOOK" "Bash" '{"command":"git log --oneline -5"}')"
if any_trip "$OUT"; then
  fail "R1: a read-only burst tripped the brake (it must be transparent to consec)"
else
  pass "R1: 12 identical read-only git-log calls did not trip max_consecutive"
fi

echo
echo "── R2: 10 identical MUTATING calls (rm x) → trip ─────────────────────────"
OUT="$(fire_n 10 "$HOOK" "Bash" '{"command":"rm x"}')"
if any_trip "$OUT"; then
  pass "R2: 10 identical mutating rm calls tripped max_consecutive (unchanged)"
else
  fail "R2: a repeated mutating command did NOT trip — protection regressed"
fi

echo
echo "── R2b: 10 identical Write calls (mutating non-Bash) → trip ──────────────"
OUT="$(fire_n 10 "$HOOK" "Write" '{"file_path":"/tmp/x","content":"y"}')"
if any_trip "$OUT"; then
  pass "R2b: 10 identical Write calls tripped max_consecutive (unchanged)"
else
  fail "R2b: a repeated Write did NOT trip — protection regressed"
fi

echo
echo "── R3: read-only calls still count toward total; max_total ceiling trips ─"
# Lower max_total to 5 so a read-only-only burst hits the ceiling deterministically.
OUT="$(fire_n 6 "$HOOK" "Bash" '{"command":"ls -la"}' 'runaway:
  max_total: 5')"
if any_trip "$OUT"; then
  pass "R3: read-only-only session still trips max_total (total accumulates)"
else
  fail "R3: max_total did NOT trip on read-only calls — the ceiling was bypassed"
fi

echo
echo "── R4: read-only prefix + appended mutating clause (git log && rm x) → trip"
OUT="$(fire_n 10 "$HOOK" "Bash" '{"command":"git log && rm x"}')"
if any_trip "$OUT"; then
  pass "R4: 'git log && rm x' classified NOT read-only — counts and trips"
else
  fail "R4: a chained mutating command was treated as read-only — carve-out too wide"
fi

echo
echo "── R6: allowlist-leak classes must COUNT (not read-only) — each trips ────"
# Security-review (PR #354) found four genuinely-mutating commands that the first
# cut of the allowlist misclassified as read-only: `find -delete` (find dropped),
# `git branch <name>` (creates), `git remote add` (mutates config), and a write-
# redirecting `git log --output=f`. Each, repeated, must trip max_consecutive —
# proving it is COUNTED, i.e. classified NOT read-only.
while IFS= read -r spec; do
  [ -n "$spec" ] || continue
  R6TI="$(python3 -c 'import json,sys;print(json.dumps({"command":sys.argv[1]}))' "$spec")"
  OUT="$(fire_n 10 "$HOOK" "Bash" "$R6TI")"
  if any_trip "$OUT"; then
    pass "R6: '$spec' classified NOT read-only — counts and trips"
  else
    fail "R6: '$spec' treated as read-only — a mutating command leaked through the allowlist"
  fi
done <<'SPECS'
find . -delete
git branch newbranch
git remote add origin foo
git log --output=/tmp/f
SPECS

echo
echo "── R5: must-fail half — carve-out stripped → R1-shape input now trips ────"
# Build a patched hook that forces read_only=0 always (carve-out neutralized).
PATCH_TMP="$(mktemp -d)"
PATCH_HOOK="$PATCH_TMP/runaway-brake-nocarve.sh"
python3 - "$HOOK" "$PATCH_HOOK" <<'PY'
import re, sys
src = open(sys.argv[1]).read()
# Neutralize the carve-out: force read_only to 0 regardless of classification.
patched = src.replace(
    'read_only=0\nif is_read_only "$tn" "$cmd"; then read_only=1; fi',
    'read_only=0   # carve-out neutralized for the must-fail half'
)
assert patched != src, "must-fail patch did not change the hook (anchor drift)"
open(sys.argv[2], "w").write(patched)
PY
OUT="$(fire_n 12 "$PATCH_HOOK" "Bash" '{"command":"git log --oneline -5"}')"
rm -rf "$PATCH_TMP"
if any_trip "$OUT"; then
  pass "R5 must-fail half: with the carve-out stripped, the read-only burst trips — confirms R1 has teeth"
else
  fail "R5 must-fail half: the patched (no-carve) hook did NOT trip — the patch may not have neutralized the carve-out"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "Gate 53 (runaway read-only carve-out): ALL ASSERTIONS PASS"
  exit 0
else
  echo "Gate 53 (runaway read-only carve-out): $FAIL assertion(s) FAILED"
  exit 1
fi
