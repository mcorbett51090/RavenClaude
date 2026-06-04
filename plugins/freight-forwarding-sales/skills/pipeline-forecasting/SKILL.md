---
name: pipeline-forecasting
description: "Veteran playbook for freight-sales pipeline and forecast discipline — stage definitions tied to buyer behavior, coverage ratio, sales velocity, weighted vs commit vs best-case forecast, the deal-inspection checklist, single-threaded-risk flags, and the long multi-stakeholder logistics cycle (6 to 18 months). Consulted by pipeline-forecast-coach."
---

# Pipeline & Forecasting Skill

**Purpose:** help `pipeline-forecast-coach` keep the CRM honest and the forecast defensible in a long, multi-stakeholder sales cycle. A stage is what the **buyer did**, not how the seller feels.

## When to use
- A pipeline review or forecast call.
- Deal-by-deal inspection for at-risk deals.
- Checking whether coverage is enough to hit quota.

## 1. Stage discipline (behavior-based)
Each stage has an **exit criterion the buyer demonstrably meets**:

| Stage | Exit criterion (buyer behavior) | Default probability* |
|---|---|---|
| Lead / Prospect | responded, agreed to talk | 5–10% |
| Discovery / Qualify | confirmed need + lanes + volumes + decision process | 20% |
| Solution / Scoping | requirements agreed; we're a shortlisted option | 40% |
| Proposal / Quote | pricing/proposal formally presented | 60% |
| Negotiation | terms in redline; verbal/contingent yes | 80% |
| Closed-Won | signed contract / SOW / first booking | 100% |

\* Calibrate to your own historical win-rates by stage — these are starting defaults, not truth.

**Rule:** if you can't name what the customer *did* to enter a stage, the deal isn't in it.

## 2. Coverage ratio
`coverage = open weighted pipeline ÷ remaining quota`. In long, lower-win-rate logistics cycles the healthy multiple runs higher (commonly 3–4×+; calibrate to your win-rate). Surface the ratio and the implied gap — and surface it **early**, because a 6–18 month cycle can't be fixed at quarter-end.

## 3. Sales velocity
`velocity = (# qualified opps × avg deal value × win rate) ÷ avg cycle length (days)`
— the "how fast is revenue moving" number. Improving **any** of the four levers (more opps, bigger deals, higher win-rate, shorter cycle) increases velocity. Use it to compare reps, lanes, or quarters, and to see which lever to pull.

## 4. Three forecast numbers, labeled
Never one blended guess:
- **Commit** — deals the seller will personally stand behind (near-certain).
- **Best-case** — commit + credible upside.
- **Weighted** — Σ(deal value × stage probability) across the pipeline.
Report all three; the gap between them is the conversation.

## 5. Deal-inspection checklist
For each material deal:
- Last **meaningful** activity (not an auto-email).
- **Next step + date** — missing = effectively dead.
- **Contacts**: how many, how senior — **single contact = single-threaded risk** (P1 in logistics, where procurement + ops + finance all gate).
- Decision **criteria** known? **Compelling event** (a contract end, a peak, a disruption)?
- Competition / incumbent and why-we-win.
- Realistic close date vs the CRM date (count the **pushes**).

## 6. The logistics-cycle reality
Managed-logistics / 3PL contracts run **6–18 months** with **procurement** (budget), **operations** (requirements), and **finance** (cost model) all approving. A one-contact deal is structurally fragile; multi-threading is the mitigation. This is why coverage must be built far ahead of the quarter you want to land.

## 7. Hygiene sweep (run every review)
Flag: stuck deals (no stage change in N weeks), serial-pushed close dates, zombie deals (open, zero activity), missing-data deals, and single-threaded deals. Clean the pipeline before you forecast off it — a dirty pipeline produces a fictional number.

## Hand-offs
- Coverage gap needs net-new → `prospect-outreach` skill / `prospecting-outreach-strategist`.
- Expansion deals in current accounts → `qbr-account-planning` skill / `key-account-manager`.
- Building a real CRM/pipeline **dashboard** → `data-platform` plugin / `ravenclaude-core` `data-engineer`.
