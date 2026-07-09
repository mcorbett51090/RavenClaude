# Changelog — mobile-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.3] — 2026-07-09

### Changed

- **Capability map — React Native New Architecture row.** Updated from "GA-ing / verify per RN version" to state the New Architecture (Fabric/TurboModules) is the **sole** architecture since RN 0.82 (2025-10-08): the Legacy Architecture was removed from core and `newArchEnabled=false` / `RCT_NEW_ARCH_ENABLED=0` are now ignored. Ships React 19.1.1 + opt-in Hermes V1. Dated marker (2026-07-09) + `[verify-at-use]`. Source: [reactnative.dev/blog/2025/10/08/react-native-0.82](https://reactnative.dev/blog/2025/10/08/react-native-0.82).

## [0.3.1] — 2026-06-22

Version bump previously unlogged here; the change that set `0.3.1`:

- Repo review autonomous fixes + B1–B6 deferred items + dead-regex CI guard (#449)

## [0.3.0] — 2026-06-05

Value-add build-out — extending the plugin against the full value-add menu, mirroring the `backend-engineering` recipe for a **code** domain (the LSP runtime tier genuinely applies). Every menu item is dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `cold-start-jank-main-thread` (cold start is a main-thread budget problem — trace before optimizing), `offline-sync-conflict-duplication` (mint the dedup key on the device, carry it through retries), `ios-code-signing-release-pipeline` (reproducible fetched signing assets + API key, not one person's Keychain), `push-notification-delivery-gaps` (push is a wake-up hint, not a delivery channel — pull state on wake). Matches the existing `scenarios/README.md` index and the 9-field schema.
- **Decision-tree knowledge.** `knowledge/mobile-state-and-architecture-decision-trees.md` — two Mermaid trees (MVVM-vs-MVI-vs-unidirectional pattern; per-platform state-management library choice for SwiftUI / Compose / React Native / Flutter), complementing the existing tree file (platform choice, offline-sync, background, conflict, storage, RN-nav, permissions, retry). Cited, dated; library rows `[verify-at-use]`.
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (LSP runtime tier — per-server install table, two servers ship inside the SDK/toolchain), §7 (recommended-not-bundled / evaluate-first MCP servers), and the §8 value-add completeness disposition table.

### Decisions (recorded, not built)

- **No bundled MCP server.** Every real, published mobile MCP server (`@mobilenext/mobile-mcp`, Apache-2.0; the official `appium/appium-mcp` and community Appium-MCP variants) is a device-*automation* server — write-capable, needs a per-consumer toolchain (Xcode CLT + `adb`) and a *booted* simulator/emulator/device, and is community supply-chain. The doctrine sends "write-capable + per-consumer-config + community" to **evaluate-first, never default** with a mandatory `security-reviewer` gate. Documented the recommended `claude mcp add` path instead. No invented servers.
- **No runnable `scripts/` calculator.** Unlike the veterinary `vet_calc.py`, the mobile decisions are qualitative (architecture/platform/state) or live against the consumer's app (served by the LSP tier + advisory hook), not arithmetic models. A semver/release helper would duplicate `devops-cicd`.
- **No `bin/`, output-styles, monitors, settings defaults, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate an existing surface or a neighbouring plugin" bar.
- **Skills/commands/templates/hooks coverage held sufficient** — no 5th agent or skill added; the new decision-tree extends reach (team-growth-as-knowledge house rule).

### Verify-at-use

- LSP support landed in Claude Code 2.0.74; the Kotlin server choice (fwcd community `kotlin-language-server` vs JetBrains' maturing official `Kotlin/kotlin-lsp`); the SourceKit-LSP / Dart-analysis-server SDK-bundling; the published mobile MCP servers' package names, licenses, and maintenance status; the per-platform state libraries and "recommended" status (SwiftUI `@Observable`, Compose ViewModel+StateFlow, RN server-vs-client split, Flutter Riverpod/Bloc/Provider). All version-volatile — re-confirm against the vendor before quoting.

## [0.2.x] — earlier

4-agent mobile-engineering team (mobile-architect, ios-engineer, android-engineer, cross-platform-engineer): 6 skills, a decision-tree knowledge bank (platform-choice + offline-sync + background + conflict + storage + RN-nav + permissions + retry trees + a dated 2026 capability map), 12 best-practices, 4 templates, 4 commands, 1 advisory hook, `.lsp.json` (Swift/Kotlin/Dart/TS). Seams to frontend-engineering, api-engineering/backend-engineering, auth-identity, devops-cicd. (Consolidated decision-trees + best-practices + templates landed via PR #315.)
</content>
