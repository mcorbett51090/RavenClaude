# Mobile Engineering Plugin — Team Constitution

> Team constitution for the `mobile-engineering` Claude Code plugin — **4** specialist agents for building native and cross-platform mobile apps well — the native-vs-cross-platform choice, iOS (Swift/SwiftUI) and Android (Kotlin/Compose) craft, offline/sync and app lifecycle, and the release/store pipeline. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`mobile-architect`](agents/mobile-architect.md) | Mobile architecture and platform strategy: the native-vs-React-Native-vs-Flutter decision, app architecture (MVVM/MVI/unidirectional), module structure, offline/sync strategy, and the navigation model | "native or React Native or Flutter?", "architect our mobile app", "how should offline work?", "which mobile architecture pattern?" |
| [`ios-engineer`](agents/ios-engineer.md) | Native iOS: Swift, SwiftUI (and UIKit interop), the app/scene lifecycle, Swift Concurrency (async/await, actors), Keychain secure storage, and iOS-specific patterns and Human Interface Guidelines | "build this iOS screen", "SwiftUI state isn't updating", "store this token securely on iOS", "handle the iOS lifecycle" |
| [`android-engineer`](agents/android-engineer.md) | Native Android: Kotlin, Jetpack Compose, the activity/fragment lifecycle, coroutines/Flow, the Keystore + EncryptedSharedPreferences, WorkManager for background, and Material/Android conventions | "build this Android screen", "recomposition is looping", "store secrets on Android", "do background work correctly" |
| [`cross-platform-engineer`](agents/cross-platform-engineer.md) | React Native and Flutter: shared-codebase architecture, the bridge/native-module boundary, platform-channel/native interop, navigation, performance pitfalls, and the cross-cutting mobile concerns (push, deep links, offline) in a shared codebase | "build this in React Native", "our Flutter app is janky", "call a native API from RN", "set up navigation + deep links" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Choose native vs cross-platform by the app, not by preference.** Heavy platform-specific UX / performance / latest-OS-feature → native; shared business app across both with one team → React Native/Flutter. Name the trade; don't default.
2. **Mobile is offline-first or it's fragile.** The network is intermittent by nature. Design for offline reads, queued writes, and conflict resolution from the start — bolting it on later is a rewrite.
3. **Respect the platform lifecycle.** Apps get backgrounded, killed, and restored. State restoration, background-task limits, and lifecycle-aware components are not optional — ignoring them is how you get data loss and ANRs/crashes.
4. **Secure storage is the Keychain/Keystore, not preferences.** Tokens and secrets go in the platform secure store, never in plain UserDefaults/SharedPreferences. On-device data is on a device you don't control.
5. **The store is part of the pipeline.** Signing, provisioning, review guidelines, phased rollout, and the update lag (users don't update instantly) are engineering concerns — design for multiple live versions.
6. **Battery and data are the user's budget, not yours.** Polling, wakeups, and chatty networking drain trust and battery. Batch, defer, and use push instead of polling.

## 3. Seams (the bridges to neighbouring plugins)

- **Shared web/React patterns, TypeScript, and component thinking** → `frontend-engineering` (especially relevant for React Native).
- **The backend API the app consumes (contract, pagination, errors, sync endpoints)** → `api-engineering` + `backend-engineering`.
- **Authentication, OAuth/PKCE on mobile, token handling** → `auth-identity` (we store tokens in the secure store; they own the flow).
- **CI/CD, code signing, and store deployment automation** → `devops-cicd` (mobile signing + Fastlane-style pipelines).
- **Push-notification backend and delivery infra** → the cloud plugin / `backend-engineering`; we own the on-device handling, deep links, and permissions.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/mobile-engineering-decision-trees.md`](knowledge/mobile-engineering-decision-trees.md) (native-vs-cross-platform, offline/sync, background-work API, conflict resolution, on-device storage, RN navigation, runtime permissions, network retry, plus a dated capability map) and [`knowledge/mobile-state-and-architecture-decision-trees.md`](knowledge/mobile-state-and-architecture-decision-trees.md) (MVVM-vs-MVI-vs-unidirectional, and the per-platform state-management library choice). **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol. Capability/library rows are dated and `[verify-at-use]`; re-confirm against the vendor before quoting.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (cold-start jank on the main thread, offline-sync conflict/duplication, iOS code-signing release pipeline, push-notification delivery gaps). Secondary source; never replaces the knowledge bank. The most-likely-to-benefit specialists should check the bank when a situation matches.

## 6. Technical-runtime tier — LSP code intelligence (bundled config, binaries installed separately)

Mobile engineering is a **code** domain, so the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time code intelligence — go-to-definition, find-references, diagnostics — instead of grep-and-guess. Verified against the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) (LSP servers section); LSP support landed in Claude Code 2.0.74 `[verify-at-use]`.

It configures four language servers covering this plugin's stacks (Swift, Kotlin, Dart/Flutter, and TypeScript/JS for React Native):

| Language | Server | `command` (as wired in `.lsp.json`) | Install (consumer, separate) `[verify-at-use]` |
|---|---|---|---|
| Swift (iOS) | SourceKit-LSP ([swiftlang/sourcekit-lsp](https://github.com/swiftlang/sourcekit-lsp), Apache-2.0) | `sourcekit-lsp` | **Bundled with the Swift toolchain / Xcode 11.4+** (or its Command Line Tools); run via `xcrun sourcekit-lsp` if not on `PATH`. Verified 2026-06-05. |
| Kotlin (Android) | kotlin-language-server ([fwcd/kotlin-language-server](https://github.com/fwcd/kotlin-language-server), MIT, community) | `kotlin-language-server` | Download a release from the repo and put the launcher on `PATH`. **Alternative:** JetBrains' official [`Kotlin/kotlin-lsp`](https://github.com/Kotlin/kotlin-lsp) (announced KotlinConf May 2025; alpha through late-2025/2026, Kotlin 2.3 support) — re-evaluate once it's GA. `[verify-at-use]` — pick the maintained option at adoption. |
| Dart/Flutter | Dart analysis server (LSP mode), in the Dart SDK | `dart language-server --client-id claude-code.mobile-engineering` | **Bundled with the Dart/Flutter SDK** (`dart language-server`, LSP since Dart 2.2.0). Verified 2026-06-05. |
| TypeScript/JS (React Native) | typescript-language-server | `typescript-language-server --stdio` | `npm install -g typescript-language-server typescript` |

**The plugin ships the *config*, not the *binary*.** Per the plugins reference: "LSP plugins configure how Claude Code connects to a language server, but they don't include the server itself." If a server's binary isn't on `PATH`, it shows `Executable not found in $PATH` in the `/plugin` Errors tab and that one language degrades — Claude Code and all other tools keep working (the same **loud-but-non-fatal** posture as a missing MCP prerequisite). LSP servers start only after the workspace is trusted, and `/reload-plugins` is needed to pick up a config change mid-session. Note two stacks (Swift, Dart) ship their server *inside the SDK/toolchain*, so a developer who can build the app already has the server — the most likely "missing" one is the community Kotlin server.

> Commands are verified against each ecosystem's docs (2026-06-05): SourceKit-LSP bundled with the Swift toolchain/Xcode; `dart language-server` is the documented LSP entrypoint (`--client-id` per the Dart LSP docs); `kotlin-language-server` is the fwcd launcher name; `typescript-language-server --stdio` per its README. The Kotlin server choice (fwcd community vs the maturing JetBrains official) and the 2.0.74 LSP-support version are version-volatile — re-confirm at use.

## 7. Recommended (not bundled) MCP servers — device/automation context

This plugin **bundles no MCP server**, on purpose. Per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**; a write-capable, per-consumer-environment, or community-supply-chain server is **recommend-not-bundle / evaluate-first**. The real, published mobile MCP servers are device-*automation* servers — they fail that bar decisively, so we document the recommended `claude mcp add …` path (behind a `security-reviewer` gate) instead of shipping an `mcpServers` entry.

| Server | Why recommend-not-bundle / evaluate-first | Recommended setup `[verify-at-use]` |
|---|---|---|
| **Mobile MCP** ([`@mobilenext/mobile-mcp`](https://github.com/mobile-next/mobile-mcp), Apache-2.0, community) | **Write-capable** — it taps/swipes/launches/terminates apps on a live simulator/emulator/device (not read-only) → an Absolute-rule `security-reviewer` gate before it ships. **Per-consumer environment** — needs Xcode command-line tools, Android platform-tools (`adb`), and a *booted* simulator/emulator (or a real device + WebDriverAgent); none of that is hardcodable. Plus a **community supply-chain** dependency. All three send it to **evaluate-first, never bundle**. | `claude mcp add mobile -- npx -y @mobilenext/mobile-mcp@<pinned-version>` — pin the version, run only against a dev simulator/emulator (never an end-user device), and gate adoption through `ravenclaude-core/security-reviewer`. Verified Apache-2.0 + write-capable 2026-06-05 from the upstream repo. |
| **Appium-based MCP servers** (e.g. the official [`appium/appium-mcp`](https://github.com/appium/appium-mcp); several community variants exist) | Same shape — Appium-backed device *automation* (write-capable), needing a configured Appium/driver stack + a target device/emulator (per-consumer). Multiple competing community implementations → vet maintenance/license at adoption. | Evaluate-first, `security-reviewer`-gated; prefer the most-maintained, clearly-licensed implementation, pinned. Don't bundle. |

**Why none are bundled (the load-bearing reasoning):** every published mobile MCP that actually does something is a **device-automation** server — it *controls* a simulator/emulator/device, so it is write-capable by nature; it needs a per-consumer toolchain + a booted target (not zero-config); and the maintained options are community packages. The doctrine's decision table sends "write-capable + per-consumer-config + community, no first-party equivalent" straight to **evaluate-first, never default**, with a mandatory `security-reviewer` gate. No invented servers: the two rows above are real, published, and license-checked. If a genuinely zero-config, read-only, broadly-useful mobile server appears, revisit with [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 1's decision table.

> Verified 2026-06-05: `@mobilenext/mobile-mcp` (Apache-2.0, controls iOS/Android simulators/emulators/devices, needs Xcode CLT + Android platform-tools + a booted target/WebDriverAgent) per its GitHub repo; the existence of `appium/appium-mcp` and community Appium-MCP variants per their repos. Package names, licenses, and maintenance status are volatile — re-confirm at use.

## 8. Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason). Mobile is a **code** domain, so the technical-runtime tier (LSP) is genuinely applicable — unlike a pure-advisory vertical.

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 scenarios (cold-start jank / main-thread, offline-sync conflict + duplication, iOS code-signing release pipeline, push-notification delivery gaps) matching the existing `scenarios/README.md` index + 9-field schema. |
| 2 | **Decision-tree knowledge** | **BUILT** — `knowledge/mobile-state-and-architecture-decision-trees.md` (MVVM-vs-MVI-vs-unidirectional; per-platform state-library choice), **complementing** PR #315's existing trees (platform choice / offline-sync / background / conflict / storage / RN-nav / permissions / retry). Grounded, cited, dated; library rows `[verify-at-use]`. |
| 3 | **LSP server** | **BUILT (pre-existing, documented this round)** — `.lsp.json` wires SourceKit-LSP (Swift), kotlin-language-server (Kotlin), the Dart analysis server (Dart/Flutter), and typescript-language-server (RN TS/JS), via `plugin.json` `lspServers`. §6 documents the per-server install (two ship inside the SDK/toolchain); ships config, not binaries; loud-but-non-fatal if missing. |
| 4 | **Bundled MCP server** | **N-A (evaluate-first, recommend-not-bundle)** — §7. The real, published mobile MCP servers (`@mobilenext/mobile-mcp`, Appium-based variants) are device-*automation* servers: write-capable, per-consumer toolchain + booted target, community supply-chain → all three disqualify bundling and require a `security-reviewer` gate. Documented the recommended `claude mcp add` path instead. No invented servers. |
| 5 | **Runnable script (`scripts/`)** | **N-A** — no stdlib-Python calculator clears the "real value, doesn't duplicate a surface" bar here. The plugin's decisions are qualitative (architecture/platform/state) or live against the *consumer's* app (better served by LSP + the advisory hook), not arithmetic models like the veterinary `vet_calc.py`. A release-version/semver helper would duplicate `devops-cicd`. |
| 6 | **bin/ · monitors · output-styles · settings defaults · themes** | **N-A** — none clears "groundable + broadly valuable, doesn't duplicate an existing surface or a neighbouring plugin." The advisory hook (`hooks/check-mobile-engineering-anti-patterns.sh`) + skills already cover proactive guidance; an output-style would overlap the agents' Output Contract; nothing here needs a background monitor. |
| 7 | **skills/hooks/commands/templates** | **Coverage sufficient** — 6 skills (iOS/Android/cross-platform craft, platform choice, release pipeline + more), 4 commands, 4 templates, 1 advisory hook already cover platform choice, native + cross-platform implementation, offline-sync, secure storage, and release. The new state/architecture decision-tree extends reach without a 5th agent (team-growth-as-knowledge house rule). |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top entry for this build-out. No `NOTICE.md` (nothing third-party is bundled; the recommended MCP servers are referenced, not vendored). |
