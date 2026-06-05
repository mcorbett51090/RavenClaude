---
scenario_id: 2026-06-05-push-notification-delivery-gaps
contributed_at: 2026-06-05
plugin: mobile-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [push, apns, fcm, delivery, background, doze, notifications]
confidence: medium
reviewed: false
---

## Problem

A messaging app's push notifications were "unreliable" — users reported messages arriving minutes late, in bursts, or not at all until they opened the app. The backend logged successful sends to APNs and FCM, so the team assumed a client bug. The drop-off was worst on Android (especially after the phone sat idle overnight) and on iOS for *data-only* (silent) pushes used to pre-fetch content.

## Constraints context

- Push delivery is **best-effort**, not guaranteed — APNs and FCM both reserve the right to throttle, coalesce, or drop, especially low-priority and silent pushes. The team had been treating push as a reliable transport.
- Android **Doze / App Standby** batches and defers background work and non-high-priority FCM messages when the device is idle — exactly the overnight pattern users reported.
- iOS **silent (content-available) pushes** are explicitly rate-limited and budgeted by the system; the OS decides if/when to wake the app, and an app the user rarely opens gets a smaller budget.
- A stale/expired device token problem: tokens rotate (reinstall, OS update, restore), and the backend kept sending to dead tokens, counting the send as "success" because the push service accepted it for delivery — acceptance is not delivery.

## Attempts

- Tried: increasing send frequency / re-sending the same notification to "force" delivery. Made it worse — more coalescing, users got duplicate or clustered notifications, and the silent-push budget got exhausted faster. Treating a best-effort channel as retry-until-delivered backfires.
- Tried: relying on silent (data-only) pushes to keep content fresh in the background. Failed by design — the OS budgets and throttles silent wakeups; they are a *hint*, not a guarantee, and an idle/rarely-opened app gets few of them.
- Tried (the fix): treated push as a **wake-up hint, not a data channel**. High-priority notifications for genuinely time-sensitive, user-facing messages; on wake, the app **pulls** the actual state from the server (push says "something changed," the app fetches the truth). Added token lifecycle handling (capture rotations, prune tokens the service reports as unregistered), and used a foreground/WorkManager + BGTask sync as the reliable backstop so content is correct even when a push never arrives.

## Resolution

**Push is a best-effort wake-up hint; correctness must come from the app pulling state, never from assuming every push is delivered.** The reliable shape:

1. **Push notifies, the app reconciles.** A push means "something may have changed — wake and fetch." The source of truth is the server, fetched on wake or next foreground, not the push payload. An app that's correct only if every push lands will look broken to every user the OS throttles.
2. **Respect the OS battery/idle regime.** Android Doze/App Standby and iOS silent-push budgets *will* defer and drop background pushes; design for late, batched, or absent delivery (the project's "Background work" tree). Use high priority only for genuinely time-sensitive user-facing messages — abusing it burns trust and budget.
3. **Manage the token lifecycle.** Tokens rotate; capture rotations, and prune tokens the push service reports as unregistered/invalid. "The service accepted the send" is *acceptance*, not *delivery* — don't count it as success.
4. **Have a pull backstop.** A foreground refresh + a scheduled background sync (WorkManager / BGTask) keeps content correct even when no push arrives. Push improves latency; the backstop guarantees eventual correctness.
5. **Don't spam to compensate.** Re-sending to force delivery causes coalescing, duplicates, and budget exhaustion — the opposite of reliability.

The mental model: push is a doorbell, not a delivery truck. It tells the app to go look; it does not carry the package, and sometimes it doesn't ring at all. Build for the doorbell to be missed.

**Action for the next engineer:** when push is "unreliable," stop trying to make the channel guaranteed. Switch to push-as-wake-up-then-pull, verify token lifecycle handling (acceptance ≠ delivery), and add a pull-based sync backstop. Then audit priority/silent-push usage against the OS battery regime (Doze / silent-push budget).

Cross-reference: complements [`../best-practices/use-push-not-polling.md`](../best-practices/use-push-not-polling.md), [`../best-practices/background-work-uses-os-schedulers.md`](../best-practices/background-work-uses-os-schedulers.md), and [`../best-practices/battery-and-data-are-the-users-budget.md`](../best-practices/battery-and-data-are-the-users-budget.md). The push-notification *backend* and delivery infra are the cloud / `backend-engineering` lane; this team owns on-device handling, the wake-then-pull model, and token lifecycle. See the "Background work" tree in [`../knowledge/mobile-engineering-decision-trees.md`](../knowledge/mobile-engineering-decision-trees.md).
</content>
