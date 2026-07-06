#!/usr/bin/env bash
# flag-dfir-hygiene-smells.sh
# PreToolUse hook for Edit | Write | MultiEdit on DFIR / incident-response files.
# Flags two mechanically-detectable violations of the incident-response-dfir
# team constitution (see plugins/incident-response-dfir/CLAUDE.md and the
# best-practices/ rules):
#
#   1. An incident report / post-mortem that names an individual as AT-FAULT —
#      blame/fault/incompetent wording. Post-mortems are blameless: root-cause
#      the system, not a person (best-practices/... the post-mortem is blameless).
#   2. A runbook / IR-plan / incident file that mentions a destructive
#      remediation ("power off" / "shut down" / "reimage" / "wipe") with NO
#      nearby mention of "memory" / "acquisition" / "evidence" / "volatility" /
#      "chain of custody" — you must preserve volatile evidence before you
#      remediate (best-practices/preserve-evidence-before-you-remediate.md).
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set DFIR_STRICT=1 to make
# violations blocking (exit 2).
#
# Patterns use POSIX ERE only (grep -E / -iE) — no PCRE constructs (no \d, no
# lookaheads) — per the check-grep-ere-pcre.py CI gate.
#
# Claude Code PreToolUse: exit 2 = BLOCK the tool call with stderr surfaced to
# the agent. exit 1 = non-blocking error (silently swallowed).

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base=$(basename "$file")
base_lc=$(printf '%s' "$base" | tr '[:upper:]' '[:lower:]')

# Only reason about markdown/text files — skip binaries, images, etc.
case "$base_lc" in
  *.md | *.markdown | *.txt) ;;
  *) exit 0 ;;
esac

warnings=()

# --- Check 1: blameless-postmortem violation ---
# Fires only on incident-report / post-mortem / post-incident named files.
is_postmortem=0
case "$base_lc" in
  *postmortem* | *post-mortem* | *post-incident* | *incident-report* | *incident_report*)
    is_postmortem=1
    ;;
esac
if [[ "$is_postmortem" -eq 1 ]]; then
  if grep -iqE '(fault of|at fault|to blame|blame the|blamed|incompetent|negligent|should have known)' "$file"; then
    warnings+=("incident report/post-mortem names an individual as at-fault (blame/fault/incompetent wording) — post-mortems are BLAMELESS: root-cause the system and process, not a person (templates/incident-report-postmortem.md).")
  fi
fi

# --- Check 2: preserve-evidence violation ---
# Fires on runbook / IR-plan / incident files that mention a destructive
# remediation but no evidence-preservation nearby.
is_ir_doc=0
case "$base_lc" in
  *runbook* | *incident* | *ir-plan* | *ir_plan* | *response-plan* | *playbook*)
    is_ir_doc=1
    ;;
esac
if [[ "$is_ir_doc" -eq 1 ]]; then
  if grep -iqE '(power[ -]?off|shut[ -]?down|reimage|re-image|wipe the disk|wipe and)' "$file"; then
    if ! grep -iqE '(memory|acquisition|acquire|evidence|volatilit|chain of custody|forensic)' "$file"; then
      warnings+=("file mentions a destructive remediation (power off / shut down / reimage / wipe) with no mention of memory/acquisition/evidence/volatility — capture volatile evidence BEFORE you remediate (best-practices/preserve-evidence-before-you-remediate.md).")
    fi
  fi
fi

if [[ ${#warnings[@]} -eq 0 ]]; then
  exit 0
fi

{
  echo "incident-response-dfir — advisory hygiene check flagged $file:"
  for w in "${warnings[@]}"; do
    echo "  • $w"
  done
} >&2

if [[ "${DFIR_STRICT:-0}" == "1" ]]; then
  exit 2
fi
exit 0
