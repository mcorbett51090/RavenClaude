# Implement certificate pinning for high-risk network communication

**Status:** Pattern
**Domain:** Mobile security / networking
**Applies to:** `mobile-engineering`

---

## Why this exists

TLS validates that a certificate was signed by a trusted CA — but a device with an added corporate or malicious root CA can intercept TLS traffic invisibly. Certificate pinning goes further: the app validates that the server's certificate or public key matches a known-good value hardcoded at build time. For high-risk operations (financial transactions, health data, credential exchange), the additional protection against MITM attacks — including from malicious MDM-installed root CAs — is worth the operational cost of managing pin rotation.

## How to apply

```swift
// iOS: URLSession + TrustKit or NSURLSession delegate
// TrustKit approach [verify-at-build — check version]:
let trustKitConfig: [String: Any] = [
    kTSKSwizzleNetworkDelegates: false,
    kTSKPinnedDomains: [
        "api.example.com": [
            kTSKEnforcePinning: true,
            kTSKIncludeSubdomains: false,
            kTSKPublicKeyHashes: [
                "base64-encoded-sha256-of-leaf-spki=",
                "base64-encoded-sha256-of-backup-key=",  // rotation backup
            ],
            kTSKExpirationDate: "2027-01-01",  // force pin refresh before expiry
        ]
    ]
]
TrustKit.initShared(withConfiguration: trustKitConfig)
```

```kotlin
// Android: OkHttp CertificatePinner
val pinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/base64-encoded-spki-hash=")
    .add("api.example.com", "sha256/backup-key-hash=")  // rotation backup
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(pinner)
    .build()
```

**Do:**
- Pin the Subject Public Key Info (SPKI) hash, not the full certificate — SPKI is stable across certificate renewals.
- Always include at least one backup pin (from a different CA / future rotation key) to allow key rotation without a forced app update.
- Set an expiration date on pins and build a server-side pin update delivery mechanism.
- Test pin failures in development so you know what users see when pinning blocks a connection.

**Don't:**
- Pin in development or QA environments — it breaks proxy-based debugging and automated test tools.
- Ship a single pin without a backup — a certificate renewal without a matching pin update will lock users out.
- Use pinning as the only security layer — it complements, not replaces, proper TLS configuration and authentication.

## Edge cases / when the rule does NOT apply

Low-risk apps (content browsing, marketing apps) do not require certificate pinning — the operational cost of key rotation outweighs the marginal security gain. Apps that exclusively serve behind an enterprise MDM (where the root CA is controlled) may prefer MDM-managed certificate validation.

## See also

- [`../agents/ios-engineer.md`](../agents/ios-engineer.md) — owns iOS networking and TrustKit integration.
- [`../agents/android-engineer.md`](../agents/android-engineer.md) — owns OkHttp and Android network security config.

## Provenance

OWASP Mobile Security Testing Guide (MSTG) — network communication section. TrustKit and OkHttp documentation. Codifies `mobile-architect`'s and platform engineers' security posture for sensitive mobile apps.

---

_Last reviewed: 2026-06-05 by `claude`_
