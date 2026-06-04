---
name: mobile-platform-choice
description: "Decide native vs React Native vs Flutter by the app's real needs (platform-specific UX, performance, OS-feature access, team), and set the offline-first sync strategy (local source of truth, write queue, conflict resolution) and lifecycle-survival plan."
---

# Mobile Platform Choice

## Native vs cross-platform
| Need | Approach |
|---|---|
| Heavy platform-specific UX / top performance / newest OS features | **Native** (Swift+Kotlin) |
| Largely shared business app, one team, faster shared iteration | **React Native / Flutter** |

Name the trade; don't default to preference.

## Offline-first (from day one)
Local DB = **source of truth**, synced to server; a **write queue** for offline mutations; a **conflict-resolution** policy (last-write-wins / merge / prompt). Retrofitting offline is a rewrite.

## Lifecycle
Survive backgrounding, process death, restoration. The OS will kill you; plan for it.
