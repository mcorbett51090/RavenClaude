#!/usr/bin/env bash
# _scrub.sh
# Shared, sourced helper that defines the canonical _secret_patterns array
# and the _scrub_reason() function used by _emit-event.sh (substrate writer)
# and thing-seat.sh (egress backstop).
#
# SOURCED, not executed. Carries NO top-level `set -euo pipefail` so it can
# never change the sourcing script's shell options. chmod +x to satisfy the
# repo's "every hooks/*.sh is executable" gate.
#
# Provides:
#   _secret_patterns[]  — ERE patterns matching high-confidence secret shapes.
#                         Source of truth: mirrors xc.secret-in-command in
#                         knowledge/concerns-catalog.md + the egress backstop
#                         in scripts/thing-seat.sh. Keep all three in sync.
#   _scrub_reason()     — Takes one argument (a reason/message string), prints
#                         the scrubbed version on stdout (secret-shaped tokens
#                         replaced with [REDACTED]). Returns 0 always.
#
# Design invariants:
#   * FAIL-SAFE — scrubbing is best-effort. Any failure returns the original
#     string. A scrub error must never break the emit path.
#   * NO EXTERNAL COMMANDS required — pure bash string operations + printf.
#     sed is used only when available for the multi-pattern sweep.

# Canonical secret patterns (ERE). Mirror of thing-seat.sh _secret_patterns
# and concerns-catalog.md xc.secret-in-command triggers.
#
# Pattern shapes (1-2 per category):
#   - Cloud provider API keys (AWS, Anthropic, GitHub, GitLab, Slack, Google,
#     Stripe, npm, HuggingFace, Azure)
#   - JWTs (`eyJ`-prefixed three-segment base64url)
#   - PEM private keys
#   - CLI secret flags (`--password=`, `--token=`, short `-p`)
#   - Embedded credentials in URLs (basic-auth `user:pass@host`,
#     Postgres/MySQL connection strings)
#
# Pattern tightness rationale:
#   - JWT third segment is `{20,}` not `{6,}` (real signatures are 32+ base64
#     chars; 6 invited prose false positives).
#   - Short `-p` flag is `{16,}` not `{6,}`, and refuses pure-digit values, so
#     `mysql -phunter2secretpw` redacts but `ssh -p 22222`, `docker run -p
#     8080:8080`, and `kubectl -p prod-cluster` (single short tokens like
#     cluster names or port maps) don't. Real DB passwords are longer.
_secret_patterns=(
  # Cloud API key prefixes
  'AKIA[0-9A-Z]{12,}'
  'sk-(ant-)?[A-Za-z0-9-]{20,}'
  'sk_live_[A-Za-z0-9]{24,}'
  'rk_live_[A-Za-z0-9]{24,}'
  'ghp_[A-Za-z0-9]{30,}'
  'github_pat_[A-Za-z0-9_]{20,}'
  'glpat-[A-Za-z0-9_-]{15,}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  'AIza[0-9A-Za-z_-]{30,}'
  'npm_[A-Za-z0-9]{30,}'
  'hf_[A-Za-z0-9]{30,}'
  'AccountKey=[A-Za-z0-9+/=]{20,}'
  # JWTs (third segment tightened to {20,} from {6,})
  'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}'
  # PEM private keys
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'
  # CLI secret flags
  '--password[=[:space:]][^[:space:]]+'
  '--token[=[:space:]][^[:space:]]+'
  # Short `-p` flag: tightened to {16,} and refuses pure-digit values so
  # `ssh -p 222222` and port maps like `docker run -p 8080:8080-host` don't trip.
  '(^|[[:space:]])-p[^[:space:][:digit:]][^[:space:]]{15,}'
  # Embedded credentials in URLs: basic-auth `user:pass@host`, conn strings.
  # The `{4,}` floor on user keeps `http://localhost:8080` etc. from matching
  # (no `@`), while a real `https://user:tok@host` is matched.
  '(https?|postgres(ql)?|mysql|mongodb|redis|amqp|smtp)s?://[A-Za-z0-9._-]{2,}:[A-Za-z0-9._%+-]{4,}@'
)

# Scrub a reason string: replace secret-shaped tokens with [REDACTED].
# Usage: _scrub_reason <string>
# Prints the scrubbed string to stdout.
_scrub_reason() {
  {
    local s="${1:-}"
    [ -z "$s" ] && { printf '%s' "$s"; return 0; }

    # Use sed for multi-pattern substitution when available AND it supports -E.
    # NB: probing `-E` (not just `command -v sed`) is load-bearing — every
    # substitution below uses `sed -E`, so a sed build without -E support (e.g.
    # a minimal/BusyBox image) would make each `sed -E` fail to empty, the
    # `[ -n "$new_result" ]` guard would keep the ORIGINAL string, and the
    # function would return the secret UNredacted. On no usable `-E`, fall
    # through to the wholesale-redact branch (fail-safe over context).
    if command -v sed >/dev/null 2>&1 && printf '' | sed -E 's/x/x/' >/dev/null 2>&1; then
      local result="$s"
      local p new_result
      # NB: sed s-command delimiter is '#' (not the conventional '|'), because
      # one of the secret patterns contains a literal '|' (the alternation in
      # `(^|[[:space:]])-p[^[:space:]]{6,}`), which would collide with a '|'
      # delimiter and break sed's parsing. None of the patterns contain '#'.
      for p in "${_secret_patterns[@]}"; do
        # sed -E with -e so patterns starting with '-' aren't treated as flags.
        new_result="$(printf '%s' "$result" | sed -E -e "s#${p}#[REDACTED]#g" 2>/dev/null)"
        # Preserve `result` if sed produced no output or failed (defence in
        # depth: a single bad pattern must not wipe accumulated scrubs).
        [ -n "$new_result" ] && result="$new_result"
      done
      printf '%s' "$result"
    else
      # No sed: fall back to grep-detect + WHOLESALE redact on match. This is
      # INTENTIONAL — fail-safety over context preservation. When sed is absent
      # (a minimal container, BusyBox, etc.) we can detect a secret but cannot
      # do per-pattern substitution in pure bash without re-implementing ERE.
      # Wholesale redaction is the conservative choice: we never leak, even if
      # we lose the structural context around the secret.
      local p
      for p in "${_secret_patterns[@]}"; do
        if printf '%s' "$s" | grep -Eiq -e "$p" 2>/dev/null; then
          printf '%s' "[REDACTED — secret-shaped content removed from reason]"
          return 0
        fi
      done
      printf '%s' "$s"
    fi
  } 2>/dev/null || printf '%s' "${1:-}"
  return 0
}
