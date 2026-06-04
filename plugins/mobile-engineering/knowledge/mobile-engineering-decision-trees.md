# Mobile Engineering — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before choosing a platform approach or an offline strategy.

## Decision Tree: Native or cross-platform?

Choose by the app's real needs, not team familiarity.

```mermaid
graph TD
  A[A mobile app] --> B{Heavy platform-specific UX or top-tier performance?}
  B -- Yes --> C[Native: Swift + Kotlin]
  B -- No --> D{Need newest OS features immediately?}
  D -- Yes --> C
  D -- No --> E{Largely shared business logic across both?}
  E -- Yes --> F{Team strength?}
  F -- React/JS --> G[React Native]
  F -- Dart/greenfield --> H[Flutter]
  E -- No, one platform only --> I[Native for that platform]
```

_Name the trade — cross-platform buys shared iteration and pays at the native boundary + last-5% UX._

## Decision Tree: Offline & sync strategy

Mobile is offline-first; design the source of truth and conflict policy up front.

```mermaid
graph TD
  A[Data in the app] --> B{Must work offline / on flaky network?}
  B -- No, always-online tool --> C[Cache for resilience; server is source of truth]
  B -- Yes --> D[Local DB = source of truth]
  D --> E[Write queue for offline mutations]
  E --> F{Concurrent edits possible?}
  F -- No --> G[Last-write-wins on sync]
  F -- Yes --> H{Auto-mergeable?}
  H -- Yes --> I[Field-merge / CRDT]
  H -- No --> J[Prompt user to resolve]
```


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| SwiftUI + Swift Concurrency | GA | State-driven; actors for races |
| Jetpack Compose + Coroutines/Flow | GA | State hoisting; lifecycle scopes |
| React Native new architecture (Fabric/TurboModules) | GA-ing | Verify per RN version |
| Flutter | GA | Const widgets; impeller renderer |
| Keychain / Android Keystore | GA | Secure storage for secrets |
| WorkManager / BGTaskScheduler | GA | Battery-respecting background |
| Push (APNs / FCM) | GA | On-device handling here; backend elsewhere |
