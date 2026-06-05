# Run background work through the OS scheduler, not a long-running service

**Status:** Absolute rule
**Domain:** Mobile background execution
**Applies to:** `mobile-engineering`

---

## Why this exists

Both mobile OSes aggressively reclaim background CPU, network, and wakelocks to protect battery —
Android via Doze and App Standby buckets, iOS by simply not scheduling your code when the app is
suspended. A naive "keep a service running and poll" design is the single biggest cause of battery
complaints and of work that silently never runs: the OS kills the service, defers the alarm, or
throttles the bucket, and the developer never sees it because it "worked on my device" plugged in.
The reliable pattern is to *describe* the work and its constraints to the OS scheduler and let the
platform pick the moment — it will batch it with other apps' work to amortize the radio wakeup.

## How to apply

Use the platform's deferrable-work API with constraints, and make the work idempotent because it
may run later, twice, or after a reboot:

```
Android: WorkManager — OneTime/PeriodicWorkRequest with Constraints
         (network type, charging, battery-not-low); survives reboot; auto-backoff.
iOS:     BGTaskScheduler — BGAppRefreshTask (short, frequent) and
         BGProcessingTask (longer, e.g. on charger); register identifiers in Info.plist.
```

**Do:**

- Express **constraints** (needs network / charging / unmetered) and let the OS choose timing — don't fight the scheduler with exact alarms.
- Make each job **idempotent**; deferred work can run after a reboot, late, or be retried with backoff.
- Use **push** to trigger time-sensitive sync rather than periodic polling (see the push doc).
- Test under **Doze / Low Power Mode and on battery**, not just a plugged-in debug build.

**Don't:**

- Hold a partial wakelock or foreground service to keep polling — reserve foreground services for genuinely user-visible ongoing work (navigation, media, active upload) with a notification.
- Assume periodic work runs on a precise interval; the OS coalesces and defers it.

## Edge cases / when the rule does NOT apply

- **Genuinely continuous, user-visible tasks** (turn-by-turn nav, audio playback, an active file transfer) legitimately use a foreground service / background mode with the right entitlement.
- **Exact-time obligations** (a medication alarm) use the platform's exact-alarm API with the explicit permission — a deliberate, justified exception to deferral.

## See also

- [`../agents/android-engineer.md`](../agents/android-engineer.md) — WorkManager, Doze, and standby buckets.
- [`./use-push-not-polling.md`](./use-push-not-polling.md) — push as the trigger for time-sensitive sync instead of background polling.

## Provenance

Codifies the `android-engineer` / `ios-engineer` background-execution discipline (WorkManager +
BGTaskScheduler with constraints, idempotent jobs) and the platform battery-governance model (Doze,
App Standby, iOS suspension).

---

_Last reviewed: 2026-06-05 by `claude`_
