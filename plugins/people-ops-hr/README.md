# People Ops / HR

The **people-ops-hr** plugin — the People Operations / HR craft for small-to-midsize companies: the human side of running a company across the employee lifecycle, structured hiring, and total rewards. Distinct from `staffing-operations` (the staffing-**agency** business). **This plugin does not give legal advice — employment-compliance basics (FLSA, at-will, EEO, leave) are flagged for qualified counsel, never opined on.**

## Agents

- **`people-ops-generalist`** — The people-operations backbone: the employee lifecycle (onboarding → 30/60/90 → offboarding), handbook and policy authoring (plain-language: statement → scope → rule → process → edge cases), HRIS data hygiene (the canonical fields payroll and compliance depend on), leave/PTO program design, and a fair, documented approach to employee-relations basics.
- **`talent-acquisition-lead`** — Structured, fair, measurable hiring: job ladders and leveling for open roles, interview kits with one competency per assessor and anchored scorecards, a structured debrief, hiring-funnel metrics (conversion + time-in-stage, not applicant volume), candidate experience, and a clean offer process.
- **`total-rewards-analyst`** — The compensation and total-rewards architecture: the leveling / job-architecture ladder underneath salary bands, range midpoints/spreads from a market-data strategy, a pay-equity review that controls for legitimate factors and surfaces the *unexplained* residual, a benefits-design overview, and defensible merit/promotion cycles.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install people-ops-hr@ravenclaude
```

## Seams

- **The staffing-agency business (placing candidates at clients at scale, agency operations)** → `staffing-operations`; this plugin runs *internal* HR for a company, not the staffing business.
- **Payroll runs, GL coding of compensation, the comp budget** → `finance`; we design the bands and lifecycle, they run payroll and own the budget.
- **Benefits insurance, carrier selection, plan funding/underwriting** → `insurance-life-health-benefits`; we own the benefits-design *overview*, they own the carrier deal.
- **Any employment-law question (FLSA, EEO, ADA/leave, equal-pay, pay-transparency, termination)** → qualified counsel; this plugin *flags* the issue and routes the determination, it does not opine.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.
