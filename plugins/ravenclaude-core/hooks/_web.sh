#!/usr/bin/env bash
# _web.sh — the ONE host parser shared by the two website-access hooks.
# Sourced (not run) by:
#   guard-web-access.sh      PreToolUse(WebFetch)  — reads the per-session seen file
#   mark-web-domain-seen.sh  PostToolUse(WebFetch) — writes it
#
# hooks-11 (2026-10-19): each hook carried a private copy of the host parser, and
# the copies had drifted. The writer did not cut the authority at `?` `#` or `\`
# before stripping userinfo, so for `https://ok.example?@other.example/` the
# reader keyed consent on ok.example while the writer marked other.example — the
# first-use prompt never latched, and the wrong domain was recorded as consented.
# One function now, so reader and writer cannot disagree.
#
# No `set -e` here (sourced into callers with their own options). bash 3.2-safe.

# _rc_web_host URL — print the host URL names, normalised:
#   1. strip the scheme;
#   2. cut the authority at the FIRST `/` `?` `#` or `\` — BEFORE stripping
#      userinfo, so `a.example#@b.example` is a.example (SH-F2, 2026-10-06);
#   3. strip userinfo and port, lowercase, drop one trailing FQDN dot;
#   4. canonicalise a pure-numeric IPv4 host (decimal / octal / hex / short forms,
#      read the way inet_aton reads them) to dotted-quad, so `2130706433` and
#      `0x7f.1` are both 127.0.0.1.
# Characters outside [a-z0-9._-] are LEFT IN: what to do with a host no rule can
# be compared against is the caller's decision.
_rc_web_host() {
  local h="${1-}" q
  h="${h#*://}"
  case "$h" in */*) h="${h%%/*}" ;; esac
  case "$h" in *\?*) h="${h%%\?*}" ;; esac
  case "$h" in *#*) h="${h%%#*}" ;; esac
  case "$h" in *\\*) h="${h%%\\*}" ;; esac
  h="${h##*@}"
  h="${h%%:*}"
  # LC_ALL=C: ASCII-only, byte-wise. Under a UTF-8 locale BSD tr expands ranges
  # by collation, which can touch non-ASCII letters (macOS CI, 2026-10-19).
  h="$(printf '%s' "$h" | LC_ALL=C tr 'A-Z' 'a-z')"
  h="${h%.}"
  if q="$(_rc_web_ipv4 "$h")"; then h="$q"; fi
  printf '%s' "$h"
}

# _rc_web_ipv4 HOST — dotted-quad form of a numeric IPv4 host, or return 1.
_rc_web_ipv4() {
  local h="${1-}" p v n=0 a=0 b=0 c=0 d=0 rest
  # Character classes are spelled out, never ranges: a range in a bracket
  # expression follows the locale's collation under bash 3.2, so [a-z] can
  # admit a non-ASCII letter on macOS (en_US.UTF-8). A listed set cannot.
  case "$h" in "" | *[!0123456789abcdefx.]* | .* | *. | *..*) return 1 ;; esac
  rest="$h."
  while [ -n "$rest" ]; do
    p="${rest%%.*}"
    rest="${rest#*.}"
    n=$((n + 1))
    [ "$n" -le 4 ] || return 1
    case "$p" in
      0x | 0x*[!0123456789abcdef]*) return 1 ;;
      0x*) [ "${#p}" -le 10 ] || return 1; v=$((16#${p#0x})) ;;
      0 | 0*[!01234567]*) [ "$p" = 0 ] || return 1; v=0 ;;
      0*) [ "${#p}" -le 12 ] || return 1; v=$((8#${p#0})) ;;
      *[!0123456789]*) return 1 ;;
      *) [ "${#p}" -le 10 ] || return 1; v=$((10#$p)) ;;
    esac
    case "$n" in 1) a=$v ;; 2) b=$v ;; 3) c=$v ;; 4) d=$v ;; esac
  done
  case "$n" in
    1) [ "$a" -le 4294967295 ] || return 1
       d=$((a & 255)); c=$(((a >> 8) & 255)); b=$(((a >> 16) & 255)); a=$(((a >> 24) & 255)) ;;
    2) [ "$a" -le 255 ] && [ "$b" -le 16777215 ] || return 1
       d=$((b & 255)); c=$(((b >> 8) & 255)); b=$(((b >> 16) & 255)) ;;
    3) [ "$a" -le 255 ] && [ "$b" -le 255 ] && [ "$c" -le 65535 ] || return 1
       d=$((c & 255)); c=$(((c >> 8) & 255)) ;;
    4) [ "$a" -le 255 ] && [ "$b" -le 255 ] && [ "$c" -le 255 ] && [ "$d" -le 255 ] || return 1 ;;
  esac
  printf '%s.%s.%s.%s' "$a" "$b" "$c" "$d"
}

# _rc_web_rule RULE — normalise one allow/deny list entry the same way a host is
# normalised: lowercase, strip a scheme and anything from the first `/`, strip a
# leading `*.` and `.`, strip a trailing `.`, canonicalise a numeric IPv4. Prints
# the normalised entry (possibly empty). A rule is matched against the host and
# every subdomain of it, so `*.x.example` and `.x.example` both mean x.example.
_rc_web_rule() {
  local r="${1-}" q
  r="$(printf '%s' "$r" | LC_ALL=C tr 'A-Z' 'a-z')"
  r="${r#*://}"
  r="${r%%/*}"
  r="${r#\*.}"
  r="${r#.}"
  r="${r%.}"
  if q="$(_rc_web_ipv4 "$r")"; then r="$q"; fi
  printf '%s' "$r"
}

# _rc_web_matchable STR — 0 when STR is a non-empty [a-z0-9._-] name a rule can match.
_rc_web_matchable() {
  case "${1-}" in "" | *[!abcdefghijklmnopqrstuvwxyz0123456789._-]*) return 1 ;; esac
  return 0
}
