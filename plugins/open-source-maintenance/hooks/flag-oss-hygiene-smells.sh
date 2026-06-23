#!/usr/bin/env bash
# flag-oss-hygiene-smells.sh
# PreToolUse hook for Edit | Write | MultiEdit on open-source maintenance files.
# Flags three mechanically-detectable violations of the open-source-maintenance
# team constitution (see plugins/open-source-maintenance/CLAUDE.md and the
# best-practices/ rules):
#
#   1. A package manifest (package.json / pyproject.toml / Cargo.toml) that
#      declares a "version" but the repo CHANGELOG has no matching entry —
#      "the changelog is for humans, keep it current" (no bump with no entry).
#   2. A package manifest with NO license field — "add the license before the
#      first public commit."
#   3. A CHANGELOG entry that mentions removal / breaking wording but carries no
#      explicit "BREAKING" marker — "breaking changes need a deprecation window"
#      and lead the entry with **BREAKING:**.
#
# Advisory by default: prints warnings to stderr (so Claude and the user both see
# them) but exits 0 so the edit is not blocked. Set OSS_MAINT_STRICT=1 to make
# violations blocking (exit 2).
#
# Patterns use POSIX ERE only (grep -E / -iE) — no PCRE constructs — per the
# check-grep-ere-pcre.py CI gate.
#
# Claude Code PreToolUse: exit 2 = BLOCK the tool call with stderr surfaced to
# the agent. exit 1 = non-blocking error (silently swallowed).

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

base=$(basename "$file")
base_lc=$(printf '%s' "$base" | tr '[:upper:]' '[:lower:]')
dir=$(dirname "$file")

warnings=()

is_manifest=0
case "$base_lc" in
  package.json | pyproject.toml | cargo.toml) is_manifest=1 ;;
esac

# --- Check 1 & 2: manifest hygiene ---
if [[ "$is_manifest" -eq 1 ]]; then
  if grep -iqE '(^|[[:space:]"])version([[:space:]]*[:=])' "$file"; then
    # Look for a sibling/repo CHANGELOG; if present, nudge to keep it current.
    changelog=""
    for cand in "$dir/CHANGELOG.md" "$dir/../CHANGELOG.md" "CHANGELOG.md"; do
      if [[ -f "$cand" ]]; then changelog="$cand"; break; fi
    done
    if [[ -z "$changelog" ]]; then
      warnings+=("manifest declares a version but no CHANGELOG.md was found — releases need a human-readable changelog (best-practices/changelog-is-for-humans-keep-it-current.md).")
    fi
  fi
  if ! grep -iqE 'license' "$file"; then
    warnings+=("manifest has no 'license' field — add a license before the first public release (best-practices/license-before-first-public-commit.md).")
  fi
fi

# --- Check 3: breaking wording in a changelog with no BREAKING marker ---
if [[ "$base_lc" == "changelog.md" || "$base_lc" == "changelog" ]]; then
  if grep -iqE '(removed|no longer|dropped support|renamed|breaking change)' "$file"; then
    if ! grep -qE 'BREAKING' "$file"; then
      warnings+=("CHANGELOG mentions removal/breaking wording but has no explicit 'BREAKING' marker — lead breaking entries with **BREAKING:** and ensure a major bump + deprecation window (best-practices/breaking-changes-need-a-deprecation-window.md).")
    fi
  fi
fi

if [[ ${#warnings[@]} -eq 0 ]]; then
  exit 0
fi

{
  echo "open-source-maintenance — advisory hygiene check flagged $file:"
  for w in "${warnings[@]}"; do
    echo "  • $w"
  done
} >&2

if [[ "${OSS_MAINT_STRICT:-0}" == "1" ]]; then
  exit 2
fi
exit 0
