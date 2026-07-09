#!/usr/bin/env bash
# setup-terminal-indicators.sh — install the VS Code terminal status indicators
# (tab 🔔 + audio chime + idle-watcher) into a repo + the current user's shell.
#
# Idempotent: safe to run on every Codespace rebuild. Re-running updates the
# installed watcher and re-writes the shell block in place (no duplicate blocks).
#
# Usage:
#   setup-terminal-indicators.sh [--project DIR] [--commands "copilot,claude"]
#     --project DIR    repo whose .vscode/settings.json to configure (default: $PWD)
#     --commands LIST  comma-separated process names the watcher rings for
#                      (default: copilot,claude; sets TERMINAL_WATCHER_COMMANDS)
#
# What it does:
#   1. merges settings-snippet.json into <project>/.vscode/settings.json (non-destructive)
#   2. copies terminal-watcher.py to ~/.local/share/ravenclaude/ (a stable, version-agnostic path)
#   3. installs a marked block in ~/.bashrc: the prompt bell hook + watch-terminals/
#      stop-watching/watcher-log helper functions
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$PWD"
COMMANDS="copilot,claude"

while [ $# -gt 0 ]; do
  case "$1" in
    --project) [ $# -ge 2 ] || { echo "--project requires a value" >&2; exit 2; }; PROJECT="$2"; shift 2 ;;
    --commands) [ $# -ge 2 ] || { echo "--commands requires a value" >&2; exit 2; }; COMMANDS="$2"; shift 2 ;;
    -h | --help) sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

# COMMANDS is interpolated into ~/.bashrc — reject anything outside a safe charset
# so a caller can't inject shell into the user's login file (e.g. --commands 'x";cmd;"').
# WHOLE-STRING check via `case` (a `grep -q` here is line-oriented and a multiline
# value whose first line is benign would slip a payload through on line 2). The glob
# `*[!…]*` matches if ANY char — including a newline — is outside the set.
case "$COMMANDS" in
  "" | *[!A-Za-z0-9_,.-]*)
    echo "invalid --commands '$COMMANDS' (allowed: letters, digits, and _ . , - ; no spaces/newlines)" >&2
    exit 2
    ;;
esac

log() { printf '\n[terminal-indicators] %s\n' "$*"; }

WATCHER_SRC="$SCRIPT_DIR/terminal-watcher.py"
SETTINGS_SRC="$SCRIPT_DIR/settings-snippet.json"
WATCHER_DEST_DIR="$HOME/.local/share/ravenclaude"
WATCHER_DEST="$WATCHER_DEST_DIR/terminal-watcher.py"
BASHRC="${HOME}/.bashrc"
BEGIN_MARK="# >>> ravenclaude terminal-status-indicators >>>"
END_MARK="# <<< ravenclaude terminal-status-indicators <<<"

if ! command -v python3 >/dev/null 2>&1; then
  log "ERROR: python3 not found — the watcher needs it. Aborting."
  exit 1
fi

# ── 1. Merge VS Code settings (non-destructive: only ADD absent keys) ─────────
if [ -f "$SETTINGS_SRC" ]; then
  VSCODE_DIR="$PROJECT/.vscode"
  SETTINGS_FILE="$VSCODE_DIR/settings.json"
  mkdir -p "$VSCODE_DIR"
  log "Merging terminal settings into $SETTINGS_FILE ..."
  SETTINGS_SRC="$SETTINGS_SRC" SETTINGS_FILE="$SETTINGS_FILE" python3 <<'PY'
import json, os, sys

src_path = os.environ["SETTINGS_SRC"]
dst_path = os.environ["SETTINGS_FILE"]
with open(src_path) as f:
    wanted = json.load(f)

existing = {}
if os.path.exists(dst_path):
    try:
        with open(dst_path) as f:
            existing = json.load(f)
    except (json.JSONDecodeError, ValueError):
        print("  WARN: existing settings.json is not strict JSON (comments/trailing "
              "commas?). Not overwriting. Add these keys by hand:")
        for k, v in wanted.items():
            print(f"    {json.dumps(k)}: {json.dumps(v)}")
        sys.exit(0)

added, present = [], []
for k, v in wanted.items():
    if k in existing:
        present.append(k)
    else:
        existing[k] = v
        added.append(k)

if added:
    # Atomic write: a crash mid-write must not truncate the user's settings.json.
    tmp = dst_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(existing, f, indent=2)
        f.write("\n")
    os.replace(tmp, dst_path)
    print("  added: " + ", ".join(added))
if present:
    print("  left as-is (already set): " + ", ".join(present))
if not added and not present:
    print("  nothing to do")
PY
else
  log "WARN: settings-snippet.json not found next to this script — skipping settings merge."
fi

# ── 2. Install the watcher to a stable, version-agnostic path ─────────────────
if [ -f "$WATCHER_SRC" ]; then
  mkdir -p "$WATCHER_DEST_DIR"
  cp "$WATCHER_SRC" "$WATCHER_DEST"
  chmod +x "$WATCHER_DEST"
  log "Installed watcher -> $WATCHER_DEST"
else
  log "ERROR: terminal-watcher.py not found next to this script. Aborting."
  exit 1
fi

# ── 3. Install / refresh the ~/.bashrc block (idempotent, marker-bounded) ─────
touch "$BASHRC"
# Strip a prior block so a re-run updates in place. Data-loss-safe: only strip a
# SINGLE, correctly-ordered, exact-line-matched marker pair. Any other state
# (lone marker, duplicate markers, out-of-order) → leave the file untouched and
# skip the install, rather than risk deleting user content to EOF.
SKIP_BASHRC=""
nb=$(grep -cxF "$BEGIN_MARK" "$BASHRC" || true)
ne=$(grep -cxF "$END_MARK" "$BASHRC" || true)
if [ "$nb" = 0 ] && [ "$ne" = 0 ]; then
  log "Adding shell block to $BASHRC"
elif [ "$nb" = 1 ] && [ "$ne" = 1 ]; then
  bl=$(grep -nxF "$BEGIN_MARK" "$BASHRC" | cut -d: -f1)
  el=$(grep -nxF "$END_MARK" "$BASHRC" | cut -d: -f1)
  if [ "$bl" -lt "$el" ]; then
    tmp="$(mktemp)"
    # Strip by LINE NUMBER (not content match) so nothing outside [bl,el] is lost.
    awk -v b="$bl" -v e="$el" 'NR < b || NR > e { print }' "$BASHRC" >"$tmp"
    mv "$tmp" "$BASHRC"
    log "Refreshed existing shell block in $BASHRC"
  else
    log "WARN: markers out of order in $BASHRC — leaving it untouched. Fix by hand, then re-run."
    SKIP_BASHRC=1
  fi
else
  log "WARN: unexpected marker state (begin=$nb end=$ne) in $BASHRC — leaving it untouched. Fix by hand, then re-run."
  SKIP_BASHRC=1
fi

if [ -z "$SKIP_BASHRC" ]; then
cat >>"$BASHRC" <<EOF
$BEGIN_MARK
# Ring the terminal bell when a shell command finishes so a VS Code tab shows 🔔.
# Guard on an INTERACTIVE shell (\$- contains 'i') so a non-interactive shell that
# sources ~/.bashrc (BASH_ENV, scripts) never installs the DEBUG trap or rings a bell.
# Match all xterm variants (Codespaces uses xterm-256color; a literal "xterm" test
# would never fire) and VS Code's injected integration.
if [[ \$- == *i* ]] && { [[ "\$TERM" == xterm* ]] || [[ -n "\${VSCODE_INJECTION:-}" ]] || [[ -n "\${VSCODE_SHELL_INTEGRATION:-}" ]]; }; then
    # The bell (precmd) is the core feature — chained safely onto PROMPT_COMMAND.
    __rc_ti_precmd()  { printf '\033]0;%s@%s: bash\007' "\${USER:-user}" "\${HOSTNAME:-host}"; printf '\a'; }
    case "\${PROMPT_COMMAND:-}" in
        *__rc_ti_precmd*) : ;;                                                     # already wired
        *) PROMPT_COMMAND="\${PROMPT_COMMAND:+\$PROMPT_COMMAND; }__rc_ti_precmd" ;;
    esac
    # The title update uses a DEBUG trap. Only install it if nothing else owns
    # DEBUG (bash-preexec / starship / atuin) — clobbering theirs would break
    # their history/prompt tooling; the bell above works regardless.
    if [[ -z "\$(trap -p DEBUG)" ]]; then
        __rc_ti_preexec() { printf '\033]0;▶ %s\007' "\${BASH_COMMAND}"; }
        trap '__rc_ti_preexec' DEBUG
    fi
fi
export TERMINAL_WATCHER_PY="\${TERMINAL_WATCHER_PY:-$WATCHER_DEST}"
export TERMINAL_WATCHER_COMMANDS="\${TERMINAL_WATCHER_COMMANDS:-$COMMANDS}"
watch-terminals() {
    if python3 "\$TERMINAL_WATCHER_PY" --is-running 2>/dev/null; then
        echo "[watcher] already running (pid=\$(head -n1 /tmp/terminal-watcher.pid 2>/dev/null))"
        return 0
    fi
    nohup python3 "\$TERMINAL_WATCHER_PY" >/tmp/terminal-watcher.log 2>&1 &
    echo "[watcher] started (pid=\$!) — log: /tmp/terminal-watcher.log"
}
stop-watching() { python3 "\$TERMINAL_WATCHER_PY" --stop; }
watcher-log()   { tail -f /tmp/terminal-watcher.log; }
$END_MARK
EOF
fi

log "Done. In a NEW terminal (or after 'source ~/.bashrc'):"
log "  watch-terminals   # start the idle-watcher"
log "  watcher-log       # follow its log"
log "  stop-watching     # stop it"
