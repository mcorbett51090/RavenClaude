#!/usr/bin/env bash
# Gate 225 — the read-only discriminator on xc.tribunal-self-disable.
#
# WHY THIS GATE EXISTS. The self-disable screen is pre-LLM, non-overridable and
# category-independent — the security floor. It was also denying ordinary
# maintenance, because it matched any command that merely NAMED the substrate.
# Measured 2026-08-18: seven legitimate operations denied in one session,
# including a read-only search whose SEARCH PATTERN contained `command_review:`,
# a stage-and-commit whose COMMIT MESSAGE described the denial, and a file whose
# NAME happened to contain a mutating verb. The guard's printed remedy ("turn
# the Thing off in the dashboard") was already applied and does not help, since
# always_screen runs before the enabled gate. A guardrail whose only exit is
# unreachable gets tunnelled rather than respected.
#
# THE CONTRACT THIS PINS, and it is bidirectional:
#   1. A provably-non-writing command is NOT screened as a self-disable.
#   2. Every genuine shell mutation of the substrate STILL denies.
#   3. Anything ambiguous (metacharacter, redirect, substitution, write flag,
#      an interpreter first token) falls back to DENY — fail-closed.
#
# ⛔ Run with --must-fail-meta to prove assertion 3 has teeth: with the
# metacharacter guard neutered, a read CHAINED to a mutation must slip through.
# Without that half, a discriminator that always returned True would pass every
# other assertion in this file.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
CONC="${REPO_ROOT}/plugins/ravenclaude-core/scripts/thing-concerns.py"
MUST_FAIL_META=0
[ "${1:-}" = "--must-fail-meta" ] && MUST_FAIL_META=1

fails=0
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

target="$CONC"
if [ "$MUST_FAIL_META" -eq 1 ]; then
  # Neuter ONLY the metacharacter conjunct — the narrowest possible mutation, so
  # a pass can only come from that conjunct being load-bearing.
  mkdir -p "$tmpdir/scripts"
  sed 's/^    if _RO_META\.search(stripped):$/    if False:/' "$CONC" > "$tmpdir/scripts/thing-concerns.py"
  ln -sfn "${REPO_ROOT}/plugins/ravenclaude-core/knowledge" "$tmpdir/knowledge"
  target="$tmpdir/scripts/thing-concerns.py"
fi

verdict() {
  python3 "$target" screen-always "$1" 2>/dev/null \
    | python3 -c 'import json,sys
try:
    print("DENY" if json.load(sys.stdin)["self_disable_deny"] else "ALLOW")
except Exception:
    print("ERROR")' 2>/dev/null
}

check() {
  local want="$1" desc="$2" cmd="$3" got
  got="$(verdict "$cmd")"
  [ -z "$got" ] && got="ERROR"
  if [ "$got" = "$want" ]; then
    printf '  ✓ %-5s %s\n' "$got" "$desc"
  else
    printf '  ✗ want=%s got=%s  %s\n' "$want" "$got" "$desc"
    fails=$((fails + 1))
  fi
}

if [ "$MUST_FAIL_META" -eq 1 ]; then
  echo "── must-fail half: metacharacter conjunct neutered ──"
  # With the conjunct gone this MUST slip through; the gate fails if it still denies.
  got="$(verdict 'grep x plugins/ravenclaude-core/hooks/a.sh && rm -rf plugins/ravenclaude-core/hooks')"
  if [ "$got" = "DENY" ]; then
    echo "  ✗ MUST-FAIL DID NOT FAIL — the metacharacter conjunct is not load-bearing."
    echo "Gate 225 FAIL — teeth not proven."
    exit 1
  fi
  echo "  ✓ chained mutation slipped through (got=$got) — the conjunct is load-bearing."
  echo "Gate 225 PASS (must-fail half) — the metacharacter guard is doing real work."
  exit 0
fi

echo "── the floor must NOT weaken: genuine substrate mutations still deny ──"
check DENY  "recursive remove of the hooks directory"   'rm -rf plugins/ravenclaude-core/hooks'
check DENY  "in-place stream edit of the orchestrator"  "sed -i 's/a/b/' plugins/ravenclaude-core/scripts/thing-orchestrator.sh"
check DENY  "move a hook out of place"                  'mv plugins/ravenclaude-core/hooks/guard-x.sh /tmp/'
check DENY  "overwrite the orchestrator"                'cp /tmp/x.sh plugins/ravenclaude-core/hooks/thing-orchestrator.sh'
check DENY  "redirect into a substrate path"            'echo x > plugins/ravenclaude-core/scripts/thing-decision.py'
check DENY  "a read CHAINED to a mutation"              'grep x plugins/ravenclaude-core/hooks/a.sh && rm plugins/ravenclaude-core/hooks/a.sh'
check DENY  "a read PIPED into a writer"                'cat plugins/ravenclaude-core/hooks/a.sh | tee plugins/ravenclaude-core/hooks/b.sh'
check DENY  "command substitution smuggling a write"    'cat $(rm plugins/ravenclaude-core/hooks/a.sh)'
check DENY  "writing the off-toggle into the posture"   'printf "thing: off" > .ravenclaude/comfort-posture.yaml'

echo
echo "── maintenance must NOT be blocked: provably-non-writing commands pass ──"
check ALLOW "read-only search of the posture file"      "grep -nE 'command_review:|enabled:' .ravenclaude/comfort-posture.yaml"
check ALLOW "read a substrate file"                     'cat plugins/ravenclaude-core/scripts/thing-orchestrator.sh'
check ALLOW "git show a substrate blob"                 'git show origin/main:plugins/ravenclaude-core/hooks/hooks.json'
check ALLOW "git log over the scripts directory"        'git log --oneline plugins/ravenclaude-core/scripts/'
check ALLOW "a search whose PATTERN names a verb"       "grep -n 'rm -rf' plugins/ravenclaude-core/hooks/hooks.json"
check ALLOW "line-count a substrate file"               'wc -l plugins/ravenclaude-core/scripts/thing-concerns.py'

echo
if [ "$fails" -eq 0 ]; then
  echo "Gate 225 PASS — the self-disable floor is intact for every shell mutation, and provably-non-writing maintenance is no longer denied."
  exit 0
fi
echo "Gate 225 FAIL — $fails assertion(s) failed."
exit 1
