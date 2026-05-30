# Enforce business logic at the lowest tier that holds: business rule → Power Fx → flow → plug-in

**Status:** Pattern — the platform-wide §3 #7 rule applied to "where does this logic live."

**Domain:** Dataverse / Plug-ins

**Applies to:** `power-platform`

---

## Why this exists

The same validation or defaulting can be implemented as a business rule, a Power Fx formula/canvas guard, a Power Automate flow, or a Dataverse plug-in — and teams reach for the most powerful (most expensive) tier by reflex. Each tier up costs more to build, test, version, and hand off, and changes *who* the logic protects. The decisive question is **scope of enforcement**: a business rule or canvas-app guard only fires in the **UI that runs it**, so logic that must hold for the **Web API, imports, flows, and other apps** has to live **server-side** (plug-in or, if async is acceptable, a Dataverse-triggered flow). Putting a critical invariant only in a canvas app means the next bulk import or integration bypasses it silently. Conversely, writing a plug-in for a same-form show/hide is two tiers of needless C#. §3 #7 ("lowest-tier mechanism that does the job — business rule before JavaScript, Power Fx before flow, flow before plug-in") is the heuristic; **"must it hold everywhere, or only in this UI?"** is the tie-breaker.

## How to apply

Pick the lowest tier whose **enforcement reach** covers where the rule must hold:

```text
Same-form show/hide/require/default, no cross-table, runs everywhere a form opens? → BUSINESS RULE
UI-only guard / instant feedback inside one canvas or model-driven app?            → POWER FX (+ business rule)
Cross-table, async, connector-driven, or scheduled — eventual enforcement OK?      → FLOW (Dataverse trigger)
Must hold for Web API / imports / every app, AND be transactional/synchronous?     → PLUG-IN (server-side)
```

```text
// BUSINESS RULE (entity scope) — fires in every client AND server-side for that table.
//   IF cnt_status = "Closed" THEN set cnt_closedon = Now() AND make cnt_reason required.
//   No code; portable; the right default for same-table field logic.

// PLUG-IN — the invariant must hold no matter HOW the row is written (API, import, flow, app).
//   e.g. "an invoice total can never go negative" — register PreOperation (20), sync, on Update.
//   A canvas-app check alone would be bypassed by the next $batch import.
```

| Tier | Enforces in | Cost | Use when |
|---|---|---|---|
| **Business rule** (entity scope) | All clients **and** server-side, that one table | Lowest — no code | Same-table require/default/show-hide/simple calc |
| **Power Fx** (canvas/MDA) | Only the app that runs it | Low | Instant UX feedback, UI-only guards (not a security boundary) |
| **Flow** (Dataverse trigger) | Server-side, **async** | Medium (+ licensing) | Cross-table, connector, scheduled — eventual consistency OK |
| **Plug-in** | Server-side, **synchronous**, every write path | High (C# + registration) | Must-hold-everywhere invariant; transactional; reject-the-write |

**Do:**
- Implement same-table field logic as a **business rule** with **entity scope** — it then holds in every client and server-side, with no code.
- Treat **Power Fx / canvas guards** as UX, not enforcement — convenience and instant feedback, never a security or integrity boundary.
- Use a **Dataverse-triggered flow** for cross-table or connector logic where **async** enforcement is acceptable.
- Use a **plug-in** when the invariant must hold across **every** write path (Web API, imports, other apps) **and** be synchronous/transactional — and register it on the stage that lets it reject (`PreValidation`/`PreOperation`).

**Don't:**
- Enforce a critical invariant **only** in a canvas app or form script — the next import, integration, or Web API call bypasses it.
- Use a **form-scoped** business rule (or JS) for a rule that must hold regardless of which form/app is used — choose **entity** scope or go server-side.
- Write a **plug-in** for show/hide/require that a business rule already does — that's climbing tiers for no reason.
- Use a **flow** where the rule must be **synchronous and transactional** (reject-or-roll-back) — flows are async and can't block the originating write.

## Edge cases / when the rule does NOT apply

- **Business rules can't do everything** — no cross-table reads, limited multi-select support, no external calls; those force a flow or plug-in even though the logic is "simple."
- **Synchronous reject-the-write** belongs in a **plug-in** (`InvalidPluginExecutionException`), not a flow — a flow can't stop the originating transaction.
- A **Dataverse-triggered flow** *is* server-side and does cover the Web-API/import path — when async enforcement is acceptable it's the cheaper-than-plug-in server-side option, not a UI-only tool.
- **Defense in depth** is legitimate: a UI guard (fast feedback) **plus** a server-side enforcer (the real boundary) is good design — the anti-pattern is the UI guard *alone* for a critical rule.
- If the logic is a **derived value** rather than a validation, route through `dataverse-rollup-vs-calculated-vs-plugin.md` instead.

## See also

- [`../skills/dataverse-web-api/resources/business-rules.md`](../skills/dataverse-web-api/resources/business-rules.md) — business-rule scope (entity vs form), supported actions, and limits
- [`../skills/dataverse-plugins/SKILL.md`](../skills/dataverse-plugins/SKILL.md) — `InvalidPluginExecutionException` for user-facing rejects; sandbox/timeout constraints
- [`./dataverse-plugin-pipeline-stage-selection.md`](./dataverse-plugin-pipeline-stage-selection.md) — if it's a plug-in, which stage rejects vs mutates
- [`./dataverse-rollup-vs-calculated-vs-plugin.md`](./dataverse-rollup-vs-calculated-vs-plugin.md) — the derived-value sibling of this decision
- [`../knowledge/dataverse-decision-trees.md`](../knowledge/dataverse-decision-trees.md) — `## Decision Tree: Logic placement — business rule vs Power Fx vs flow vs plug-in`
- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owner; "Prefers business rules over JS over plug-ins, in that order"

## Provenance

Grounded in the platform-wide house rule §3 #7 ([`../CLAUDE.md`](../CLAUDE.md): "Lowest-tier mechanism that does the job. Business rule before JavaScript. Power Fx before flow. Flow before plug-in. Plug-in before Azure Function"), the `dataverse-architect` personality ("Prefers business rules over JS over plug-ins"; "Plug-ins only when the logic must be transactional and synchronous"), and the `dataverse-plugins` skill (server-side enforcement, `InvalidPluginExecutionException`). The enforcement-reach distinction (UI-only vs every-write-path) is the documented difference between client-side business rules/Power Fx and server-side plug-ins/Dataverse-triggered flows.

---

_Last reviewed: 2026-05-30 by `claude`_
