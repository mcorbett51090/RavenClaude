# Changelog — realtime-collaboration-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-24

Initial release.

### Added

- **3 agents** — `collab-architect` (merge model: CRDT vs OT vs LWW, consistency guarantee, topology, offline posture), `sync-engine-engineer` (document model on the chosen CRDT/OT, causal identity, offline/reconnect merge, tombstone/snapshot/compaction, collaborative undo), `presence-and-transport-engineer` (WebSocket vs WebRTC, presence/awareness, connection lifecycle, scaling the sync server, access control at the boundary).
- **5 skills** — `choose-crdt-or-ot`, `design-the-document-model`, `handle-offline-and-reconnection`, `build-presence-and-awareness`, `scale-the-sync-server`.
- **Knowledge bank** — `crdt-vs-ot-decision-tree.md` and `transport-and-topology-decision-tree.md` (4 Mermaid trees), `consistency-and-merge-concepts.md` (durable distributed-systems concepts — strong eventual consistency, causal order, Lamport/vector clocks, tombstones, intention preservation), and `realtime-collab-tooling-2026.md` (dated library/service/protocol map, each entry `[verify-at-use]`).
- **8 best-practices** — pick the merge model by data shape not hype, every edit needs a stable causal identity, design for offline from day one, presence is ephemeral keep it out of the document, bound document growth (tombstones/snapshots), the server is a relay AND a source of truth (decide which), test with concurrent conflicting edits and partition, authority and access control live at the sync boundary.
- **4 templates** — collaboration-architecture decision, document-model spec, sync-server scaling plan, offline/conflict test plan.
- **3 commands** — `/choose-merge-model`, `/design-doc-model`, `/review-collab-architecture`.
- **1 advisory hook** — `flag-realtime-collab-smells.sh` (3 checks on .md/.txt; `RTC_STRICT=1` to block).

### Scope & verify-at-use

- **Engineering craft, not legal, security, or product advice.**
- All library/service/protocol specifics in `realtime-collab-tooling-2026.md` are volatile — each carries a retrieval date + `[verify-at-use]`; re-confirm against the current docs before adoption. The durable distributed-systems reasoning lives separately in `consistency-and-merge-concepts.md` (does not rot).
- Built as the top unbuilt row (`realtime-collaboration-engineering`, priority 13) of the standing new-plugin roadmap — see `docs/proposals/2026-06-24-ten-new-plugin-candidates.md`.
- Seams (not duplicated): UI/editor → `frontend-engineering`; sync service/store → `backend-engineering`; op-log fan-out → `data-streaming-engineering`; latency/load → `performance-engineering`; threat model → `security-engineering`.
