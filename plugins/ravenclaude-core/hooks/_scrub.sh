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
#                         Also the pre-egress REFUSAL set for thing-seat.sh,
#                         claude-orchestrate.sh and judge.sh (grep -Eiq).
#   _secret_redact_patterns[] — case-sensitive, redaction-only shapes
#                         (Bearer/token, -u user:pass, env assignment). Never a
#                         refusal trigger by themselves; see the comment there.
#   _scrub_reason()     — Takes one argument (a reason/message string), prints
#                         the scrubbed version on stdout (secret-shaped tokens
#                         replaced with [REDACTED]; a PEM private-key block is
#                         replaced whole). Returns 0 always.
#
# Copies: these patterns are mirrored in ~12 files (Python ports, inline
# fallbacks, the concerns-catalog deny triggers). The marketplace script
# scripts/check-secret-pattern-parity.py lists every copy and fails if one loses
# the anchored sk- or gh[pousr]_ form; add any new copy to its COPIES table.
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
#   - `sk-` carries a LEFT boundary `(^|[^A-Za-z0-9])` (2026-10-19). Unanchored,
#     it matched the tail of any word ending in "sk" followed by a 20+ char
#     kebab run (task-/risk-/disk-/ask- names), and this list is also the
#     pre-egress REFUSAL set (claude-orchestrate.sh, judge.sh, thing-seat.sh,
#     the grok/copilot delegates), so ordinary paths and branch names were
#     refused as secrets. POSIX ERE has no lookbehind; the boundary consumes
#     one character in the redaction, which is cosmetic.
#   - GitHub: gh[pousr]_ covers every token class (ghp_ personal, gho_ OAuth,
#     ghu_ app user-to-server, ghs_ app server-to-server, ghr_ refresh).
#   - ASIA carries the same left boundary: case-insensitive egress scanners
#     (grep -Eiq) would otherwise match "asia" inside an ordinary word.
#   - xapp- requires the Slack app-token version digit (`xapp-1-…`), so a
#     kebab name that merely starts with "xapp-" is not a secret.
#   - Keep this file free of '#' inside patterns: it is the sed delimiter.
#
# Two consumers parse this array out of the file (scripts/ledger.py and
# scripts/build-outcome-corpus.py): one single-quoted pattern per line, no
# single quote inside a pattern.
_secret_patterns=(
  # Cloud API key prefixes
  'AKIA[0-9A-Z]{12,}'
  '(^|[^A-Za-z0-9])ASIA[0-9A-Z]{12,}'
  '(^|[^A-Za-z0-9])sk-(ant-)?[A-Za-z0-9-]{20,}'
  'sk_live_[A-Za-z0-9]{24,}'
  'sk_test_[A-Za-z0-9]{16,}'
  'rk_live_[A-Za-z0-9]{24,}'
  'gh[pousr]_[A-Za-z0-9]{30,}'
  'github_pat_[A-Za-z0-9_]{20,}'
  'glpat-[A-Za-z0-9_-]{15,}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  'xapp-[0-9]+-[A-Za-z0-9-]{10,}'
  'AIza[0-9A-Za-z_-]{30,}'
  'ya29\.[A-Za-z0-9_-]{20,}'
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

# REDACTION-ONLY patterns (2026-10-19). _scrub_reason applies these after
# _secret_patterns. They are deliberately NOT in _secret_patterns, because the
# egress refusal scanners (thing-seat.sh, claude-orchestrate.sh, judge.sh) loop
# over _secret_patterns with `grep -Eiq`, and these shapes are only precise when
# matched case-sensitively: under -i the env-assignment shape would refuse
# `max_tokens=4096` or `def f(password=None)`. As a hard deny they are the
# false-positive class the deny sets exclude (secret_spec D-set rule). _scrub_reason
# itself uses case-sensitive sed, which is where they belong.
#   - Bearer, or `Authorization: token`, then an opaque value of 20+ chars.
#     `Bearer $T` is not matched ('$' is outside the value class), and a bare
#     "token" is not a keyword (prose such as "token signing/verification").
#   - `-u user:pass`: the user half must start with a letter, digit or _ (so
#     `date -u +%Y-%m-%dT%H:%M:%SZ` is not a credential) and the password half
#     must contain a non-digit, the same rule as `-p` above (so
#     `docker run -u 1000:1000` is not one either). One leading " is allowed.
#   - A literal-value env assignment (PGPASSWORD=…, API_KEY=…). After an
#     optional " and any digits, the value must continue with a letter or _,
#     so an env reference (TOKEN=${TOKEN}, TOKEN="$X"), a numeric setting
#     (MAX_TOKENS=4096) and a doc placeholder (API_KEY=..., TOKEN=<key>) are
#     not redacted.
#   Measured 2026-10-19 over every tracked file: the first-draft forms matched
#   `date -u +FORMAT` in 18 files, "token <phrase>" prose in 11 and doc
#   placeholders in 40; the delegates refuse anything _scrub_reason changes, so
#   those were refusals, not just cosmetic redactions.
_secret_redact_patterns=(
  '(Bearer|bearer|[Aa]uthorization:[[:space:]]*token)[[:space:]]+[A-Za-z0-9._~+/-]{20,}'
  '-u[[:space:]]+"?[A-Za-z0-9_][^[:space:]:$"]*:[^[:space:]$"]*[^[:space:]$"0-9][^[:space:]$"]*'
  '(PASSWORD|SECRET|TOKEN|API_?KEY)[A-Z_]*="?[0-9]*[A-Za-z_][^[:space:]"]*'
)

# _scrub_pem_blocks: replace every line from a `-----BEGIN … PRIVATE KEY-----`
# line through its matching END line (or to end of input, if unterminated) with
# a single [REDACTED] line. sed works line by line, so without this pass only
# the BEGIN line was redacted and the base64 body and END line survived.
# Portable awk (BSD awk, mawk, gawk); no GNU-only sed slurp.
_scrub_pem_blocks() {
  printf '%s' "${1:-}" | awk '
    inb {
      if ($0 ~ /-----END [A-Z ]*PRIVATE KEY-----/) inb = 0
      next
    }
    $0 ~ /-----BEGIN [A-Z ]*PRIVATE KEY-----/ {
      print "[REDACTED]"
      rest = $0
      sub(/.*-----BEGIN [A-Z ]*PRIVATE KEY-----/, "", rest)
      if (rest !~ /-----END [A-Z ]*PRIVATE KEY-----/) inb = 1
      next
    }
    { print }
  '
}

# Scrub a reason string: replace secret-shaped tokens with [REDACTED].
# Usage: _scrub_reason <string>
# Prints the scrubbed string to stdout.
_scrub_reason() {
  {
    local s="${1:-}"
    [ -z "$s" ] && { printf '%s' "$s"; return 0; }

    # PEM block body first, so the per-line sed pass below never sees it. Only
    # when a BEGIN marker is present (no subprocess on the common path). If awk
    # is missing or fails, redact WHOLESALE rather than let the body through.
    case "$s" in
      *"-----BEGIN "*"PRIVATE KEY-----"*)
        local pem_out=""
        if command -v awk >/dev/null 2>&1; then
          pem_out="$(_scrub_pem_blocks "$s" 2>/dev/null)" || pem_out=""
        fi
        if [ -z "$pem_out" ]; then
          printf '%s' "[REDACTED — secret-shaped content removed from reason]"
          return 0
        fi
        s="$pem_out"
        ;;
    esac

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
      for p in "${_secret_patterns[@]}" "${_secret_redact_patterns[@]}"; do
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
      for p in "${_secret_patterns[@]}" "${_secret_redact_patterns[@]}"; do
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
