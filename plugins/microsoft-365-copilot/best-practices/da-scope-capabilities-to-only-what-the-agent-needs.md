# Declare only the capabilities the agent needs — each one widens the data surface and the validation surface

**Status:** Pattern — strong default; every extra capability is reach the agent didn't need and a thing validation can reject.

**Domain:** Agent design / declarative-agent capabilities

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

A declarative agent's `capabilities` array is its reach: web search, Graph connectors, SharePoint/OneDrive knowledge, code interpreter, image generator, people, email, meetings, Dataverse, Teams messages, embedded knowledge. Each capability you add is data the agent can now touch and a behavior the runtime must police. Over-scoping is the agent equivalent of over-permissioning: a `People` capability is *unscoped* (it can search anyone in the org); an `Email` or `Meetings` capability reaches mailbox/calendar content. Declaring capabilities you don't use bloats the grounding budget, muddies the agent's behavior, increases the chance of surfacing something it shouldn't, and gives RAI/store validation more surface to reject. The schema enforces a structural guard — the array can't contain **more than one of each** capability type — but it does not stop you from over-declaring. Scope is a design decision, not a default.

## How to apply

Start from the smallest capability set that satisfies the scenario, scope each capability to the specific source, and justify any people/email/meetings reach explicitly.

```jsonc
{
  "version": "v1.7",
  "name": "Contoso Policy Assistant",
  "capabilities": [
    // Scope GraphConnectors to a NAMED connection — not "all connectors"
    { "name": "GraphConnectors", "connections": [{ "connection_id": "contosoPolicies" }] },
    // SharePoint knowledge scoped to specific sites, not the whole tenant
    { "name": "OneDriveAndSharePoint", "items_by_url": [{ "url": "https://contoso.sharepoint.com/sites/hr" }] }
    // NO People / Email / Meetings unless the scenario genuinely needs them.
  ]
}
```

**Do:**
- Declare the **minimum** capability set; add a capability only when a scenario requires it.
- **Scope** each capability to the specific connection / site / mailbox — don't leave it tenant-wide by default.
- Flag `People` (unscoped by design), `Email`, and `Meetings` as elevated reach and confirm the scenario needs them; route the data-exposure question to `copilot-admin-governance` and `ravenclaude-core/security-reviewer`.

**Don't:**
- Add capabilities "just in case" — each one is grounding budget and a validation/oversharing surface.
- Leave SharePoint/OneDrive or connector capability unscoped when the scenario only needs one site or one source.
- Ship without a `Licensing impact:` line — connector and SharePoint-knowledge grounding is seat- and quota-gated (#8).

## Edge cases / when the rule does NOT apply

A genuinely broad assistant (e.g. a general org Q&A agent) may legitimately need `OneDriveAndSharePoint` + `People` — but that is a deliberate, reviewed scope decision, documented in the design, not a default. `code interpreter` and `image generator` add no org-data reach (they're compute), so the over-sharing concern doesn't apply to them — but they still cost grounding/latency budget and add RAI surface, so the minimalism rule holds.

## See also

- [`./design-to-66-percent-of-the-declarative-agent-wall.md`](./design-to-66-percent-of-the-declarative-agent-wall.md) — capabilities feed the grounding budget
- [`./da-pass-rai-validation-design-the-prompt-for-it.md`](./da-pass-rai-validation-design-the-prompt-for-it.md) — more capabilities = more validation surface
- [`../knowledge/declarative-agent-manifest-2026.md`](../knowledge/declarative-agent-manifest-2026.md) · [`../knowledge/grounding-source-decision-2026.md`](../knowledge/grounding-source-decision-2026.md)
- [`../agents/declarative-agent-engineer.md`](../agents/declarative-agent-engineer.md)

## Provenance

Grounded in the declarative-agent v1.7 schema capability map (People is unscoped; one-of-each enforcement) and the capability scoping fields added across v1.4–v1.6 (`connections` scoping, `items_by_url`, `group_mailboxes`), retrieved from Microsoft Learn 2026-05-30. Extends house opinions #3 and #8 from [`../CLAUDE.md`](../CLAUDE.md).

---

_Last reviewed: 2026-05-30 by `claude`_
