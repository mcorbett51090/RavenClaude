---
name: cross-platform-mobile
description: "Build React Native/Flutter well: maximize shared logic while honoring per-platform conventions, manage the bridge/platform-channel native boundary (and write native modules when needed), avoid framework-specific performance pitfalls, and handle push/deep-links/offline once with secrets in the secure store."
---

# Cross-Platform Mobile

## Share + respect
Share logic/UI; honor **per-platform** navigation, conventions, accessibility. Identically non-native on both = UX fail.

## Native boundary
RN bridge / Flutter platform channels: batch crossings; write **native modules** for unavailable capabilities. Don't fight the framework for the last 5%.

## Performance
RN: FlatList virtualization, Fabric/TurboModules, avoid bridge chatter. Flutter: const widgets, avoid rebuilds. **Profile.**

## Cross-cutting once
Push + deep/universal links + offline in the shared layer. Secrets -> secure store plugin (Keychain/Keystore), never AsyncStorage in clear.
