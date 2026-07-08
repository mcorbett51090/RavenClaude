#!/usr/bin/env bash
# check-fabric-anti-patterns.sh
# PreToolUse hook for Edit | Write | MultiEdit on Fabric-ish files
# (.py/.ipynb/.sql/.kql/.tmdl/.json/.conf/.md). Flags four mechanically-detectable
# violations of the microsoft-fabric team constitution (see
# plugins/microsoft-fabric/CLAUDE.md §3 house opinions):
#
#   1. spark.ms.autotune.enabled set true — autotune is the deprecated Runtime-1.2
#      path; use the Native Execution Engine instead (house opinion #11).
#   2. "mirroring is free" claimed in prose with no "query"/"billed" qualifier —
#      Mirroring is free to REPLICATE, not free to QUERY (house opinion #1).
#   3. V-Order explicitly disabled on a gold / Direct-Lake table (house opinion #4).
#   4. "Direct Lake" written with no mode (on OneLake / on SQL) nearby — the two
#      modes behave differently on fallback (house opinion #8).
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set FABRIC_STRICT=1 to make
# violations blocking (exit 2).

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

# Only inspect Fabric-shaped files.
case "$base_lc" in
  *.py | *.ipynb | *.sql | *.kql | *.tmdl | *.json | *.conf | *.md) ;;
  *) exit 0 ;;
esac

violations=()

# --- Check 1: autotune enabled (use NEE instead) — #11 ---
case "$base_lc" in
  *.py | *.ipynb | *.json | *.conf)
    if grep -Eni 'spark\.ms\.autotune\.enabled[^a-z0-9]*(=|:|true)' "$file" >/dev/null 2>&1; then
      while IFS= read -r line; do
        violations+=("  [autotune-not-nee] $file: $line — autotune is the deprecated Runtime-1.2 path; enable the Native Execution Engine instead (CLAUDE.md §3 #11).")
      done < <(grep -Eni 'spark\.ms\.autotune\.enabled' "$file" | head -3)
    fi
    ;;
esac

# --- Check 2: "mirroring is free" with no query/billed qualifier — #1 ---
case "$base_lc" in
  *.md)
    if grep -Eni 'mirror(ing)?[^.]{0,40}\bfree\b' "$file" >/dev/null 2>&1; then
      if ! grep -Eni 'free to replicate|not free to query|query.{0,12}billed|billed.{0,12}query' "$file" >/dev/null 2>&1; then
        violations+=("  [mirroring-free-unqualified] $file claims Mirroring is 'free' without the 'free to replicate, not free to query' qualifier (CLAUDE.md §3 #1). Query compute is always billed.")
      fi
    fi
    ;;
esac

# --- Check 3: V-Order explicitly disabled on a gold / Direct-Lake table — #4 ---
case "$base_lc" in
  *.py | *.sql | *.ipynb)
    if grep -Eni '(gold|direct[ _-]?lake|vorder|v-order)' "$file" >/dev/null 2>&1; then
      if grep -Eni '(vorder|v-order|optimizewrite)[^a-z0-9]{0,12}(false|off|disable)' "$file" >/dev/null 2>&1; then
        while IFS= read -r line; do
          violations+=("  [vorder-off-on-gold] $file: $line — V-Order should be ON for gold tables consumed by Direct Lake / the SQL endpoint (CLAUDE.md §3 #4).")
        done < <(grep -Eni '(vorder|v-order|optimizewrite)[^a-z0-9]{0,12}(false|off|disable)' "$file" | head -3)
      fi
    fi
    ;;
esac

# --- Check 4: "Direct Lake" with no mode named — #8 ---
case "$base_lc" in
  *.md | *.tmdl)
    if grep -Eni 'direct[ _-]?lake' "$file" >/dev/null 2>&1; then
      if ! grep -Eni 'direct[ _-]?lake[ _-]?on[ _-]?(one ?lake|sql)|on one ?lake|on sql' "$file" >/dev/null 2>&1; then
        violations+=("  [direct-lake-no-mode] $file mentions 'Direct Lake' without naming the mode (on OneLake / on SQL). The two modes differ on DirectQuery fallback — name it (CLAUDE.md §3 #8).")
      fi
    fi
    ;;
esac

# --- Report ---
if [[ ${#violations[@]} -gt 0 ]]; then
  cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
  ⚠  Microsoft Fabric anti-pattern check flagged ${#violations[@]} issue(s) in:
       $file

EOF
  for v in "${violations[@]}"; do
    echo "$v" >&2
  done
  cat >&2 <<'EOF'

  See plugins/microsoft-fabric/CLAUDE.md §3 (house opinions) for the full
  rules. This hook is advisory — the edit was not blocked. Set
  FABRIC_STRICT=1 to make violations blocking.
────────────────────────────────────────────────────────────────────

EOF
  if [[ "${FABRIC_STRICT:-0}" == "1" ]]; then
    # exit 2 = BLOCK (Claude Code PreToolUse blocking code); exit 1 is a non-blocking
    # error Claude Code silently swallows, so STRICT would not actually block the edit.
    exit 2
  fi
fi

exit 0
