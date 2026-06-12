---
name: desktop-framework-choice
description: "Decide Electron vs Tauri vs native vs PWA by the app's real needs (bundle size, native-API depth, team skills, security surface, update needs), then set the process/security model and the renderer/backend boundary."
---

# Desktop Framework Choice

## The decision

| Need | Approach |
|---|---|
| Large existing web UI, deep native integration, one cross-platform team, mature ecosystem | **Electron** (bundled Chromium + Node; heavy bundle, ~100–200MB) |
| Small footprint, tight security surface, Rust comfort, system-webview acceptable | **Tauri** (Rust core + system webview; small bundle, secure-by-default capabilities) |
| Top-tier per-OS UX, platform-native feel, no web layer | **Native** (SwiftUI / WinUI / Qt / GTK) |
| Mostly web, light OS needs (notifications, install) | **PWA** — skip the desktop shell entirely |

Name the trade; don't default to what the team already knows.

## The non-negotiable: the renderer is untrusted

Web content can be compromised. It gets OS access **only** through a narrow allow-list:

- **Electron:** `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`, a strict CSP, and a minimal `contextBridge` backed by validated `ipcMain.handle` handlers.
- **Tauri:** a least-privilege **capabilities/permissions** set (v2) — only the commands a window needs, no wildcard `fs`/`shell` scopes.

## The renderer/backend line

Secrets, signing keys, privileged OS calls, and the data/sync API live behind the native process or a remote backend — never in the webview bundle. Route the remote contract to `api-engineering`/`backend-engineering`.

## Storage

App data in the per-OS app-data directory; secrets in the OS keychain/credential store (never plaintext `config.json`).
