# mobile-engineering — best-practice docs

Named, citable rules for the `mobile-engineering` plugin's specialists. Each file is **one rule**.

---

## Index

_22 rules across platform strategy, offline, security, iOS, Android, React Native, and accessibility._

| Doc | Status | Use when |
|---|---|---|
| [`choose-platform-by-the-app.md`](./choose-platform-by-the-app.md) | Absolute rule | Choosing native vs cross-platform — decide by the app's real needs, not team familiarity. |
| [`build-native-feel-not-a-wrapped-website.md`](./build-native-feel-not-a-wrapped-website.md) | Absolute rule | Any UI — follow platform conventions; do not port a web layout directly. |
| [`offline-first-by-design.md`](./offline-first-by-design.md) | Absolute rule | Architecture — design for offline reads and queued writes from the start. |
| [`navigation-is-state.md`](./navigation-is-state.md) | Pattern | App navigation — model navigation as declarative state so it is testable and restorable. |
| [`respect-the-lifecycle.md`](./respect-the-lifecycle.md) | Absolute rule | Any stateful component — handle background, foreground, and kill/restore transitions correctly. |
| [`survive-process-death.md`](./survive-process-death.md) | Absolute rule | App state — persist and restore all non-ephemeral state across process death. |
| [`instrument-crashes-and-anrs.md`](./instrument-crashes-and-anrs.md) | Absolute rule | Any release build — crash reporting and ANR tracking are table stakes for production. |
| [`background-work-uses-os-schedulers.md`](./background-work-uses-os-schedulers.md) | Absolute rule | Any background work — describe it to WorkManager/BGTaskScheduler with constraints; don't poll in a service. |
| [`keep-the-main-thread-free.md`](./keep-the-main-thread-free.md) | Absolute rule | Any work on the main thread — move I/O and heavy computation off the UI thread. |
| [`battery-and-data-are-the-users-budget.md`](./battery-and-data-are-the-users-budget.md) | Absolute rule | Networking and background work — batch, defer, and use push instead of polling. |
| [`use-push-not-polling.md`](./use-push-not-polling.md) | Absolute rule | Background updates — wake the app with a silent push; never poll on a fixed interval. |
| [`ask-for-permissions-in-context.md`](./ask-for-permissions-in-context.md) | Absolute rule | Any runtime permission — ask when the user is about to use the feature, not on launch. |
| [`the-store-is-part-of-the-pipeline.md`](./the-store-is-part-of-the-pipeline.md) | Absolute rule | Every release — signing, review guidelines, phased rollout, and update lag are engineering concerns. |
| [`design-for-multiple-live-versions.md`](./design-for-multiple-live-versions.md) | Absolute rule | Backend API changes — the API must support N-1 (at minimum) live app versions simultaneously. |
| [`store-tokens-in-secure-enclave.md`](./store-tokens-in-secure-enclave.md) | Absolute rule | Authentication tokens — store in Keychain (iOS) or EncryptedSharedPreferences/Keystore (Android). |
| [`certificate-pinning-for-high-risk-apps.md`](./certificate-pinning-for-high-risk-apps.md) | Pattern | High-risk network calls (financial, health) — pin the SPKI hash with a backup pin for rotation. |
| [`deep-links-need-validation.md`](./deep-links-need-validation.md) | Absolute rule | Any deep link — validate format and type before trusting parameters; check ownership server-side. |
| [`swiftui-state-ownership-hierarchy.md`](./swiftui-state-ownership-hierarchy.md) | Pattern | SwiftUI state — use the right property wrapper for each ownership scope. |
| [`compose-state-hoisting.md`](./compose-state-hoisting.md) | Pattern | Jetpack Compose — hoist state to the caller; stateless composables are testable and reusable. |
| [`react-native-list-performance.md`](./react-native-list-performance.md) | Absolute rule | React Native lists — use FlatList with keyExtractor and getItemLayout; never ScrollView for large lists. |
| [`accessibility-labels-on-all-interactive-elements.md`](./accessibility-labels-on-all-interactive-elements.md) | Absolute rule | Every interactive and image element — add accessibility labels; test with VoiceOver/TalkBack. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
