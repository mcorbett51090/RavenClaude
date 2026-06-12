# Desktop framework decision

| Factor | Weight | Electron | Tauri | Native | PWA |
|---|---|---|---|---|---|
| Native-API depth | | | | | |
| Bundle size / memory budget | | | | | |
| Security surface | | | | | |
| Team languages (web / Rust / native) | | | | | |
| Ecosystem maturity | | | | | |
| Update / distribution needs | | | | | |

**Decision:** <approach>  **Trade accepted:** <what we give up>
**Security model:** renderer untrusted → <contextBridge+ipcMain | Tauri capabilities>
**Renderer/backend line:** secrets + OS calls + data API behind <native process | remote backend>
**Storage:** app-data dir for data · OS credential store for secrets
