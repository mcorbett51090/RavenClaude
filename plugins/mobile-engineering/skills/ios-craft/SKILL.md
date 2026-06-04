---
name: ios-craft
description: "Build native iOS the platform way: state-driven SwiftUI with correct property-wrapper ownership, Swift Concurrency (async/await, actors, @MainActor), Keychain secure storage, lifecycle/background-task handling, and Human Interface Guidelines + accessibility."
---

# iOS Craft

## SwiftUI
UI = f(state). Right wrapper for ownership (`@State`/`@Observable`/`@Binding`). 'Won't update' = ownership bug.

## Concurrency
`async/await`; **actors** for shared mutable state; `@MainActor` for UI; structured over detached.

## Secrets & lifecycle
**Keychain** (never UserDefaults) with data-protection class. Save state for restoration; respect background limits.

## Platform
HIG + accessibility (VoiceOver, Dynamic Type). Watch retain cycles (`[weak self]`).
