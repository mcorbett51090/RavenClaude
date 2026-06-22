---
description: "Review + tighten a Tauri app's capabilities/permissions to least privilege and validate its command inputs."
argument-hint: "[path to src-tauri / capabilities / commands]"
---

You are running `/desktop-app-engineering:scope-tauri-capabilities`. Use `tauri-engineer` + the `tauri-capabilities-and-commands` skill.

## Steps

1. Enumerate every `#[tauri::command]` and the capability that authorizes it.
2. Flag wildcard `fs:`/`shell:` scopes; narrow each to the exact path / program + args.
3. Confirm every command validates its arguments (untrusted entry points).
4. Confirm capabilities are scoped to the windows that need them (default-deny).
5. Fill `templates/ipc-security-review.md`; emit findings + a Structured Output block.
