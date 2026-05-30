# Document the data-handoff plan at engagement design time — not at engagement end

**Status:** Absolute rule — an ELT pipeline (or custom connector) ships with a written handoff plan, or it doesn't ship. A pipeline with no exit plan is a churn vector.

**Domain:** ELT / engagement lifecycle

**Applies to:** `data-platform`

---

## Why this exists

A consulting dashboard engagement ends; the data pipeline does not. The recurring failure is "self-hosted Airbyte" (or a bespoke custom connector) handed to a client at engagement end with no runbook — six months later it breaks, the client can't fix it, and that abandonment is a renewal lost and a reference burned. The decision that determines handoff difficulty — **who operates this after we leave?** — is made at the *start* (it drives whether you choose managed-Fivetran-for-easy-handoff vs. self-hosted-Airbyte-for-cost vs. a community-contributed connector), but it's usually only confronted at the *end*, when the options are gone. The discipline: decide the post-engagement ownership at design time, let it inform the tool choice, and write the runbook as you build — not as a scramble during offboarding. For custom connectors this is sharper still, because maintenance posture (community contribution / Matt-maintained fork / client takes over) is a *design* input, not an afterthought.

## How to apply

Name the post-engagement owner up front, choose the tool to fit that owner, and ship the runbook with the pipeline.

```yaml
# stack-decision-record.md — handoff is a design input, captured at engagement start.
post_engagement_owner: client-takes-over          # client | matt-hosts | community
ingestion_tool: fivetran-free-tier                 # chosen BECAUSE client operates it & MAR<500k
handoff_artifacts:
  - runbook: "credential rotation, re-auth cadence (QBO 100-day refresh!), failure triage"
  - access: "connector ownership transferred to client's account"
  - alerting: "freshness/failure alerts route to client's on-call after cutover"
# Custom connector? maintenance_posture is mandatory:
maintenance_posture: community-contribution        # community | matt-fork | client | undecided
```

**Do:**
- Decide post-engagement ownership at design time and let it drive the tool choice (managed = easier handoff; self-hosted = cheaper while *you* run it).
- Write the runbook **as you build**: credential rotation, re-auth cadence (e.g. QBO's 100-day refresh), failure triage, alert routing.
- For custom connectors, choose a maintenance posture — community contribution back to Airbyte (gold) / Matt-maintained fork (silver) / client takes over (bronze) — at design time.
- Transfer connector/account ownership and re-point alerting to the client's on-call at cutover.

**Don't:**
- Hand off self-hosted infra or a bespoke connector with no runbook.
- Default to self-hosted Airbyte for cost when the client will operate it and lacks the ops capacity — a managed tool's handoff simplicity may be worth the spend.
- Leave the maintenance posture "undecided" past design time on a custom connector.

## Edge cases / when the rule does NOT apply

- **Ongoing retainer / Matt hosts indefinitely** — the handoff is to *future-Matt*; the runbook still exists (operational continuity), but there's no client-cutover step.
- **Snowflake/Delta Sharing engagements** — no pipeline to hand off; the "handoff" is share-grant management, documented as such.
- **Case A (portfolio)** — single-author, Matt-owned, version-controlled; no external handoff, though the build/deploy steps are still documented in the repo README.

## See also

- [`./connector-incremental-with-backfill.md`](./connector-incremental-with-backfill.md) — the connector whose ops you're documenting
- [`./connector-avoid-per-viewer-and-per-row-pricing-traps.md`](./connector-avoid-per-viewer-and-per-row-pricing-traps.md) — managed-for-handoff vs. self-host-for-cost is partly a pricing call
- [`../knowledge/ipaas-connector-landscape-2026.md`](../knowledge/ipaas-connector-landscape-2026.md) — the termination/handoff column of the decision criteria
- [`../agents/etl-pipeline-engineer.md`](../agents/etl-pipeline-engineer.md) / [`../agents/connector-developer.md`](../agents/connector-developer.md) — carry `data_handoff_plan` / `maintenance_posture` in their output contracts

## Provenance

Distilled from `etl-pipeline-engineer.md` ("Document the handoff plan up front … 'Self-hosted Airbyte' without a runbook = a churn vector") and `connector-developer.md` ("Plan the handoff at design time, not at engagement end"; community/fork/client maintenance postures), plus CLAUDE.md anti-pattern "An ELT pipeline that doesn't have a documented data-handoff plan when the engagement ends." Both agents already require these fields in their Structured Output Protocol. No volatile vendor facts.

---

_Last reviewed: 2026-05-30 by `claude`_
