# State the licensing and capacity impact of every recommendation

**Status:** Absolute rule for this plugin — every Power Platform recommendation that touches a premium connector, AI Builder, a license tier, or Dataverse capacity states the cost impact. A design that ignores licensing is a design that gets vetoed at procurement.

**Domain:** Governance / Licensing & capacity

**Applies to:** `power-platform`

---

## Why this exists

Power Platform licensing and capacity are *the constraint*, not an afterthought. A flawless architecture that requires per-user Premium for 5,000 end users when per-app would cost a quarter as much is a bad design. A solution that turns on Managed Environments without realizing that obliges a premium license for every active user is a surprise compliance bill. AI Builder used in prod with nobody tracking AI Credit consumption is a renewal-time shock. And "we're out of space" panics are usually the *log* capacity bucket (Dataverse auditing), not database — buying storage fixes the wrong thing. Because the plugin's output contract makes the `Licensing impact:` line mandatory for every agent, this rule names what that line must actually account for: it's cheaper to surface the cost in the design review than to discover it in the invoice.

## How to apply

For any recommendation, account for license type, capacity buckets, and the premium triggers. Show the math, don't just assert "it's fine."

| Concern | What to check |
|---|---|
| **License tier** | per-user Premium (makers) vs per-app / per-flow (end users) vs pay-as-you-go (unpredictable/experimental) — pick the cheapest that fits the access pattern |
| **Premium connectors** | every premium-connector recommendation states the per-user-Premium (or per-app/PAYG) requirement it imposes |
| **Managed Environments** | enabling it requires a premium per-user license for **every active user** (or capacity add-ons) — a hard trigger |
| **Capacity (3 buckets)** | **database**, **file**, **log** — most "out of space" is the *log* bucket from auditing; review retention before buying storage |
| **AI Builder / Copilot** | AI Credit consumption — track it, or get surprised at renewal |

```bash
# Audit capacity per environment before recommending more storage (it's often log, not db)
Get-AdminPowerAppEnvironment -Capacity      # capacity per env: database / file / log
# Power Automate license enforcement: admins have 90 days post-notification before
# lifecycle ops (create/copy/restore) are disabled, 180 days before flow suspension.
```

**Do:**
- Default end-user licensing to **per-app or per-flow** unless a user genuinely needs broad maker access — per-user Premium for everyone is usually 4× the cost.
- Reach for **pay-as-you-go** (Azure-billed) for unpredictable or experimental workloads — a meter, not a commitment.
- When "we're out of capacity" comes up, **check the log bucket first** — Dataverse audit retention is the usual culprit.

**Don't:**
- Recommend a premium connector, AI Builder, or Managed Environments without stating the license/credit impact.
- Buy database storage to fix a log-bucket overage.
- Assume Dataverse-for-Teams limits scale — graduate to full Dataverse before the workload outgrows them.

## Edge cases / when the rule does NOT apply

- **ALM tooling itself** (pac CLI, pipelines, source control) usually carries `Licensing impact: none` — but the moment the pipeline implies Managed Environments or a premium env tier, that's a license trigger to name.
- **Trial licenses** can cover Managed Environment users but only for 30 days (verified, MS Learn) — never a production licensing answer.
- **Standard connectors** (within O365 entitlement) don't trigger premium licensing — the rule bites on *premium* connectors, Dataverse, and AI; be precise about which a flow actually uses.

## See also

- [`./gov-managed-environments-and-sharing-limits.md`](./gov-managed-environments-and-sharing-limits.md) — the premium-license trigger Managed Environments imposes
- [`./gov-environment-strategy-and-isolation.md`](./gov-environment-strategy-and-isolation.md) — capacity is consumed per environment
- [`../agents/power-platform-admin.md`](../agents/power-platform-admin.md) — owns license/capacity math; its `Licensing impact:` line is always populated with specifics
- [`../CLAUDE.md`](../CLAUDE.md) §6 — the mandatory `Licensing impact:` output-contract line

## Provenance

Codifies house opinion §3 #8 ("Premium connector ≠ casual choice"), the mandatory `Licensing impact:` output-contract line (§6), and the `power-platform-admin` licensing/capacity opinions (three capacity buckets, per-user vs per-app, PAYG, log-bucket-first). The Managed Environments premium-per-user requirement, the 90/180-day Power Automate enforcement timeline, and the 30-day trial-license caveat are verified against Microsoft Learn (Managed Environments licensing FAQ, premium-flow enforcement), retrieved 2026-05-30. `Get-AdminPowerAppEnvironment -Capacity` verified against the Microsoft Learn capacity-report tutorial.

---

_Last reviewed: 2026-05-30 by `claude`_
