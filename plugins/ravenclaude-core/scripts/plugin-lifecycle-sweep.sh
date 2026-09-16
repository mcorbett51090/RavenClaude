#!/usr/bin/env bash
# plugin-lifecycle-sweep.sh — SessionStart body for the plugin-lifecycle sweep.
#
# Surfaces "these N plugins have been unused for >= unused_days (default 90)" and
# records the sweep run. OPT-IN, absent => inert: no comfort-posture file, or
# `plugin_lifecycle.tracking: off`, is a no-op after one cheap read.
#
# Uninstall execute is OPT-IN (M2): with auto_uninstall OFF (default) the
# engine never shells uninstall. With auto_uninstall ON, the engine may run
# `claude plugin uninstall <name@marketplace> -y` for fail-closed-eligible
# plugins (pins / mid-flight / unknown requires / ravenclaude-core hard-pin
# still apply). This body NEVER runs the high-blast cache-reset
# disaster-recovery command (AppSec condition 7 / no ragnarok).
#
# Lives under scripts/ (invoked via `bash` from hooks.json), matching the
# ask-on-ambiguity.sh / caveman-route-hook.sh precedent: the tribunal substrate
# guard denies setting the executable bit on a NEW hooks/*.sh, and a
# non-executable hooks/*.sh hard-fails the CI executability check.
#
# FAIL-SAFE: EXIT trap armed first; always exits 0 (SessionStart cannot block).
# PORTABILITY: bash 3.2-safe (no declare -A / mapfile / ${x^^} / globstar); no
# GNU-only timeout / grep -P / sed -i.

trap 'exit 0' EXIT
set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
CFG="$PROJECT_DIR/.ravenclaude/comfort-posture.yaml"

# Cheapest possible no-op for everyone who has not opted in.
[ -f "$CFG" ] || exit 0

ENGINE="${CLAUDE_PLUGIN_ROOT:-}/scripts/plugin-lifecycle.py"
if [ ! -f "$ENGINE" ]; then
  # Fall back to resolving relative to this script (dev-mirror / test invocation).
  SELF_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
  ENGINE="$SELF_DIR/plugin-lifecycle.py"
fi
[ -f "$ENGINE" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

# Mid-flight skip (AppSec 2): plugins used THIS session are recorded by the
# telemetry hook under the session run dir; feed that file to the sweep so an
# in-use plugin is never surfaced for uninstall.
SESSION_MARKER=""
if [ -n "${CLAUDE_SESSION_ID:-}" ]; then
  SESSION_MARKER="$PROJECT_DIR/.ravenclaude/runs/${CLAUDE_SESSION_ID}/plugin-lifecycle-used.txt"
fi

# sweep-hook: marks statuses, computes the fail-closed plan, optionally
# executes opt-in uninstalls, records the run, prints ONE human notice line.
# Never runs any high-blast cache-reset recovery command.
NOTICE="$(python3 "$ENGINE" --project "$PROJECT_DIR" sweep-hook \
  ${SESSION_MARKER:+--session-used-file "$SESSION_MARKER"} 2>/dev/null)" || exit 0

# Surface the notice to the user (stderr) when there is something to say.
if [ -n "$NOTICE" ]; then
  case "$NOTICE" in
    *"no plugins unused"*) : ;; # quiet when clean
    *) printf '%s\n' "$NOTICE" >&2 ;;
  esac
fi

exit 0
