# Secure storage (pattern)

## iOS
```
Keychain (kSecAttrAccessibleAfterFirstUnlock) for tokens
```
## Android
```
Keystore-backed key -> EncryptedSharedPreferences for tokens
```
## Cross-platform
```
use the secure-store plugin (Keychain/Keystore) — NOT AsyncStorage/SharedPreferences in clear
```
Auth flow (PKCE) -> auth-identity; storage -> here.
