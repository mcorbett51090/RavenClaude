# desktop-app-engineering — best-practice docs

Named, citable rules for the `desktop-app-engineering` plugin's specialists. Each file is **one rule**.

---

## Index

_12 rules across framework choice, the IPC/security boundary, signing & updates, storage, and native integration._

| Doc | Status | Use when |
|---|---|---|
| [`choose-framework-by-the-app.md`](./choose-framework-by-the-app.md) | Absolute rule | Choosing Electron vs Tauri vs native vs PWA — decide by the app's real needs, not team familiarity. |
| [`renderer-is-untrusted-web-content.md`](./renderer-is-untrusted-web-content.md) | Absolute rule | Any desktop app with a webview — treat the renderer as untrusted; it gets no direct OS access. |
| [`never-disable-context-isolation.md`](./never-disable-context-isolation.md) | Absolute rule | Any Electron BrowserWindow — keep contextIsolation on, nodeIntegration off, sandbox on. |
| [`ipc-is-an-allow-list-not-a-pipe.md`](./ipc-is-an-allow-list-not-a-pipe.md) | Absolute rule | Exposing native capability — expose named operations, never raw ipcRenderer/require. |
| [`validate-every-ipc-and-command-input.md`](./validate-every-ipc-and-command-input.md) | Absolute rule | Any IPC handler or #[tauri::command] — validate every argument; it's an untrusted entry point. |
| [`scope-capabilities-to-least-privilege.md`](./scope-capabilities-to-least-privilege.md) | Absolute rule | Tauri capabilities — grant only what a window needs; never wildcard fs/shell scopes. |
| [`sign-and-notarize-every-release.md`](./sign-and-notarize-every-release.md) | Absolute rule | Every release — sign on Windows + macOS and notarize/staple on macOS, keys in CI secrets. |
| [`verify-update-signatures-before-apply.md`](./verify-update-signatures-before-apply.md) | Absolute rule | Auto-update — verify the update's signature before applying it; never apply an unverified payload. |
| [`stage-rollouts-keep-rollback.md`](./stage-rollouts-keep-rollback.md) | Pattern | Shipping an update — roll out in stages with a rollback and a version floor, not 100% at once. |
| [`secrets-in-the-os-credential-store.md`](./secrets-in-the-os-credential-store.md) | Absolute rule | Tokens/secrets — store in Keychain / Credential Manager / libsecret, never plaintext config. |
| [`single-instance-and-validate-deep-links.md`](./single-instance-and-validate-deep-links.md) | Absolute rule | Deep links / file associations — single-instance the app and validate the untrusted payload. |
| [`follow-each-os-native-conventions.md`](./follow-each-os-native-conventions.md) | Pattern | Tray, menus, notifications — use each platform's idiom, not one cross-OS approximation. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
