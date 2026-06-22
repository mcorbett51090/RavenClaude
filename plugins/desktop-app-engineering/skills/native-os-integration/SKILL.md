---
name: native-os-integration
description: "Wire native OS integration the way each platform expects — tray/menu-bar, application menus, notifications, file associations, custom-scheme deep links routed through a single-instance lock, and secrets in the OS credential store."
---

# Native OS Integration

## Follow each OS's conventions

- **Tray / menu bar.** A macOS menu-bar item and a Windows system-tray icon behave differently — use the platform idiom, not one cross-OS approximation.
- **Application menus.** macOS expects a real app menu (with the standard App/Edit/Window items); Windows/Linux put menus on the window. Build per-OS menu templates.
- **Notifications.** Use the OS notification API; request/respect permission and the OS Do-Not-Disturb/focus state.

## Single instance + deep links + file associations

Most desktop apps should be **single-instance**:

- Acquire a single-instance lock at startup; if a second launch happens, **focus the running window** and hand it the new argv (the file path or deep-link URL).
- Register a **custom URL scheme** (`myapp://…`) and/or **file associations** at install; route both through the single-instance handler so the app reacts whether it was already running or cold-started.
- **Validate** the deep-link/file payload before acting — it is untrusted input that can arrive from a browser or another app.

## Secrets in the OS store

Tokens/secrets go in the OS credential store — Keychain (macOS), Credential Manager (Windows), libsecret (Linux) — via Electron `safeStorage` or Tauri Stronghold/keyring. Never plaintext config. When Linux has no secret service, name the fallback (e.g. an encrypted file with an explicit weaker-guarantee note) rather than silently writing plaintext.

## Lifecycle

Persist and restore window state; handle minimize-to-tray vs quit per the app's intent; flush unsaved work on `before-quit`.
