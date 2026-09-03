#!/usr/bin/env bash
# Gate 184 — guard-memory-compaction.sh
#
# Proves the guard BLOCKS an unreviewed lossy rewrite of a memory index and
# ALLOWS everything else, and proves the assertion has teeth via a must-fail half
# (a mutant with the deny branch removed MUST let the shrink through).
#
# bash 3.2 safe. No GNU-only tools.
set -uo pipefail

HOOK="$(cd "$(dirname "$0")/.." && pwd)/guard-memory-compaction.sh"
fails=0

_mkpayload() { # $1=path $2=content
  python3 -c '
import json,sys
print(json.dumps({"tool_name":"Write","tool_input":{"file_path":sys.argv[1],"content":sys.argv[2]}}))' "$1" "$2"
}

_mkpayload_multiedit() { # $1=path $2=old_string $3=new_string [$4=old2 $5=new2]
  python3 -c '
import json,sys
path=sys.argv[1]
edits=[{"old_string":sys.argv[2],"new_string":sys.argv[3]}]
if len(sys.argv) > 5:
    edits.append({"old_string":sys.argv[4],"new_string":sys.argv[5]})
print(json.dumps({"tool_name":"MultiEdit","tool_input":{"file_path":path,"edits":edits}}))' "$@"
}

_run() { # $1=hook $2=payload -> echoes exit code
  printf '%s' "$2" | bash "$1" >/dev/null 2>&1; echo $?
}

_assert() { # $1=label $2=want $3=got
  if [ "$2" = "$3" ]; then
    printf '  ok   %-38s exit=%s\n' "$1" "$3"
  else
    printf '  FAIL %-38s want=%s got=%s\n' "$1" "$2" "$3"; fails=$((fails+1))
  fi
}

T="$(mktemp -d)"; mkdir -p "$T/memory"
python3 -c "open('$T/memory/MEMORY.md','w').write('# Memory index\n'+('- padding line to exceed the 1024-byte floor\n'*200))"
ORIG=$(wc -c < "$T/memory/MEMORY.md" | tr -d ' ')
export CLAUDE_PROJECT_DIR="$T" CLAUDE_SESSION_ID=gate184

BIG=$(python3 -c "print('x'*($ORIG*2))")
HALF=$(python3 -c "print('x'*($ORIG//2))")
NEAR=$(python3 -c "print('x'*int($ORIG*0.93))")
MULTI_OLD=$(python3 -c "print('y'*$ORIG)")
TENTH_OLD=$(python3 -c "print('a'*($ORIG//10))")
SMALL_OLD=$(python3 -c "print('a'*int($ORIG*0.07))")

echo "Gate 184 — memory-compaction guard"
_assert "50% shrink is BLOCKED"      2 "$(_run "$HOOK" "$(_mkpayload "$T/memory/MEMORY.md" "$HALF")")"
_assert "growth allowed"             0 "$(_run "$HOOK" "$(_mkpayload "$T/memory/MEMORY.md" "$BIG")")"
_assert "7% shrink allowed"          0 "$(_run "$HOOK" "$(_mkpayload "$T/memory/MEMORY.md" "$NEAR")")"
_assert "non-memory path allowed"    0 "$(_run "$HOOK" "$(_mkpayload "$T/other.md" "$HALF")")"
_assert "escape hatch allowed"       0 "$(_run "$HOOK" "$(_mkpayload "$T/memory/MEMORY.md" "compaction-approved")")"

# ---- MultiEdit: the finding this gate exists to prove fixed -----------------
# MultiEdit's real tool_input shape is {file_path, edits:[{old_string,new_string},...]}
# -- a single top-level old_string/new_string never exists on a MultiEdit call.
_assert "MultiEdit 50% shrink is BLOCKED" \
  2 "$(_run "$HOOK" "$(_mkpayload_multiedit "$T/memory/MEMORY.md" "$MULTI_OLD" "$HALF")")"
_assert "MultiEdit summed-across-edits shrink BLOCKED" \
  2 "$(_run "$HOOK" "$(_mkpayload_multiedit "$T/memory/MEMORY.md" "$TENTH_OLD" "" "$TENTH_OLD" "")")"
_assert "MultiEdit small (7%) shrink allowed" \
  0 "$(_run "$HOOK" "$(_mkpayload_multiedit "$T/memory/MEMORY.md" "$SMALL_OLD" "")")"
_assert "MultiEdit escape hatch allowed" \
  0 "$(_run "$HOOK" "$(_mkpayload_multiedit "$T/memory/MEMORY.md" "$MULTI_OLD" "compaction-approved")")"

# snapshot must exist — the half that makes a lossy rewrite recoverable
snaps=$(find "$T/.ravenclaude" -name '*.bak' 2>/dev/null | wc -l | tr -d ' ')
if [ "$snaps" -ge 1 ]; then printf '  ok   %-38s (%s)\n' "snapshot written" "$snaps"
else printf '  FAIL %-38s none found\n' "snapshot written"; fails=$((fails+1)); fi

# ---- must-fail half: strip the deny, prove the assertion has teeth -----------
MUT="$T/mutant.sh"
python3 - "$HOOK" "$MUT" <<'MUTPY'
import sys
src = open(sys.argv[1]).read()
# neuter the only blocking exit; everything else identical
src = src.replace("exit 2 # 2 blocks the tool call", "exit 0 # MUTANT: deny removed")
open(sys.argv[2], "w").write(src)
MUTPY
got=$(_run "$MUT" "$(_mkpayload "$T/memory/MEMORY.md" "$HALF")")
if [ "$got" = "0" ]; then
  printf '  ok   %-38s mutant lets the shrink through\n' "must-fail half (teeth proven)"
else
  printf '  FAIL %-38s mutant still exited %s — the test is not measuring the deny\n' "must-fail half" "$got"
  fails=$((fails+1))
fi

# ---- must-fail half (MultiEdit-specific): revert to the pre-fix routing,
# prove the new MultiEdit tests have teeth against the ORIGINAL defect ---------
# The original bug was that MultiEdit fell through into the Edit branch (which
# reads .tool_input.old_string/.new_string -- fields MultiEdit never carries),
# so new_bytes was never set and the write fell through the fail-safe
# "no new_bytes -> exit 0" path with ZERO shrink measurement. Reproduce that
# exact routing by disabling the MultiEdit-specific elif so a real MultiEdit
# call falls into the same else (Edit) branch again -- the smallest possible
# change that reproduces the pre-fix defect verbatim.
MUT2="$T/mutant-multiedit.sh"
python3 - "$HOOK" "$MUT2" <<'MUTPY2'
import sys
src = open(sys.argv[1]).read()
needle = 'elif [ "$tool_name" = "MultiEdit" ]; then'
assert needle in src, "fixture out of sync with guard-memory-compaction.sh"
src = src.replace(needle, 'elif [ "$tool_name" = "MultiEdit-DISABLED-FOR-MUTANT" ]; then')
open(sys.argv[2], "w").write(src)
MUTPY2
got=$(_run "$MUT2" "$(_mkpayload_multiedit "$T/memory/MEMORY.md" "$MULTI_OLD" "$HALF")")
if [ "$got" = "0" ]; then
  printf '  ok   %-38s mutant lets the MultiEdit shrink through\n' "MultiEdit must-fail half (teeth proven)"
else
  printf '  FAIL %-38s mutant exited %s — the MultiEdit test is not measuring the fix\n' "MultiEdit must-fail half" "$got"
  fails=$((fails+1))
fi

echo
if [ "$fails" -eq 0 ]; then echo "Gate 184 PASS"; exit 0; else echo "Gate 184 FAIL ($fails)"; exit 1; fi
