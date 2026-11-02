#!/usr/bin/env bash
# test-guard-heredoc-interpreter.sh — a heredoc whose body is EXECUTED by an
# interpreter must be scanned, not blanked as inert data.
#
# 2026-10-18: the interpreter check looked only at the simple command's FIRST word,
# so an interpreter behind a wrapper (sudo/doas/nohup/timeout/exec/nice) or a heredoc
# piped into one on its opening line (`cat <<'EOF' | bash`) was blanked and every
# deny pattern inside the body was skipped.
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-guard-heredoc-interpreter.sh

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

HOOK="$REPO_ROOT/plugins/ravenclaude-core/hooks/guard-destructive.sh"
PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

_gd() {
  GD_RC=0
  printf '%s' "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":$(printf '%s' "$1" | jq -Rs .)}}" \
    | bash "$HOOK" >/dev/null 2>&1 || GD_RC=$?
}

# Payload assembled at run time so a parent hook scanning this file sees data.
RM="rm"" -rf"
NL=$'\n'
body="${RM} /${NL}EOF"

echo
echo "── heredoc into an interpreter through a wrapper or a pipe: DENY ─────────"
deny=(
  "sudo bash <<'EOF'${NL}${body}"
  "sudo -u root bash <<'EOF'${NL}${body}"
  "doas sh <<'EOF'${NL}${body}"
  "nohup bash <<'EOF'${NL}${body}"
  "timeout 5 bash <<'EOF'${NL}${body}"
  "exec bash <<'EOF'${NL}${body}"
  "nice -n 10 sh <<EOF${NL}${body}"
  "cat <<'EOF' | bash${NL}${body}"
  "cat <<'EOF' | sudo sh -s${NL}${body}"
  "cat <<\"EOF\" |& bash${NL}${body}"
  "cat <<'EOF' | /bin/bash -s --${NL}${body}"
  "cat <<'EOF' | python3${NL}import os; os.system('${RM} /')${NL}EOF"
  # regression: the forms that were already caught stay caught
  "bash <<'EOF'${NL}${body}"
  "env FOO=1 bash <<'EOF'${NL}${body}"
)
for c in "${deny[@]}"; do
  _gd "$c"
  if [ "$GD_RC" -eq 2 ]; then pass "deny: ${c%%$NL*}"; else fail "deny expected 2, got $GD_RC: ${c%%$NL*}"; fi
done

echo
echo "── heredoc that is only data stays blanked: ALLOW ─────────────────────────"
allow=(
  "cat <<'EOF' > notes.md${NL}${body}"
  "cat <<'EOF' | grep rf${NL}${body}"
  "git commit -F - <<'EOF'${NL}docs: explain why ${RM} / is denied${NL}EOF"
  "cat <<'EOF' | wc -l${NL}${body}"
)
for c in "${allow[@]}"; do
  _gd "$c"
  if [ "$GD_RC" -eq 0 ]; then pass "allow: ${c%%$NL*}"; else fail "allow expected 0, got $GD_RC: ${c%%$NL*}"; fi
done

echo
echo "── mutation: reverting the fix makes the wrapper/pipe cases pass again ────"
MUT="$(mktemp)"
python3 - "$HOOK" "$MUT" <<'PY'
import sys
src = open(sys.argv[1]).read()
anchor = "def _heredoc_feeds_interpreter(prefix, opening=\"\"):\n"
assert anchor in src
src = src.replace(anchor, anchor + "    return bool(_INTERP_BASE.match((re.split(r\"[\\n;&|(]\", prefix)[-1].split() or [''])[0].rsplit('/', 1)[-1]))\n", 1)
open(sys.argv[2], "w").write(src)
PY
GD_RC=0
printf '%s' "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":$(printf '%s' "sudo bash <<'EOF'${NL}${body}" | jq -Rs .)}}" \
  | bash "$MUT" >/dev/null 2>&1 || GD_RC=$?
if [ "$GD_RC" -eq 0 ]; then pass "mutant (first-word-only check) lets sudo bash <<EOF through — test can go red"; else fail "mutant still denied (rc=$GD_RC): test is not sensitive"; fi
rm -f "$MUT"

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
