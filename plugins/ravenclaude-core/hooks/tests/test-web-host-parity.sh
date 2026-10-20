#!/usr/bin/env bash
# test-web-host-parity.sh — the website-access hooks agree on the host, and the
# guard normalises rules and odd hosts.
#
# hooks-11 (2026-10-19): guard-web-access.sh (PreToolUse reader) and
# mark-web-domain-seen.sh (PostToolUse writer of the first-use seen file) now
# share _web.sh's _rc_web_host. For URLs with ? # backslash-@ userinfo port
# uppercase and a trailing dot, the slug the writer records must be the host the
# guard checks, so first-use consent latches.
# hooks-12: percent-encoded / non-ASCII hosts ask when a deny list exists; a
# numeric IPv4 host is canonicalised before matching; '*.x', '.x' and 'x.' rules
# match; an entry that can never match is warned about once.
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-web-host-parity.sh

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HOOKS="$REPO_ROOT/plugins/ravenclaude-core/hooks"
PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }
command -v jq >/dev/null 2>&1 || { echo "test-web-host-parity: jq required" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# _run <hooks-dir> <hook> <proj> <session> <url> -> OUT (stdout), ERR (stderr), RC
_run() {
  local pl
  pl="$(jq -cn --arg u "$5" --arg s "$4" '{tool_name:"WebFetch",tool_input:{url:$u},session_id:$s}')"
  RC=0
  printf '%s' "$pl" | env -u CLAUDE_SESSION_ID CLAUDE_PROJECT_DIR="$3" bash "$1/$2" \
    >"$TMP/out" 2>"$TMP/err" || RC=$?
  OUT="$(cat "$TMP/out")"
  ERR="$(cat "$TMP/err")"
}
_decision() {
  [ -n "$OUT" ] || { echo none; return; }
  printf '%s' "$OUT" | jq -r '.hookSpecificOutput.permissionDecision // "none"' 2>/dev/null || echo none
}

# A hooks dir variant: the real hooks, with optional python replacements applied
# to ONE file. usage: _variant <name> <file> [<old> <new> ...]
_variant() {
  local d="$TMP/v-$1" f="$2" h
  shift 2
  mkdir -p "$d"
  for h in guard-web-access.sh mark-web-domain-seen.sh _web.sh _emit-event.sh _scrub.sh; do
    [ -f "$HOOKS/$h" ] && cat "$HOOKS/$h" >"$d/$h"
  done
  if [ "$#" -gt 0 ]; then
    python3 - "$d/$f" "$@" <<'PY' || return 1
import sys
from pathlib import Path
p = Path(sys.argv[1]); src = p.read_text(); pairs = sys.argv[2:]
for old, new in zip(pairs[0::2], pairs[1::2]):
    if old not in src:
        sys.exit(2)
    src = src.replace(old, new, 1)
p.write_text(src)
PY
  fi
  printf '%s' "$d"
}

echo
echo "── hooks-11: the writer's slug is the reader's host, and consent latches ───"
P="$TMP/proj"
mkdir -p "$P/.ravenclaude"
printf 'allow:\n  - ok.example\ndeny: []\n' >"$P/.ravenclaude/web-access.yaml"
i=0
_latch_case() { # <hooks-dir> <url> -> LATCH_OK=1 when slug==ok.example and the 2nd fetch allows
  local hd="$1" url="$2" sid seen files
  i=$((i + 1)); sid="parity$i$RANDOM"
  seen="$P/.ravenclaude/runs/$sid/web-first-seen"
  LATCH_OK=0
  _run "$hd" guard-web-access.sh "$P" "$sid" "$url"; local d1; d1="$(_decision)"
  _run "$hd" mark-web-domain-seen.sh "$P" "$sid" "$url"
  files="$(ls "$seen" 2>/dev/null | tr '\n' ' ')"
  _run "$hd" guard-web-access.sh "$P" "$sid" "$url"; local d2; d2="$(_decision)"
  LATCH_DETAIL="first=$d1 seen='${files% }' second=$d2"
  [ "$d1" = ask ] && [ "${files% }" = ok.example ] && [ "$d2" = allow ] && LATCH_OK=1
}
BS='\'
for url in \
  "https://ok.example/path?x=1" \
  "https://ok.example?@other.example/" \
  "https://ok.example#@other.example/" \
  "https://ok.example${BS}@other.example/" \
  "https://user:pw@ok.example/" \
  "https://ok.example:8443/x" \
  "https://OK.Example/x" \
  "https://ok.example./x"; do
  _latch_case "$HOOKS" "$url"
  if [ "$LATCH_OK" = 1 ]; then pass "latches: $url ($LATCH_DETAIL)"; else fail "no latch: $url ($LATCH_DETAIL)"; fi
done

echo
echo "── hooks-12: odd hosts ask, numeric hosts canonicalise, rules normalise ────"
D="$TMP/deny"
mkdir -p "$D/.ravenclaude"
cat >"$D/.ravenclaude/web-access.yaml" <<'YAML'
deny:
  - evil.example
  - 127.0.0.1
  - "*.wild.example"
  - .dot.example
  - trail.example.
  - https://scheme.example/some/path
allow: []
YAML
_expect() { # <want: deny|ask|none> <label> <proj> <url>
  _run "$HOOKS" guard-web-access.sh "$3" "s-$RANDOM" "$4"
  local got
  if [ "$RC" -eq 2 ]; then got=deny; else got="$(_decision)"; fi
  if [ "$got" = "$1" ]; then pass "$2 -> $got"; else
    # Show the parsed host as bytes, so a platform-only failure is diagnosable from the log.
    local hb
    hb="$(bash -c '. "$1/_web.sh"; _rc_web_host "$2"' _ "$HOOKS" "$4" | od -An -tx1 | tr -s ' \n' ' ')"
    fail "$2: expected $1, got $got (rc=$RC, parsed host bytes:${hb})"
  fi
}
FW="$(printf '\357\275\205')"   # U+FF45 FULLWIDTH LATIN SMALL LETTER E
_expect ask  "percent-encoded host"            "$D" "https://%65vil.example/x"
_expect ask  "fullwidth first letter"          "$D" "https://${FW}vil.example/x"
_expect deny "decimal 127.0.0.1"               "$D" "http://2130706433/"
_expect deny "hex short form 0x7f.1"           "$D" "http://0x7f.1/"
_expect deny "octal 0177.0.0.1"                "$D" "http://0177.0.0.1/"
_expect deny "'*.wild.example' matches a.wild.example" "$D" "https://a.wild.example/"
_expect deny "'.dot.example' matches dot.example"      "$D" "https://dot.example/"
_expect deny "'trail.example.' matches trail.example"  "$D" "https://trail.example/x"
_expect deny "a scheme+path rule matches its host"     "$D" "https://scheme.example/"
_expect deny "plain deny still denies"                 "$D" "https://EVIL.example./x"
_expect none "unlisted host falls through"             "$D" "https://unlisted.example/x"
_expect none "a numeric host not on the list falls through" "$D" "http://10.1/"
_expect none "percent host with NO deny list falls through" "$P" "https://%65vil.example/x"

W="$TMP/warn"
mkdir -p "$W/.ravenclaude"
printf 'deny:\n  - evil.example\n  - "bad host.example"\nallow: []\n' >"$W/.ravenclaude/web-access.yaml"
_run "$HOOKS" guard-web-access.sh "$W" "s-warn" "https://evil.example/"
n="$(printf '%s\n' "$ERR" | grep -c 'can never match a host')"
if [ "$RC" -eq 2 ] && [ "$n" -eq 1 ]; then pass "an entry that can never match: one warning, the rest still applies"
else fail "unmatchable entry: rc=$RC warnings=$n err='$ERR'"; fi

echo
echo "── teeth: reverting each fix re-opens its gap ──────────────────────────────"
OLDPARSE='host="${url#*://}"
host="${host%%/*}"
host="${host##*@}"
host="${host%%:*}"
host="$(printf '"'"'%s'"'"' "$host" | tr '"'"'A-Z'"'"' '"'"'a-z'"'"')"
host="${host%.}"'
if V="$(_variant oldwriter mark-web-domain-seen.sh 'host="$(_rc_web_host "$url")"' "$OLDPARSE")"; then
  _latch_case "$V" "https://ok.example?@other.example/"
  [ "$LATCH_OK" = 0 ] && pass "teeth (hooks-11): the old private writer parser does not latch the ? form ($LATCH_DETAIL)" \
    || fail "teeth (hooks-11): old writer parser still latched — the parity check is not measuring the shared parser"
else
  fail "teeth (hooks-11): could not build the old-writer variant"
fi
if V="$(_variant noask guard-web-access.sh 'if [ "${#deny_list[@]}" -gt 0 ]; then' 'if false; then')"; then
  _run "$V" guard-web-access.sh "$D" "s-t2" "https://%65vil.example/x"
  [ "$RC" -eq 0 ] && [ "$(_decision)" = none ] && pass "teeth (hooks-12 ask): without it a percent host falls through silently" \
    || fail "teeth (hooks-12 ask): mutant gave rc=$RC decision=$(_decision)"
else
  fail "teeth (hooks-12 ask): could not build the variant"
fi
if V="$(_variant noipv4 _web.sh '  if q="$(_rc_web_ipv4 "$h")"; then h="$q"; fi' ':')"; then
  _run "$V" guard-web-access.sh "$D" "s-t3" "http://2130706433/"
  [ "$RC" -ne 2 ] && pass "teeth (hooks-12 numeric): without canonicalisation the decimal host is not denied" \
    || fail "teeth (hooks-12 numeric): mutant still denied"
else
  fail "teeth (hooks-12 numeric): could not build the variant"
fi
if V="$(_variant norule guard-web-access.sh '    r="$(_rc_web_rule "$raw")"' '    r="$raw"')"; then
  _run "$V" guard-web-access.sh "$D" "s-t4" "https://dot.example/"
  [ "$RC" -ne 2 ] && pass "teeth (hooks-12 rules): without rule normalisation '.dot.example' does not match" \
    || fail "teeth (hooks-12 rules): mutant still denied"
else
  fail "teeth (hooks-12 rules): could not build the variant"
fi

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
