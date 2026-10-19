#!/usr/bin/env bash
# test-guard-delete-method.sh — regression table for guard-destructive.sh's
# _seg_has_delete_method (the HTTP DELETE detector behind
# `destructive-delete-api-call`).
#
# hooks-8 (2026-10-19): this detector had NO regression test, so its rounds
# 11-16 hardening (Bugbot / Cursor Security Agent) was protected by nothing.
# The deny table below pins every one of those shapes; it must pass on the code
# as it was BEFORE any narrowing and after it.
#
# Dangerous words are assembled at run time — the live guards scan this file's
# own text.
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-guard-delete-method.sh

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

HOOK="$REPO_ROOT/plugins/ravenclaude-core/hooks/guard-destructive.sh"
PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

# Fixtures deny on purpose; keep their events out of the calling session.
_gd() {
  GD_RC=0
  printf '%s' "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":$(printf '%s' "$1" | jq -Rs .)}}" \
    | env -u CLAUDE_PROJECT_DIR -u CLAUDE_SESSION_ID bash "$HOOK" >/dev/null 2>&1 || GD_RC=$?
}

C="cu""rl"
D="DEL""ETE"
U="https://api.example.com/v1/items/1"

echo
echo "── rounds 11-16: every DELETE-method spelling denies ───────────────────────"
deny=(
  "$C -X $D $U"
  "$C $U -X$D|cat"
  "$C $U --request $D|cat"
  "gh api repos/o/r/git/refs/heads/x --method=$D|cat"
  "gh api repos/o/r -X=$D"
  "$C -X \$M $U"
  "\$CLIENT -X $D $U"
  "printf $D | xargs $C $U -X"
  "gh api -X delete repos/o/r/hooks/1"
  "$C -X\$(printf $D) $U"
  "$C --method \$M $U"
  "xargs -I{} $C -X{} $U"
  "$C -X \$1 $U"
  # a literal DELETE method is never suppressed, whatever the command word
  "mvn -X $D"
  "ls -X $D"
  "java -X $D"
  # command runners are never exempt
  "ssh host $C -X $D $U"
  "ssh -X host $C -X $D $U"
  "ssh -X \$HOST"
  "sudo $C -X $D $U"
  "env $C -X $D $U"
  "nohup $C -X $D $U &"
  "sh -c '$C -X $D $U'"
  "python3 -c 'import os; os.system(\"$C -X $D $U\")'"
  # an exempt word in an EARLIER pipe stage does not exempt a later one
  "ls | xargs $C $U -X"
  "ls -X | xargs $C $U -X"
  "mvn -X clean | xargs $C $U -X"
  "echo x > m; ls m | xargs $C $U -X"
  "(ls; $C -X $D $U)"
  # a bare trailing -X glued to a closer / redirect is still a bare -X
  "(printf $D | xargs $C $U -X)"
  "x=\$(printf $D | xargs $C $U -X)"
  "printf $D | xargs $C $U -X>/dev/null"
  "($C -X \$M $U)"
  "java -Xmx1g -jar a.jar; $C -X \$M $U"
)
for c in "${deny[@]}"; do
  _gd "$c"
  if [ "$GD_RC" -eq 2 ]; then pass "deny: $c"; else fail "deny expected 2, got $GD_RC: $c"; fi
done

# Teeth: with the detector call removed, the table's plainest case must pass —
# proving the denies above come from _seg_has_delete_method and not elsewhere.
_mutant_rc() { # $1=python-old $2=python-new $3=command -> sets GD_RC (99 if no anchor)
  local mut save
  mut="$(mktemp)"
  if ! python3 - "$HOOK" "$mut" "$1" "$2" <<'PY'
import sys
from pathlib import Path
src = Path(sys.argv[1]).read_text()
if sys.argv[3] not in src:
    sys.exit(2)
Path(sys.argv[2]).write_text(src.replace(sys.argv[3], sys.argv[4]))
PY
  then
    GD_RC=99
    rm -f "$mut"
    return
  fi
  save="$HOOK"; HOOK="$mut"
  _gd "$3"
  HOOK="$save"
  rm -f "$mut"
}
_mutant_rc '_seg_has_delete_method "$seg" && return 0' ':' "$C -X $D $U"
if [ "$GD_RC" -eq 0 ]; then
  pass "teeth: without the detector the plainest DELETE is allowed (the table measures it)"
else
  fail "teeth: detector-removed mutant gave rc $GD_RC (expected 0)"
fi

echo
echo "── hooks-8: -X on tools where it is not an HTTP method is allowed ──────────"
XF="-""X"
allow=(
  "mvn $XF clean"
  "mvn clean install $XF"
  "./mvnw $XF package"
  "gradle build $XF"
  "./gradlew $XF test"
  "ls $XF"
  "ls -l$XF"
  "java $XF"
  "java ${XF}mx\$HEAP -jar app.jar"
  "java ${XF}ss\$STACK -cp . Main"
  "sort $XF file.txt"
  "sort $XF \$M"
  "mvn $XF \$GOALS"
  "(ls $XF)"
  "(mvn $XF clean)"
  "x=\$(ls $XF)"
  "ls $XF | head"
)
for c in "${allow[@]}"; do
  _gd "$c"
  if [ "$GD_RC" -eq 0 ]; then pass "allow: $c"; else fail "allow expected 0, got $GD_RC: $c"; fi
done
_mutant_rc '_DELETE_X_EXEMPT=" mvn mvnw gradle gradlew ls java sort "' '_DELETE_X_EXEMPT=" "' \
  "mvn clean install $XF"
if [ "$GD_RC" -eq 2 ]; then
  pass "teeth: with an empty exemption list the trailing mvn -X is denied again"
else
  fail "teeth: empty-exemption mutant gave rc $GD_RC (expected 2)"
fi

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
