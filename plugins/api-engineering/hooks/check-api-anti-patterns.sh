#!/usr/bin/env bash
# check-api-anti-patterns.sh
# PreToolUse hook for Edit | Write | MultiEdit on API spec / code files. Flags five
# mechanically-detectable violations of the api-engineering team constitution
# (see CLAUDE.md §3/§4). Conservative: the spec-only checks fire only on files that
# actually look like an OpenAPI/AsyncAPI/Swagger document.
#
#   1. API key in the query string  — an OpenAPI `apiKey` scheme with `in: query`
#      leaks the key into logs/history/Referer. Use a header or Authorization (§4).
#   2. HTTP Basic auth scheme        — `scheme: basic` is not an API auth scheme;
#      use OAuth2 / bearer tokens (§4).
#   3. Hardcoded token/secret        — `Authorization: Bearer <literal>` or
#      api[_-]?key = "<literal>" in code; secrets are injected, never literals (§3 #8).
#   4. Wildcard CORS + credentials   — `Access-Control-Allow-Origin: *` alongside
#      `Allow-Credentials: true` is forbidden by browsers and a trust-boundary smell (§4).
#   5. Stale OpenAPI version         — `openapi: 3.0.x` / `swagger: "2.0"`; prefer
#      OpenAPI 3.1+ (JSON-Schema-aligned) (§3 #12). [verify-at-build]
#
# Advisory by default: prints to stderr, exits 0. Set APIENG_STRICT=1 to block (exit 2).
set -euo pipefail

file="${1:-}"
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives only
# via the canonical stdin JSON contract. Fall back to it — same dual-source
# pattern regen-on-manifest-change.sh / guard-destructive.sh already use.
if [[ -z "$file" ]] && [[ ! -t 0 ]] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [[ -n "$payload" ]]; then
    file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base_lc=$(basename "$file" | tr '[:upper:]' '[:lower:]')

is_spec=0
is_code=0
case "$base_lc" in
  *.yaml | *.yml | *.json)
    # Only treat it as an API spec if it declares one (conservative — avoids unrelated YAML/JSON).
    if grep -Eiq '^[[:space:]]*"?(openapi|asyncapi|swagger)"?[[:space:]]*:' "$file"; then
      is_spec=1
    fi
    ;;
  *.ts | *.tsx | *.js | *.jsx | *.py | *.go | *.java | *.rb | *.cs | *.php)
    is_code=1
    ;;
esac

# Nothing we recognize → no-op.
[[ "$is_spec" -eq 0 && "$is_code" -eq 0 ]] && exit 0

violations=()

if [[ "$is_spec" -eq 1 ]]; then
  # --- Check 1: API key in query (§4) ---
  if grep -Eiq 'type:[[:space:]]*apiKey' "$file" && grep -Eiq 'in:[[:space:]]*query' "$file"; then
    violations+=("[apikey-in-query] An apiKey security scheme appears to use 'in: query'. Keys in the URL leak into server logs, browser history, and Referer headers. Move it to a header or use Authorization / OAuth2 (CLAUDE.md §4).")
  fi

  # --- Check 2: HTTP Basic scheme (§4) ---
  if grep -Eiq 'scheme:[[:space:]]*basic\b' "$file"; then
    violations+=("[http-basic-scheme] An HTTP Basic auth scheme is declared. Basic is not an API authentication scheme — use OAuth2 bearer tokens with validated scopes (CLAUDE.md §4). Escalate the auth design to api-security-engineer.")
  fi

  # --- Check 5: stale OpenAPI version (§3 #12) ---
  if grep -Eiq '^[[:space:]]*openapi:[[:space:]]*"?3\.0' "$file" || grep -Eiq '^[[:space:]]*swagger:[[:space:]]*"?2\.0' "$file"; then
    violations+=("[stale-spec-version] This spec targets OpenAPI 3.0.x / Swagger 2.0. Prefer OpenAPI 3.1+ (JSON-Schema-aligned); 3.1→3.2 is non-breaking. Flag the upgrade rather than defaulting to the old version (CLAUDE.md §3 #12). [verify-at-build]")
  fi
fi

# --- Check 3: hardcoded token/secret (§3 #8) [security] — code or spec example ---
# A bearer token literal, or an api key assigned a non-empty quoted/non-reference literal.
if grep -Eiq 'authorization:[[:space:]]*bearer[[:space:]]+[A-Za-z0-9._-]{12,}' "$file" \
  || grep -Eiq '(api[_-]?key|apikey|access[_-]?token|client[_-]?secret)["'\'' ]*[=:][[:space:]]*["'\''][^"'\''$%{<[:space:]][^"'\'' ]{8,}' "$file"; then
  violations+=("[hardcoded-secret] A token / API key / secret looks hardcoded as a literal. Secrets are injected from a secret store / env, never literals in code or a committed spec (CLAUDE.md §3 #8). Escalate to ravenclaude-core/security-reviewer.")
fi

# --- Check 4: wildcard CORS + credentials (§4) ---
if grep -Eiq 'access-control-allow-origin[^a-z0-9]{1,8}\*' "$file" \
  && grep -Eiq 'access-control-allow-credentials[^a-z0-9]{0,8}true' "$file"; then
  violations+=("[cors-wildcard-credentials] 'Access-Control-Allow-Origin: *' is combined with 'Access-Control-Allow-Credentials: true'. Browsers forbid this combination and it signals a misconfigured trust boundary (CLAUDE.md §4). Reflect a vetted allow-list of origins instead.")
fi

[[ ${#violations[@]} -eq 0 ]] && exit 0

{
  echo "⚠️  api-engineering anti-pattern check — $file"
  for v in "${violations[@]}"; do echo "  • $v"; done
  echo "  Advisory by default. Set APIENG_STRICT=1 to make these blocking."
} >&2

if [[ "${APIENG_STRICT:-0}" == "1" ]]; then
  exit 2
fi
exit 0
