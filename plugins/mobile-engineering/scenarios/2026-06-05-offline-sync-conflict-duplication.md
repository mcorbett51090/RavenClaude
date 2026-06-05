---
scenario_id: 2026-06-05-offline-sync-conflict-duplication
contributed_at: 2026-06-05
plugin: mobile-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [offline-first, sync, conflict, idempotency, last-write-wins, duplication]
confidence: high
reviewed: false
---

## Problem

A field-service app let technicians create work-order notes offline and synced them when connectivity returned. In the field, users reported **duplicate notes** — the same note appearing two or three times — and occasionally a note's edit silently vanished. The duplication spiked when a tech moved through patchy coverage (LTE flickering on and off), which is exactly when the feature most needed to work.

## Constraints context

- Offline-first by design: the local DB (SQLite) was the source of truth; mutations queued while offline and replayed on reconnect.
- The sync client POSTed each queued mutation to the server and marked it "synced" *after* a 2xx. The server assigned the canonical ID and returned it.
- The flaky-network failure: the POST reached the server and the row was created, but the **response** never made it back (timeout / connection drop). The client, seeing no 2xx, left the mutation queued and retried on the next sync — creating a second server row. Classic at-least-once delivery from the client's side.
- Concurrent edits were possible: two techs (or the same tech on two devices) could edit the same work order, and the server used last-write-wins by arrival time, quietly dropping one edit.

## Attempts

- Tried: marking the mutation synced *before* the POST so it wouldn't retry. Replaced duplication with *data loss* — if the POST genuinely failed, the mutation was gone. Strictly worse; rejected.
- Tried: a longer client timeout so responses had more time to arrive. Reduced the duplicate rate but didn't eliminate it — a dropped connection drops the response regardless of timeout. Treating the symptom.
- Tried: a server-side dedup window ("ignore identical notes within 5 min"). Brittle heuristic — a tech legitimately entering two similar notes got one swallowed. Wrong primitive.
- Tried (the fix): a **client-generated stable ID** (UUID minted on the device when the note is created) carried as an idempotency key, plus a server unique constraint on it. A retried POST with the same client ID is recognized as a replay and returns the existing row instead of creating a new one. For the concurrent-edit case, added a per-record version and surfaced a conflict instead of silent last-write-wins on the fields that mattered.

## Resolution

**Offline sync is an at-least-once pipeline from the client; the dedup key must be minted on the device, not assigned by the server.** The reliable shape:

1. **Mint a stable ID on the device at creation time** (UUID), and carry it as the mutation's idempotency key through every retry. The server's unique constraint on that key makes a replayed POST a no-op that returns the existing resource — so a lost *response* can never create a second row.
2. **Never mark synced before the server confirms, and never let a lost response cause a duplicate.** Those two pull in opposite directions unless the dedup key breaks the tie — which is exactly what the client ID does. Mark synced only on a 2xx (or a recognized "already exists for this key" reply).
3. **Pick a conflict policy by how costly a wrong merge is** (the project's "Resolving a sync conflict" tree). Additive/commutative fields → field-merge/CRDT; disjoint fields → field-level merge; same field, high-stakes → detect via a version/vector clock and surface both versions; only low-stakes fields get last-write-wins. Silent LWW is the default that quietly destroys an edit.
4. **Make sync resumable and idempotent on both ends.** The flaky-network case is the *normal* case on mobile — design for the response to vanish, not for the happy path.

The mental model: on mobile, the network will deliver your write and then lose your acknowledgement. If the server can't recognize the retry as the same logical operation, every flaky reconnect manufactures a duplicate.

**Action for the next engineer:** if an offline-sync feature is duplicating records, the first thing to check is whether the dedup identity is **client-minted and carried through retries** or **server-assigned after the fact**. Server-assigned IDs can't dedup a write whose response was lost — only a device-side stable key plus a server unique constraint can.

Cross-reference: complements [`../best-practices/offline-first-by-design.md`](../best-practices/offline-first-by-design.md) and the [`offline-sync-design`](../templates/offline-sync-design.md) template, and traverses the "Offline & sync strategy" and "Resolving a sync conflict" trees in [`../knowledge/mobile-engineering-decision-trees.md`](../knowledge/mobile-engineering-decision-trees.md). The server-side idempotency-key mechanics (unique index, replay) are the `backend-engineering` lane — this is the *client* side of the same contract.
</content>
