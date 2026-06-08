# wealth-management-advisory

The **RIA / financial-advisor practice team** that helps an advisor prepare their own work — not a
tool that advises end clients. Covers practice strategy and AUM growth, the financial-planning
process, portfolio review and rebalancing, client relationship management and prospecting, and
advisory compliance (Reg BI / suitability / fiduciary).

> **The one-line philosophy:** fiduciary duty is the floor, not the ceiling. Document the rationale,
> clear suitability before every recommendation, and never imply a return — the advisor's credibility
> is the practice's only durable asset.

---

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "How do I grow AUM / segment my book / build a service model?" | **wealth-management-advisory** (`advisory-practice-lead`) |
| "Help me outline or document a financial plan for this client profile" | **wealth-management-advisory** (`financial-planning-specialist`) |
| "Review this allocation against the IPS / write the portfolio review narrative" | **wealth-management-advisory** (`portfolio-review-analyst`) |
| "Prep my review agenda / draft a follow-up / build a prospecting sequence" | **wealth-management-advisory** (`client-relationship-manager`) |
| "Does this recommendation pass Reg BI? What disclosures do I need?" | **wealth-management-advisory** (`advisory-compliance-advisor`) |
| "Build a 3-statement model / DCF for a business-owner client's company" | `finance` |
| "Deep SEC/FINRA exam response / enforcement analysis / state registration" | `regulatory-compliance` |
| "Store or transmit client PII securely" | `ravenclaude-core/security-reviewer` |

---

## What's inside

- **5 agents** — `advisory-practice-lead`, `financial-planning-specialist`, `portfolio-review-
  analyst`, `client-relationship-manager`, `advisory-compliance-advisor`.
- **3 skills** — `financial-planning-process`, `portfolio-review-and-rebalancing`,
  `client-review-and-prospecting`.
- **3 commands** — `/wealth-management-advisory:prep-client-review`,
  `:build-financial-plan-outline`, `:review-portfolio`.
- **2 templates** — `financial-plan-outline.md`, `investment-policy-statement.md`.
- **Knowledge bank** — `knowledge/advisory-decision-trees.md`: Mermaid trees for suitability/Reg-BI
  clearance, rebalance-now-or-not, and prospect qualification; plus a dated 2026 capability map of
  planning tools, CRM platforms, and custodians.
- **6 best-practices** and **1 advisory hook** (flags guarantee language, plaintext PII,
  unsupported recommendations, undisclosed performance claims).

---

## House opinions (the short list)

1. This plugin prepares the advisor's work — it does not advise clients. The advisor reviews and
   takes responsibility before anything reaches a client.
2. Suitability / Reg BI clearance before any recommendation — no exceptions.
3. Never guarantee or imply a return.
4. Fiduciary duty is the floor, not the ceiling.
5. Document the rationale, every time.
6. Protect client PII and account data; strip or mask before any example use.

---

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
