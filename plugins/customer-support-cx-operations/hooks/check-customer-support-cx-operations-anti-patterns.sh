#!/usr/bin/env bash
# check-customer-support-cx-operations-anti-patterns.sh — advisory PreToolUse hook for the
# customer-support-cx-operations plugin. Flags mechanically-detectable CX operations anti-patterns
# on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice to stderr);
# set CX_OPS_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text/config files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.txt | *.py | *.sh) ;;
*) exit 0 ;;
esac

findings=()

# 1. SLA target with no staffing or queue basis.
# Flag: a file that states an SLA target (e.g. "80/20", "80% within", "first response within")
# but has no reference to Erlang, agents, staffing, or queue — common in strategy docs that
# commit an SLA before modeling whether it is achievable.
if grep -nEi "\b(sla|service.level|first.response.within|[0-9]+%.{1,20}within)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(erlang|agent.?s?.needed|staffing.model|queue.model|agents.?required|cx_calc)\b" "$file" >/dev/null 2>&1; then
    findings+=("SLA target present with no staffing/queue model reference — every SLA commitment must be backed by an Erlang C model (see staff-to-the-curve-not-the-average-erlang rule and scripts/cx_calc.py).")
  fi
fi

# 2. CSAT and CES conflation — combined into one index or described as equivalent.
# Catches patterns like "CSAT/CES score", "combined CSAT and CES", "CSAT and CES average".
if grep -nEi "(csat.{0,5}/.{0,5}ces|ces.{0,5}/.{0,5}csat|combined.{0,20}(csat|ces)|(csat|ces).{0,20}combined|average.{0,20}(csat|ces)|(csat|ces).{0,20}average)" "$file" >/dev/null 2>&1; then
  findings+=("CSAT and CES appear to be combined or used interchangeably — they measure different things (outcome satisfaction vs interaction effort). Report separately (see csat-and-ces-measure-different-things rule).")
fi

# 3. Macro with PII pattern — a hardcoded customer-specific value without a merge-field placeholder.
# Detect obvious PII shapes inside files that look like macro/template definitions.
# Only fire on files matching macro-like naming or under support-conventional paths.
case "$file" in
*macro* | *canned* | *template* | *response*)
  # SSN-shaped pattern
  if grep -nE "\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b" "$file" >/dev/null 2>&1; then
    findings+=("SSN-shaped value in a macro/template file — check for hardcoded customer PII. Use merge-field placeholders (e.g., {{customer_name}}) instead of literal values.")
  fi
  # Full credit card pattern (simplified)
  if grep -nE "\b[0-9]{4}[- ][0-9]{4}[- ][0-9]{4}[- ][0-9]{4}\b" "$file" >/dev/null 2>&1; then
    findings+=("Payment-card-shaped value in a macro/template file — check for hardcoded PII. Remove or replace with a merge-field placeholder.")
  fi
  # Unconditional wall language
  if grep -nEi "we (cannot|can't|are unable to) help (with|you)" "$file" >/dev/null 2>&1; then
    findings+=("Unconditional 'we cannot help' wall language in a macro/template — deflect with answers, not walls (see deflect-with-answers-not-walls rule). Add a resolution path or a specific escalation route.")
  fi
  ;;
esac

# 4. AI-deflection flow with no human-handoff path.
# Flag: a file describing a bot or AI deflection flow that doesn't mention handoff, escalation,
# or a human-routing step.
if grep -nEi "\b(bot|ai.agent|deflect|chatbot|virtual.agent|automated.response)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "\b(hand.?off|escalat|human.agent|transfer|route.to.human|talk.to.a.person|live.agent)\b" "$file" >/dev/null 2>&1; then
    findings+=("AI/bot deflection described with no handoff or escalation path — AI deflection must know when to hand off (see ai-deflection-must-know-when-to-hand-off rule). Add trigger criteria and a routing target for must-escalate and low-confidence intents.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── customer-support-cx-operations advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${CX_OPS_STRICT:-0}" = "1" ]; then
  echo "(blocking: CX_OPS_STRICT=1)" >&2
  exit 2
fi
exit 0
