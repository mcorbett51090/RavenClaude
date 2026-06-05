# Use push notifications to wake the app, not polling

**Status:** Absolute rule
**Domain:** Battery and data efficiency
**Applies to:** `mobile-engineering`

---

## Why this exists

A background polling loop that wakes the app every N minutes — to check for new messages, to sync state, to detect changes — drains the battery, consumes the user's data plan, and keeps the radio active when it would otherwise sleep. This is the exact pattern that earns one-star reviews about "my battery only lasts half a day since I installed this app." Modern mobile platforms provide push notification infrastructure (APNs on iOS, FCM on Android) precisely to replace polling: the server pushes a silent data notification when there is something to sync, and the device wakes only when needed.

## How to apply

```swift
// iOS: silent/background push to wake the app for a sync
// In AppDelegate:
func application(_ application: UIApplication,
                 didReceiveRemoteNotification userInfo: [AnyHashable: Any],
                 fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
    // Called when a silent push (content-available: 1) arrives
    Task {
        do {
            try await syncService.fetchLatestChanges()
            completionHandler(.newData)
        } catch {
            completionHandler(.failed)
        }
    }
}
```

```kotlin
// Android: FCM data message (silent) triggers background sync
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(message: RemoteMessage) {
        if (message.data.isNotEmpty()) {
            // Schedule a one-off WorkManager task for the sync
            val workRequest = OneTimeWorkRequestBuilder<SyncWorker>().build()
            WorkManager.getInstance(applicationContext).enqueue(workRequest)
        }
    }
}
```

**Do:**
- Use silent/data pushes to signal that fresh data is available; let the app fetch on wake.
- Use WorkManager (Android) / BGAppRefreshTask (iOS) for deferred sync that doesn't need real-time delivery.
- Implement exponential back-off and circuit-breaker logic for push re-registration on token refresh.
- Request push notification permissions in context (when the user performs an action that benefits from push).

**Don't:**
- Poll on a fixed interval as the primary update mechanism.
- Use foreground services to maintain a persistent polling connection — this is what push solves.
- Assume pushes arrive in order or are never dropped — the app must be resilient to missed pushes by reconciling on foreground resume.

## Edge cases / when the rule does NOT apply

Real-time financial trading apps or live video calls have sub-second latency requirements that push delivery cannot guarantee — they use persistent connections (WebSocket) instead of push. Polling is also correct for a short sync window when a user is actively using the app (e.g., pulling to refresh).

## See also

- [`../agents/mobile-architect.md`](../agents/mobile-architect.md) — owns the offline/push architecture decision.
- [`./battery-and-data-are-the-users-budget.md`](./battery-and-data-are-the-users-budget.md) — the foundational rule; this doc specifies the push pattern that satisfies it.

## Provenance

Apple WWDC sessions on background execution, Android developer docs on FCM and WorkManager. Codifies CLAUDE.md §2 rule 6 ("Battery and data are the user's budget, not yours").

---

_Last reviewed: 2026-06-05 by `claude`_
