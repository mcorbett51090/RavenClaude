#!/usr/bin/env bash
# Gate — nudge-dataverse-preflight.sh (PreToolUse Bash advisory).
#   A: a Dataverse create/update (POST/PATCH to /api/data/) under a comfort-posture -> nudge.
#   B: a Dataverse GET under posture -> silent (write-only).
#   C: a create/update with NO comfort-posture -> silent (opt-in).
#   D: teeth — a mutant with the write-filter neutered fires on a GET.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK="$(cd "$HERE/.." && pwd)/nudge-dataverse-preflight.sh"
fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}
TMP="$(mktemp -d)"
POSTURE="$TMP/p"
mkdir -p "$POSTURE/.ravenclaude"
printf 'schema_version: 5\n' >"$POSTURE/.ravenclaude/comfort-posture.yaml"
NOPOSTURE="$TMP/np"
mkdir -p "$NOPOSTURE"

POST_CMD='curl -X POST https://x.crm.dynamics.com/api/data/v9.2/contoso_balancesheets --data @p.json'
GET_CMD='curl https://x.crm.dynamics.com/api/data/v9.2/contoso_balancesheets?$top=1'

# fires? = the hook printed the nudge marker to stderr from inside $cwd
fires() { # $1=hook $2=cwd $3=command
  local out
  out="$(cd "$2" && printf '{"tool_name":"Bash","tool_input":{"command":%s}}' "$(printf '%s' "$3" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')" | bash "$1" 2>&1 1>/dev/null)"
  printf '%s' "$out" | grep -q "pre-flight the payload"
}

fires "$HOOK" "$POSTURE" "$POST_CMD" && pass "Dataverse create/update under posture -> nudge" || fail "A: did not fire on a POST"
fires "$HOOK" "$POSTURE" "$GET_CMD" && fail "B: fired on a GET (should be write-only)" || pass "Dataverse GET under posture -> silent"
fires "$HOOK" "$NOPOSTURE" "$POST_CMD" && fail "C: fired without a comfort-posture (should be opt-in)" || pass "no comfort-posture -> silent (opt-in)"

# D — teeth: neuter the write-only filter; a GET must then fire
MUT="$TMP/mut.sh"
sed 's/\[ "\$is_write" -eq 0 \] && exit 0/:/' "$HOOK" >"$MUT"
chmod +x "$MUT"
if ! grep -qE '^\s*:\s*$' "$MUT" && ! grep -q 'is_write" -eq 0 ] && :' "$MUT"; then
  # fall back: just confirm the sed changed something
  if ! diff -q "$HOOK" "$MUT" >/dev/null; then :; else fail "D: could not neuter the write filter (sed no-op)"; fi
fi
if ! diff -q "$HOOK" "$MUT" >/dev/null 2>&1; then
  fires "$MUT" "$POSTURE" "$GET_CMD" && pass "must-fail half: neutered write-filter fires on a GET (the filter is load-bearing)" \
    || fail "D: neutered write-filter still silent on a GET (no teeth)"
else
  fail "D: sed did not modify the hook"
fi

echo ""
if [ "$fails" -eq 0 ]; then
  echo "nudge gate PASS — fires on Dataverse create/update under posture, silent on GET / opt-out, has teeth."
  exit 0
else
  echo "nudge gate FAIL — $fails subtest(s)."
  exit 1
fi
