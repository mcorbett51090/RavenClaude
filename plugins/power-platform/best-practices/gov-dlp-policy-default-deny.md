# DLP is default-deny: classify Business deliberately, block by exception

**Status:** Pattern — strong default for any tenant handling real corporate data. Deviate only where a documented business case and active monitoring justify opening a connector.

**Domain:** Governance / DLP

**Applies to:** `power-platform`

---

## Why this exists

A tenant with no Data Loss Prevention policy treats *every* connector as Business by default — meaning any maker can wire Power Apps or Power Automate to anything the connector reaches, including arbitrary HTTP endpoints, unsanctioned SaaS, and external SharePoint/OneDrive tenants. That is an open data-exfiltration surface dressed up as productivity. The default-deny posture inverts the burden: a connector is Non-Business or Blocked unless someone has *justified* classifying it Business. The cost of an over-strict policy is a fast, reversible "please exempt this connector" ticket; the cost of an over-loose policy is data leaving the tenant through a flow nobody reviewed. Reverting a too-tight DLP policy takes minutes; recovering from exfiltration does not. Lock it down, then exempt with evidence.

## How to apply

Three buckets, only three. A flow/app cannot combine a Business and a Non-Business connector — that isolation *is* the data boundary, so draw the Business line carefully. Set the tenant policy as the strict floor; tighten per-environment where needed.

| Bucket | What goes here | Examples |
|---|---|---|
| **Business** | Connectors the org has sanctioned for corporate data | Dataverse, SharePoint (sanctioned), Outlook 365, Teams, approved LOB custom connectors |
| **Non-Business** | Personal-productivity, never corporate data | Twitter/X, RSS, MSN Weather, personal OneDrive |
| **Blocked** | Must never appear in any in-scope app/flow | generic HTTP, HTTP with Azure AD off-tenant, arbitrary-connection-string SQL, unsanctioned SaaS |

```bash
# Enumerate the blast radius of any policy change BEFORE you flip it — every in-scope
# flow/app is re-evaluated on change and can be suspended.
Get-AdminPowerAppEnvironment
Get-AdminFlow                 # cross-reference against the new classification
# (DLP policy CRUD: New-/Set-DlpPolicy via the Power Apps Administration PowerShell module.)
```

**Do:**
- Treat **generic HTTP** as Blocked at tenant scope — it's the highest-blast-radius connector (it can call anything reachable); allow per-env only with a specific case and monitoring.
- Classify **custom connectors** deliberately — each is its own DLP object, exactly as risky as the API it wraps (usually riskier, because a maker built it).
- Run a pre-change impact audit and notify affected owners 7–14 days ahead; policy changes silently suspend running flows otherwise.

**Don't:**
- Classify everything Business "so nothing breaks" — that's no DLP at all.
- Block SharePoint tenant-wide "to be safe" — it breaks every legitimate flow in the org at once.
- Use DLP to enforce data residency or sensitivity labels — that's Purview/Information Protection, not DLP.

## Edge cases / when the rule does NOT apply

- **`Send an HTTP request to Dataverse`** is a *different* DLP object than the **Dataverse** connector — block the former and you've shut down the common Dataverse-bulk-ops pattern while thinking you only allowed Dataverse. Decide each explicitly.
- **Action-level control** can block a specific action inside an otherwise-allowed connector (e.g. block `Send HTTP request` in Office 365 Outlook) — prefer this over blocking the whole connector when only one action is the risk.
- **Sandboxed dev environments** may run a *looser* env-scoped policy than the tenant floor — env-scoped policies override tenant-wide (more specific wins); never the reverse.

## See also

- [`./gov-environment-strategy-and-isolation.md`](./gov-environment-strategy-and-isolation.md) — env-scoped policies ride on top of the env topology
- [`./gov-secure-the-default-environment.md`](./gov-secure-the-default-environment.md) — the default env needs its own strict DLP
- [`../skills/dlp-policy-design/SKILL.md`](../skills/dlp-policy-design/SKILL.md) — 3-bucket model, precedence, exemption process, comms/rollback plan
- [`../knowledge/alm-governance-decision-trees.md`](../knowledge/alm-governance-decision-trees.md) — `## Decision Tree: DLP — classifying a connector`

## Provenance

Codifies the `dlp-policy-design` skill's Core Principle #1 ("default-deny philosophy") and the `power-platform-admin` opinions on DLP. The three-bucket model, HTTP blast radius, custom-connector-as-DLP-object, env-vs-tenant precedence, and the policy-change re-evaluation behavior are from the `dlp-policy-design` skill (grounded in Microsoft Learn DLP docs). `Get-AdminPowerAppEnvironment` / `Get-AdminFlow` are from the Microsoft.PowerApps.Administration.PowerShell module [unverified — confirm exact cmdlet names against your installed module version].

---

_Last reviewed: 2026-05-30 by `claude`_
