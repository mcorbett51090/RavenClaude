# IPC / capability security review

**App:** <name>  **Framework:** <Electron | Tauri>  **Reviewer:** <who>  **Date:** <YYYY-MM-DD>

## Electron baseline (per BrowserWindow)

| Setting | Required | Actual | OK? |
|---|---|---|---|
| `contextIsolation` | true | | |
| `nodeIntegration` | false | | |
| `sandbox` | true | | |
| `webSecurity` | true | | |
| `@electron/remote` | absent | | |
| Content-Security-Policy | strict, no unsafe-eval | | |

## Exposed operations (the allow-list)

| Op name | Args (validated?) | Touches FS/shell? | Scope | Reason it exists |
|---|---|---|---|---|
| | | | | |

## Tauri capabilities (if applicable)

| Capability | Windows | Permissions | Wildcard fs/shell? (must be no) |
|---|---|---|---|
| | | | |

**Findings:** <list>
**Verdict:** <pass | fix required> — concrete appsec verdicts route to `ravenclaude-core/security-reviewer`.
