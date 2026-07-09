#!/usr/bin/env bash
# nudge-dataverse-preflight.sh
# PreToolUse(Bash) ADVISORY nudge. When a Bash command looks like a Dataverse Web API
# CREATE or UPDATE (a POST/PATCH to an entity-set under /api/data/vX.Y/), it reminds you to
# run the `dataverse-payload-preflight` skill FIRST — which validates every field against live
# metadata in ONE pass (nonexistent columns, option-set values, lookup binds, required fields,
# owner) instead of the fix-one-field-and-re-fire loop the Contoso retro (2026-06-24) suffered.
#
# OPT-IN: no-op unless the project has a .ravenclaude/comfort-posture.yaml (a single stat; zero
# cost for non-adopters). ADVISORY: exits 0 ALWAYS — it never blocks the command. FAIL-SAFE: any
# error / missing jq / non-Bash / non-matching command -> exit 0 silently. It cannot tell whether
# you already ran the preflight; it only nudges on the create/update shape (honest limit).

set -uo pipefail

# Read the PreToolUse stdin payload ({tool_name, tool_input:{command}, ...}); degrade if absent.
payload="$(cat 2>/dev/null || true)"
[ -z "$payload" ] && exit 0

cmd=""
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty' 2>/dev/null || true)"
fi
[ -z "$cmd" ] && exit 0

# OPT-IN: bounded walk-up for a comfort-posture (else no-op).
posture=0
dir="$PWD"
for _ in 1 2 3 4 5 6 7 8 9 10; do
  [ -z "$dir" ] && break
  [ -f "$dir/.ravenclaude/comfort-posture.yaml" ] && { posture=1; break; }
  [ "$dir" = "/" ] && break
  dir="$(dirname "$dir")"
done
[ "$posture" -eq 0 ] && exit 0

# A Dataverse entity-set endpoint: /api/data/vX.Y/<entityset>
printf '%s' "$cmd" | grep -qiE '/api/data/v[0-9]+\.[0-9]+/[a-z][a-z0-9_]+' || exit 0

# A WRITE: explicit -X/--request POST|PATCH, OR a data body without an explicit read method.
# The data-flag set includes curl's --json (curl >= 7.82), which implies a POST body.
is_write=0
printf '%s' "$cmd" | grep -qiE '(-X|--request)[[:space:]]*[="'\'']?(POST|PATCH)' && is_write=1
if [ "$is_write" -eq 0 ]; then
  if printf '%s' "$cmd" | grep -qiE '(--data-raw|--data-binary|--data|--json|[[:space:]]-d)[[:space:]=]' \
     && ! printf '%s' "$cmd" | grep -qiE '(-X|--request)[[:space:]]*[="'\'']?(GET|DELETE|PUT)'; then
    is_write=1
  fi
fi
[ "$is_write" -eq 0 ] && exit 0

cat >&2 <<'EOF'

────────────────────────────────────────────────────────────────────
  ⚠  Dataverse create/update detected — pre-flight the payload FIRST.
     Run the `dataverse-payload-preflight` skill against the target entity's LIVE metadata:
       python3 plugins/power-platform/skills/dataverse-payload-preflight/preflight.py \
         --org <org-url> --entity <logical> --payload <payload.json>
     It validates EVERY field in one pass (nonexistent columns · option-set values · lookup
     binds · required fields · owner) so you don't fix-one-field-and-re-fire. (Skip if you
     already validated this exact payload.) This hook is ADVISORY — it did NOT block the command.
────────────────────────────────────────────────────────────────────

EOF
exit 0
