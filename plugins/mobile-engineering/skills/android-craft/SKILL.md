---
name: android-craft
description: "Build native Android the platform way: state-driven Jetpack Compose (state hoisting, remember, list keys), coroutines/Flow with lifecycle-scoped structured concurrency, Keystore/EncryptedSharedPreferences, WorkManager background respecting Doze, and Material + accessibility."
---

# Android Craft

## Compose
UI = f(state). Hoist state, `remember` correctly, **key** lists. Recomposition loops = unstable state / missing keys.

## Coroutines
Lifecycle-scoped (`viewModelScope`), `Flow`/`StateFlow`, right dispatcher, cancel with scope. No leaked coroutines.

## Secrets & background
**Keystore** / EncryptedSharedPreferences (never plain prefs). **WorkManager** for background (respects Doze).

## Platform
Lifecycle-aware components, process-death handling, Material + TalkBack + predictive back.
