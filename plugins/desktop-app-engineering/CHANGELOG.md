# Changelog — desktop-app-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.4] — 2026-09-14

### Changed

- `desktop-platform-engineer`: `model: opus` → `model: sonnet`. Second model-tier pass — signing/notarization, auto-update and OS-integration wiring — the same shape as `electron-engineer` / `tauri-engineer`, which already pin `sonnet`; `desktop-architect` stays on `opus`. This is the `sonnet` row of the marketplace's tier table (`ravenclaude-core/knowledge/model-tier-delegation.md`: bounded, well-specified work against a design made upstream), and the sibling-plugin parity rule the doctrine now states: the same role shape gets the same tier across plugins. Listed by the model-tier-fit gate's `--report` pair-review queue (`check-model-tier-fit.py`, Gate 288). No behaviour change beyond the model the agent runs on — it moves tier, not role.

## [0.1.3] — 2026-09-14

### Changed

- `electron-engineer` and `tauri-engineer`: `model: opus` → `model: sonnet`. The role is the implementation half of an architect/engineer pair — bounded, well-specified work against a design made upstream — which is the `sonnet` row of the marketplace's tier table (`ravenclaude-core/knowledge/model-tier-delegation.md`), and the tier the earlier app-craft plugins (backend / frontend / api / database) already give their implementers. Enforced going forward by the marketplace's model-tier-fit CI gate (`check-model-tier-fit.py`, Gate 288). No behaviour change beyond the model the agent runs on; the architect sibling stays on `opus`.

## [0.1.2] — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself; Gate 206 forbids the digit.

## [0.1.0] — 2026-06-12

Initial build — the **desktop runtime** sibling the app-craft cluster (backend / frontend / mobile / api / database / auth-identity) was missing. Mirrors the proven `mobile-engineering` recipe for a **code** domain.

### Added

- **4 agents** (scenario-authoring schema complete, each description ≤300 chars): `desktop-architect` (Electron/Tauri/native/PWA choice, process-security model, renderer/backend boundary, distribution), `electron-engineer` (main/preload/renderer, the hardened baseline, a validated contextBridge + ipcMain allow-list), `tauri-engineer` (Rust core, `#[tauri::command]`, v2 capabilities/permissions, sidecars), `desktop-platform-engineer` (signing + notarization, safe signed auto-update, native OS integration, secure storage).
- **5 skills** — desktop-framework-choice, electron-security-hardening, tauri-capabilities-and-commands, packaging-signing-and-updates, native-os-integration.
- **Knowledge bank** — `knowledge/desktop-engineering-decision-trees.md`: framework-choice + renderer→privileged IPC-security + signing/notarization/auto-update Mermaid trees, a storage/secrets prior, and a dated 2026 capability map (`[verify-at-use]`).
- **12 best-practices** — framework choice, renderer-is-untrusted, never-disable-context-isolation, IPC-is-an-allow-list, validate-every-input, scope-Tauri-capabilities, sign-and-notarize, verify-update-signatures, stage-rollouts/rollback, secrets-in-OS-store, single-instance/validate-deep-links, follow-each-OS-conventions.
- **4 templates** (framework-decision, ipc-security-review, release-signing-checklist, native-integration-plan), **4 commands** (choose-desktop-framework, harden-electron, scope-tauri-capabilities, plan-release-signing), **1 advisory hook** (`check-desktop-engineering-anti-patterns.sh` — insecure Electron webPreferences, wildcard Tauri capabilities, plaintext secrets, deprecated `altool`; `DESKTOP_STRICT=1` to block).
- **3-scenario bank** — Electron `nodeIntegration` RCE, macOS notarization/Gatekeeper block, an auto-update fleet outage.
- **`.lsp.json`** — typescript-language-server (Electron/renderer) + rust-analyzer (Tauri); ships config, not binaries.
- **README.md + CLAUDE.md** (team constitution), and registration in `.claude-plugin/marketplace.json` + the `docs/architecture.md` roster.

### Decisions (recorded, not built)

- **No bundled MCP server** — desktop build/sign/notarize tooling is per-consumer-environment (certs, Apple/Windows accounts, a build toolchain) and write/side-effecting → evaluate-first, documented not bundled. No invented servers.
- **No runnable `scripts/` calculator** — the decisions are qualitative or live against the consumer's app (served by the LSP tier + advisory hook), not arithmetic models; a version/semver helper would duplicate `devops-cicd`.

### Verify-at-use

- Electron security defaults per major; Tauri v2 permission/capability identifiers; macOS `notarytool` (replaced the deprecated `altool`) + hardened runtime + stapling; Windows Authenticode/EV SmartScreen behavior; the LSP-support Claude Code version (2.0.74). All version-volatile — re-confirm against the vendor before quoting.
