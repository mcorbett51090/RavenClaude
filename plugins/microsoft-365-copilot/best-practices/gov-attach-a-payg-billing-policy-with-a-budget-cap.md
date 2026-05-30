# Attach a pay-as-you-go billing policy with a budget cap before metered agent usage — and always state the Licensing impact

**Status:** Pattern — strong default; metered Copilot consumption bills an Azure subscription, and an uncapped policy is an open spend; every org-data recommendation carries a `Licensing impact:` line.

**Domain:** Governance / licensing & PAYG

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

Microsoft 365 Copilot extensibility has two licensing models that authors conflate. Users with a **paid Copilot seat** consume against their license. But agents can also run for users *without* a Copilot license via a **pay-as-you-go (PAYG)** meter — Microsoft 365 Copilot Chat agents, SharePoint agents, and the Retrieval API all bill consumption to an **Azure subscription** through a **billing policy**, metered in **Copilot Credits** (sold in 25,000-credit packs, or pure PAYG). The trap is enabling metered consumption with no spend control: a single popular agent can run up consumption against the linked subscription with nothing to stop it. The mechanism to prevent that is built in — a billing policy supports an optional **budget** with a limit and a reset cadence (monthly/quarterly/yearly) plus email alerts at percentage milestones — and it is routinely skipped. On top of the spend story, connectors meter **item quotas** per tenant (a large source can exhaust them) and the **Retrieval API PAYG** ($/API call) requires at least one Copilot license in the tenant. House opinion #8: no org-data grounding without a license story, and the `Licensing impact:` line is mandatory on every recommendation.

## How to apply

Create the billing policy, link it to the Copilot service, scope it to the right users/group, and set a budget cap with alerts before metered usage runs. State the impact every time.

```text
PAYG setup (M365 admin center > Copilot > Billing & usage, or Cost Management)
  1. Add a billing policy   → name + Azure subscription + resource group + region
  2. Choose users           → All users (default for non-M365-Copilot services) or a Specific group
  3. Set a BUDGET           → limit + reset (1st of month / quarter / year) + % milestone email alerts
  4. Connect the policy to the Copilot service (M365 Copilot Chat / SharePoint agents)
  Roles: AI Administrator / Billing Administrator / Global Administrator (prefer least-privilege)
```

```text
Mandatory output line on EVERY org-data / metered recommendation:
  Licensing impact: <Copilot seats | PAYG meter + Azure subscription + budget cap
                     | connector item quota | E5/Suite for Purview DLP | downstream API cost>
```

**Do:**
- Create + link the **billing policy** and set a **budget cap** with milestone alerts before metered usage.
- Scope the policy to a **specific group** when only some users should incur metered cost.
- Account for **connector item quotas** (per-tenant) and the Retrieval-API PAYG's "≥1 Copilot license in tenant" prerequisite.
- Put a concrete **`Licensing impact:`** line on every org-data grounding / metered recommendation (#8).

**Don't:**
- Enable metered agent consumption with **no budget cap** — that's uncapped Azure spend.
- Conflate seat-based and PAYG models — non-Copilot-licensed users run on the PAYG meter, not a seat.
- Recommend connector/SharePoint-knowledge grounding without naming the seat + quota impact.

## Edge cases / when the rule does NOT apply

A fully **seat-licensed** deployment (every user has a paid Copilot license, no metered agents) doesn't need a PAYG billing policy — but you still state the seat cost in the `Licensing impact:` line. **Copilot-Studio** metered consumption is governed via the Power Platform admin center (a related but separate billing surface) — that's the `power-platform` seam. Exact meter rates, Copilot-Credit pack sizes, and PAYG prerequisites are `[verify-at-build]` — re-confirm before quoting numbers.

## See also

- [`./gov-route-agents-and-mcp-tools-through-the-agent-registry.md`](./gov-route-agents-and-mcp-tools-through-the-agent-registry.md) — the approval gate that precedes go-live
- [`./connector-choose-synced-vs-federated-and-set-crawl-refresh.md`](./connector-choose-synced-vs-federated-and-set-crawl-refresh.md) — connector item-quota metering
- [`../knowledge/copilot-admin-governance-2026.md`](../knowledge/copilot-admin-governance-2026.md) · [`../agents/copilot-admin-governance.md`](../agents/copilot-admin-governance.md)
- [M365 Copilot pay-as-you-go overview](https://learn.microsoft.com/microsoft-365/copilot/pay-as-you-go/overview) · [Set up PAYG billing in the Copilot node](https://learn.microsoft.com/microsoft-365/commerce/services/pay-as-you-go-setup-copilot)

## Provenance

Codifies house opinion #8 (license story) from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the Microsoft Learn M365-Copilot PAYG pages: billing policy + Azure subscription + budget with reset cadence and milestone alerts; Copilot Credits (25,000/pack); the Retrieval-API PAYG "≥1 Copilot license in tenant" prerequisite ($0.10/call preview); AI/Billing/Global Admin roles, all retrieved 2026-05-30. Rates/packs `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
