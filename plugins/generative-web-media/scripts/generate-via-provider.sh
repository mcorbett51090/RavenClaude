#!/usr/bin/env bash
# generate-via-provider.sh — direct-provider generation fallback (off the fal MCP).
#
# The fal hosted MCP is the primary substrate (declared in plugin.json). This thin
# curl path lets the PREFERRED provider — notably Grok/xAI on api.x.ai/v1 — be reached
# directly, so it is not gated behind fal adoption. It is a FALLBACK and a smoke-test,
# not the main generation loop.
#
# PROBE-AND-DEGRADE: it LOUD-SKIPs (never a silent pass) if curl or the provider key
# env-var is absent, printing exactly what to set. Secrets are read from the
# environment by NAME (FAL_KEY / XAI_API_KEY) — never written to the repo.
#
# Usage:
#   XAI_API_KEY=… scripts/generate-via-provider.sh --provider xai   --prompt "…" [--model grok-2-image] [--out asset.png]
#   FAL_KEY=…     scripts/generate-via-provider.sh --provider fal   --model fal-ai/flux/schnell --prompt "…"
#   scripts/generate-via-provider.sh --check           # probe env + curl, print readiness, exit
set -euo pipefail

PROVIDER=""
PROMPT=""
MODEL=""
OUT=""
CHECK=0

loud_skip() {
  # A LOUD-SKIP is NOT a pass. Print to stderr and exit non-zero.
  printf '\n[generate-via-provider] LOUD-SKIP — THIS IS NOT A PASS.\n%s\n\n' "$1" >&2
  exit 3
}

usage() {
  cat <<'EOF'
generate-via-provider.sh — direct-provider generation fallback (off fal)

  --provider xai|fal   which provider (required unless --check)
  --prompt "<text>"    the generation prompt (required unless --check)
  --model <id>         provider model id (optional; a sane default per provider)
  --out <file>         write the response body to a file (optional)
  --check              probe curl + the provider keys and report readiness

Keys are read from the environment by name (never committed):
  XAI_API_KEY   for --provider xai (api.x.ai/v1)
  FAL_KEY       for --provider fal (queue.fal.run)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --provider) PROVIDER="${2:-}"; shift 2 ;;
    --prompt) PROMPT="${2:-}"; shift 2 ;;
    --model) MODEL="${2:-}"; shift 2 ;;
    --out) OUT="${2:-}"; shift 2 ;;
    --check) CHECK=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) loud_skip "Unknown argument: $1" ;;
  esac
done

if ! command -v curl >/dev/null 2>&1; then
  loud_skip "curl is not installed on this host. Install curl, or use the fal MCP substrate / an editor-side HTTP client."
fi

if [[ "$CHECK" -eq 1 ]]; then
  xai="absent"; fal="absent"
  [[ -n "${XAI_API_KEY:-}" ]] && xai="set"
  [[ -n "${FAL_KEY:-}" ]] && fal="set"
  printf 'readiness: curl=present  XAI_API_KEY=%s  FAL_KEY=%s\n' "$xai" "$fal"
  if [[ "$xai" == "absent" && "$fal" == "absent" ]]; then
    loud_skip "No provider key set. export XAI_API_KEY=… (Grok direct) or FAL_KEY=… (fal), then re-run."
  fi
  echo "OK — at least one provider key is set; direct generation is reachable."
  exit 0
fi

[[ -z "$PROVIDER" ]] && loud_skip "Missing --provider (xai|fal). See --help."
[[ -z "$PROMPT" ]] && loud_skip "Missing --prompt. See --help."

# jq builds the JSON payload safely (proper escaping of $PROMPT / $MODEL) — a
# hand-built string breaks on any " or \ in the prompt. jq is a repo prerequisite.
if ! command -v jq >/dev/null 2>&1; then
  loud_skip "jq is not installed on this host. Install jq — it is used to build the JSON payload safely."
fi

case "$PROVIDER" in
  xai)
    [[ -z "${XAI_API_KEY:-}" ]] && loud_skip "XAI_API_KEY is not set. export XAI_API_KEY=… then re-run (Grok has NO IP indemnity — flag for client work)."
    MODEL="${MODEL:-grok-2-image}"
    endpoint="https://api.x.ai/v1/images/generations"
    payload=$(jq -n --arg model "$MODEL" --arg prompt "$PROMPT" '{model: $model, prompt: $prompt}')
    auth_header="Authorization: Bearer ${XAI_API_KEY}"
    ;;
  fal)
    [[ -z "${FAL_KEY:-}" ]] && loud_skip "FAL_KEY is not set. export FAL_KEY=… then re-run (or wire the fal MCP via /wire-media-substrate)."
    MODEL="${MODEL:-fal-ai/flux/schnell}"
    endpoint="https://queue.fal.run/${MODEL}"
    payload=$(jq -n --arg prompt "$PROMPT" '{prompt: $prompt}')
    auth_header="Authorization: Key ${FAL_KEY}"
    ;;
  *)
    loud_skip "Unknown --provider '$PROVIDER' (expected xai|fal)."
    ;;
esac

echo "[generate-via-provider] POST ${endpoint} (model=${MODEL})" >&2
# --fail so an HTTP error is a non-zero exit, not a silently-saved error body.
if [[ -n "$OUT" ]]; then
  curl --fail --show-error --silent --connect-timeout 10 -m 300 \
    -H "$auth_header" -H "Content-Type: application/json" \
    -d "$payload" "$endpoint" -o "$OUT" \
    || loud_skip "Provider request failed (see curl error above). Endpoint/model/key may be wrong, or the provider is down. Verify against the provider docs [verify-at-use]."
  echo "Saved response to ${OUT}"
else
  curl --fail --show-error --silent --connect-timeout 10 -m 300 \
    -H "$auth_header" -H "Content-Type: application/json" \
    -d "$payload" "$endpoint" \
    || loud_skip "Provider request failed (see curl error above). Endpoint/model/key may be wrong, or the provider is down. Verify against the provider docs [verify-at-use]."
fi
