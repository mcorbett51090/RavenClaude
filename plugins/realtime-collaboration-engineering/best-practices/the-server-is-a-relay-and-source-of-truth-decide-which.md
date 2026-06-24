# The server is a relay AND a source of truth — decide which

**Status:** Absolute rule
**Domain:** Topology
**Applies to:** `realtime-collaboration-engineering`

> Engineering craft, not product advice.

---

## Why this exists

A sync server can play two very different roles: a **dumb relay** that fans ops out and never decides anything, or an **authoritative source of truth** that orders, persists, and authorizes every edit. These imply different consistency models, different offline behavior, and different failure modes. Leaving it implicit means nobody can answer "what happens when the server and a client disagree?"

## How to apply

- Traverse [`../knowledge/transport-and-topology-decision-tree.md`](../knowledge/transport-and-topology-decision-tree.md) and state the server's role explicitly.
- Server-authoritative → the server's order wins; clients reconcile to it; offline is harder.
- Relay + CRDT → clients converge among themselves; the server fans out and persists but doesn't arbitrate; offline is natural.
- Even a "relay" usually needs a **persistence peer** so a document survives when every client is offline — decentralized truth and durable storage are separate concerns.

**Do:** name the server's role; align it with the merge model and offline posture.
**Don't:** assume "there's a server" answers where truth lives.

## Edge cases / when the rule does NOT apply

Pure P2P with no server at all is valid for small, ephemeral sessions — but then *durability* is explicitly out of scope (or pushed to a client that volunteers to persist).

## See also

- [`../skills/scale-the-sync-server/SKILL.md`](../skills/scale-the-sync-server/SKILL.md)
- [`../best-practices/authority-and-access-control-live-at-the-sync-boundary.md`](authority-and-access-control-live-at-the-sync-boundary.md)

## Provenance

Codifies `collab-architect` + `presence-and-transport-engineer` house opinion.

---

_Last reviewed: 2026-06-24 by `claude`_
