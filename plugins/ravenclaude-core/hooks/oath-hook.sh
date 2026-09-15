#!/usr/bin/env bash
# oath-hook.sh — Oath-hook (GUPP) SessionStart surface.
#
# If ledger-backed Runes hang on this actor's hook, inject MUST-RUN context.
# SessionStart cannot block; always exit 0. Fail-silent.
#
# Cosmology: docs/norse-mythology-feature-map.md (do not overload Norns panel).
# Delivery batch = Longship (Sage sole land; never auto-merge).

set -euo pipefail

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
command -v python3 >/dev/null 2>&1 || exit 0

assembler="${CLAUDE_PLUGIN_ROOT:-}/scripts/oath_hook.py"
if [[ ! -f "$assembler" ]]; then
  scripts_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../scripts" 2>/dev/null && pwd || true)"
  assembler="${scripts_dir:-}/oath_hook.py"
fi
[[ -f "$assembler" ]] || exit 0

out="$(python3 "$assembler" --root "$project_dir" 2>/dev/null || true)"
[[ -n "$out" ]] && printf '%s\n' "$out"
exit 0
