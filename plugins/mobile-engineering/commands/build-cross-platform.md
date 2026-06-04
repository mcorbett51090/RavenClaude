---
description: "Build a React Native/Flutter feature that respects each platform, manages the native boundary, and handles cross-cutting concerns once."
argument-hint: "[cross-platform feature or perf issue]"
---

You are running `/mobile-engineering:build-cross-platform`. Use `cross-platform-engineer` + the `cross-platform-mobile` skill.

## Steps
1. Share logic; honor per-platform conventions/accessibility.
2. Manage the bridge/platform-channel boundary; native module if needed.
3. Profile + fix framework-specific perf (lists, rebuilds, bridge chatter).
4. Handle push/deep-links/offline once; secrets in the secure store.
5. Emit + Structured Output block.
