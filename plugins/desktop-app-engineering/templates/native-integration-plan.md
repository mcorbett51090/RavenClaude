# Native OS integration plan

**App:** <name>  **Targets:** <macOS | Windows | Linux>

| Concern | macOS | Windows | Linux |
|---|---|---|---|
| Tray / menu-bar | | | |
| Application menus | | | |
| Notifications | | | |
| Keyboard shortcuts | Cmd-based | Ctrl-based | Ctrl-based |
| File associations | | | |
| Deep-link scheme (`myapp://`) | | | |
| Secret storage | Keychain | Credential Manager | libsecret (fallback: __) |

**Single-instance:** yes/no — second-launch focuses running window + passes argv/URL
**Deep-link/file payload validation:** <rule before acting on untrusted input>
**Lifecycle:** window-state restore · minimize-to-tray vs quit · flush on before-quit
