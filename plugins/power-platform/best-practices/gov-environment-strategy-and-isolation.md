# Real workloads get dedicated environments, sized by users + sensitivity + ALM

**Status:** Pattern — strong default. Promote a workload up the environment tiers as users, data sensitivity, business impact, or ALM need increases; never run real production in the Default environment.

**Domain:** Governance / Environment strategy

**Applies to:** `power-platform`

---

## Why this exists

An environment is the isolation boundary for everything Power Platform: apps, flows, Dataverse data, connections, DLP scope, and capacity. Put unrelated workloads in one environment and you've coupled their security, their data, their capacity consumption, and their release cadence — a DLP change for one breaks the other, one team's runaway flow eats the other's API limits, and there's no clean dev → test → prod story for either. The opposite failure is environment sprawl: hundreds of ad-hoc envs nobody governs. The discipline is to size the environment to the workload using four observable drivers — **number of users, data confidentiality, monetary/reputational impact, and ALM need** — and to provision a *dedicated* environment the moment any one of them crosses a threshold. The Default environment, which every tenant gets and every user can build in, is for experimentation only — never for anything real.

## How to apply

Pick the tier by the drivers, then isolate. Use `pac admin` (or PPAC) to provision; scope membership with security groups; separate dev/test/prod for anything on a release path.

```bash
# Provision a dedicated, security-group-scoped environment for a real workload
pac admin create --name "Partners PROD" --type Production \
    --domain mc-partners-prod --region unitedstates --currency USD

# Tighten membership to a security group (not named users) so onboarding/offboarding
# is one group-membership change, and the env isn't open to every licensed user.
pac admin list --type Production     # audit what exists; hunt for sprawl + orphans
```

Tier guide (promote up as any driver increases):

| Tier | Use when | ALM |
|---|---|---|
| **Default** (secured) | 1–10 users, non-confidential, no ALM, low impact — experimentation only | none |
| **Shared** dedicated | ~7–30 users, confidential, monetary/reputational impact, or needs ALM | dev/test/prod via pipelines |
| **Dedicated** (per BU / per critical app) | >30 users, highly confidential, or business-critical | strict DLP + dedicated ALM |

**Do:**
- Separate **dev / test / prod** for any workload on a release path — the environment *is* the promotion boundary.
- Scope environment membership with **security groups**, not named users — auditable, one-step onboarding/offboarding.
- Use **environment groups** to apply policy in bulk across many dev/sandbox envs once you have more than a handful.

**Don't:**
- Run a production workload in the **Default** environment (the #1 governance gap — see the securing-the-default rule).
- Clone PROD to make a "sandbox" without sanitizing PII and resetting connection refs + env-var values.
- Let a Sandbox env quietly carry production-like load for 18 months "because it works."

## Edge cases / when the rule does NOT apply

- **Developer / Trial environments** are legitimately single-user, short-lived spaces — they don't need the full tiering; the rule targets shared and production workloads.
- **Dataverse for Teams** environments auto-provision per Team and have their own (capped) capacity and a graduation path to full Dataverse — fine for in-Team apps, but graduate before they outgrow the limits.
- **Per-app-criticality vs per-business-unit** dedicated environments are both valid topologies — choose by what changes independently (release cadence vs data-access boundary); the decision tree covers the split.

## See also

- [`./gov-secure-the-default-environment.md`](./gov-secure-the-default-environment.md) — locking down the env this rule says never to use for real work
- [`./gov-managed-environments-and-sharing-limits.md`](./gov-managed-environments-and-sharing-limits.md) — what to turn on once an env holds real workloads
- [`./gov-dlp-policy-default-deny.md`](./gov-dlp-policy-default-deny.md) — env-scoped DLP rides on this topology
- [`../knowledge/managed-environments-and-governance-2026.md`](../knowledge/managed-environments-and-governance-2026.md) — the `## Decision Tree: which environment tier?`
- [`../knowledge/alm-governance-decision-trees.md`](../knowledge/alm-governance-decision-trees.md) — `## Decision Tree: Environment topology`

## Provenance

Codifies the `power-platform-admin` environment-strategy surface and the four-driver tier model from [`../knowledge/managed-environments-and-governance-2026.md`](../knowledge/managed-environments-and-governance-2026.md) (grounded in Microsoft Learn environment-strategy guidance). `pac admin create/list --type` flags verified against the Microsoft Learn `pac admin` reference, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
