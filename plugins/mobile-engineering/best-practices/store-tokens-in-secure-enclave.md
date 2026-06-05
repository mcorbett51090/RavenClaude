# Store authentication tokens in the platform secure store, never in plain storage

**Status:** Absolute rule
**Domain:** Mobile security
**Applies to:** `mobile-engineering`

---

## Why this exists

Tokens stored in plain `UserDefaults` (iOS) or `SharedPreferences` (Android) are readable by any app with a backup extractor or physical access to a rooted device. The Keychain (iOS) and Android Keystore are hardware-backed secure enclaves specifically designed for credential storage — they are not accessible to other apps, they survive app reinstall, and on modern devices the private key material never leaves the secure element. A token stored outside the secure store is a credential waiting to be extracted.

## How to apply

```swift
// iOS — Keychain via Security framework
import Security

func saveToken(_ token: String, forKey key: String) throws {
    let data = token.data(using: .utf8)!
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecValueData as String: data,
        kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
    ]
    SecItemDelete(query as CFDictionary)  // delete before update
    let status = SecItemAdd(query as CFDictionary, nil)
    guard status == errSecSuccess else { throw KeychainError.saveFailed(status) }
}
```

```kotlin
// Android — EncryptedSharedPreferences backed by Keystore
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val securePrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
)
securePrefs.edit().putString("auth_token", token).apply()
```

**Do:**
- Use `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` (iOS) — requires device unlock; not backed up to iCloud.
- Use `EncryptedSharedPreferences` or `Keystore`-backed encryption (Android) for any sensitive value.
- Clear tokens on logout with an explicit delete call.
- Store only the token itself in the secure store; store non-sensitive metadata (username display) in regular storage.

**Don't:**
- Store tokens in `UserDefaults`, `NSUserDefaults`, `SharedPreferences`, or `NSCoder` archives.
- Store tokens in plain files in the app sandbox, even if the device is not rooted.
- Use `kSecAttrAccessibleAlways` or `kSecAttrAccessibleAfterFirstUnlock` if your threat model includes device theft in the locked state.

## Edge cases / when the rule does NOT apply

Non-sensitive preferences (UI theme, language, display name) do not need the secure store. The secure store has limited capacity; bulk data never belongs there — only secrets and credentials.

## See also

- [`../agents/ios-engineer.md`](../agents/ios-engineer.md) — owns iOS Keychain integration.
- [`../agents/android-engineer.md`](../agents/android-engineer.md) — owns Android Keystore and EncryptedSharedPreferences.

## Provenance

iOS Security framework docs (developer.apple.com/documentation/security), Android EncryptedSharedPreferences docs (developer.android.com). Codifies CLAUDE.md §2 rule 4: "Secure storage is the Keychain/Keystore, not preferences."

---

_Last reviewed: 2026-06-05 by `claude`_
