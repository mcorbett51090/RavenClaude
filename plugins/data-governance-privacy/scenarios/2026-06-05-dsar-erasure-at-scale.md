---
scenario_id: 2026-06-05-dsar-erasure-at-scale
contributed_at: 2026-06-05
plugin: data-governance-privacy
product: gdpr
product_version: "n/a"
scope: likely-general
tags: [dsar, erasure, lineage, fan-out, retention-carve-out]
confidence: high
reviewed: false
---

## Problem

A B2C company received a steady trickle of GDPR Article 17 erasure requests and was fulfilling each one **by hand**: an engineer ran a `DELETE` against the primary Postgres `users` table and called it done. An audit (triggered by a regulator inquiry into an unrelated complaint) asked them to *prove* a given subject's data had been erased everywhere. They could not. The person's PII was still live in the analytics warehouse (a nightly CDC copy), in three downstream microservice databases that had cached the profile, in object-storage event logs, and in a SaaS support tool. The `DELETE` on the source of record had erased *one* of seven copies, and nobody could enumerate the other six. This is the failed-capability shape from CLAUDE.md §2 #4 — "we can't locate all their data" **is** a failed DSR.

## Constraints context

- ~15 erasure requests/month — low enough that nobody had built a pipeline, high enough that manual fulfillment was both error-prone and unprovable.
- No data catalog and no lineage: the warehouse and microservice copies of PII were undocumented, so the fan-out of a single person's data was unknown.
- A genuine **retention carve-out**: some of the subject's records were tied to completed financial transactions the company is legally required to retain — so "erase everything" was the *wrong* answer, but so was "erase nothing." (The legal interpretation of *which* records and *for how long* routes out — CLAUDE.md §2 #6.)
- GDPR's clock: a controller has **one month** to respond, extensible by **two further months** for complex requests (Art. 12(3)) — verified 2026-06-05, `[verify-at-use]`. The manual process was already brushing that deadline.

## Attempts

- Tried: keep doing it by hand but add a checklist of "the seven places." Failed — the list went stale the moment a new pipeline copied PII somewhere the checklist didn't know about. A static list is not lineage.
- Tried: a single `DELETE` cascade via foreign keys. Failed — the copies live in *separate* systems (warehouse, microservices, object store, SaaS) with no FK relationship to the source; a cascade can't cross a system boundary.
- Tried (the move that worked): build **discovery + lineage first**, then make erasure a **fan-out pipeline keyed on a stable subject identifier**. (1) Catalog every system that holds personal data and capture lineage so each *derived/copied* location of a subject's PII is enumerable — you can't erase what you can't find (§2 #1). (2) Turn the DSR into an orchestrated job: resolve the subject to their identifier, fan out a delete/anonymize instruction to every system lineage says holds their data, **carve out** the legally-required-retention records into an isolated, access-restricted store rather than deleting them, and **verify** each leg completed. (3) Emit an audit record per request — *what was erased, what was retained and under which obligation, when, and confirmation back to the subject*.

## Resolution

The gap was never the `DELETE` statement — it was **not knowing where the data had spread** and having **no proof** of completion. Erasure at scale is an engineered fan-out that depends entirely on the catalog/lineage existing first; the retention carve-out is a deliberate, documented exception, not an excuse to skip the rest.

**Action for the next engineer hitting this pattern:** before writing any deletion code, confirm a lineage map exists that enumerates every *copied and derived* location of a subject's PII (the warehouse CDC copy and the cached microservice profiles are the ones teams forget). Make erasure idempotent and verifiable per-leg, isolate the retention carve-out instead of deleting it, and produce a per-request audit trail — the regulator's question is "prove it," not "did you run a query." Confirm the GDPR response-deadline math (`one month + two`) and any sector-specific retention obligation against current law at use; the legal *interpretation* of the carve-out routes to legal / `regulatory-compliance` (§3).

Cross-reference: complements the **Handle a data-subject request** and **Can this data be deleted now?** trees in [`../knowledge/data-governance-privacy-decision-trees.md`](../knowledge/data-governance-privacy-decision-trees.md), the [`dsr-runbook`](../templates/dsr-runbook.md) template, and [`../best-practices/dsr-pipeline-covers-all-systems.md`](../best-practices/dsr-pipeline-covers-all-systems.md).

**Sources (retrieved 2026-06-05):**
- GDPR Art. 17 (right to erasure) and Art. 12(3) (one month, extensible by two) — https://gdpr-info.eu/art-17-gdpr/ and https://gdpr-info.eu/art-12-gdpr/

GDPR deadlines and the existence/scope of any retention obligation are jurisdiction-specific and volatile — `[verify-at-use]` against current law and the org's specific sector before any deliverable.
