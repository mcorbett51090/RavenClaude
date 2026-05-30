# Turn on Managed Environments for production; set sharing limits

**Status:** Pattern — strong default for any production environment, given the premium licensing it requires. The sharing limit and weekly digest alone justify the SKU for prod.

**Domain:** Governance / Managed Environments

**Applies to:** `power-platform`

---

## Why this exists

Out of the box, a maker can share a canvas app or flow with the entire tenant, and you find out *after* the over-share, by which point the data exposure already happened. **Managed Environments** (surfaced as **Environment management** in the new admin center) flips governance from reactive to **proactive, in-product** — guardrails enforced *before* the action. The flagship is **sharing limits**: cap how broadly an app/flow/agent can be shared (≤ N users, or block security-group sharing entirely), enforced at share time, not reported after. You also get the weekly digest (inactive apps, usage, recommendations), usage insights, solution-checker enforcement on import, IP firewall, and the Managed security + Managed governance feature pillars. For a production environment carrying real users and real data, this is the baseline control surface. The CoE Starter Kit complements it for reactive analytics and gaps Managed Environments doesn't yet cover — but lead with Managed Environments, not the CoE kit.

## How to apply

Enable Managed Environments on every production (and sensitive) environment; set a sharing limit; confirm licensing before flipping it on (the licensing is the gate — see Edge cases).

```bash
# Enable Managed Environments / configure sharing limits via the Power Platform admin
# center (Environments > select env > Edit Managed Environment), or programmatically via
# the Power Platform API / admin PowerShell. Set: sharing limit (e.g. ≤ 20 users, no
# security-group sharing), weekly digest recipients, solution-checker enforcement = block.
pac admin list --type Production    # inventory which prod envs need it turned on
```

**Do:**
- Enable it on **every prod environment** and any environment holding confidential data.
- Set a **sharing limit** that matches the workload (a 30-user line-of-business app shouldn't be shareable to 5,000 people).
- Turn on **solution-checker enforcement** so imports that fail checker rules are blocked, and route the **weekly digest** to the environment owners.

**Don't:**
- Enable it without confirming the **premium licensing** is in place — see Edge cases; this is a hard licensing trigger, not a free toggle.
- Treat the **CoE Starter Kit** as the governance foundation — it's reactive sample implementations you customize, layered *on top of* Managed Environments, not a substitute.
- Leave the **Default** environment unmanaged — it's everyone's sandbox and the #1 governance gap (see the securing-the-default rule).

## Edge cases / when the rule does NOT apply

- **Licensing is mandatory and enforced.** Enabling Managed Environments on an environment requires **every active user** to hold a premium per-user license (Power Apps Premium, Power Automate Premium, or a Dynamics 365 Enterprise license) **or** the environment to have capacity-based add-ons allocated. Microsoft begins admin compliance notifications March 2026 and end-user in-app notifications June 2026 (verified, MS Learn Managed Environments licensing, 2026-05-30). Confirm entitlement before enabling — surprise compliance notifications erode trust.
- **Developer Plan** environments do **not** get Managed Environments as an entitlement when users run their assets (verified, same source) — don't promise the feature on a Developer-Plan-only footing.
- **Dev/sandbox environments** may not need it — the proactive controls matter most where real users and data live; weigh the per-user license cost against the governance benefit per environment.

## See also

- [`./gov-environment-strategy-and-isolation.md`](./gov-environment-strategy-and-isolation.md) — which environments warrant this
- [`./gov-secure-the-default-environment.md`](./gov-secure-the-default-environment.md) — turning it on for the Default env specifically
- [`./gov-licensing-and-capacity-awareness.md`](./gov-licensing-and-capacity-awareness.md) — the premium-license math this triggers
- [`../knowledge/managed-environments-and-governance-2026.md`](../knowledge/managed-environments-and-governance-2026.md) — full feature table + Managed Environments vs CoE
- [`../knowledge/alm-governance-decision-trees.md`](../knowledge/alm-governance-decision-trees.md) — `## Decision Tree: Does this environment need Managed Environments?`

## Provenance

Codifies the `power-platform-admin` opinion ("Managed environments turned on for any prod env — the sharing limit and weekly digest alone pay for the SKU") and [`../knowledge/managed-environments-and-governance-2026.md`](../knowledge/managed-environments-and-governance-2026.md). The premium per-user licensing requirement, the March/June 2026 enforcement-notification timeline, and the Developer-Plan exclusion are verified against Microsoft Learn (Managed Environments licensing FAQ), retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
