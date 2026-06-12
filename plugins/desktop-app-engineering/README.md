# desktop-app-engineering

> Build cross-platform desktop apps well — the **missing app-craft sibling** of `backend` / `frontend` / `mobile` / `api` / `database` / `auth-identity`. A 4-agent team for the Electron-vs-Tauri-vs-native-vs-PWA decision, a hardened process/security model, packaging + code-signing + safe auto-update, and native OS integration.

## What you get

- **4 specialist agents**
  - `desktop-architect` — framework choice (Electron / Tauri / native / PWA), the process/security model, the renderer/backend boundary, distribution + updates.
  - `electron-engineer` — the main/preload/renderer model, the hardened baseline (contextIsolation / nodeIntegration off / sandbox / CSP), a narrow `contextBridge` + validated `ipcMain` handlers, the build.
  - `tauri-engineer` — the Rust core + system webview, `#[tauri::command]` handlers with validated input, the v2 capabilities/permissions allow-list, sidecars, state.
  - `desktop-platform-engineer` — code-signing + notarization (Win + macOS), safe signed auto-update (channels / staged rollout / rollback / version floor), and native OS integration (tray, menus, notifications, file associations, deep links, secure storage).
- **5 skills** — desktop-framework-choice, electron-security-hardening, tauri-capabilities-and-commands, packaging-signing-and-updates, native-os-integration.
- **A decision-tree knowledge bank** — framework-choice + IPC-security + signing/update Mermaid trees, a storage prior, and a dated 2026 capability map (`[verify-at-use]`).
- **12 best-practices**, **4 templates**, **4 commands**, **1 advisory hook**, a **3-scenario bank**, and an **`.lsp.json`** (TypeScript + Rust).

## Commands

- `/desktop-app-engineering:choose-desktop-framework` — Electron vs Tauri vs native vs PWA, with the security model + renderer/backend boundary.
- `/desktop-app-engineering:harden-electron` — audit + harden an Electron app to the secure baseline; convert raw IPC into a validated allow-list.
- `/desktop-app-engineering:scope-tauri-capabilities` — tighten a Tauri app's capabilities to least privilege; validate command inputs.
- `/desktop-app-engineering:plan-release-signing` — plan signing + notarization (Win + macOS) and a safe signed auto-update.

## House opinions

1. Choose the framework by the app's needs, not by what the team already knows — and name the trade.
2. The renderer is untrusted web content; it reaches the OS only through a narrow, validated allow-list.
3. The secure baseline has no exceptions (contextIsolation on / nodeIntegration off / sandbox on / least-privilege Tauri capabilities).
4. Sign + notarize every release; keys in CI secrets, never a laptop.
5. Auto-update is signed, staged, and reversible — verify the signature before apply, roll out in stages, keep a rollback + version floor.
6. Secrets in the OS credential store; app data in the per-OS app-data dir.

## Seams

Renderer UI → `frontend-engineering` · backend/API → `api-engineering` / `backend-engineering` · auth flow → `auth-identity` · CI signing → `devops-cicd` · the mobile sibling → `mobile-engineering` · appsec verdicts → `ravenclaude-core/security-reviewer`.

## Requirements

Requires `ravenclaude-core@>=0.7.0`. The `.lsp.json` servers (typescript-language-server, rust-analyzer) are installed separately by the consumer; the plugin ships the config, not the binaries.

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and [`CHANGELOG.md`](CHANGELOG.md) for version history.
