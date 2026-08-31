#!/usr/bin/env bash
# resolve-plugin-root.sh — print the ravenclaude-core plugin root that holds
# ALL THREE FORGE helpers (forge-route.py, forge-worktree.sh, premise-gate.py).
#
# Why: /forge and skills/forge-pipeline cite helpers as
# ${CLAUDE_PLUGIN_ROOT}/scripts/…. Claude Code sets that variable. VS Code
# Copilot Chat (and a consumer tree after ravenclaude install) does not.
# This script finds the same directory without requiring the variable.
#
# A PARTIAL set is a fail — never "routing exists, premise/worktree do not".
# Missing any one of the three is exit 2, same as finding nothing.
#
# Resolution order (first hit that has all three):
#   1. $CLAUDE_PLUGIN_ROOT
#   2. $PLUGIN_ROOT (Codex / _portable.sh alias)
#   3. this script's parent (invoke-by-path; dirname $0/..)
#   4. skill-symlink walk: .claude/skills/forge-pipeline and
#      .agents/skills/forge-pipeline, from cwd then $CLAUDE_PROJECT_DIR
#   5. command -v rc → bin/rc → ..
#   6. $RAVENCLAUDE_MARKET/plugins/ravenclaude-core
#
# Portability: bash 3.2 (no declare -A / mapfile / ${x^^} / grep -P / sed -i).
#
# Usage:
#   resolve-plugin-root.sh              print plugin root, exit 0
#   resolve-plugin-root.sh --self-test  scratch fixtures (nonzero on failure)
#
# Exit 0 = printed an absolute plugin root.
# Exit 2 = no candidate held all three; stderr names every try.
# Exit 1 = usage / could-not-run.

set -euo pipefail

_TRIED=""

_note() {
  # $1 = label
  _TRIED="${_TRIED}  - ${1}
"
}

_abs() {
  # $1 = path; print realpath. python3 first (this repo requires it); else cd.
  if command -v python3 >/dev/null 2>&1; then
    python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))" "$1" 2>/dev/null && return 0
  fi
  (cd "$1" 2>/dev/null && pwd)
}

_has_three() {
  local root="${1:-}"
  [ -n "$root" ] || return 1
  [ -f "$root/scripts/forge-route.py" ] || return 1
  [ -f "$root/scripts/forge-worktree.sh" ] || return 1
  [ -f "$root/scripts/premise-gate.py" ] || return 1
  return 0
}

# If $2 is a plugin root with all three helpers, print it and return 0.
_try() {
  local label="$1" cand="$2"
  _note "$label → ${cand:-<empty>}"
  [ -n "$cand" ] || return 1
  local abs
  abs="$(_abs "$cand")" || return 1
  [ -n "$abs" ] || return 1
  if _has_three "$abs"; then
    printf '%s\n' "$abs"
    return 0
  fi
  return 1
}

_skill_walk() {
  # $1 = base directory to look in
  local base="$1" rel p real root
  [ -n "$base" ] && [ -d "$base" ] || return 1
  for rel in .claude/skills/forge-pipeline .agents/skills/forge-pipeline; do
    p="${base}/${rel}"
    if [ -e "$p" ]; then
      real="$(_abs "$p")" || continue
      [ -n "$real" ] || continue
      # skill dir is …/ravenclaude-core/skills/forge-pipeline → ../.. = plugin root
      root="$(cd "$real/../.." 2>/dev/null && pwd)" || continue
      if _try "skill-walk ${rel} from ${base}" "$root"; then
        return 0
      fi
    else
      _note "skill-walk ${rel} from ${base} → <missing>"
    fi
  done
  return 1
}

_self_root() {
  local src link
  src="${BASH_SOURCE[0]}"
  if [ -L "$src" ]; then
    link="$(readlink "$src")"
    case "$link" in
      /*) src="$link" ;;
      *) src="$(dirname "$src")/${link}" ;;
    esac
  fi
  (cd "$(dirname "$src")/.." && pwd)
}

cmd_resolve() {
  local root rc_path rc_dir market

  if _try "CLAUDE_PLUGIN_ROOT" "${CLAUDE_PLUGIN_ROOT:-}"; then
    return 0
  fi
  if _try "PLUGIN_ROOT" "${PLUGIN_ROOT:-}"; then
    return 0
  fi
  if _try "script-parent" "$(_self_root)"; then
    return 0
  fi

  if _skill_walk "$PWD"; then
    return 0
  fi
  if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ "${CLAUDE_PROJECT_DIR}" != "$PWD" ]; then
    if _skill_walk "$CLAUDE_PROJECT_DIR"; then
      return 0
    fi
  fi

  rc_path="$(command -v rc 2>/dev/null || true)"
  if [ -n "$rc_path" ]; then
    if [ -L "$rc_path" ]; then
      link="$(readlink "$rc_path")"
      case "$link" in
        /*) rc_path="$link" ;;
        *) rc_path="$(dirname "$rc_path")/${link}" ;;
      esac
    fi
    rc_dir="$(cd "$(dirname "$rc_path")/.." 2>/dev/null && pwd)" || rc_dir=""
    if _try "command -v rc" "$rc_dir"; then
      return 0
    fi
  else
    _note "command -v rc → <not on PATH>"
  fi

  if [ -n "${RAVENCLAUDE_MARKET:-}" ]; then
    market="${RAVENCLAUDE_MARKET}/plugins/ravenclaude-core"
    if _try "RAVENCLAUDE_MARKET" "$market"; then
      return 0
    fi
  else
    _note "RAVENCLAUDE_MARKET → <unset>"
  fi

  printf 'resolve-plugin-root.sh: no candidate held all three FORGE helpers\n' >&2
  printf '(scripts/forge-route.py, scripts/forge-worktree.sh, scripts/premise-gate.py).\n' >&2
  printf 'Tried:\n%s' "$_TRIED" >&2
  return 2
}

# --- self-test --------------------------------------------------------------

_st_fail() {
  echo "SELF-TEST FAIL: $1" >&2
  ST_RC=1
}

_plant_three() {
  # $1 = plugin root
  mkdir -p "$1/scripts" "$1/skills/forge-pipeline"
  : >"$1/scripts/forge-route.py"
  : >"$1/scripts/forge-worktree.sh"
  : >"$1/scripts/premise-gate.py"
}

cmd_self_test() {
  ST_RC=0
  local scratch lonely plugin consumer out rc
  scratch="$(mktemp -d "${TMPDIR:-/tmp}/rpr-st.XXXXXX")"
  # A copy of THIS script that is NOT next to the three helpers, so
  # script-parent does not short-circuit the env / walk fixtures.
  lonely="${scratch}/lonely"
  mkdir -p "$lonely"
  cp "$0" "${lonely}/resolve-plugin-root.sh"
  chmod +x "${lonely}/resolve-plugin-root.sh"

  # Fixture 1: CLAUDE_PLUGIN_ROOT set to a fake plugin with the three files.
  plugin="${scratch}/p1"
  _plant_three "$plugin"
  out="$(CLAUDE_PLUGIN_ROOT="$plugin" PLUGIN_ROOT="" RAVENCLAUDE_MARKET="" \
    env -u CLAUDE_PROJECT_DIR \
    bash "${lonely}/resolve-plugin-root.sh" 2>/dev/null)" || rc=$?
  rc="${rc:-0}"
  if [ "$rc" -ne 0 ] || [ "$(_abs "$out")" != "$(_abs "$plugin")" ]; then
    _st_fail "CLAUDE_PLUGIN_ROOT hit (rc=$rc out=$out)"
  fi

  # Fixture 2: unset + .claude/skills/forge-pipeline symlink.
  plugin="${scratch}/p2"
  consumer="${scratch}/c2"
  _plant_three "$plugin"
  mkdir -p "${consumer}/.claude/skills"
  ln -s "$plugin/skills/forge-pipeline" "${consumer}/.claude/skills/forge-pipeline"
  rc=0
  out="$(cd "$consumer" && env -u CLAUDE_PLUGIN_ROOT -u PLUGIN_ROOT -u RAVENCLAUDE_MARKET \
    -u CLAUDE_PROJECT_DIR PATH="/usr/bin:/bin" \
    bash "${lonely}/resolve-plugin-root.sh" 2>/dev/null)" || rc=$?
  if [ "$rc" -ne 0 ] || [ "$(_abs "$out")" != "$(_abs "$plugin")" ]; then
    _st_fail "skill-walk .claude (rc=$rc out=$out)"
  fi

  # Fixture 3: unset + .agents/skills/forge-pipeline symlink (Codex path).
  plugin="${scratch}/p3"
  consumer="${scratch}/c3"
  _plant_three "$plugin"
  mkdir -p "${consumer}/.agents/skills"
  ln -s "$plugin/skills/forge-pipeline" "${consumer}/.agents/skills/forge-pipeline"
  rc=0
  out="$(cd "$consumer" && env -u CLAUDE_PLUGIN_ROOT -u PLUGIN_ROOT -u RAVENCLAUDE_MARKET \
    -u CLAUDE_PROJECT_DIR PATH="/usr/bin:/bin" \
    bash "${lonely}/resolve-plugin-root.sh" 2>/dev/null)" || rc=$?
  if [ "$rc" -ne 0 ] || [ "$(_abs "$out")" != "$(_abs "$plugin")" ]; then
    _st_fail "skill-walk .agents (rc=$rc out=$out)"
  fi

  # Fixture 4: cp -r skill (no symlink) must NOT invent a path.
  plugin="${scratch}/p4"
  consumer="${scratch}/c4"
  _plant_three "$plugin"
  mkdir -p "${consumer}/.claude/skills"
  cp -R "$plugin/skills/forge-pipeline" "${consumer}/.claude/skills/forge-pipeline"
  rc=0
  out="$(cd "$consumer" && env -u CLAUDE_PLUGIN_ROOT -u PLUGIN_ROOT -u RAVENCLAUDE_MARKET \
    -u CLAUDE_PROJECT_DIR PATH="/usr/bin:/bin" \
    bash "${lonely}/resolve-plugin-root.sh" 2>/dev/null)" || rc=$?
  if [ "$rc" -eq 0 ]; then
    _st_fail "cp -r skill invented a path ($out)"
  fi
  if [ "$rc" -ne 2 ]; then
    _st_fail "cp -r skill expected exit 2, got $rc"
  fi

  # Fixture 5: all candidates empty → exit 2, stderr lists tries.
  consumer="${scratch}/c5"
  mkdir -p "$consumer"
  rc=0
  err="$(cd "$consumer" && env -u CLAUDE_PLUGIN_ROOT -u PLUGIN_ROOT -u RAVENCLAUDE_MARKET \
    -u CLAUDE_PROJECT_DIR PATH="/usr/bin:/bin" \
    bash "${lonely}/resolve-plugin-root.sh" 2>&1 >/dev/null)" || rc=$?
  if [ "$rc" -ne 2 ]; then
    _st_fail "empty candidates expected exit 2, got $rc"
  fi
  printf '%s' "$err" | grep -q 'Tried:' || _st_fail "empty candidates stderr missing Tried:"

  # Fixture 6: plugin root missing one of the three → exit 2.
  plugin="${scratch}/p6"
  _plant_three "$plugin"
  rm -f "$plugin/scripts/premise-gate.py"
  rc=0
  out="$(CLAUDE_PLUGIN_ROOT="$plugin" PLUGIN_ROOT="" RAVENCLAUDE_MARKET="" \
    env -u CLAUDE_PROJECT_DIR PATH="/usr/bin:/bin" \
    bash "${lonely}/resolve-plugin-root.sh" 2>/dev/null)" || rc=$?
  if [ "$rc" -eq 0 ]; then
    _st_fail "missing-one-of-three accepted ($out)"
  fi
  if [ "$rc" -ne 2 ]; then
    _st_fail "missing-one-of-three expected exit 2, got $rc"
  fi

  rm -rf "$scratch"
  if [ "$ST_RC" -eq 0 ]; then
    echo "SELF-TEST PASS: resolve-plugin-root.sh (6 fixtures)"
  fi
  return "$ST_RC"
}

main() {
  local sub="${1:-}"
  case "$sub" in
    --self-test | self-test) cmd_self_test ;;
    "" )
      cmd_resolve
      ;;
    -h | --help | help)
      grep -E '^#( |$)' "$0" | sed -E 's/^# ?//'
      ;;
    *)
      echo "resolve-plugin-root.sh: unknown argument '$sub' (try --self-test)" >&2
      exit 1
      ;;
  esac
}

main "$@"
