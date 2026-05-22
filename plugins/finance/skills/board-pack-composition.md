---
name: board-pack-composition
description: Compose narrative-first board / investor / lender reporting packs — section sequencing, KPI selection, executive-summary patterns. Numbers don't ship without commentary. Used by `board-pack-composer` (primary).
---

# Skill: board-pack-composition

**Purpose:** How to assemble a board / investor / lender reporting pack that gets read and drives decisions. Used by `board-pack-composer` (primary).

## When to use

- Quarterly board cycles
- Monthly / quarterly investor updates
- Lender covenant-compliance packages
- Fundraising data rooms
- Ad-hoc board materials (M&A, restructuring, special situations)

## Audience first

Same data, different framing. Identify the audience before you write a single slide.

| Audience | Reads for | Lead with |
|---|---|---|
| Founder board | Direction-setting, hires, customer strategy | Vision + traction + asks |
| PE / VC board | Plan-vs-actual, value-creation milestones | KPIs vs LP-promised + risks |
| Lender | Covenant compliance, cash runway, asset quality | Compliance certificate + liquidity |
| Investor / LP update | Confidence + transparency + asks | Headline number + commentary + asks |
| Fundraising prospect | Why this round, why now, why us | Traction proof + use of proceeds |

If you can't name the audience, the pack is going to drift. Ask the Team Lead before assembling.

## The narrative spine

Every pack has a story. Decide the story before picking the slides.

A typical board-pack arc:
1. **Headline (1 slide)** — the one thing the board most needs to know this period.
2. **Operating summary (2-3 slides)** — KPIs, what moved, why.
3. **Financial summary (2-3 slides)** — P&L, cash, balance-sheet highlights.
4. **Strategic update (2-4 slides)** — what we said we'd do, what we did, what's next.
5. **Key risks / RAID (1-2 slides)** — what could blow up, what's being done.
6. **Decisions / asks (1 slide)** — what the board needs to decide / approve / weigh in on.
7. **Appendix (as needed)** — detailed financials, KPI definitions, supporting analyses.

Total: 12-15 slides body + appendix. Anything above 25 body slides is a slow-read meeting.

## Slide-craft rules

1. **Title is the takeaway.** "Q3 revenue beat plan on enterprise upsell," not "Q3 Revenue."
2. **One idea per slide.** Two charts on one slide is two slides.
3. **Numbers come with commentary.** Every table or chart has 1-3 sentences explaining what it means.
4. **Charts > tables for trend.** Tables > charts for precision.
5. **Color discipline.** A small palette (3-4 colors max) with consistent semantic mapping (green = favorable, red = unfavorable, gray = neutral).
6. **No 6-point font.** If it requires zoom, it's appendix material.
7. **Footnotes for definitions.** First time a non-standard KPI appears, footnote the definition.
8. **Confidentiality marking.** "Draft — Confidential — Board Use Only" on every page.

## KPI selection

5-7 on the front pages, no more. Pick them by:

- **Strategic relevance** — does this KPI tie to the company's stated strategy?
- **Sensitivity to action** — can leadership move this in the next quarter?
- **Defensibility of definition** — is there a clean, agreed definition?
- **Trend-readability** — does a multi-period view of this KPI tell a story?

KPIs that fail these checks go in the appendix, not the front pages.

## Variance commentary in a board pack

Use the [`./variance-commentary.md`](./variance-commentary.md) skill for the prose. Place commentary **inline with the variance**, not in a separate section. Reading a number and then having to flip 8 pages for the explanation is a UX failure.

## The decisions / asks slide

This is the most underused slide in board packs. Without it, the meeting drifts and the board doesn't know what they actually approved.

Format:
1. **Decision needed:** [specific decision] — proposed answer: [yes/no/option]
2. **Decision needed:** ...
3. **Input requested:** [topic where management wants opinions, not a yes/no]
4. **For your information:** [no decision needed, just awareness]

Put this as the last body slide, before the appendix.

## Investor-update specifics

Monthly cadence. Letter format, not deck.

Structure:
1. **Headline** — one paragraph: what happened this month, what matters most.
2. **Metrics** — 5-7 KPIs, ideally with a trend chart.
3. **Wins** — 2-4 specific.
4. **Losses** — 1-3 specific (yes, share these — credibility comes from honesty).
5. **Asks** — intros, hires, pricing feedback, anything the investor base can help with.
6. **What's next** — one paragraph: what we'll be working on between now and the next update.

## Lender pack specifics

Lender packs are colder, more numerical, less narrative. The lender wants:

1. **Compliance certificate** — covenant calculations vs. covenants, with agreement section references (see [`../agents/treasury-analyst.md`](../agents/treasury-analyst.md)).
2. **Borrowing base** (if asset-based) — eligible AR, eligible inventory, exclusions, availability.
3. **Financial statements** — P&L, BS, CF for the period.
4. **Forecast** — 12-18 month projection.
5. **Material developments** — anything they should know (litigation, customer concentration changes, major contracts).

Lender packs ship with audit-trail discipline (source citations on every figure). Lenders' inside counsel will probe these.

## Fundraising data-room organization

Top-level structure:
- `01_Financials/` — historicals, forecast, model, audit reports
- `02_KPIs/` — KPI history, cohort analyses, unit economics
- `03_Customer/` — customer concentration, contracts (redacted), retention analyses
- `04_Team/` — org chart, key bios, comp philosophy, options outstanding
- `05_Legal/` — entity structure, IP, material contracts, litigation
- `06_Tech/` — architecture, security, IP, third-party dependencies
- `07_Strategy/` — market analysis, competitive positioning, roadmap
- `99_Q&A/` — bilateral Q&A log

Naming: prefix every file with the section number + version + date (`02_KPIs/cohort-retention-v3-2026-Q2.pdf`).

## Anti-patterns

- Pack delivered same-day as the meeting
- Slide titles that describe content, not meaning ("Q3 Revenue" vs. "Q3 revenue beat plan")
- KPI definitions changed mid-year without footnote
- "Decisions / Asks" slide missing
- Confidentiality / draft mark missing on a draft
- Lender pack without a covenant certificate
- Investor update with no ask
- Tables jammed with 20+ rows and no commentary
- 6-point font, 80-slide pack with no executive summary

## See also

- Template: [`../templates/board-pack-outline.md`](../templates/board-pack-outline.md)
- Template: [`../templates/kpi-pack-template.md`](../templates/kpi-pack-template.md)
- Skill: [`./variance-commentary.md`](./variance-commentary.md)
- Agent: [`../agents/board-pack-composer.md`](../agents/board-pack-composer.md)
