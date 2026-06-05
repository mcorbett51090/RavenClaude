#!/usr/bin/env bash
# check-auth-identity-anti-patterns.sh — advisory PreToolUse hook for the auth-identity plugin.
# Flags mechanically-detectable end-user-auth/identity anti-patterns on Edit/Write/MultiEdit.
# Advisory by default (exit 0, prints a notice); set AUTH_STRICT=1 to make it blocking (exit 2).
#
# These are HEURISTIC text matches, not a security review — a clean run is NOT a sign-off.
# Every concrete auth/secret/token change still routes through ravenclaude-core/security-reviewer
# (auth-identity CLAUDE.md §8). False positives are expected; AUTH_STRICT stays opt-in for that reason.
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

findings=()

# 1) Token in localStorage/sessionStorage — one XSS discloses every token (CLAUDE.md §3 #3).
if grep -nEi "(localStorage|sessionStorage)\.(set|get)Item\(\s*['\"][^'\"]*(token|jwt|auth|session|access|refresh)" "$file" >/dev/null 2>&1; then
  findings+=("Token-like value in localStorage/sessionStorage — readable by any JS in the origin; use memory + an HttpOnly+Secure+SameSite cookie.")
fi

# 2) OAuth Implicit flow (response_type=token) — removed in OAuth 2.1 (CLAUDE.md §3 #2).
if grep -nEi "response_type\s*[=:]\s*['\"]?token\b" "$file" >/dev/null 2>&1; then
  findings+=("OAuth Implicit flow (response_type=token) — removed in OAuth 2.1; migrate to Authorization Code + PKCE.")
fi

# 3) Wildcard / non-exact redirect URI — RFC 9700 requires exact matching (CLAUDE.md best-practice).
if grep -nEi "redirect_uri\s*[=:].*(\*|/\s*['\"]|\{[^}]*\})" "$file" >/dev/null 2>&1; then
  findings+=("redirect_uri looks non-exact (wildcard/pattern/interpolated) — RFC 9700 requires exact string matching; register exact per-environment URIs.")
fi

# 4) JWT decoded without verification — decode != verify (CLAUDE.md §3 #5).
if grep -nEi "(jwt\.decode\([^)]*verify\s*[=:]\s*(false|False)|decode\([^)]*\{?\s*complete|jwtDecode\(|jwt_decode\()" "$file" >/dev/null 2>&1; then
  findings+=("JWT decoded without verification — decoding is not validating; verify the signature against the issuer JWKS + check iss/aud/exp server-side.")
fi

# 5) Hardcoded client secret / signing key / service key — must come from env/secret store (CLAUDE.md §4).
if grep -nEi "(client_secret|service_role|signing_?key|api[_-]?secret|private_?key)\s*[=:]\s*['\"][A-Za-z0-9_./+-]{12,}['\"]" "$file" >/dev/null 2>&1; then
  findings+=("A secret/signing/service key looks hardcoded — load it from env or a secret store; the service key must never reach the browser.")
fi

# 6) Session cookie without HttpOnly — JS-readable session cookie (CLAUDE.md §3 #3/#4).
if grep -nEi "(set-?cookie|cookies?\.set|res\.cookie)\b" "$file" >/dev/null 2>&1; then
  if ! grep -nEi "httponly" "$file" >/dev/null 2>&1; then
    findings+=("A cookie is set but no HttpOnly appears in this file — session/refresh cookies need HttpOnly + Secure + SameSite.")
  fi
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── auth-identity advisory: review these before committing (heuristic, not a security review) ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done
printf "%s\n" "Route concrete auth/secret/token changes through ravenclaude-core/security-reviewer (CLAUDE.md §8)." >&2

if [ "${AUTH_STRICT:-0}" = "1" ]; then
  echo "(blocking: AUTH_STRICT=1)" >&2
  exit 2
fi
exit 0
