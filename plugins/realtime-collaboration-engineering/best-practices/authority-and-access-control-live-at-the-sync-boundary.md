# Authority and access control live at the sync boundary

**Status:** Absolute rule
**Domain:** Security / transport
**Applies to:** `realtime-collaboration-engineering`

> Engineering craft, not legal/security advice — pair with `security-engineering` for the threat model.

---

## Why this exists

The merge engine **trusts the ops it receives** — it converges whatever it is given. So *who may join a room, who may edit vs view, and whether a specific op is allowed* must be decided at the **server edge where connections terminate**, before an op reaches the document layer. Authorizing inside the merge engine (or worse, on the client) means a malformed or hostile client can corrupt the shared state.

## How to apply

- Authenticate the connection and authorize **room join** at the transport boundary.
- Enforce **edit vs view** and any per-op authorization at the server edge, before applying.
- Never rely on the client to self-restrict; never re-check authorization inside the CRDT/OT apply path as the *only* gate.
- Keep the boundary's authorization model in sync with the topology decision (server-authoritative makes this natural; pure P2P makes it genuinely hard — name that).

**Do:** authorize at the connection edge; treat the merge engine as trusting.
**Don't:** authorize in the document layer alone; trust the client.

## Edge cases / when the rule does NOT apply

End-to-end-encrypted P2P collaboration changes the model — the server can't read ops to authorize content — and needs a dedicated design (capability tokens, client attestation). Flag it to `security-engineering`.

## See also

- [`../skills/scale-the-sync-server/SKILL.md`](../skills/scale-the-sync-server/SKILL.md)
- Seam: threat model → [`../../security-engineering/CLAUDE.md`](../../security-engineering/CLAUDE.md)

## Provenance

Codifies `presence-and-transport-engineer` house opinion.

---

_Last reviewed: 2026-06-24 by `claude`_
