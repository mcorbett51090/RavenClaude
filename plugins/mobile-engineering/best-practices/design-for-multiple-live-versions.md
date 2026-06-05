# Design the backend API to support multiple live app versions simultaneously

**Status:** Absolute rule
**Domain:** Mobile architecture / API versioning
**Applies to:** `mobile-engineering`

---

## Why this exists

App store updates are not instant. Users with auto-update disabled, corporate-managed devices, and users who simply do not update will run the previous version (or the one before that) for weeks to months. When the backend makes a breaking change, it silently breaks every user still running the old version. Mobile apps are the canonical motivation for additive-only API changes, versioned endpoints, and graceful handling of unknown server fields — the old app must continue to function for a defined support window after a new version ships.

## How to apply

```swift
// iOS: version-aware response handling — unknown fields should not crash the app
struct UserProfile: Codable {
    let id: String
    let name: String
    let email: String
    // New fields added by the server are ignored automatically
    // because Codable by default ignores unknown keys
}

// Prompt the user to update only when the server indicates the version is unsupported
func checkVersionSupport(response: ServerVersionResponse) {
    switch response.supportStatus {
    case .current:  break
    case .deprecated:  showSoftUpdateBanner()   // recommend, don't force
    case .unsupported:  showForceUpdateScreen()  // only when truly broken
    }
}
```

```kotlin
// Android: Moshi / Gson ignores unknown fields by default — do not add @SerializedName strictness
// Announce deprecation gracefully:
if (appVersion < minSupportedVersion) {
    showForceUpdateDialog()
    return
}
```

**Do:**
- Define a minimum supported version contract with the backend; agree on a deprecation window (e.g., 90 days) before a version is declared unsupported.
- Make all app clients ignore unknown JSON fields (the default in most mobile JSON libraries).
- Build a version-check endpoint / version header in the API so the app can react gracefully to deprecation.
- Use phased rollout in the store so a bad release can be stopped before 100% of users update.

**Don't:**
- Hard-fail when the server returns an unknown enum value or extra field — treat it as the default/unknown case.
- Require all users to have the latest version before backend changes ship — coordinate timelines.
- Force update on every version mismatch; reserve force-update for genuine incompatibilities.

## Edge cases / when the rule does NOT apply

Beta channels and internal test tracks where all devices are managed and update on a fixed cadence may support a shorter (or zero) backward-compatibility window.

## See also

- [`../agents/mobile-architect.md`](../agents/mobile-architect.md) — owns versioning strategy and multi-version compatibility design.
- [`./the-store-is-part-of-the-pipeline.md`](./the-store-is-part-of-the-pipeline.md) — phased rollout and release management are the tools that make multi-version operation safe.

## Provenance

CLAUDE.md §2 rule 5 ("The store is part of the pipeline — update lag is an engineering concern"). Standard mobile API compatibility practice. Codifies `mobile-architect` and platform engineer responsibilities.

---

_Last reviewed: 2026-06-05 by `claude`_
