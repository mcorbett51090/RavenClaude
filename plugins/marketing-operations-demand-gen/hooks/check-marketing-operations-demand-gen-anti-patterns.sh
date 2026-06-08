#!/usr/bin/env bash
# check-marketing-operations-demand-gen-anti-patterns.sh — advisory PreToolUse hook for the
# marketing-operations-demand-gen plugin. Flags mechanically-detectable marketing-ops
# anti-patterns on Edit/Write/MultiEdit. Advisory by default (exit 0, prints a notice);
# set MARKETING_OPS_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect text/config files; skip binaries.
case "$file" in
*.md | *.yaml | *.yml | *.json | *.txt | *.csv) ;;
*) exit 0 ;;
esac

findings=()

# 1. Campaign with no UTM/tracking convention — a link with ? parameters but no utm_source or
#    utm_medium suggests a tracked URL with no proper UTM taxonomy applied.
if grep -nEi "https?://[^\"' >]+\?[^\"' >]+" "$file" >/dev/null 2>&1 && \
   ! grep -nEi "utm_source=" "$file" >/dev/null 2>&1; then
  findings+=("URL with query parameters found but no utm_source detected — every external campaign link needs utm_source, utm_medium, and utm_campaign per the UTM taxonomy. See templates/utm-taxonomy.md.")
fi

# 2. Attribution claim stated as truth with no model named — "contributed X% of pipeline" or
#    "attribution shows" without identifying which model.
if grep -nEi "(contributed|drove|generated|attributed).{0,60}(pipeline|revenue|deals)" "$file" >/dev/null 2>&1 && \
   ! grep -nEi "(first.touch|last.touch|linear|u.shaped|w.shaped|time.decay|data.driven|attribution model)" "$file" >/dev/null 2>&1; then
  findings+=("Attribution claim (contributed/drove/generated pipeline) without a named model — every attribution report must state the model used (first-touch, last-touch, linear, U-shaped, W-shaped, data-driven). See best-practices/attribution-is-a-model-not-the-truth.md.")
fi

# 3. Hard-coded conversion rate or CAC figure with no date — numeric % used as a benchmark
#    without a verify-at-use or retrieval date marker.
if grep -nEi "(conversion.rate|cac|cost.per.mql|cost.per.sql|mql.to.sql|sql.to.opp|pipeline.to.spend).{0,40}[0-9]+[%x]?" "$file" >/dev/null 2>&1 && \
   ! grep -nEi "(verify.at.use|\[verify\]|retrieved|as of [0-9]{4}|[0-9]{4}-[0-9]{2})" "$file" >/dev/null 2>&1; then
  findings+=("Hard-coded conversion rate, CAC, or benchmark figure without a retrieval date or [verify-at-use] marker — benchmark figures age quickly. Mark them with a date or [verify-at-use] so consumers know to re-confirm.")
fi

# 4. Email send with no consent/suppression note — a file that describes an email send or
#    sequence without mentioning consent, opt-in, unsubscribe, or suppression.
if grep -nEi "(email.send|send.email|email.sequence|nurture.email|bulk.email|email.campaign)" "$file" >/dev/null 2>&1 && \
   ! grep -nEi "(consent|opt.in|unsubscribe|suppression|can.spam|gdpr|casl)" "$file" >/dev/null 2>&1; then
  findings+=("Email send or sequence described without a consent/suppression note — every email send design must confirm opt-in status, honor unsubscribes, and apply suppression lists. See best-practices/nurture-the-not-yet-ready-dont-spam-them.md.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── marketing-operations-demand-gen advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${MARKETING_OPS_STRICT:-0}" = "1" ]; then
  echo "(blocking: MARKETING_OPS_STRICT=1)" >&2
  exit 2
fi
exit 0
