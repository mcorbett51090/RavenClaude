---
description: "Audit + harden an Electron app to the secure baseline and convert any raw IPC into a narrow validated allow-list."
argument-hint: "[path to the Electron app or the window/preload code]"
---

You are running `/desktop-app-engineering:harden-electron`. Use `electron-engineer` + the `electron-security-hardening` skill.

## Steps

1. Check every BrowserWindow against the baseline (contextIsolation on, nodeIntegration off, sandbox on, strict CSP, no remote).
2. Find raw `ipcRenderer`/`require` exposure; replace with a named `contextBridge` API + validated `ipcMain.handle` handlers.
3. Validate every IPC argument; resolve paths against an allowed base.
4. Fill `templates/ipc-security-review.md`; route concrete appsec verdicts to `ravenclaude-core/security-reviewer`.
5. Emit findings + a Structured Output block.
