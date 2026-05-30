# Copilot data residency + compliance (2026)

**Last reviewed:** 2026-05-30
**Confidence:** Medium-High — residency is PDL-driven (first-party) but the detail moves. `[verify-at-build]` on EU Data Boundary scope + per-feature residency.
**Read when:** answering "where does our Copilot data live?" or planning audit/eDiscovery/retention for Copilot.

---

## Residency is PDL-driven

Microsoft 365 Copilot data residency follows the tenant's **Product Data Location (PDL)** — derived from the tenant's setup/country and any **Advanced Data Residency (ADR)** / **Multi-Geo** configuration. Copilot interactions (prompts/responses) are stored per the user's mailbox/substrate location. Grounding: [M365 data residency — Copilot service](https://learn.microsoft.com/microsoft-365/enterprise/m365-dr-service-copilot).

| Lever | Effect |
|---|---|
| **PDL** | the default residency for the tenant's M365 data, including Copilot |
| **Advanced Data Residency (ADR)** | tenant-wide commitment to a geo `[verify-at-build]` |
| **Multi-Geo** | per-user satellite geos for the substrate |
| **EU Data Boundary (EUDB)** | EU/EFTA processing + storage commitment `[verify-at-build]` |

## Audit / eDiscovery / retention

Copilot interactions are **auditable** (Purview Audit), **discoverable** (eDiscovery), and subject to **retention policies** — they live in the user's mailbox substrate. Plan retention + hold like any other M365 content.

## Licensing impact

ADR / Multi-Geo / advanced compliance are add-on / E5-gated; Copilot itself is per-seat. State the residency + compliance add-on impact.

## The seam

Cross-domain residency/identity questions (Entra tenant geo, Azure-side data residency for a custom-engine agent's host) route to `azure-cloud` + `ravenclaude-core/architect`. The Copilot-substrate residency is this plugin's; the host's residency is `azure-cloud`'s.

## Refresh triggers
- EU Data Boundary scope or ADR/Multi-Geo behavior changes.
- New Copilot features land with their own residency caveats `[verify-at-build]`.
