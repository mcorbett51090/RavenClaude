#!/usr/bin/env bash
# Gate 127 — pseudonymize.py: the reversible name/entity pseudonymizer's security invariants.
# Drives the REAL script:
#   A self-test: the built-in fixtures (FM2 Al/Alabama, FM3 homoglyph, FM9 mangled-token
#     decode, round-trip, FM1 abbreviation scan) all pass.
#   B no-egress: a listed name is absent from encode's stdout; the vault is 0600.
#   C FM7: `--ner` with no backend exits 10 with EMPTY stdout (distinct, non-suppressible;
#     never a silent exit-0 downgrade).
#   D FM8 fail-closed: an unreadable --entities-file exits nonzero with EMPTY stdout
#     (no raw echo).
#   E teeth (must-fail half): a mutant whose encode fail-closed path is turned fail-OPEN
#     (echoes stdin) DOES leak the raw name — proving the fail-closed guard is real code.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$(cd "$HERE/../.." && pwd)/scripts/pseudonymize.py"
fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}

TMP="$(mktemp -d)"
ENTS="$TMP/ents.txt"
printf '# known\nAcme Corporation | ORG\nJane Doe\n' >"$ENTS"

# A — self-test
if python3 "$SCRIPT" self-test >/dev/null 2>&1; then
  pass "A: self-test (FM1/FM2/FM3/FM9/round-trip) passes"
else
  fail "A: self-test failed"
fi

# B — no-egress + vault perms
ENC="$TMP/enc.txt"
printf 'Jane Doe at Acme Corporation.' | python3 "$SCRIPT" encode --map-file "$TMP/v.json" --entities-file "$ENTS" >"$ENC" 2>/dev/null
if grep -qE 'Jane Doe|Acme Corporation' "$ENC"; then
  fail "B: a listed name leaked into encode stdout"
else
  pass "B: listed names absent from encode stdout (no-egress)"
fi
perms="$(stat -c '%a' "$TMP/v.json" 2>/dev/null || stat -f '%Lp' "$TMP/v.json" 2>/dev/null)"
[ "$perms" = "600" ] && pass "B: vault is 0600 from creation" || fail "B: vault perms $perms (want 600)"

# C — FM7: --ner absent -> exit 10, empty stdout
NEROUT="$TMP/ner.txt"
printf 'text' | python3 "$SCRIPT" encode --map-file "$TMP/vn.json" --ner >"$NEROUT" 2>/dev/null
rc=$?
if [ "$rc" -eq 10 ] && [ ! -s "$NEROUT" ]; then
  pass "C: FM7 --ner-without-backend -> exit 10 + empty stdout (non-suppressible)"
else
  fail "C: FM7 expected exit 10 + empty stdout, got exit $rc, stdout $([ -s "$NEROUT" ] && echo NONEMPTY || echo empty)"
fi

# D — FM8: unreadable entities-file -> nonzero + empty stdout
FCOUT="$TMP/fc.txt"
printf 'Jane Doe secret' | python3 "$SCRIPT" encode --map-file "$TMP/v2.json" --entities-file "$TMP/NOPE.txt" >"$FCOUT" 2>/dev/null
rc=$?
if [ "$rc" -ne 0 ] && [ ! -s "$FCOUT" ]; then
  pass "D: FM8 unreadable entities-file -> fail closed (nonzero + empty stdout)"
else
  fail "D: FM8 expected fail-closed, got exit $rc, stdout $([ -s "$FCOUT" ] && echo NONEMPTY-LEAK || echo empty)"
fi

# E — teeth: turn the encode fail-closed path fail-OPEN; it must then leak.
# The mutant imports pseudonymize-brief.py relative to its OWN dir, so copy it alongside.
MUT="$TMP/mutant.py"
cp "$(dirname "$SCRIPT")/pseudonymize-brief.py" "$TMP/pseudonymize-brief.py"
python3 - "$SCRIPT" "$MUT" <<'PY'
import sys
src=open(sys.argv[1]).read()
needle='            sys.stderr.write(f"pseudonymize encode failed (nothing egressed): {exc}\\n")\n            return 1'
repl='            sys.stdout.write(text)  # MUTANT fail-open\n            return 1'
assert needle in src, "teeth: could not locate the fail-closed block (fixture stale)"
open(sys.argv[2],"w").write(src.replace(needle, repl))
PY
if [ ! -f "$MUT" ]; then
  fail "E: could not build the fail-open mutant (fixture stale)"
else
  MUTOUT="$TMP/mut.txt"
  printf 'Jane Doe secret' | python3 "$MUT" encode --map-file "$TMP/v3.json" --entities-file "$TMP/NOPE.txt" >"$MUTOUT" 2>/dev/null
  if grep -q 'Jane Doe secret' "$MUTOUT"; then
    pass "E: teeth — fail-open mutant leaks raw input (guard is real code)"
  else
    fail "E: teeth — mutant did NOT leak; the test can't prove the guard has teeth"
  fi
fi

echo ""
if [ "$fails" -eq 0 ]; then
  echo "Gate 127 PASS — pseudonymize.py invariants hold (fail-closed, no-egress, FM7/FM8, teeth)."
  exit 0
else
  echo "Gate 127 FAIL — $fails check(s) failed."
  exit 1
fi
