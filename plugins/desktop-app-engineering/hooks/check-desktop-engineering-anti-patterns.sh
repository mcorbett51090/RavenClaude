#!/usr/bin/env bash
# check-desktop-engineering-anti-patterns.sh — advisory PreToolUse hook for the desktop-app-engineering plugin.
# Flags mechanically-detectable desktop security anti-patterns on Edit/Write/MultiEdit. Advisory by
# default (exit 0, prints a notice); set DESKTOP_STRICT=1 to make it blocking (exit 2).
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

findings=()

# Electron: insecure webPreferences.
if grep -nEi "nodeintegration[[:space:]]*:[[:space:]]*true" "$file" >/dev/null 2>&1; then
  findings+=("Electron: 'nodeIntegration: true' exposes Node to untrusted web content — keep it false and bridge via contextBridge.")
fi
if grep -nEi "contextisolation[[:space:]]*:[[:space:]]*false" "$file" >/dev/null 2>&1; then
  findings+=("Electron: 'contextIsolation: false' breaks the preload trust boundary — keep it true.")
fi
if grep -nEi "(sandbox[[:space:]]*:[[:space:]]*false|websecurity[[:space:]]*:[[:space:]]*false)" "$file" >/dev/null 2>&1; then
  findings+=("Electron: sandbox/webSecurity disabled — keep both on; disabling them removes OS-level renderer isolation.")
fi
if grep -nEi "(allowrunninginsecurecontent[[:space:]]*:[[:space:]]*true|@electron/remote|enableremotemodule[[:space:]]*:[[:space:]]*true)" "$file" >/dev/null 2>&1; then
  findings+=("Electron: insecure content / remote module enabled — drop @electron/remote and don't allow insecure content.")
fi

# Tauri: wildcard fs/shell capability scopes.
if grep -nEi "(\"fs:allow-(read|write)?-?all|shell:allow-execute|\"fs:default\"[[:space:]]*,?[[:space:]]*\"shell)" "$file" >/dev/null 2>&1; then
  findings+=("Tauri: wildcard fs/shell capability — scope to exact paths / exact program+args, never allow-all.")
fi

# Secrets in plaintext / web storage.
if grep -nEi "(localstorage|sessionstorage)\.setitem\(.*(token|secret|password|apikey|api_key|credential)" "$file" >/dev/null 2>&1; then
  findings+=("Secret written to localStorage/sessionStorage — use the OS credential store (safeStorage/Keychain/Credential Manager).")
fi

# Deprecated macOS notarization tool.
if grep -nEi "\baltool\b" "$file" >/dev/null 2>&1; then
  findings+=("macOS: 'altool' is deprecated for notarization — use 'notarytool'.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── desktop-app-engineering advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${DESKTOP_STRICT:-0}" = "1" ]; then
  echo "(blocking: DESKTOP_STRICT=1)" >&2
  exit 2
fi
exit 0
