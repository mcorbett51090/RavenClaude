---
scenario_id: 2026-06-05-broken-object-level-authz-remediation
contributed_at: 2026-06-05
plugin: security-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [authz, bola, idor, access-control, multi-tenant]
confidence: high
reviewed: false
---

## Problem

A threat model of a new "share a report by link" feature surfaced that `GET /api/reports/{id}` returned any report by integer id with only an *authentication* check — any logged-in user could increment the id and read another tenant's report. This is Broken Object-Level Authorization (BOLA / IDOR), the #1 item on the OWASP API Security Top 10. It was found at design time, before the endpoint shipped — but a sibling endpoint with the same pattern was *already in production*. The owner needed both the design fix and the right urgency on the live hole.

## Constraints context

- Multi-tenant SaaS; "who owns this object" is the entire security boundary, and the app was checking "are you logged in" but not "is this object yours."
- The already-shipped sibling endpoint (`GET /api/exports/{id}`) had the identical defect and was internet-facing and reachable by any authenticated user — a live cross-tenant data-read hole.
- Sequential integer ids made enumeration trivial (id+1 walks the whole table).

## Attempts

- Tried: "switch the ids to UUIDs so they can't be guessed." Rejected as the *primary* fix — that's security by obscurity. Unguessable ids raise the cost of enumeration but do **not** establish authorization; a leaked or logged UUID still reads cross-tenant. UUIDs are a defense-in-depth *addition*, not the control.
- Tried: add a tenant filter in the one new endpoint's handler. Correct locally but doesn't scale — the same check, copy-pasted per endpoint, is one forgotten paste away from the next BOLA. And it left the live sibling endpoint unaddressed.
- Tried (the move that worked): **enforce object ownership at the data-access layer, not per-handler** — every object fetch is scoped by the caller's tenant/owner (`WHERE id = ? AND tenant_id = ?`), so an object the caller doesn't own returns 404, centrally, for every endpoint. Separated the two bugs by blast radius: the **live** sibling endpoint is a Critical (unauthenticated-to-the-data cross-tenant read, internet-facing) → stop-and-fix + route the verdict; the **unshipped** new endpoint is fixed in the normal cycle before launch since it's not yet exposed.

## Resolution

The fix was **authorization at the data layer**, scoping every fetch by the caller's tenant so cross-tenant reads return 404 everywhere by construction — plus UUIDs as a defense-in-depth layer, not as the control. The two findings were triaged separately: the production endpoint as a Critical (route the verdict, fix now), the design-time one in the normal pre-launch flow.

The mental model: **authentication answers "who are you"; authorization answers "are you allowed to touch *this object*."** BOLA is an authorization bug, and the only durable fix is to make the ownership check a property of the data-access layer that no endpoint can forget — not a per-handler check and definitely not unguessable ids.

**Action for the next engineer:** when an object is addressed by id, check that the fetch is scoped by ownership *at the data layer*, return 404 (not 403) for not-yours so you don't leak existence, and treat unguessable ids as defense-in-depth only. A live, reachable, cross-tenant case is a Critical — route its ship/no-ship verdict to `ravenclaude-core/security-reviewer`. Note the seam: **API-specific authorization flaws (BOLA/BOPLA/BFLA) and the OWASP API Top 10 are `api-engineering/api-security-engineer`'s craft** — this team threat-models the design and finds the class; the API specialist owns the API-surface remediation pattern.

Cross-reference: complements [`../knowledge/security-engineering-decision-trees.md`](../knowledge/security-engineering-decision-trees.md) ("Auth-vs-authz failure triage" + "Vulnerability triage priority"), the [`../skills/threat-modeling-stride`](../skills/threat-modeling-stride/SKILL.md) skill, and [`../best-practices/least-privilege-by-default.md`](../best-practices/least-privilege-by-default.md).

**Sources (retrieved 2026-06-05):**
- OWASP API Security Top 10 — API1:2023 Broken Object Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
- OWASP Top 10 2021 — A01 Broken Access Control — https://owasp.org/Top10/A01_2021-Broken_Access_Control/

OWASP editions are versioned (a 2025 web refresh is tracked) — `[verify-at-use]` against the current edition before any deliverable.
