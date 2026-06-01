# Make the refresh reliable — the day-2 layer the model design doesn't cover

**Status:** Primary diagnostic — when a published report is stale, intermittently failing to refresh, or timing out, check the refresh + gateway configuration before touching the model.

**Domain:** Power BI / operations

**Applies to:** `power-platform`

---

## Why this exists

The four existing `bi-*` rules cover *modeling* (measures, star schema, RLS, storage mode) — getting the dataset right on the desktop. None of them cover what breaks *after* publish: scheduled refresh failing at 6 a.m., an on-premises data gateway that's a single point of failure, a full refresh timing out on a large fact table, or a refresh that runs as a departed employee's account. "It worked in Desktop but won't refresh in the Service" is a distinct, common failure class with its own fixes — and on a consulting deliverable that must keep running after handoff, it's the part that pages someone at 2 a.m.

## How to apply

**Refresh strategy by table size:**

- Small/medium dimension tables → scheduled full refresh is fine.
- Large fact tables → **incremental refresh** (define `RangeStart`/`RangeEnd` parameters, partition by date, refresh only recent partitions). A full refresh of a 100M-row fact table will eventually exceed the refresh time limit.
- Set the refresh schedule below the capacity's refresh limit and stagger datasets so they don't all fire at once.

**Gateway (for any on-prem or VNet-bound source):**

- Use a **standard** (not personal) gateway, and cluster it (≥2 gateway members) so one node's reboot doesn't kill every refresh.
- Size the gateway host for the spool/mashup memory of the heaviest refresh; gateway OOM is a top silent-failure cause.

**Identity:**

- Refresh and data-source credentials should run as a **service principal or a service account**, never a named user — a person leaving or an MFA prompt silently kills the schedule.

**Triage when a refresh fails:** read the refresh history error → classify as credential/auth, gateway-unreachable, timeout/limit, or source-side (query folding broke, schema changed) → fix that class, don't blindly re-run.

**Do:**

- Incremental refresh for large fact tables; service principal for credentials; clustered standard gateway for on-prem.
- Alert on refresh failure (don't discover staleness from a stakeholder).

**Don't:**

- Full-refresh a large fact table on a schedule and hope it stays under the limit.
- Bind refresh to a personal gateway or a named user's credentials.

## Edge cases / when the rule does NOT apply

A cloud-only source (e.g. Dataverse, SharePoint Online, an Azure SQL DB reachable from the Service) needs **no gateway** — don't stand one up out of habit. Direct Lake / a Fabric-hosted model has a different refresh model (it reads OneLake directly) — see the storage-mode rule and the deployment/refresh tree. Exact refresh time limits and capacity refresh-concurrency numbers are SKU-/capacity-specific — `[verify-at-build]`.

## See also

- [`./bi-storage-mode-selection.md`](./bi-storage-mode-selection.md) — Import vs DirectQuery vs Direct Lake changes what "refresh" even means
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — the deployment & refresh decision tree
- [`../agents/power-bi-engineer.md`](../agents/power-bi-engineer.md) — owns refresh/gateway
- [Power BI incremental refresh](https://learn.microsoft.com/power-bi/connect-data/incremental-refresh-overview) · [On-premises data gateway](https://learn.microsoft.com/data-integration/gateway/) — authoritative

## Provenance

Surfaced by the two-panel coverage audit (2026-06-01): the `power-bi-engineer` owns "refresh/gateway issues" per the plugin CLAUDE.md, but the rule layer had only modeling rules and no operational refresh/gateway rule. Grounded in the Microsoft Learn incremental-refresh and on-premises-data-gateway docs. Refresh limits + capacity concurrency are `[verify-at-build]`.

---

_Last reviewed: 2026-06-01 by `claude`_
