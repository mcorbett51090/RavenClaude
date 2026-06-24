# Design for offline from day one

**Status:** Strong default
**Domain:** Offline / reconnection
**Applies to:** `realtime-collaboration-engineering`

> Engineering craft, not product advice.

---

## Why this exists

Offline capability is an **architectural property**, not a feature you bolt on later: it forces a merge model that converges without a central order (a CRDT, or a carefully bounded sync engine). Discovering at integration time that the chosen model needs a central server to merge is the expensive way to learn this.

## How to apply

- Decide the offline posture **with the merge model** ([`../skills/choose-crdt-or-ot/SKILL.md`](../skills/choose-crdt-or-ot/SKILL.md)), not after.
- Buffer local ops with stable causal ids while disconnected; the local replica stays fully usable.
- On reconnect, resume from the last acknowledged version and merge the delta — never replay offline edits as new.
- Reconnect with jittered backoff; clear stale presence on timeout.

**Do:** make offline a named day-one constraint that selects the model.
**Don't:** ship server-authoritative-only and "add offline later" if offline is a real requirement.

## Edge cases / when the rule does NOT apply

A strictly server-authoritative product where being offline means "read-only, no edits" is a legitimate choice — then offline-merge is explicitly out of scope, stated as a decision.

## See also

- [`../skills/handle-offline-and-reconnection/SKILL.md`](../skills/handle-offline-and-reconnection/SKILL.md)
- [`../templates/offline-conflict-test-plan.md`](../templates/offline-conflict-test-plan.md)

## Provenance

Codifies `collab-architect` + `sync-engine-engineer` house opinion.

---

_Last reviewed: 2026-06-24 by `claude`_
