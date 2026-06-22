---
scenario_id: 2026-06-12-electron-nodeintegration-rce
contributed_at: 2026-06-12
plugin: desktop-app-engineering
product: electron
product_version: "unknown"
scope: likely-general
tags: [electron, security, nodeintegration, context-isolation, rce, xss]
confidence: high
reviewed: false
---

## Problem

An Electron app embedded a third-party web view (a help/docs panel and an in-app "what's new" page loaded from a remote URL) inside a `BrowserWindow` that had `nodeIntegration: true` and `contextIsolation: false` — turned on early in the project so the renderer could "just use `fs` and `path` directly." A security review flagged it: any script that executed in that window — from the remote page, a compromised dependency, or a stored-XSS string rendered without escaping — had full Node.js access and could read/write the user's filesystem and spawn processes. It was a remote-code-execution hole, not a theoretical one.

## Constraints context

- The renderer genuinely used a few Node APIs (read a local config file, resolve paths), which is *why* `nodeIntegration` had been switched on — disabling it looked like it would break working features.
- The app loaded **remote** content in the same window class, so "we control the page" was false for at least one window.
- Shipping was close; the team wanted the smallest safe change, not a rewrite.

## Attempts

- Tried: keeping `nodeIntegration: true` but "sanitizing" the remote HTML. Rejected — input sanitization is not a security boundary against a window that already has Node; one missed escape or one compromised dependency re-opens RCE.
- Tried: a separate, locked-down window only for remote content, leaving the "trusted" local windows with Node on. Better, but still left every local window one stored-XSS away from RCE, and the boundary now depended on never loading anything untrusted in a "trusted" window — a rule that erodes.
- Tried (the fix): turned the baseline back to secure for **every** window (`contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`) and moved the handful of real Node needs into the **main process** behind named, validated `ipcMain.handle` handlers, exposed to the renderer through a minimal `contextBridge` API.

## Resolution

**The renderer never gets Node; the few things it legitimately needs go through a narrow, validated IPC allow-list.** The shape that worked:

1. **Secure baseline everywhere.** `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`, strict CSP, no `@electron/remote` — uniformly, with no "trusted window" exception that would rot.
2. **Move the work, not the boundary.** Each real Node need (read config, resolve a path) became a named main-process operation (`config:read`, etc.), each validating its arguments, exposed via `contextBridge.exposeInMainWorld("api", { … })`.
3. **Remote content stays sandboxed and CSP-restricted**, and external links open via `shell.openExternal` after URL validation rather than navigating the app window.

The mental model: the renderer is a web page on the open internet that happens to be yours today. Give it Node and you've shipped a browser with filesystem access to whoever compromises any script it runs.

**Action for the next engineer:** if a renderer "needs `fs`," that is never a reason to enable `nodeIntegration` — it's a reason to add one validated IPC command. Audit every `BrowserWindow` for the secure baseline; a single window with the boundary off is the whole app's RCE surface.

Cross-reference: complements [`../best-practices/never-disable-context-isolation.md`](../best-practices/never-disable-context-isolation.md), [`../best-practices/ipc-is-an-allow-list-not-a-pipe.md`](../best-practices/ipc-is-an-allow-list-not-a-pipe.md), and the IPC-security tree in [`../knowledge/desktop-engineering-decision-trees.md`](../knowledge/desktop-engineering-decision-trees.md). Concrete appsec verdicts route to `ravenclaude-core/security-reviewer`.
