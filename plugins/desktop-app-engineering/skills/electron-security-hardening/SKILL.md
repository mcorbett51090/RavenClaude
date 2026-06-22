---
name: electron-security-hardening
description: "Harden an Electron app to the secure baseline — contextIsolation on, nodeIntegration off, sandbox on, a strict CSP, no remote module — and bridge to the OS through a narrow typed contextBridge backed by validated ipcMain handlers."
---

# Electron Security Hardening

## The baseline (every BrowserWindow)

```js
new BrowserWindow({
  webPreferences: {
    contextIsolation: true, // isolate preload from renderer globals
    nodeIntegration: false, // no Node in the renderer
    sandbox: true, // OS-level renderer sandbox
    webSecurity: true, // keep same-origin enforcement
    preload: path.join(__dirname, "preload.js"),
  },
});
```

Plus: a strict `Content-Security-Policy` (no `unsafe-eval`, no remote `script-src`), **no** `@electron/remote`, block navigation to untrusted origins (`will-navigate` / `setWindowOpenHandler`), and open external links via `shell.openExternal(url)` only after validating the URL.

## The IPC bridge (allow-list, not a pipe)

```js
// preload.js — expose named operations, never raw ipcRenderer
const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("api", {
  readDoc: (id) => ipcRenderer.invoke("doc:read", id),
});
```

```js
// main.js — validate every argument
const { ipcMain } = require("electron");
ipcMain.handle("doc:read", async (_evt, id) => {
  if (typeof id !== "string" || !/^[\w-]{1,64}$/.test(id)) throw new Error("bad id");
  return loadDoc(id);
});
```

## When the renderer "needs Node"

Move the work to the main process behind a typed command. **Never** re-enable `nodeIntegration` to satisfy a renderer dependency.

## Secrets

Use `safeStorage` (OS-backed encryption) for tokens; never write secrets to plaintext config. Auth flow → `auth-identity`.
