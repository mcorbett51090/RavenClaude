# IPC is an allow-list, not a pipe

**Status:** Absolute rule
**Domain:** Desktop security boundary
**Applies to:** `desktop-app-engineering`

---

## Why this exists

The bridge between untrusted web content and the privileged process is the entire desktop security model. If you expose a general-purpose pipe — the raw `ipcRenderer`, a `require`, or a wildcard Tauri capability — you have handed the renderer (and anything that compromises it) the keys to the OS. The boundary must expose a **finite, named set of operations**, each of which validates its input, so that the privileged side does exactly the handful of things the app needs and nothing else.

## How to apply

```js
// Electron — preload exposes NAMED operations, never raw ipcRenderer
const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("api", {
  saveDoc: (id, body) => ipcRenderer.invoke("doc:save", id, body),
  // NOT: send: (...args) => ipcRenderer.send(...args)   ← a pipe
});
```

```rust
// Tauri — a named command, authorized by a scoped capability (not a wildcard)
#[tauri::command]
fn save_doc(id: String, body: String) -> Result<(), String> { /* validate, then save */ }
```

**Do:**
- Expose one named operation per real need, with the narrowest signature that works.
- Back each Electron op with `ipcMain.handle` (request/response) and validate arguments there.
- In Tauri, authorize each command with a capability scoped to the specific window, path, or program.

**Don't:**
- Expose `ipcRenderer`, `require`, `child_process`, or the Node `process` to the renderer.
- Grant a wildcard `fs:`/`shell:` capability "to move fast."
- Trust an IPC argument because "it came from our own frontend" — the frontend is the untrusted side.

## Edge cases / when the rule does NOT apply

A high-frequency one-way event stream (e.g. log lines main→renderer) can use `send`/`on` in the privileged→renderer direction; the rule is about not exposing an *inbound* general-purpose pipe from untrusted content into the privileged process.

## See also

- [`./renderer-is-untrusted-web-content.md`](./renderer-is-untrusted-web-content.md) — the principle this rule implements.
- [`./validate-every-ipc-and-command-input.md`](./validate-every-ipc-and-command-input.md) — the input-validation half.
- [`../knowledge/desktop-engineering-decision-trees.md`](../knowledge/desktop-engineering-decision-trees.md) — the IPC-security decision tree.

## Provenance

Electron security checklist (context isolation, IPC) and Tauri v2 capabilities/permissions docs. Codifies CLAUDE.md §2 ("the renderer is untrusted; IPC is a narrow allow-list").

---

_Last reviewed: 2026-06-12 by `claude`_
