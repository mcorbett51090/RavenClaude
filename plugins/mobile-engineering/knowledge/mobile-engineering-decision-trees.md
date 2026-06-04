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


## Decision Tree: Background work — which API, and is it even allowed?

The OS, not your code, decides when background work runs; pick the API that matches the job's urgency and constraints.

```mermaid
graph TD
  A[Work to run not-in-foreground] --> B{Must complete now, user-initiated, finishes in seconds?}
  B -- Yes --> C[Foreground service Android / short bg task iOS - shows it's working]
  B -- No --> D{Deferrable, needs guaranteed eventual run?}
  D -- Yes --> E[WorkManager Android / BGProcessingTask iOS - OS schedules under Doze/budget]
  D -- No, time-sensitive but server-driven --> F[Push to wake the app - silent/data push, then short task]
  C --> G{Long-running media/location?}
  G -- Yes --> H[Declared background mode + the right entitlement/foreground type]
  E --> I[Assume it runs late, batched, and maybe not at all on low battery]
  F --> I
```

_There is no "run whenever I want" background API — the OS throttles everything. Design the work to be deferrable, batched, and resumable, and let push wake the app for time-sensitive cases._

## Decision Tree: Resolving a sync conflict

The concurrent edit will happen; decide the policy by how costly a wrong merge is.

```mermaid
graph TD
  A[Local + server both changed a record] --> B{Is the field set additive/commutative?}
  B -- Yes, e.g. counters, sets --> C[CRDT / field-merge - converges automatically]
  B -- No --> D{Do edits touch disjoint fields?}
  D -- Yes --> E[Field-level merge - combine non-overlapping changes]
  D -- No, same field both sides --> F{Is silently losing one edit acceptable?}
  F -- Yes, low-stakes --> G[Last-write-wins by server timestamp/version]
  F -- No, high-stakes --> H[Surface both versions; let the user resolve]
  C --> I[Track a version/vector clock to detect divergence]
  E --> I
  G --> I
```

_Last-write-wins is the cheap default that quietly destroys one user's edit; for anything the user would miss, detect the conflict with a version and let a merge or the human decide._

## Decision Tree: Where should this data live on the device?

Match the store to sensitivity and shape; the secure store is for secrets, not bulk data.

```mermaid
graph TD
  A[Data to persist on device] --> B{Is it a credential/token/secret?}
  B -- Yes --> C[Keychain / Android Keystore - never plain prefs]
  B -- No --> D{Structured, queried, or large/relational?}
  D -- Yes --> E[Local DB: Room/SQLite/Core Data/SwiftData - the offline source of truth]
  D -- No --> F{Small key-value app settings?}
  F -- Yes --> G[UserDefaults / SharedPreferences - non-sensitive only]
  F -- No, files/blobs --> H[App sandbox files; mark sensitive ones protected/encrypted]
  E --> I{Contains personal/sensitive records?}
  I -- Yes --> J[Encrypt at rest - SQLCipher/file protection]
```

_Preferences stores are plaintext and the secure store is small — put secrets in the Keychain/Keystore and structured offline data in an (encrypted-if-sensitive) local database, never the other way around._

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
