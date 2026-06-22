# startup-fundraising

> Venture fundraising for **founders and operators** — the operator-in-the-room who has run rounds before. Round strategy, the pitch narrative, cap-table & dilution math, term-sheet & SAFE literacy, the investor pipeline, the data room, and investor updates.
>
> **Founder-side literacy only — NOT legal or financial advice.** Binding term-sheet review routes to `legal-ops-clm`; financial-model mechanics to `finance`; the product what/why to `product-management`.

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Should I raise a pre-seed/seed/Series A, and how much?" | Stage diagnosis + a raise sized off 18-24mo runway-to-milestone + SAFE-vs-priced + the implied dilution |
| "What does my cap table look like after this round?" | A fully-diluted post-round ownership table + the option-pool shuffle + the post-money-cap dilution gotcha, with worked math |
| "Walk me through this term sheet — what do I push back on?" | A plain-language map of the economic + control terms, then a hard handoff to `legal-ops-clm` for binding review |
| "Who should I pitch and how?" | A tiered, stage-fit investor pipeline + a warm-intro-first outreach sequence |
| "Turn what we do into a fundable story / review my deck" | A problem→solution→why-now→market→traction→team→ask arc, or a slide-by-slide critique |
| "Draft our investor update" | A metrics-first monthly update (highlights, lowlights, KPIs, specific asks) |

**Two rules it never breaks:** *size the raise off runway-to-the-next-milestone, not a round-size meme*, and *always show the dilution* (including the post-money-cap gotcha).

## What's inside

- **2 agents** — `fundraising-strategist` (round strategy, cap-table/dilution math, term-sheet literacy, pipeline, data room) and `pitch-and-narrative-coach` (the narrative, the deck, the ask, investor updates).
- **3 skills** — `build-investor-pipeline`, `model-cap-table-and-dilution`, `prepare-data-room`.
- **2 knowledge files** — a Mermaid fundraising-stages decision tree (stage → instrument → range), and a term-sheet & SAFE essentials reference (founder-side literacy).
- **2 templates** — a 10-12 slide pitch-deck outline, and a monthly investor-update template.

## How it seams with other plugins

```
startup-fundraising  →  founder-side literacy: how much, what instrument, what dilution, what to ask
finance              →  the financial model mechanics, projections, valuation defensibility
product-management   →  the product what/why behind the story
legal-ops-clm        →  binding term-sheet / SAFE review — what is enforceable, what to sign
```

This plugin gives founders the **literacy to negotiate and the math to understand dilution**. It does **not** give legal or financial advice — those seams are hard lines, enforced in every agent's output contract.

## A note on market norms

Typical round sizes, valuations, and dilution bands are **volatile and market-dependent**. Every such figure in this plugin carries a **retrieval date (2026-06)** and is framed as a **range, not a guarantee** — re-verify before quoting in a real raise.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install startup-fundraising@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
