# Desktop App Engineering Plugin — Team Constitution

> Team constitution for the `desktop-app-engineering` Claude Code plugin — **4** specialist agents for building cross-platform desktop apps well: the framework choice (Electron / Tauri / native / PWA), a hardened process/security model, packaging + signing + safe auto-update, and native OS integration. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`desktop-architect`](agents/desktop-architect.md) | Desktop architecture & strategy: the Electron-vs-Tauri-vs-native-vs-PWA decision, the process/security model, the renderer/backend boundary, the distribution + update strategy, and local persistence | "Electron, Tauri, native, or a PWA?", "architect our desktop app", "how should the renderer talk to the privileged side?", "how do we ship + auto-update?" |
| [`electron-engineer`](agents/electron-engineer.md) | Electron implementation: the main/preload/renderer model, the hardened security baseline (contextIsolation/nodeIntegration/sandbox/CSP), a narrow contextBridge + validated ipcMain handlers, window/lifecycle, and the build (electron-builder/Forge) | "is my Electron config safe?", "expose this to the renderer safely", "my renderer needs fs", "set up electron-builder" |
| [`tauri-engineer`](agents/tauri-engineer.md) | Tauri implementation: the Rust core + system-webview model, `#[tauri::command]` handlers with validated input, the v2 capabilities/permissions allow-list, sidecars, and state management | "call a Rust function from the webview", "lock down my Tauri capabilities", "run a sidecar binary", "share state across commands" |
| [`desktop-platform-engineer`](agents/desktop-platform-engineer.md) | The cross-cutting platform layer: code-signing + notarization (Win + macOS), safe signed auto-update (channels/rollout/rollback/version-floor), and native OS integration (tray, menus, notifications, file associations, deep links, secure storage) | "my app is blocked by Gatekeeper/SmartScreen", "auto-update safely", "add a tray + notifications", "where do tokens go on desktop?" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.

## 2. Cross-cutting house opinions (every agent enforces)

1. **Choose the framework by the app, not by familiarity.** Native-depth / bundle-size / security-surface / team / update needs decide Electron vs Tauri vs native vs PWA. Name the trade; don't default.
2. **The renderer is untrusted web content.** It gets no direct filesystem/shell/OS access — only a narrow, validated allow-list (Electron `contextBridge` + validated `ipcMain.handle`; Tauri `#[tauri::command]` authorized by a scoped capability). This boundary is the entire security model.
3. **The secure baseline has no exceptions.** Electron: `contextIsolation` on, `nodeIntegration` off, `sandbox` on, strict CSP, no `@electron/remote`. Tauri: least-privilege capabilities, never wildcard `fs:`/`shell:`. If the renderer "needs Node," move the work to the privileged side behind a validated command.
4. **Validate every IPC/command input.** A handler is a public API endpoint reachable from compromised web content — validate type/length/format and resolve paths against an allowed base.
5. **Signing is part of the architecture.** Sign on Windows + macOS; notarize + staple on macOS; keys in CI secrets/HSM. An unsigned/un-notarized build fails on users' machines.
6. **Auto-update is signed, staged, and reversible.** Verify the signature before apply; ship via channels with staged rollout, rollback, and a version floor — you can't instantly un-install code from the fleet.
7. **Secrets live in the OS credential store**, never plaintext config. App data goes in the per-OS app-data directory.
8. **Follow each OS's native conventions** for tray, menus, notifications, and shortcuts — a shared codebase is not a shared UX.

## 3. Seams (the bridges to neighbouring plugins)

- **The renderer UI / component architecture (React, etc.)** → `frontend-engineering` (we own the desktop shell, security boundary, and OS integration; they own the UI).
- **The backend/API the app consumes (contract, sync endpoints, pagination, errors)** → `api-engineering` + `backend-engineering`.
- **Authentication, OAuth/PKCE, token flow** → `auth-identity` (we store the result in the OS secure store; they own the flow).
- **CI/CD, code signing + notarization automation, release pipeline** → `devops-cicd` (we design the signing/update strategy; they wire the pipeline).
- **The mobile sibling (offline-first, lifecycle, secure storage on a device you don't control)** → `mobile-engineering` — the same instincts, a different runtime.
- **Concrete appsec verdicts on the IPC/capability surface** → `ravenclaude-core/security-reviewer`.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/desktop-engineering-decision-trees.md`](knowledge/desktop-engineering-decision-trees.md) — the framework-choice tree, the renderer→privileged IPC-security tree, the signing/notarization/auto-update tree, a storage/secrets prior, and a dated 2026 capability map. **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol. Capability rows are dated and `[verify-at-use]`; re-confirm against the vendor before quoting (Electron majors, Tauri v2 permission identifiers, `notarytool` vs the deprecated `altool`, SmartScreen/Gatekeeper behavior).
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (Electron `nodeIntegration` RCE, macOS notarization/Gatekeeper block, an auto-update fleet outage). Secondary source; never replaces the knowledge bank.

## 6. Technical-runtime tier — LSP code intelligence (bundled config, binaries installed separately)

Desktop engineering is a **code** domain, so the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time code intelligence for the two dominant desktop stacks:

| Language | Server | `command` | Install (consumer, separate) `[verify-at-use]` |
|---|---|---|---|
| TypeScript/JS (Electron + the renderer) | typescript-language-server | `typescript-language-server --stdio` | `npm install -g typescript-language-server typescript` |
| Rust (Tauri core) | rust-analyzer | `rust-analyzer` | `rustup component add rust-analyzer` (or the editor's install) |

**The plugin ships the *config*, not the *binary*.** If a server isn't on `PATH` it shows in the `/plugin` Errors tab and that one language degrades — Claude Code and everything else keep working (loud-but-non-fatal). LSP support landed in Claude Code 2.0.74 `[verify-at-use]`.

## 7. Recommended (not bundled) MCP servers

This plugin **bundles no MCP server**, on purpose. Per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be zero-config and read-only by default. Desktop build/sign/notarize tooling is per-consumer-environment (certs, Apple/Windows accounts, a build toolchain) and write/side-effecting, so it is **evaluate-first, never bundle**. No invented servers.

## 8. Value-add disposition (build-out 2026-06-12, v0.1.0)

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 3 scenarios (Electron nodeIntegration RCE, macOS notarization/Gatekeeper block, auto-update fleet outage) on the 9-field schema. |
| 2 | **Decision-tree knowledge** | **BUILT** — framework-choice + IPC-security + signing/update Mermaid trees, a storage prior, and a dated 2026 capability map. |
| 3 | **LSP server** | **BUILT** — `.lsp.json` wires typescript-language-server (Electron/renderer) + rust-analyzer (Tauri), via `plugin.json` `lspServers`. Ships config, not binaries. |
| 4 | **Bundled MCP server** | **N-A (evaluate-first)** — desktop build/sign tooling is per-consumer and write-capable; documented, not bundled. |
| 5 | **Runnable script (`scripts/`)** | **N-A** — the decisions here are qualitative (framework/security/signing) or live against the consumer's app (served by the LSP tier + the advisory hook), not arithmetic models. A version/semver helper would duplicate `devops-cicd`. |
| 6 | **skills/hooks/commands/templates** | **BUILT / sufficient** — 5 skills, 4 commands, 4 templates, 1 advisory hook (insecure Electron webPreferences, wildcard Tauri capabilities, plaintext secrets, deprecated altool). |
| 7 | **CHANGELOG.md** | **BUILT** — top entry for the v0.1.0 initial build. No `NOTICE.md` (nothing third-party is bundled). |
