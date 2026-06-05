# Validate deep link parameters before trusting them

**Status:** Absolute rule
**Domain:** Mobile security
**Applies to:** `mobile-engineering`

---

## Why this exists

A deep link is an external input from any actor: another app, a web browser, an email, a QR code. An app that parses a deep link URL and directly uses its parameters to navigate, prefill data, or trigger actions without validation is executing untrusted input — the mobile equivalent of SQL injection. Attackers craft links that navigate users to unexpected screens, pass attacker-controlled IDs as object identifiers, or force actions the app didn't intend to expose publicly. Universal Links (iOS) and App Links (Android) reduce the spoofing risk, but the parameter content still needs validation.

## How to apply

```swift
// iOS: validate deep link parameters before using them
func handleDeepLink(_ url: URL) {
    guard let components = URLComponents(url: url, resolvingAgainstBaseURL: true),
          let path = components.path.components(separatedBy: "/").dropFirst().first
    else { return }

    switch path {
    case "order":
        guard let orderIdString = components.queryItems?.first(where: { $0.name == "id" })?.value,
              let orderId = UUID(uuidString: orderIdString)  // validate format
        else { return }  // silently reject malformed input
        // Load order and check ownership server-side before displaying
        navigateToOrder(orderId)
    default:
        // Unknown path — navigate to home, not crash
        navigateToHome()
    }
}
```

```kotlin
// Android: validate intent data in the activity
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    val uri = intent.data ?: return
    val orderId = uri.getQueryParameter("id")
        ?.takeIf { it.matches(Regex("[0-9a-f-]{36}")) }  // UUID format only
        ?: run { navigateToHome(); return }
    loadOrder(orderId)  // server checks ownership
}
```

**Do:**
- Validate the format and type of every deep link parameter before using it.
- Treat deep link destination routing the same as any user navigation — apply the same authorization checks.
- Use Universal Links (iOS) / App Links (Android) to prevent deep link hijacking by other apps.
- Log deep link arrival with origin information for security monitoring.

**Don't:**
- Pass deep link parameters directly to queries, file paths, or navigation without validation.
- Trust that a deep link came from your own app or website without Universal Links / App Links verification.
- Display deep link parameter content directly in the UI without sanitization.

## Edge cases / when the rule does NOT apply

Deep links in development debug builds that bypass validation for testing convenience — gate these behind a debug build flag and strip them from production builds.

## See also

- [`../agents/ios-engineer.md`](../agents/ios-engineer.md) — owns Universal Links and iOS deep link handling.
- [`../agents/android-engineer.md`](../agents/android-engineer.md) — owns App Links and Android intent filter handling.

## Provenance

OWASP Mobile Security Testing Guide (MSTG) — deep link validation. Apple Universal Links documentation. Codifies the mobile security posture across platform engineers in this plugin.

---

_Last reviewed: 2026-06-05 by `claude`_
