#!/usr/bin/env bash
# check-wordpress-anti-patterns.sh — advisory PreToolUse hook for the wordpress-cms-engineering plugin.
# Flags mechanically-detectable WordPress anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set WPENG_STRICT=1 to make it blocking (exit 2).
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
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect files where these patterns are meaningful.
case "$file" in
  *.php|*.js|*.jsx|*.ts|*.tsx) ;;
  *) exit 0 ;;
esac

findings=()

# 1. $wpdb->query/get_results/etc. with string concatenation or interpolation instead of prepare.
if grep -nE '\$wpdb->(query|get_results|get_row|get_var|get_col|prepare)?[^;]*("[^"]*"[[:space:]]*\.|\.[[:space:]]*"[^"]*"|\{?\$)' "$file" 2>/dev/null \
     | grep -vE 'prepare[[:space:]]*\(' >/dev/null 2>&1; then
  findings+=("\$wpdb query built with string concatenation/interpolation — use \$wpdb->prepare() with %s/%d/%i placeholders; never concatenate input into SQL.")
fi

# 2. Superglobal input ($_GET/$_POST/$_REQUEST) used without a sanitize_/esc_/absint/wp_unslash nearby on the same line.
if grep -nE '\$_(GET|POST|REQUEST)\[' "$file" 2>/dev/null \
     | grep -vE 'sanitize_|esc_|absint|intval|wp_unslash|wp_verify_nonce|check_admin_referer|check_ajax_referer' >/dev/null 2>&1; then
  findings+=("\$_GET/\$_POST/\$_REQUEST used without a sanitize_/esc_/absint/wp_unslash on the same line — sanitize untrusted input on the way in and escape on the way out.")
fi

# 3. eval( — arbitrary code execution.
if grep -nE '\beval[[:space:]]*\(' "$file" >/dev/null 2>&1; then
  findings+=("eval( is a code-execution risk — remove it; there is almost always a safe alternative.")
fi

# 4. extract( — clobbers scope, hides injected variables.
if grep -nE '\bextract[[:space:]]*\(' "$file" >/dev/null 2>&1; then
  findings+=("extract( imports array keys as variables and is a security/maintainability hazard — assign variables explicitly.")
fi

# 5. wp_enqueue_script/style without a version argument (the 4th arg: handle, src, deps, ver).
#    Heuristic: flag an enqueue call line that has fewer than 3 commas (deps/ver omitted).
#    ERE has no nesting; count commas on the line so an empty array() in deps doesn't fool us.
while IFS= read -r line; do
  [ -z "$line" ] && continue
  commas=$(printf '%s' "$line" | tr -cd ',' | wc -c)
  if [ "$commas" -lt 3 ]; then
    findings+=("wp_enqueue_script/style appears to omit a version argument — pass an explicit \$ver (the cache-bust); never enqueue without a versioned handle.")
    break
  fi
done < <(grep -nE 'wp_(enqueue|register)_(script|style)[[:space:]]*\(' "$file" 2>/dev/null || true)

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── wordpress-cms-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${WPENG_STRICT:-0}" = "1" ]; then
  echo "(blocking: WPENG_STRICT=1)" >&2
  exit 2
fi
exit 0
