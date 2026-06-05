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

## Decision Tree: Which navigation architecture for a React Native app?

**When this applies:** You are setting up navigation in a React Native application and must choose between navigation libraries and decide the navigation state model. Triggered at project setup or when the current navigation structure causes deep-linking or state-restoration problems.

**Last verified:** 2026-06-05 against React Navigation 6 and Expo Router documentation.

```mermaid
flowchart TD
    START[React Native app needs navigation] --> Q1{Using Expo or bare React Native?}
    Q1 -->|Expo managed or SDK workflow| Q2{Need file-based routing like Next.js?}
    Q2 -->|Yes - large app, web-parity desired| EXPOROUTER[Expo Router - file-based, deep links auto-configured]
    Q2 -->|No - prefer explicit stack config| REACTNAV[React Navigation 6 - explicit navigator config]
    Q1 -->|Bare React Native| REACTNAV
    REACTNAV --> Q3{Deep links required?}
    Q3 -->|Yes| LINKING[Configure linking prop on NavigationContainer]
    Q3 -->|No| STACKS[Define stacks and tabs declaratively]
    EXPOROUTER --> DEEPAUTO[Deep links handled by file convention]
    LINKING --> STACKS
    STACKS --> Q4{Cross-tab state needed in nav state?}
    Q4 -->|Yes - e.g. badge counts| ZUSTAND[Lift to Zustand or context outside nav state]
    Q4 -->|No| DONE[Navigation state is self-contained]
```

**Rationale per leaf:**
- *Expo Router* — file-based routing reduces navigation boilerplate and makes deep links automatic; best for Expo SDK apps with many routes.
- *React Navigation 6* — the explicit stack/tab/drawer API gives precise control; the standard for bare React Native.
- *Linking config* — required for Universal Links and App Links to map URLs to screens.
- *Zustand outside nav state* — navigation state is not the right place for cross-tab business state; keep nav state purely navigational.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Expo Router | Low | File-convention coupling | None | Expo SDK app, many routes |
| React Navigation 6 | Medium | Explicit config overhead | None | Bare RN or complex nav trees |
| Zustand for cross-tab state | Low | External dep | None | Shared state across tab roots |

## Decision Tree: Handle a runtime permission request — when and how?

**When this applies:** The app needs a runtime permission (camera, location, notifications, contacts) and you must decide when to ask and how to handle denial.

**Last verified:** 2026-06-05 against Apple Human Interface Guidelines (permission best practices) and Android developer documentation.

```mermaid
flowchart TD
    START[App needs a runtime permission] --> Q1{Is the feature the user is trying to use right now blocked without the permission?}
    Q1 -->|No - asking proactively on launch| WAIT[Don't ask yet - wait for in-context trigger]
    Q1 -->|Yes - user just initiated the feature| Q2{Has permission been permanently denied before?}
    Q2 -->|Yes - iOS never ask again / Android permanently denied| SETTINGS[Show explanation + deep link to Settings to enable manually]
    Q2 -->|No - first ask or previously denied once| Q3{High-value feature where the reason is obvious?}
    Q3 -->|Yes - camera in a camera app| ASKDIRECT[Ask directly - the context makes the reason clear]
    Q3 -->|No - less obvious value to the user| RATIONALIZE[Show a pre-permission rationale UI first, then ask]
    ASKDIRECT --> Q4{Granted?}
    RATIONALIZE --> Q4
    Q4 -->|Yes| PROCEED[Proceed with the feature]
    Q4 -->|No| DEGRADE[Degrade gracefully - offer limited functionality without the permission]
```

**Rationale per leaf:**
- *Wait for context* — asking on launch without context produces denial; users don't know why the app needs the permission.
- *Settings deep link* — once permanently denied, the OS will not show the permission dialog again; the only path is manual Settings.
- *Ask directly* — when context makes the need obvious (camera in a camera app), an explanation screen adds friction without value.
- *Pre-permission rationale* — a brief "we need your location to show nearby stores" screen before the OS dialog improves grant rates.
- *Graceful degradation* — the app must work (with reduced features) for users who deny; never crash or block on a denied permission.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Ask directly | Minimal | May reduce grant rate | None | Feature need is self-evident |
| Rationale then ask | Low | Better grant rate | None | Non-obvious permission |
| Settings deep link | Low | Friction for user | None | Permanently denied |
| Graceful degradation | Medium | Reduced feature set | None | Permission denied or not yet granted |

## Decision Tree: Implement network retry for a mobile API call

**When this applies:** A mobile API call fails and you need to decide whether to retry, show an error, or queue for later. Triggered by a network error, a 5xx response, or a timeout during any foreground or background network operation.

**Last verified:** 2026-06-05 against URLSession and OkHttp retry documentation and standard mobile networking patterns.

```mermaid
flowchart TD
    START[API call failed] --> Q1{What is the failure type?}
    Q1 -->|4xx - client error - bad request / auth| Q2{Is it a 401 Unauthorized?}
    Q2 -->|Yes| REFRESH[Refresh the auth token - retry once - if still 401 log out]
    Q2 -->|No - other 4xx| DISPLAY[Display error to user - do not retry client errors]
    Q1 -->|5xx or network error or timeout| Q3{Is the operation safe to retry - idempotent?}
    Q3 -->|No - POST with side effects, no idempotency key| QUEUE[Queue for explicit user retry - do not auto-retry]
    Q3 -->|Yes - GET or idempotent POST| Q4{Is the user waiting for the result?}
    Q4 -->|Yes - foreground request| BACKOFF[Retry up to 3 times with exponential backoff - surface error if exhausted]
    Q4 -->|No - background sync| WORKMANAGER[Defer to WorkManager - Android - or BGProcessingTask - iOS - with retry policy]
    REFRESH --> DONE[Retry with new token]
    BACKOFF --> DONE
    WORKMANAGER --> DONE
```

**Rationale per leaf:**
- *Token refresh then retry* — a 401 usually means an expired access token; refresh and retry once before logging out.
- *Display 4xx errors* — client errors indicate a bug or a user action that cannot succeed by retrying; auto-retry would loop forever.
- *Queue for user retry* — non-idempotent writes (create order, submit payment) should not auto-retry; the user should confirm.
- *Exponential backoff for foreground* — transient server errors usually resolve quickly; a few retries with backoff are appropriate.
- *WorkManager / BGTask for background* — the OS job scheduler handles retry policy, battery budgets, and connectivity waits.

**Tradeoffs summary:**

| Method | Cost / time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| Immediate retry | Minimal | May amplify server load | None | Very short transient errors |
| Exponential backoff | Low | Bounded retry count | None | Foreground transient failures |
| User-initiated retry | Minimal | User friction | None | Non-idempotent operations |
| WorkManager / BGTask | Low-medium | OS-deferred | None | Background sync, deferrable |
