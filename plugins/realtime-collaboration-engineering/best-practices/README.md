# Realtime-collaboration-engineering — best-practice docs

Named, citable rules for the `realtime-collaboration-engineering` plugin's three agents. Each file is **one rule**, grounded in this plugin's knowledge bank and the agents' house opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md)) or the automated smell checks in the advisory hook. They take one opinion each and make it a standalone, exception-documented rule.

---

## Index

_8 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`pick-the-merge-model-by-data-shape-not-hype.md`](./pick-the-merge-model-by-data-shape-not-hype.md) | Absolute rule | Choosing CRDT vs OT vs LWW — drive it off the data shape + offline need, not the trend. |
| [`every-edit-needs-a-stable-causal-identity.md`](./every-edit-needs-a-stable-causal-identity.md) | Absolute rule | Designing the op/document model — `(clientID, counter)` ids and identity-based positions. |
| [`design-for-offline-from-day-one.md`](./design-for-offline-from-day-one.md) | Strong default | Offline is a real requirement — it is a day-one constraint that selects the merge model. |
| [`presence-is-ephemeral-keep-it-out-of-the-document.md`](./presence-is-ephemeral-keep-it-out-of-the-document.md) | Absolute rule | Building cursors/selections/who's-here — a separate, throttled, expiring channel. |
| [`bound-document-growth-tombstones-and-snapshots.md`](./bound-document-growth-tombstones-and-snapshots.md) | Absolute rule (CRDT) | A CRDT document — plan snapshots + compaction + tombstone GC before launch. |
| [`the-server-is-a-relay-and-source-of-truth-decide-which.md`](./the-server-is-a-relay-and-source-of-truth-decide-which.md) | Absolute rule | Picking the topology — name whether the server arbitrates or just fans out. |
| [`test-with-concurrent-conflicting-edits-and-partition.md`](./test-with-concurrent-conflicting-edits-and-partition.md) | Absolute rule | Verifying — concurrent edits, partition, reconnect, growth — not a turn-taking demo. |
| [`authority-and-access-control-live-at-the-sync-boundary.md`](./authority-and-access-control-live-at-the-sync-boundary.md) | Absolute rule | Securing — authorize at the connection edge; the merge engine trusts what it receives. |

---

_Last reviewed: 2026-06-24 by `claude`._
