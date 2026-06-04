# RavenClaude Idea Board

One place for every strategic idea: what it is, where it stands, and what unlocks it.
Statuses: **🟢 endorsed** (panel-reviewed, actionable) · **🟡 gated** (real, but opens only when a named gate is met) · **🔵 parked** (deliberate wait) · **⚪ folded-in** (lives on inside another idea) · **🔴 de-prioritized** (evidence says no, for now).

_Last updated: 2026-06-04 · Full evidence trail: [`docs/research/2026-06-04-future-niche/`](research/2026-06-04-future-niche/)_

---

## The lead idea

| Idea | One-liner | Status | Next step |
|---|---|---|---|
| **Closebook** | An AI workbench that drafts the recurring parts of month-end close + 13-week cash forecast across all of a company's systems and shows its work line-by-line — their own controller signs in hours instead of days. Sold against the cost of the next $130k finance hire ($30–38k First Close → $5–9k/mo retainer). | 🟢 endorsed — final panel voted **5/5 endorse-with-changes** (2026-06-04) | Matt answers the 3 owner questions (Track B appetite, Year-1 runway number, liability underwriting); then Month-0 actions: court 2–3 fractional-CFO referral practices, build the sample-GL demo, define finance Stop patterns |

Concept document: [v6 (post-panel)](research/2026-06-04-future-niche/08-concept-v6-closebook.md) · [v5](research/2026-06-04-future-niche/02-concept-v5-closebook-leash.md) · [panel report](research/2026-06-04-future-niche/06-panel-report.md)

**Why it won:** the only candidate that pairs a pain buyers already budget for (close/cash, finance-hire money) with the governance assets nobody else has (binding tribunal, posture dial, audit substrate) and Matt's founder-fit (a financial analyst selling to finance operators). The 4-round critic loop locked in the honesty: single-signer rule (buyer's controller signs, never Matt), bespoke per-customer reconciliation scripts (no "general engine" fantasy), Year 1 as a funded runway, Year-2 solo floor ~$130–190k margin.

## Track B — the ambition levers (stacked on Closebook, opt-in, gated)

| # | Lever | Status | Gate that unlocks it |
|---|---|---|---|
| B1 | **Origination partner** — a fractional-CFO firm sells on revenue-share while Matt delivers | 🟡 gated (Year 1, near-zero cost — pull first) | 2–3 practices courted in Month 0; one signs a referral arrangement |
| B2 | **Second delivery person** — a builder (never a signer) does mapping + script-build under Matt's review; attacks the real ceiling (delivery weeks) without touching the liability posture | 🟡 gated (Year 2) | ≥4 full-price closes delivered AND measured build-hour reduction AND 6-month cash buffer |
| B3 | **Productize the governance IP** ("the Leash" — tribunal/posture/audit) for the developer/compliance buyer; the funding line if outside money ever comes in | 🟡 gated (Year 2+, hardest gate) | ≥3 recurring finance-judgment categories route cleanly through the tribunal AND a design partner's reviewer confirms the verdict-bearing lineage card is decision-useful AND multi-tenant isolation + tamper-evident logging shipped & pen-tested |

## The other 2026-06-04 candidates — dispositions (recorded, not drifted)

| Idea | One-liner | Status | Where it lives now |
|---|---|---|---|
| **Verdict** | AI decision log / gateway API for regulated teams | ⚪ folded-in | The Track B3 governance-IP product, aimed at its real (developer) buyer |
| **Aegis** | AI governance binder / evidence pack for insurance & vendor questionnaires | 🟡 gated micro-line | Bundled into the Closebook retainer now; standalone only if the ISO GenAI E&O exclusion trigger verifies against the primary filing (currently unverified-secondary) |
| **The Compounding Engagement (Forge)** | Consulting where every engagement deposits reusable IP back into the marketplace | ⚪ folded-in | Closebook's internal delivery method (`/wrap` → pattern library → FORGE); not a sellable thing |
| **Leash** (standalone) | "The safety inspection for the AI you let touch your business" | ⚪ folded-in | Closebook's trust surface. "Leash" dropped from buyer-facing naming (fear metaphor); internal/dev vocabulary only |
| **FORGE-as-planning-product** | Sell the gated planning pipeline itself | 🔴 de-prioritized | Anthropic owns the primitive (Ultraplan); keep as internal differentiator |

## Research-backed niche territories (the map behind the ideas)

From the 5-lens research sweep ([synthesis](research/2026-06-04-future-niche/01-research-synthesis.md)), ranked T1–T6:

| Territory | Verdict | Carried by |
|---|---|---|
| T1 — Agent governance for non-developer small shops | Top whitespace (~12–18 mo window); genuine white space: nobody ships a binding multi-agent verdict on live actions, nobody serves non-developers | Track B3 |
| T2 — Boutique "implementation-gap" AI delivery for SMB finance/ops | The validated commercial vehicle ($25–60k engagements) | Closebook core |
| T3 — Evidence-of-AI-controls package (insurance renewal / vendor questionnaire) | Real trigger, unverified sourcing — verify before counting | Aegis micro-line |
| T4 — Regulated-vertical overlay, finance-first | Win as governed delivery, never as a standalone copilot (Microsoft owns that layer) | Closebook positioning |
| T5 — Fractional AI-governance advisor | Solo-credible but leans away from the dashboard-first wedge | Not pursued |
| T6 — FORGE as product | Thin and shrinking | De-prioritized |

**Key market finding (the surprise):** the EU-AI-Act deadline pitch is dead (high-risk obligations slipped to Dec 2027/Aug 2028; Colorado repealed) — but demand strengthened anyway, because the forcing function moved to **insurers** (AI exclusions in Tech E&O effective Jan 2026) and **procurement questionnaires**. Sell to the underwriter's question, not the regulator's calendar.

## Previously parked (pre-dating this board)

| Idea | Status | Wake condition |
|---|---|---|
| Competitor-analysis plugin | 🔵 parked (2026-05-22) | A real engagement needs a competitor brief |
| Research dashboard with fact-check verdicts | 🔵 parked (2026-05-22) | Base per-plugin dashboard ships and one plugin uses it |
| Dataverse token-acquisition improvement (power-platform) | 🔵 parked (draft/held) | Tribunal PR landed (done) — ready to schedule when capacity allows |

## The 3 open owner questions (panel → Matt)

1. **Track B appetite** — is the solo ~$130–190k/yr ceiling the life being chosen, or should the levers be pulled? (Values call, not a math call.)
2. **Year-1 runway number** — partial analyst income + household burn + savings tolerance → the GO/NO-GO. The plan doesn't start without it.
3. **Liability underwriting** — DPA/confidentiality exposure now; E&O posture if B3 ships. Needs a lawyer conversation.

---

_Board convention: new ideas get a row + a status + a named gate or wake condition. An idea with no gate and no next step is a 🔵 parked idea pretending to be active — give it one or park it honestly. Update this file in the same commit as the research that changes an idea's status._
