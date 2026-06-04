# Mobile Engineering

The **mobile-engineering** plugin — building native and cross-platform mobile apps well — the native-vs-cross-platform choice, iOS (Swift/SwiftUI) and Android (Kotlin/Compose) craft, offline/sync and app lifecycle, and the release/store pipeline.

## Agents

- **`mobile-architect`** — Mobile architecture and platform strategy: the native-vs-React-Native-vs-Flutter decision, app architecture (MVVM/MVI/unidirectional), module structure, offline/sync strategy, and the navigation model
- **`ios-engineer`** — Native iOS: Swift, SwiftUI (and UIKit interop), the app/scene lifecycle, Swift Concurrency (async/await, actors), Keychain secure storage, and iOS-specific patterns and Human Interface Guidelines
- **`android-engineer`** — Native Android: Kotlin, Jetpack Compose, the activity/fragment lifecycle, coroutines/Flow, the Keystore + EncryptedSharedPreferences, WorkManager for background, and Material/Android conventions
- **`cross-platform-engineer`** — React Native and Flutter: shared-codebase architecture, the bridge/native-module boundary, platform-channel/native interop, navigation, performance pitfalls, and the cross-cutting mobile concerns (push, deep links, offline) in a shared codebase

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install mobile-engineering@ravenclaude
```

## Seams

- **Shared web/React patterns, TypeScript, and component thinking** → `frontend-engineering` (especially relevant for React Native).
- **The backend API the app consumes (contract, pagination, errors, sync endpoints)** → `api-engineering` + `backend-engineering`.
- **Authentication, OAuth/PKCE on mobile, token handling** → `auth-identity` (we store tokens in the secure store; they own the flow).
- **CI/CD, code signing, and store deployment automation** → `devops-cicd` (mobile signing + Fastlane-style pipelines).
- **Push-notification backend and delivery infra** → the cloud plugin / `backend-engineering`; we own the on-device handling, deep links, and permissions.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
