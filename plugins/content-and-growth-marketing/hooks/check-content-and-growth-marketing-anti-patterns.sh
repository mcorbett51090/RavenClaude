#!/usr/bin/env bash
# check-content-and-growth-marketing-anti-patterns.sh — advisory PreToolUse hook for the content-and-growth-marketing plugin.
# Flags mechanically-detectable marketing anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set MARKETING_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1. A content brief with no audience and/or no CTA — the audience-job + funnel-hook rules.
if grep -qiE "content brief|^#+\s*brief\b|target query|search intent" "$file" 2>/dev/null; then
  if ! grep -qiE "audience|job[ -]to[ -]be[ -]done|jtbd|reader" "$file" 2>/dev/null; then
    findings+=("Content brief with no audience / job-to-be-done — a piece written to a keyword but not a reader job ranks and bounces.")
  fi
  if ! grep -qiE "\bCTA\b|call[ -]to[ -]action|next action|conversion" "$file" 2>/dev/null; then
    findings+=("Content brief with no CTA / next action — content with no funnel hook is a cost center; name the reader's next step.")
  fi
fi

# 2. An email flow / nurture doc that's a blast (no segmentation/trigger) — the segment-and-trigger rule.
if grep -qiE "nurture|email flow|lifecycle (flow|email)|drip|broadcast|email blast|newsletter" "$file" 2>/dev/null; then
  if ! grep -qiE "segment|trigger|entry criteria|exit criteria|behavior" "$file" 2>/dev/null; then
    findings+=("Email/nurture flow with no segmentation or trigger — a batch-and-blast is not a flow; define the trigger, segment, and entry/exit.")
  fi
fi

# 3. Copy optimizing for a vanity metric — the measure-outcomes rule.
if grep -qiE "open rate|opens|pageviews|list size|impressions|follower count" "$file" 2>/dev/null; then
  if ! grep -qiE "conversion|engaged|inbox placement|revenue|click[ -]through|outcome|pipeline" "$file" 2>/dev/null; then
    findings+=("Optimizing for a vanity metric (opens / pageviews / list size) with no paired outcome — pair every throughput metric with conversion / engaged-list health / revenue.")
  fi
fi

# 4. A deliverability doc missing email authentication — the deliverability-is-the-foundation rule.
if grep -qiE "deliverability|sender reputation|spam folder|inbox placement|sunset policy" "$file" 2>/dev/null; then
  if ! grep -qiE "SPF|DKIM|DMARC|authentication" "$file" 2>/dev/null; then
    findings+=("Deliverability doc with no SPF/DKIM/DMARC — authentication is the foundation; copy fixes won't rescue an unauthenticated sender.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── content-and-growth-marketing advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${MARKETING_STRICT:-0}" = "1" ]; then
  echo "(blocking: MARKETING_STRICT=1)" >&2
  exit 2
fi
exit 0
