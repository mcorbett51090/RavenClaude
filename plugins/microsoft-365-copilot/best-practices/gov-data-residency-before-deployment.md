# Verify data residency and EU Data Boundary posture before deploying Copilot to regulated tenants

**Status:** Absolute rule
**Domain:** Copilot governance / compliance
**Applies to:** `microsoft-365-copilot`

---

## Why this exists

Microsoft 365 Copilot processes prompts and grounded content in Azure regions determined by the tenant's Product Data Location (PDL) setting. For organizations subject to EU data-sovereignty, financial-services data-residency regulations, or national security frameworks, the default multi-region PDL may route Copilot interactions through datacenters outside the jurisdiction. Enabling Copilot without verifying residency is an incident waiting for the first regulatory audit. The EU Data Boundary, Advanced Data Residency (ADR), and Multi-Geo are the controls — and each has prerequisites, lead time, and a cost impact that must be surfaced before deployment.

## How to apply

Pre-deployment residency checklist:

| Check | Where | Implication if missed |
|---|---|---|
| Confirm tenant's current PDL region | M365 admin center → Organization profile → Data location | Default may not match regulatory requirement |
| EU tenant: is EU Data Boundary enrolled? | M365 admin center → Settings → Org settings → Security & privacy | Non-enrolled EU tenants may have data processed outside EU |
| Regulated tenant: is ADR purchased? | Licensing dashboard or CSP / EA portal | ADR is an add-on; not included in standard E3/E5 |
| Multi-Geo tenant: are user PDLs set per-user? | Entra user properties → `preferredDataLocation` | Multi-Geo is per-user; unset users fall back to the tenant default |
| Copilot interaction logs: where are audit logs stored? | Microsoft Purview audit search | Interaction logs are subject to the same PDL as other M365 data |

Document the residency posture in the deployment run-book:
```
Tenant PDL: EU (Netherlands)
EU Data Boundary: enrolled, effective 2026-01-01
ADR: not purchased (standard E3/E5; EU Data Boundary covers M365)
Multi-Geo: not deployed
Copilot audit log location: EU region (verified in Purview)
```

**Do:**
- Run the `copilot-admin-governance` agent's residency verification checklist before any Copilot enablement decision.
- Surface the ADR lead time (typically 30–90 days from purchase to provisioning) to the customer before the project start, not after.
- Verify that data residency applies to **Copilot interaction data** specifically — some tenants have EU PDL for mailbox/calendar but have not confirmed Copilot prompt data.

**Don't:**
- Assume EU tenants are automatically EU Data Boundary compliant — enrollment is a separate, non-default step.
- Equate data residency with data sovereignty — residency controls where data is stored and processed; additional security controls govern access.
- Recommend Copilot for a regulated tenant without a `Licensing impact:` line that includes ADR or EU Data Boundary costs if applicable.

## Edge cases / when the rule does NOT apply

For purely internal productivity tenants with no regulatory data-residency obligation, the default PDL is acceptable. Document the "no regulatory requirement" decision explicitly.

## See also

- [`../agents/copilot-admin-governance.md`](../agents/copilot-admin-governance.md) — owns residency verification and the governance posture before Copilot deployment
- [`./remediate-oversharing-before-enabling-copilot.md`](./remediate-oversharing-before-enabling-copilot.md) — the complementary pre-deployment security step

## Provenance

Codifies CLAUDE.md §8 knowledge bank `data-residency-and-compliance-2026.md` as a mandatory pre-deployment step; Microsoft Learn EU Data Boundary and Advanced Data Residency documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
