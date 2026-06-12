---
description: "Decide Electron vs Tauri vs native vs PWA by the app's needs, and set the process/security model + renderer/backend boundary."
argument-hint: "[app + team + native-depth/size/security needs]"
---

You are running `/desktop-app-engineering:choose-desktop-framework`. Use `desktop-architect` + the `desktop-framework-choice` skill.

## Steps

1. Traverse the framework-choice tree in `knowledge/desktop-engineering-decision-trees.md`; name the trade.
2. Set the process/security model (renderer untrusted → contextBridge+ipcMain | Tauri capabilities).
3. Draw the renderer/backend line (secrets + OS calls + data API behind native process | backend).
4. Set storage (app-data dir + OS credential store).
5. Emit (from `templates/framework-decision.md`) + a Structured Output block.
