# Default to a single org with a tiered environment chain — go multi-org only for a hard reason

**Status:** Pattern — strong default; a multi-org split is a deliberate, expensive, written decision.

**Domain:** Platform architecture / org strategy

**Applies to:** `salesforce`

---

## Why this exists

"How many production orgs?" is one of the most expensive decisions in Salesforce, and it is nearly irreversible — merging two orgs later is a multi-year migration, and splitting one is almost as bad. The gravitational default is **a single org**: shared data model, one 360° view of the customer, one set of automation, one security model, no cross-org integration tax. Multi-org buys real things — regulatory data residency, true business-unit autonomy, isolation of an acquisition, governor/storage headroom at extreme scale — but every one of them is paid for in duplicated metadata, cross-org integration middleware, and split reporting. Teams that reach for multi-org because two departments "want their own space" discover they've bought a permanent integration project to solve a governance problem. Underneath the production decision sits the **environment chain** — the non-prod orgs that feed prod — and that chain is non-negotiable regardless of how many prod orgs you run: you never develop in, or click-deploy to, production (house opinion #15).

## How to apply

Decide the production topology against hard constraints, then stand up a promotion chain feeding each prod org.

```
PRODUCTION TOPOLOGY — pick the most-restrictive that a hard constraint forces:
  Single org ........... default. Shared customer, shared model, one security model.
  Single + divisions ... business-unit separation WITHOUT a second org (Divisions, restriction rules, BU-scoped sharing)
  Multi-org ............ ONLY for: data residency law, M&A isolation, hard governor/storage ceiling, true autonomy mandate

ENVIRONMENT CHAIN feeding each prod org (source-tracked, promoted, never clicked):
  scratch org / dev sandbox  ->  integration  ->  UAT (Partial/Full copy)  ->  PROD
        (feature work)            (merge point)     (business sign-off, sized data)
```

```bash
# Sandbox tiers map to chain stages; pick the copy type by what the stage must prove
sf org create sandbox --name uat --license-type PartialCopy --target-org prod   # representative data subset
# Full copy only where prod-scale data/perf must be exercised (long refresh, license cost)
```

**Do:**
- Start single-org; make multi-org justify itself against a *hard* constraint (law, M&A, ceiling), not a preference.
- Solve "business units want separation" inside one org first — restriction rules, scoped sharing, divisions — before splitting.
- Match each sandbox tier to what it must prove: Developer for code, Partial Copy for representative data, Full Copy for LDV/perf/UAT.
- Keep the promotion chain source-tracked end-to-end so every stage is reproducible.

**Don't:**
- Split into multiple prod orgs to dodge a governance/sharing problem that a single-org design solves.
- Develop directly in a shared UAT or prod org — drift makes the chain a lie.
- Forget the cross-org integration and master-data-management cost when you do choose multi-org — budget it up front.

## Edge cases / when the rule does NOT apply

Genuine **data-residency regulation** (data must physically stay in a region/instance), a freshly **acquired company** you must isolate before integrating, or an org hitting **hard platform ceilings** (storage, daily API, custom-object limits) at a scale a single org can't absorb — these are legitimate multi-org drivers, and forcing them into one org is the wrong call. Likewise, a very small org may collapse the chain (a single dev sandbox + prod) — the *principle* (don't build in prod) holds even when the chain is short. ISV/AppExchange development is a different topic entirely: packaging orgs and Dev Hub, governed by the packaging rules, not this one.

## See also

- [`alm-2gp-unlocked-package-modularization.md`](./alm-2gp-unlocked-package-modularization.md) — how the org's metadata is modularized once topology is set
- [`alm-scratch-orgs-and-source-tracking.md`](./alm-scratch-orgs-and-source-tracking.md) — the development end of the environment chain
- [`package-and-deploy-in-dependency-order.md`](./package-and-deploy-in-dependency-order.md) — how releases move along the chain
- [`../knowledge/platform-alm-agentforce-decision-trees.md`](../knowledge/platform-alm-agentforce-decision-trees.md) — the single-vs-multi-org decision tree
- [`../knowledge/sharing-and-security-model.md`](../knowledge/sharing-and-security-model.md) — the in-org separation alternatives to a second org

## Provenance

Codifies the `salesforce-platform-architect`'s "structural calls that are expensive to reverse" mandate and house opinion #15's environment discipline. Grounded in [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) and Salesforce's "Enterprise Territory / Org Strategy" and environment-management guidance. Sandbox license types and limits are version-sensitive — `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
