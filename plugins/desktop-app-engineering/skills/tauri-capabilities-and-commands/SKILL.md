---
name: tauri-capabilities-and-commands
description: "Expose native capability in Tauri through #[tauri::command] handlers with validated input, authorized by a least-privilege capabilities/permissions allow-list (v2) scoped to the windows that need it — no wildcard fs/shell scopes."
---

# Tauri Capabilities & Commands

## A command is an untrusted entry point

```rust
// src-tauri/src/lib.rs — validate every argument
#[tauri::command]
fn read_doc(id: String) -> Result<String, String> {
    if id.len() > 64 || !id.chars().all(|c| c.is_ascii_alphanumeric() || c == '-') {
        return Err("bad id".into());
    }
    load_doc(&id).map_err(|e| e.to_string())
}
```

The frontend calls it with `invoke("read_doc", { id })`. The command runs in Rust; the frontend never touches the filesystem directly.

## Capabilities authorize what the frontend may call (v2)

```json
// src-tauri/capabilities/default.json — least privilege
{
  "identifier": "default",
  "windows": ["main"],
  "permissions": ["core:default", "fs:allow-read-text-file"]
}
```

Default-deny: add only the permissions a window actually uses. **Never** grant wildcard `fs:` or `shell:` scopes — scope filesystem permissions to specific paths and shell permissions to the exact program + argument shape.

## Sidecars

Bundle an external binary as a sidecar and narrow the shell/scope permission to that exact program and its allowed args — not a blanket execute capability.

## State

Share state across commands with `tauri::State` (managed state; `Mutex`/`RwLock` for shared-mutable) so borrows stay race-free.

> Tauri v2's permission/capability model is the assumed baseline — `[verify-at-use]` against the current docs before quoting specifics. Signing/notarization/update → `desktop-platform-engineer`.
