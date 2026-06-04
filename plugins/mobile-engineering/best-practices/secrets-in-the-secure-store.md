# Store secrets in the Keychain/Keystore, never in preferences

Tokens, credentials, and sensitive data belong in the platform secure store — iOS Keychain, Android Keystore/EncryptedSharedPreferences — never in UserDefaults, SharedPreferences, or AsyncStorage, which are plaintext on a device you do not control. On-device storage assumes a hostile environment (lost/rooted/jailbroken devices), and the secure store is the only acceptable place for credentials.
