# Realtime Collaboration — Tooling & Library Map (2026)

> **Dated reference. `[verify-at-use]`.** This file names specific libraries, services, and protocol details — the **most volatile** part of the knowledge bank. Every entry carries the assumption "as understood 2026-06; confirm against the current docs before it drives a dependency or a guarantee." The durable reasoning lives in [`consistency-and-merge-concepts.md`](consistency-and-merge-concepts.md) and the two decision trees; this file is only the current landscape.
>
> _Retrieved / last reviewed: 2026-06-24 by `claude`. Treat versions, feature claims, and licensing as `[verify-at-use]`._

---

## CRDT libraries (data/document layer) — `[verify-at-use]`

| Library | Ecosystem | Shape | Note (verify) |
|---|---|---|---|
| **Yjs** | JS/TS (ports elsewhere) | Sequence + map + array + rich-text (XML/Text) types; binary update encoding | Mature, widely used; rich editor bindings (ProseMirror, TipTap, CodeMirror, Monaco, Slate). Awareness protocol ships separately from the doc. |
| **Automerge** | Rust core + JS/other bindings | JSON-document CRDT; full history | Document-as-JSON model; history & change-based sync. Heavier history story; confirm current compaction/perf guidance. |
| **Loro** | Rust + JS/Wasm | Sequence/text/list/map/tree; movable tree | Newer; positions itself on performance + rich types. Confirm maturity/stability for your use. |
| **Collabs / others** | JS | Composable CRDT toolkit | For building custom types; confirm activity/maintenance. |

> Confirm **license**, **maintenance status**, **editor bindings**, and **performance/compaction** claims for any of these before adoption — see [`../../open-source-maintenance/CLAUDE.md`](../../open-source-maintenance/CLAUDE.md) for the dependency-intake lens.

## OT engines — `[verify-at-use]`

| Library | Note (verify) |
|---|---|
| **ShareDB** | JSON OT, server-authoritative, with a pub/sub + persistence model. Confirm current maintenance and the OT type you need. |
| **json0 / rich-text OT types** | The transform functions behind OT systems. Correct transforms across all op pairs are the hard part — prefer a battle-tested type over hand-rolling. |

## Sync infrastructure / managed platforms — `[verify-at-use]`

| Service / framework | Role | Note (verify) |
|---|---|---|
| **Liveblocks** | Managed presence + storage (CRDT-backed) | Hosted rooms, presence, and conflict-free storage. Confirm pricing/limits/self-host options. |
| **PartyKit / partyserver-style** | Stateful per-room server (often on edge runtimes) | One server object per room — maps cleanly to the "room is the shard" pattern. Confirm runtime + persistence. |
| **y-websocket / y-webrtc / y-sweet** | Yjs transport/sync providers | WS or WebRTC sync providers; y-sweet-style servers add persistence. Confirm provider maturity. |
| **ElectricSQL / Convex / Replicache / Zero** | Local-first / sync-engine platforms | Sync a local store to a backend with conflict handling. Different consistency models — confirm which fits your offline needs. |
| **Ably / Pusher / managed WS** | Pub/sub + presence transport | Managed fan-out + presence channels; you bring the merge model. Confirm presence semantics + limits. |

## Transport / connectivity — `[verify-at-use]`

| Concern | Current options (verify) |
|---|---|
| Client-server data | **WebSocket** (default); SSE for one-way push |
| P2P / low-latency / media | **WebRTC** data channels + media; needs **STUN** (discovery) and **TURN** (relay fallback) |
| NAT traversal fallback | A **TURN** server (self-hosted coturn or managed) — budget for relay bandwidth |

## Editor bindings (when the shared state is a rich-text editor) — `[verify-at-use]`

ProseMirror / TipTap, CodeMirror 6, Monaco, Slate, Lexical — each has community or first-party CRDT bindings (commonly Yjs). Confirm the binding's maturity and which CRDT it targets before committing the editor choice.

---

## How to keep this file honest

- Anything quoted from here into an architecture decision **must** be re-checked against the library's current docs and carry the retrieval date.
- When a fact here is confirmed stale, fix it here in the same change — do not let a dated map rot silently (the marketplace's standing accuracy discipline).
- Durable reasoning that does **not** belong here (it doesn't rot): the consistency model, causal ordering, tombstone/snapshot mechanics → [`consistency-and-merge-concepts.md`](consistency-and-merge-concepts.md).
