#!/usr/bin/env bash
# Gate 191: the check-workflow-hygiene.py.template ships a PASSING --self-test, AND
# that self-test genuinely tests the new advisory Rule 3 (the default-GITHUB_TOKEN
# downstream-suppression trap). stdlib-only python3; no network. bash 3.2-safe, no
# GNU-only tools (portable `sed` stream edit, never `sed -i`).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
TMPL="$ROOT/plugins/ravenclaude-core/templates/agent-ready-repo/check-workflow-hygiene.py.template"
rc=0

# ── must-pass: the shipped template's self-test is green. ──
if python3 "$TMPL" --self-test >/dev/null 2>&1; then
  echo "  ✓ check-workflow-hygiene.py.template --self-test passes"
else
  echo "  ✗ check-workflow-hygiene.py.template --self-test FAILED"
  python3 "$TMPL" --self-test || true
  rc=1
fi

# ── must-fail (teeth): neuter Rule 3 detection; the self-test MUST then fail. ──
# If a Rule-3-neutered mutant still passes, the self-test is not actually testing
# Rule 3 — the gate would be green for the wrong reason.
d="$(mktemp -d)"
mutant="$d/mutant.py"
sed 's/if push_signal and not app_pat_signal:/if False and push_signal and not app_pat_signal:/' \
  "$TMPL" >"$mutant"
if python3 "$mutant" --self-test >/dev/null 2>&1; then
  echo "  ✗ teeth: a Rule-3-neutered mutant STILL passed the self-test (no teeth)"
  rc=1
else
  echo "  ✓ teeth: a Rule-3-neutered mutant fails the self-test"
fi
rm -rf "$d"

exit "$rc"
