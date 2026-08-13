#!/usr/bin/env bash
# Gate 198 — macOS-portability lint (in-loop hook + CI backstop).
#
# The class this closes is the highest-recurrence one in the inventory: eighteen
# separate commits have closed a stock-macOS door.
#
# What was MEASURED for this change (control run 2026-08-13 under
# `env -i PATH=/usr/bin:/bin` on the authoring machine, bidirectional so the probe
# is shown able to return the opposite): `timeout` and `gtimeout` did not resolve,
# while `perl`, `python3`, `grep`, `sed` and `readlink` all did; `grep -P` exited 2
# with "invalid option -- P"; `bash --version` reported 3.2.57; `declare -A` exited
# 2; `${v^^}` reported "bad substitution".
#
# The reason those matter so much here is the harness's exit-code contract, which
# this repo documents at length (a hook exit other than 2 is treated as a
# non-blocking error) — that part is the repo's documented contract, NOT something
# this change re-measured. Under it, the exit-1 and exit-127 shapes above are the
# quiet ones.
#
# Two surfaces, ONE token table (knowledge/portability-tokens.json). Neither
# hard-codes a pattern, so they cannot drift — the parity is structural. This test
# asserts BOTH read the same table, because two hand-maintained lists is exactly
# the drift this initiative exists to prevent.
#
# Fixture tokens are assembled from fragments where a literal would be scanned by
# a sibling guard — the same self-reference constraint the premise and destructive
# guards hit. Do NOT "simplify" them back into literals.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HOOK="$HERE/../enforce-portability.sh"
REPO="$(cd "$HERE/../../../.." && pwd)"
LINT="$REPO/scripts/check-portability-lint.py"
PASS=0; FAIL=0
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

ok()  { PASS=$((PASS+1)); printf '  ok    %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  FAIL  %s (%s)\n' "$1" "$2"; }

PROJ="$TMP/proj"; mkdir -p "$PROJ/.ravenclaude" "$PROJ/plugins/x/hooks" "$PROJ/docs"

_posture() { # mode ("" = no key, "none" = no file)
  if [ "$1" = "none" ]; then rm -f "$PROJ/.ravenclaude/comfort-posture.yaml"; return; fi
  { echo "schema_version: 5"; [ -n "$1" ] && echo "macos_portability_lint: $1"; } \
    > "$PROJ/.ravenclaude/comfort-posture.yaml"
}

_run() { # hook file content -> "exit|stderr"
  local err rc=0 body
  body="$(python3 -c 'import json,sys;print(json.dumps({"tool_name":"Write","tool_input":{"file_path":sys.argv[1],"content":sys.argv[2]}}))' "$2" "$3")"
  err="$(printf '%s' "$body" | CLAUDE_PROJECT_DIR="$PROJ" bash "$1" 2>&1 >/dev/null)" || rc=$?
  printf '%s|%s' "$rc" "$err"
}

D="-"
BANNED="$(printf '#!/bin/bash\ndeclare %sA m\n' "$D")"
SHIMMED='#!/bin/bash
_rc_timeout 5 sleep 1'
TARGET="$PROJ/plugins/x/hooks/demo.sh"

echo "── Gate 198: macOS-portability lint ──"

# ── Control: the fixture really does trip the lint ──────────────────────────
# Asserted FIRST. Every "not flagged" result below is only meaningful if this
# fixture would otherwise fire — an inert fixture makes them all vacuous.
_posture warn
r="$(_run "$HOOK" "$TARGET" "$BANNED")"
case "$r" in 0\|*portability\ notice*) ok "control: the banned-token fixture IS flagged (warn, exit 0)";;
  *) bad "control fixture" "got [$r]";; esac

# ── Knob behaviour ─────────────────────────────────────────────────────────
_posture block
r="$(_run "$HOOK" "$TARGET" "$BANNED")"
case "$r" in 2\|*BLOCKED*) ok "block: denies with exit 2";; *) bad "block" "got [$r]";; esac

_posture off
r="$(_run "$HOOK" "$TARGET" "$BANNED")"
[ "$r" = "0|" ] && ok "off: silent no-op" || bad "off" "got [$r]"

_posture none
r="$(_run "$HOOK" "$TARGET" "$BANNED")"
[ "$r" = "0|" ] && ok "absent posture: silent no-op (opt-in by presence)" || bad "absent posture" "got [$r]"

_posture ""
r="$(_run "$HOOK" "$TARGET" "$BANNED")"
case "$r" in 0\|*portability\ notice*) ok "posture present, key absent: defaults to warn";;
  *) bad "default warn" "got [$r]";; esac

# ── The lint must stay usable — this is why it survives its first week ──────
_posture block
r="$(_run "$HOOK" "$TARGET" "$SHIMMED")"
[ "$r" = "0|" ] && ok "the shimmed form is not flagged" || bad "shimmed form" "got [$r]"

r="$(_run "$HOOK" "$TARGET" "$(printf 'declare %sA m  # noport: documented example\n' "$D")")"
[ "$r" = "0|" ] && ok "a '# noport' line is skipped" || bad "noport sentinel" "got [$r]"

r="$(_run "$HOOK" "$TARGET" "$(printf '# never use declare %sA here\n' "$D")")"
[ "$r" = "0|" ] && ok "a comment naming the token is not flagged" || bad "comment" "got [$r]"

# Out of scope: prose, no shebang. Note the fixture deliberately carries NO
# shebang — scope is by shape, not by extension, and a shebang'd file is a script
# whatever it is called (see the extension-less assertion below).
r="$(_run "$HOOK" "$PROJ/docs/notes.md" "$(printf 'Prose about declare %sA in a doc.\n' "$D")")"
[ "$r" = "0|" ] && ok "an out-of-scope prose file is not screened" || bad "out-of-scope" "got [$r]"

# The inverse, and it is the one that matters: an EXTENSION-LESS script must be
# screened. Two of the most recent real breaks were outside hooks/**, one of them
# in an extension-less installer that a `*.sh` glob silently misses.
r="$(_run "$HOOK" "$PROJ/scripts/ravenclaude" "$BANNED")"
case "$r" in 2\|*BLOCKED*) ok "an extension-less shebang'd script IS screened";;
  *) bad "extension-less script" "got [$r]";; esac

r="$(_run "$HOOK" "$PROJ/plugins/x/hooks/_portable.sh" "$BANNED")"
[ "$r" = "0|" ] && ok "the shim file itself is exempt (self-non-recursion)" || bad "exempt file" "got [$r]"

# ── TEETH — a mutant that neuters the deny MUST let the block-knob violation
# through, or the "block: denies" assertion is not measuring the deny.
MUT="$TMP/mutant.sh"
python3 - "$HOOK" "$MUT" <<'PY'
import sys
src, dst = sys.argv[1], sys.argv[2]
t = open(src, encoding="utf-8").read().replace('if [ "$mode" = "block" ]; then',
                                               'if false; then', 1)
open(dst, "w", encoding="utf-8").write(t)
PY
_posture block
r="$(_run "$MUT" "$TARGET" "$BANNED")"
case "$r" in 0\|*) ok "teeth: deny-neutered mutant lets the block-knob violation through";;
  *) bad "teeth (hook)" "expected exit 0 from the mutant, got [$r]";; esac

# ── The CI backstop: its own teeth + the shared-table parity ────────────────
if python3 "$LINT" --self-test >/dev/null 2>&1; then
  ok "CI linter: teeth verified (every token caught, every companion clean)"
else
  bad "CI linter teeth" "check-portability-lint.py --self-test failed"
fi

if (cd "$REPO" && python3 "$LINT" >/dev/null 2>&1); then
  ok "CI linter: the live tree is clean"
else
  bad "CI linter on live tree" "findings present — run: python3 scripts/check-portability-lint.py"
fi

# Structural parity: BOTH surfaces read the SAME table, and neither hard-codes a
# pattern. A hard-coded pattern is how two surfaces silently diverge.
TABLE_REF="knowledge/portability-tokens.json"
if grep -q "$TABLE_REF" "$HOOK" && grep -q "$TABLE_REF" "$LINT"; then
  ok "both surfaces read the same token table (parity is structural)"
else
  bad "shared table" "one surface does not reference $TABLE_REF"
fi

n_hook="$(python3 -c '
import json,sys
toks=json.load(open(sys.argv[1],encoding="utf-8"))["tokens"]
src=open(sys.argv[2],encoding="utf-8").read()
print(sum(1 for t in toks if t["pattern"] in src))' \
  "$HERE/../../knowledge/portability-tokens.json" "$HOOK" 2>/dev/null || echo 0)"
[ "$n_hook" = "0" ] && ok "the hook hard-codes no pattern from the table" \
  || bad "hook hard-codes patterns" "$n_hook pattern(s) inlined — they will drift"

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
