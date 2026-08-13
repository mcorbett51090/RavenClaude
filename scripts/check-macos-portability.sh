#!/usr/bin/env bash
# check-macos-portability.sh — prove RavenClaude's hooks actually RUN on a stock macOS
# toolchain. Runs on `macos-latest` in CI (validate-macos.yml) and on any mac locally.
#
# WHY THIS EXISTS (all three were shipped, green, and broken for months):
#   door 1  bash 3.2      `shopt -s globstar` -> exit 1 -> enforce-layout silently
#                         no-opped every macOS session; the layout gate was bypassed.
#   door 2  no `timeout`  coreutils is absent -> exit 127 -> route-decision-review's
#                         engine was never consulted; every routed yes/no auto-allowed.
#   door 3  BSD grep      no `-P` -> exit 2 -> reads as NO MATCH inside `if grep -Pzi`;
#                         12 anti-pattern hooks silently never fired.
#
# WHY A RUNNER AND NOT A LINTER: none of the three is bash *syntax*. `bash -n` cannot see
# them (valid syntax, runtime failure, conditional code paths), and a static linter is
# type-blind by construction (`${!assoc[@]}` and `${!indexed[@]}` are textually identical)
# AND cannot see doors 2-3 at all — they are an ABSENT BINARY and a FLAG difference, not
# bash constructs. Only executing the hooks under the stock toolchain catches this class.
#
# WHY CI IS NOT ENOUGH ON LINUX: ubuntu has bash 5 + coreutils + GNU grep, so all three
# doors are green there. The Linux gates were passing the entire time they were broken.
#
# Bidirectional: each door has a positive test AND a must-fail half that re-introduces the
# original defect and asserts we catch it. A gate that cannot fail is not a gate.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORE="$ROOT/plugins/ravenclaude-core"
STOCK=(env -i "PATH=/usr/bin:/bin" "HOME=$HOME")   # stock userland ONLY — no homebrew
pass=0; fail=0
ok()   { printf "  \033[32m✓\033[0m %s\n" "$1"; pass=$((pass+1)); }
bad()  { printf "  \033[31m✗\033[0m %s\n" "$1"; fail=$((fail+1)); }

# ── Preflight: refuse to report a false green ────────────────────────────────────────
# A "pass" on a non-stock toolchain proves NOTHING — it is exactly how these doors stayed
# green in CI. If the environment is not what this gate claims to test, say so loudly.
if [ "$(uname -s)" != "Darwin" ]; then
  echo "LOUD SKIP: not Darwin (uname=$(uname -s)) — THIS IS NOT A PASS."
  echo "  This gate only has teeth on macOS. On Linux every door is green regardless,"
  echo "  which is precisely why all three shipped. In CI this must run on macos-latest."
  exit 0
fi

echo "── Preflight: is this actually a STOCK macOS toolchain? ──"
bv="$(/bin/bash --version | head -1)"
case "$bv" in
  *"version 3."*) ok "/bin/bash is 3.x  ($(printf '%s' "$bv" | sed 's/.*version \([0-9.]*\).*/\1/'))" ;;
  *) bad "/bin/bash is NOT 3.x — the runner image changed: $bv"
     echo "     This gate asserts the stock-mac baseline. If Apple/GitHub ever ship bash>=4,"
     echo "     this gate stops testing what it claims to and MUST be re-grounded, not muted." ;;
esac
"${STOCK[@]}" /bin/bash -c 'command -v timeout >/dev/null 2>&1' \
  && bad "coreutils 'timeout' is PRESENT under stock PATH — not a stock mac; door 2 untested" \
  || ok "coreutils 'timeout' absent under stock PATH (door 2's precondition)"
printf 'x' | /usr/bin/grep -P 'x' >/dev/null 2>&1 \
  && bad "/usr/bin/grep HAS -P — not BSD grep; door 3 untested" \
  || ok "/usr/bin/grep lacks -P (door 3's precondition)"

TD="$(mktemp -d)"; trap 'rm -rf "$TD"' EXIT

# ── Door 1: enforce-layout must RUN and ENFORCE under bash 3.2 ───────────────────────
echo
echo "── Door 1: bash 3.2 — the layout gate ──"
_layout() { # $1=path -> exit code
  printf '{"tool_name":"Write","tool_input":{"file_path":"%s","content":"x"}}' "$1" \
    | "${STOCK[@]}" "CLAUDE_PROJECT_DIR=$ROOT" /bin/bash "$CORE/hooks/enforce-layout.sh" >/dev/null 2>&1
  echo $?
}
[ "$(_layout "$ROOT/plugins/ravenclaude-core/skills/forge-pipeline/SKILL.md")" = "0" ] \
  && ok "in-pattern write -> allow (0)" || bad "in-pattern write did NOT allow"
[ "$(_layout "$ROOT/totally/off/pattern.txt")" = "2" ] \
  && ok "off-pattern write -> DENY (2) — the gate is armed" \
  || bad "off-pattern write did not deny with 2 (exit 1 = the hook crashed = silent fail-open)"

# must-fail: re-introduce globstar and prove the gate catches it
mut="$TD/enforce-layout.mut.sh"
sed 's/^shopt -s extglob nullglob$/shopt -s extglob globstar nullglob/' "$CORE/hooks/enforce-layout.sh" > "$mut"
if ! cmp -s "$mut" "$CORE/hooks/enforce-layout.sh"; then
  rc="$(printf '{"tool_name":"Write","tool_input":{"file_path":"%s","content":"x"}}' "$ROOT/totally/off/pattern.txt" \
        | "${STOCK[@]}" "CLAUDE_PROJECT_DIR=$ROOT" /bin/bash "$mut" >/dev/null 2>&1; echo $?)"
  [ "$rc" != "2" ] && ok "TEETH: re-adding globstar breaks the gate (exit $rc, not 2)" \
                   || bad "TEETH FAILED: globstar re-added but the hook still denied — this test cannot fail"
else
  bad "TEETH: could not build the mutant (the shopt line moved — re-ground this test)"
fi

# ── Door 2: _rc_timeout must bound a command with NO coreutils ───────────────────────
echo
echo "── Door 2: absent \`timeout\` ──"
t0=$(date +%s)
"${STOCK[@]}" /bin/bash -c ". '$CORE/hooks/_portable.sh'; _rc_timeout 1 sleep 10" >/dev/null 2>&1
el=$(( $(date +%s) - t0 ))
[ "$el" -lt 5 ] && ok "_rc_timeout 1 sleep 10 returned in ${el}s (ceiling held with no coreutils)" \
                || bad "_rc_timeout did NOT bound the command (${el}s) — the shim is not working"
[ "$("${STOCK[@]}" /bin/bash -c ". '$CORE/hooks/_portable.sh'; _rc_timeout 5 echo ok" 2>/dev/null)" = "ok" ] \
  && ok "_rc_timeout passes a fast command through" || bad "_rc_timeout broke a fast command"
[ "$("${STOCK[@]}" /bin/bash -c ". '$CORE/hooks/_portable.sh'; _rc_upper yes" 2>/dev/null)" = "YES" ] \
  && ok "_rc_upper yes -> YES (\${v^^} is bash 4.0)" || bad "_rc_upper failed"

# the door-2 defect in situ: bare `timeout` yields EMPTY, which the caller reads as "allow"
out="$("${STOCK[@]}" /bin/bash -c 'printf x | timeout 80 cat 2>/dev/null || echo ""')"
[ -z "$out" ] && ok "TEETH: bare \`timeout\` yields empty (the exact silent-allow shape)" \
              || bad "TEETH FAILED: bare timeout worked — this is not a stock mac"

# ── Door 3: the anti-pattern hooks must actually FIRE ────────────────────────────────
echo
echo "── Door 3: BSD grep has no -P ──"
printf 'module "x" {\n  source = "./mod"\n}\n'                    > "$TD/bad.tf"
printf 'module "x" {\n  source = "./mod"\n  version = "1.0"\n}\n' > "$TD/good.tf"
_tf() {
  "${STOCK[@]}" "CLAUDE_PLUGIN_ROOT=$CORE" /bin/bash \
    "$ROOT/plugins/terraform-iac/hooks/check-terraform-iac-anti-patterns.sh" "$1" 2>&1 </dev/null
}
[ -n "$(_tf "$TD/bad.tf")" ]  && ok "terraform hook FIRES on a known-bad fixture" \
                              || bad "terraform hook is SILENT on known-bad — door 3 is open again"
[ -z "$(_tf "$TD/good.tf")" ] && ok "terraform hook is silent on a known-good fixture" \
                              || bad "terraform hook fires on known-good (false positive, or the skipped-advisory is back)"
# must-fail: the pre-fix grep -Pzi form must be silent on the bad fixture
"${STOCK[@]}" /bin/bash -c \
  'if grep -Pzi "source\s*=\s*\"[^\"]+\"(?![\s\S]{0,80}version\s*=)" "'"$TD/bad.tf"'" >/dev/null 2>&1; then exit 0; fi; exit 1' \
  && bad "TEETH FAILED: grep -Pzi matched on this host — not BSD grep" \
  || ok "TEETH: the old grep -Pzi form reads as NO MATCH here (the original silent bug)"
# _rc_pcre_match's empty-file edge (a naive -0777 shim exits 0 = 'match')
: > "$TD/empty.tf"
"${STOCK[@]}" /bin/bash -c ". '$CORE/hooks/_portable.sh'; _rc_pcre_match '$TD/empty.tf' 'source\s*='" \
  && bad "empty file reported a MATCH — the BEGIN/END guard regressed" \
  || ok "empty file -> no-match (the BEGIN/END guard holds)"

echo
echo "──────────────────────────────────────────────"
printf "  macOS portability: %d passed, %d failed\n" "$pass" "$fail"
[ "$fail" -eq 0 ] || { echo "  A stock-macOS door is OPEN. Do not claim macOS support."; exit 1; }
echo "  All doors closed on a stock macOS toolchain."
