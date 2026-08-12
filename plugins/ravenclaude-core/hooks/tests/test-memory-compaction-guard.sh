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

echo "Gate 184 — memory-compaction guard"
_assert "50% shrink is BLOCKED"      2 "$(_run "$HOOK" "$(_mkpayload "$T/memory/MEMORY.md" "$HALF")")"
_assert "growth allowed"             0 "$(_run "$HOOK" "$(_mkpayload "$T/memory/MEMORY.md" "$BIG")")"
_assert "7% shrink allowed"          0 "$(_run "$HOOK" "$(_mkpayload "$T/memory/MEMORY.md" "$NEAR")")"
_assert "non-memory path allowed"    0 "$(_run "$HOOK" "$(_mkpayload "$T/other.md" "$HALF")")"
_assert "escape hatch allowed"       0 "$(_run "$HOOK" "$(_mkpayload "$T/memory/MEMORY.md" "compaction-approved")")"

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

echo
if [ "$fails" -eq 0 ]; then echo "Gate 184 PASS"; exit 0; else echo "Gate 184 FAIL ($fails)"; exit 1; fi
