#!/usr/bin/env bash
# open-dashboard.sh — one command to open the marketplace's own comfort-posture
# dashboard (the unified index.html portal, served with live /__* endpoints).
#
#   (default)   probe for a dashboard already serving THIS checkout and REUSE it;
#               otherwise start one on port 8000 (background, survives this script)
#               and print the actually-bound URL.
#   --stop      stop this checkout's dashboard server(s) found on the 8000 walk range.
#   --stop-all  stop every dashboard server that belongs to THIS checkout, any port.
#   --no-open   do not open a browser (postStartCommand / CI / non-interactive).
#   --port N    use port N instead of 8000 (a bare numeric first arg also works).
#   -h, --help  show this help.
#
# It launches the ROOT dev server (scripts/serve-dashboards.py). That server's
# REPO_ROOT is derived from its own __file__ and os.chdir'd, so it always serves
# THIS checkout — run it from a worktree and it edits THAT worktree's
# .ravenclaude/comfort-posture.yaml. It NEVER kills a process it has not positively
# identified as this checkout's own server (a fail-closed ps-command + cwd match).
# Consumer repos use .ravenclaude/dashboard.sh / `rc dashboard` instead.
set -euo pipefail

usage() {
  sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^#\{1,\} \{0,1\}//'
}

# ── Resolve this checkout's root + its ROOT server ──────────────────────────────
# Prefer the git top-level (worktree-correct — the plan's H1 reason for spawning the
# ROOT server of the current checkout); fall back to the script's own location when
# git is unavailable or points at a tree without our server.
_git_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
_script_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -n "$_git_root" ] && [ -f "$_git_root/scripts/serve-dashboards.py" ]; then
  ROOT="$_git_root"
else
  ROOT="$_script_root"
fi
SERVER="$ROOT/scripts/serve-dashboards.py"
[ -f "$SERVER" ] || {
  echo "dashboard server not found: $SERVER" >&2
  exit 1
}

# ── Parse args ──────────────────────────────────────────────────────────────────
PORT=8000
ACTION=start
OPEN=1
while [ $# -gt 0 ]; do
  case "$1" in
    --stop) ACTION=stop ;;
    --stop-all) ACTION=stop_all ;;
    --no-open) OPEN=0 ;;
    --port)
      shift
      PORT="${1:?--port needs a value}"
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    '' | *[!0-9]*)
      echo "unknown argument: $1 (see --help)" >&2
      exit 2
      ;;
    *) PORT="$1" ;; # a bare all-digits token is the port (back-compat)
  esac
  shift
done
# The ROOT server walks range(PORT, PORT+6) = 6 ports; poll/scan the same span so a
# fallback bind is still found (deletes the old 6-vs-11 poll-range mismatch).
WALK=5

# ── Mirror serve-dashboards.py's _port_holder_pids / _holder_cwd / _is_our_dashboard ──
# The launcher is bash, so it shells out to lsof/ps rather than importing them. The
# check is FAIL-CLOSED and two-part — a serve-dashboards.py process whose resolved cwd
# equals THIS checkout — so we never signal an unrelated server (another project's live
# dashboard included).
_holder_pids() { # $1 = port -> PIDs LISTENing on it
  lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null || true
}
_is_our_dashboard() { # $1 = pid -> 0 iff it is a serve-dashboards.py serving THIS checkout
  local pid="$1" cmd cwd
  cmd="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  case "$cmd" in
    *serve-dashboards.py*) ;;
    *) return 1 ;;
  esac
  cwd="$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -1)"
  [ -n "$cwd" ] || return 1
  [ "$(cd "$cwd" 2>/dev/null && pwd -P || true)" = "$(cd "$ROOT" && pwd -P)" ]
}

# ── --stop / --stop-all: SIGTERM ONLY this checkout's own servers ────────────────
if [ "$ACTION" = stop ] || [ "$ACTION" = stop_all ]; then
  pids=""
  if [ "$ACTION" = stop_all ]; then
    pids="$(pgrep -f 'serve-dashboards\.py' 2>/dev/null || true)"
  else
    for cand in $(seq "$PORT" $((PORT + WALK))); do
      pids="$pids $(_holder_pids "$cand")"
    done
  fi
  stopped=0
  for pid in $(printf '%s\n' $pids | sort -un); do
    if _is_our_dashboard "$pid"; then
      if kill "$pid" 2>/dev/null; then
        echo "stopped serve-dashboards.py (pid $pid) for $ROOT"
        stopped=$((stopped + 1))
      fi
    fi
  done
  [ "$stopped" -gt 0 ] || echo "no running dashboard server for this checkout ($ROOT)"
  exit 0
fi

announce_and_open() { # $1 = bound port
  local port="$1" url browser_bin
  if [ -n "${CODESPACE_NAME:-}" ]; then
    url="https://${CODESPACE_NAME}-${port}.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}/index.html"
  else
    url="http://127.0.0.1:${port}/index.html"
  fi
  if [ "$OPEN" -eq 1 ] && [ -t 1 ]; then
    # Resolve the first word of $BROWSER via PATH so a bare command name (BROWSER=firefox)
    # is honored, not just an absolute path. Time-bound the fallback so a terminal browser
    # can never block. Skipped when there is no controlling TTY (postStartCommand / CI).
    browser_bin="$(command -v "${BROWSER%% *}" 2>/dev/null || true)"
    if [ -n "${BROWSER:-}" ] && [ -n "$browser_bin" ]; then
      read -ra browser_cmd <<<"$BROWSER"
      "${browser_cmd[@]}" "$url" >/dev/null 2>&1 || true
    else
      timeout 5 python3 -m webbrowser "$url" >/dev/null 2>&1 || true
    fi
  fi
  echo "Dashboard: $url"
}

# ── Probe-then-reuse: adopt a live server that already serves THIS checkout ──────
find_our_live_port() {
  local cand pid
  for cand in $(seq "$PORT" $((PORT + WALK))); do
    if curl -fsS -o /dev/null "http://127.0.0.1:${cand}/index.html" 2>/dev/null; then
      for pid in $(_holder_pids "$cand"); do
        if _is_our_dashboard "$pid"; then
          echo "$cand"
          return 0
        fi
      done
    fi
  done
  return 1
}

if reuse_port="$(find_our_live_port)"; then
  echo "Reusing the dashboard already serving this checkout ($ROOT)."
  announce_and_open "$reuse_port"
  exit 0
fi

# ── Spawn the ROOT server, fully detached so it outlives this script ─────────────
# Create the log via mktemp (O_EXCL, unpredictable suffix) rather than a fixed,
# world-predictable /tmp path opened with ">" — a plain redirect follows a symlink.
LOG="$(mktemp "/tmp/rc-dashboard-${PORT}-XXXXXX.log" 2>/dev/null)" || LOG="/tmp/rc-dashboard-${PORT}.$$.log"
bind_args=()
if [ -z "${CODESPACE_NAME:-}" ]; then
  # Explicit loopback bind off-Codespace (C2 — stronger than relying on the default).
  # In a Codespace let the server default to 0.0.0.0 so the forwarded port is
  # reachable — the pre-existing deliberate branch, safe because nothing auto-starts.
  bind_args=(--bind 127.0.0.1)
fi
nohup python3 "$SERVER" --port "$PORT" --no-open "${bind_args[@]}" >"$LOG" 2>&1 &
disown 2>/dev/null || true

# Wait until it answers, discovering the ACTUAL bound port. The server reclaims a
# stale server OF OURS on $PORT, else walks PORT..PORT+5, so never assume $PORT bound.
bound_port=""
for _ in $(seq 1 20); do
  for cand in $(seq "$PORT" $((PORT + WALK))); do
    if curl -fsS -o /dev/null "http://127.0.0.1:${cand}/index.html" 2>/dev/null; then
      bound_port="$cand"
      break 2
    fi
  done
  sleep 0.5
done
if [ -z "$bound_port" ]; then
  echo "dashboard server did not come up — see $LOG" >&2
  exit 1
fi
announce_and_open "$bound_port"
echo "(server log: $LOG — run 'bash scripts/open-dashboard.sh --stop' to stop it)"
