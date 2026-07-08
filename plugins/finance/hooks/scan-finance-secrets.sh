#!/usr/bin/env bash
# scan-finance-secrets.sh - pattern-based secret / PII shape scanner for finance files.
#
# WHY THIS EXISTS (FORGE red-team P0 follow-up)
#   Finance deliverables carry the highest-sensitivity data in the marketplace —
#   bank details, wire instructions, payroll, customer PII — and the controller
#   autopilot writes CSV/JSON/Markdown artifacts under plugins/finance/. This gate
#   is a mechanical last line of defence: it catches secret/PII *shapes* (an AWS
#   key, a PEM header, an SSN) BEFORE they land in a committed artifact. It does
#   NOT authenticate or decrypt anything; it is a shape detector, so treat a clean
#   run as "no obvious secret shape found", never as "proven secret-free".
#
# WHAT IT LOOKS FOR
#   - OAuth client secrets ( client_secret = <value> )
#   - generic api_key / password / token assignments that carry a literal VALUE
#   - PEM private-key headers ( -----BEGIN ... PRIVATE KEY----- )
#   - AWS access keys ( AKIA/ASIA + 16 )
#   - Slack tokens ( xox[baprs]-... )
#   - bearer tokens ( Bearer <token> )
#   - US SSN ( NNN-NN-NNNN )
#   - full credit-card PANs ( Visa / Mastercard / Amex / Discover )
#   - IBANs
#   All regexes are POSIX ERE (grep -E). Groups are ERE capturing groups `(...)`,
#   never PCRE non-capturing `(?:...)` (grep -E does not support `(?:...)`).
#
# MODES
#   default      ADVISORY  — print findings to stderr, ALWAYS exit 0. Safe to wire
#                            as a PostToolUse hook: it never blocks an edit.
#   --ci         GATE      — exit non-zero (1) if ANY finding survives filtering.
#                            Use in a pre-merge CI step to fail the build.
#
# ARGS
#   Any number of file or directory paths. Directories are scanned recursively.
#   With no path args the default scope is  plugins/finance/ .
#
# EXCLUSIONS (never a finding)
#   - this script, the gate's own knowledge doc + test file
#   - the sanctioned "env-var NAME only" pattern (os.environ / getenv /
#     process.env / ${VAR} / client_secret_env) — referencing a credential by
#     env-var NAME is CORRECT and must not trip the gate
#   - documented placeholders: 'ENV-VAR NAME', '<out-of-band>', example.com
#
# FAIL-SAFE
#   If grep is unavailable the scan cannot run; it warns and exits 0 (never a
#   spurious block or gate failure from a missing tool).
#
# INTENDED PostToolUse WIRING (Team Lead wires hooks.json — do NOT edit it here)
#   Add to plugins/finance/hooks/hooks.json under "PostToolUse", matcher
#   "Edit|Write|MultiEdit":
#     {
#       "type": "command",
#       "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scan-finance-secrets.sh \"$CLAUDE_TOOL_FILE_PATH\"",
#       "comment": "Advisory secret/PII shape scan on every finance edit. Non-blocking; run with --ci in CI to gate a merge."
#     }
#   See plugins/finance/knowledge/secrets-pii-gate.md for the full rationale.

set -euo pipefail

SELF="$(basename "${BASH_SOURCE[0]}")"

print_help() {
  sed -n '2,60p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

MODE="advisory"
PATHS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --ci) MODE="ci"; shift ;;
    -h|--help) print_help; exit 0 ;;
    --) shift; while [ $# -gt 0 ]; do PATHS+=("$1"); shift; done ;;
    -*) echo "scan-finance-secrets: unknown option: $1" >&2; exit 2 ;;
    *) PATHS+=("$1"); shift ;;
  esac
done

if [ ${#PATHS[@]} -eq 0 ]; then
  PATHS=("plugins/finance/")
fi

# Fail-safe: a missing grep must never spuriously block or fail a gate.
if ! command -v grep >/dev/null 2>&1; then
  echo "scan-finance-secrets: grep unavailable; skipping scan (fail-safe, exit 0)." >&2
  exit 0
fi

# Lines that reference a credential by env-var NAME (the sanctioned pattern) or a
# documented placeholder are NOT secrets — drop them before counting a finding.
PLACEHOLDER_RE='ENV-VAR NAME|<out-of-band>|client_secret_env|example\.com|os\.environ|getenv|process\.env|System\.getenv|\bENV\[|\$\{?[A-Za-z_][A-Za-z0-9_]*\}?|000-00-0000|123-45-6789|111-11-1111|078-05-1120|XXX-XX-XXXX|FAKE-[A-Z]|-FAKE\b|\bFAKE\b|obviously.fake|_synthetic'

# Parallel rule arrays: name -> POSIX-ERE pattern.
RULE_NAMES=(
  "aws-access-key"
  "pem-private-key"
  "slack-token"
  "bearer-token"
  "oauth-client-secret"
  "generic-secret-assignment"
  "us-ssn"
  "credit-card-pan"
  "iban"
)
RULE_RES=(
  "(AKIA|ASIA)[0-9A-Z]{16}"
  "-----BEGIN [A-Z ]*PRIVATE KEY-----"
  "xox[baprs]-[A-Za-z0-9-]{10,}"
  "[Bb]earer[[:space:]]+[A-Za-z0-9._~+/=-]{20,}"
  "client_secret[\"' ]*[:=][[:space:]]*[\"']?[A-Za-z0-9_.~+/=-]{8,}"
  "(api[_-]?key|apikey|api[_-]?secret|secret[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|pwd)[\"' ]*[:=][[:space:]]*[\"']?[^\"'[:space:]]{6,}"
  "\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b"
  "\b(4[0-9]{12}([0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(011|5[0-9]{2})[0-9]{12})\b"
  "\b[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\b"
)

findings=""
count=0

for i in "${!RULE_NAMES[@]}"; do
  name="${RULE_NAMES[$i]}"
  re="${RULE_RES[$i]}"
  # grep -r recursive, -I skip binary, -E ERE, -n line numbers, -H file names.
  # `|| true` so a no-match (exit 1) or a missing path never aborts under set -e.
  raw="$(grep -rIEnH \
          --exclude="$SELF" \
          --exclude="secrets-pii-gate.md" \
          --exclude="test_secrets_gate.py" \
          --exclude-dir="__pycache__" \
          --exclude-dir=".git" \
          -e "$re" -- "${PATHS[@]}" 2>/dev/null || true)"
  [ -z "$raw" ] && continue
  filtered="$(printf '%s\n' "$raw" | grep -Ev "$PLACEHOLDER_RE" || true)"
  [ -z "$filtered" ] && continue
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    findings+="  [$name] ${line:0:200}"$'\n'
    count=$((count + 1))
  done <<< "$filtered"
done

if [ "$count" -gt 0 ]; then
  {
    echo ""
    echo "──────────────────────────────────────────────────────────────────"
    echo "  scan-finance-secrets: $count potential secret/PII match(es) [$MODE]"
    echo ""
    printf '%s' "$findings"
    echo ""
    echo "  Each is a SHAPE match, not proof of a live secret. Verify every one:"
    echo "  replace any real credential with an env-var NAME reference (never a"
    echo "  value), scrub PII from example data, and rotate anything committed."
    if [ "$MODE" = "advisory" ]; then
      echo "  (advisory: NOT blocking — run with --ci to gate a merge.)"
    else
      echo "  (--ci: this run will FAIL. Remove/scrub the findings above.)"
    fi
    echo "──────────────────────────────────────────────────────────────────"
  } >&2
fi

if [ "$MODE" = "ci" ] && [ "$count" -gt 0 ]; then
  exit 1
fi
exit 0
