# Desktop flows (RPA) are the last-resort tier — if the system has an API, build a connector instead

**Status:** Pattern — strong default; deviate only with a written reason (a genuinely API-less system). Choosing RPA where a REST call exists is a named anti-pattern. (House rule §4 + `flow-engineer` opinion "desktop flows are last-resort.")

**Domain:** Power Automate / RPA

**Applies to:** `power-platform`

---

## Why this exists

A desktop flow (Power Automate for desktop / RPA) automates a system by *driving its UI* — clicking buttons, reading screen fields, typing into forms. That makes it the most fragile automation tier on the platform: a vendor UI change, a relocated button, a slow-loading screen, or a locale difference breaks it without warning and without a clean error. It also needs a machine (or machine group) and a gateway to run, carries premium/RPA licensing, and is hard to test in CI. A **cloud flow calling an API** — a first-party connector, a custom connector over the system's REST API, or a direct HTTP action — is observable, testable, and doesn't break when the vendor moves a button. So RPA sits at the bottom of the "lowest-tier mechanism that does the job" ladder: reach for it only when there is genuinely no programmatic surface. (Attended vs unattended, machine groups, and gateway requirements are RPA platform facts — `[verify current licensing against Microsoft Learn before quoting capacity numbers]`.)

## How to apply

Before building a desktop flow, exhaust the API ladder:

```
1. First-party connector exists for the system?        -> cloud flow, done.
2. System has a documented REST/OData/SOAP API?         -> custom connector (OAuth 2.0), cloud flow.
3. API exists but no connector worth building?          -> HTTP action (premium) in a cloud flow.
4. Genuinely no API — UI is the only surface?           -> THEN desktop flow (RPA), as last resort.
```

When RPA is genuinely the answer, build it defensively:

**Do:**
- Prefer **unattended** runs on a dedicated machine group for production schedules; keep **attended** for human-in-the-loop steps only.
- Use **stable selectors / UI elements**, not coordinate clicks — coordinate-based steps break on resolution or layout change.
- Wrap brittle steps in **on-error** blocks with retry and a clear failure path; treat a desktop flow's failure as expected, not exceptional.
- Use **secure input/output** for any credential or PII the RPA flow handles.
- Keep the desktop flow **thin** — let it do only the UI bridge, and hand structured data back to a cloud flow for the real logic.

**Don't:**
- Use RPA to do what one REST call could do — the canonical anti-pattern (`flow-engineer` flags "a desktop flow doing what a single REST API call could do").
- Hard-code waits with fixed sleeps where a "wait for element" exists — fixed sleeps are both slower and more fragile.
- Run unattended RPA against a system you don't control the release cadence of without a monitoring/alert path — you'll find out it broke from the business, not the flow.

## Edge cases / when the rule does NOT apply

- **Legacy / mainframe / desktop-only apps with no API** — RPA is the *correct* tool here, not a last resort; this is exactly what it's for.
- **A one-time data migration** from an API-less UI — RPA can be the pragmatic choice over a never-reused custom connector.
- **Citizen-developer constraints** — if the maker genuinely cannot get a custom connector approved/registered but *can* run RPA, RPA may be the only available path; document the fragility and the eventual API migration.

## Edge of the boundary: when it leaves Power Automate entirely

If the integration belongs in an Azure subscription (high volume, Bicep/Terraform-governed, Service Bus / Event Grid), it's not a desktop flow *or* a cloud flow — it's a Logic App / Function, and `flow-engineer` hands off to `azure-cloud/integration-engineer` (CLAUDE.md §11).

## See also

- [`./flow-error-handling-and-retry-policy.md`](./flow-error-handling-and-retry-policy.md) — desktop-flow steps need on-error/retry just like cloud actions
- [`../knowledge/flow-decision-trees.md`](../knowledge/flow-decision-trees.md) — `## Decision Tree: Automation surface — cloud flow vs desktop flow (RPA)`
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — "Desktop flows are last-resort. If the system has a REST API, build a custom connector instead."
- [`../CLAUDE.md`](../CLAUDE.md) §3 #7 — lowest-tier mechanism that does the job

## Provenance

Codifies the `flow-engineer` agent's "desktop flows are last-resort" opinion and the house anti-pattern "Power Automate desktop flows doing what a REST API call could do" (CLAUDE.md §4). The API-ladder ordering mirrors the Capability Grounding Protocol's "REST → SDK → CLI → portal" alternative-paths scan. RPA platform specifics (attended/unattended, machine groups, gateway, licensing) marked `[unverified — training knowledge]` pending current Microsoft Learn check.

---

_Last reviewed: 2026-05-30 by `claude`_
