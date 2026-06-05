# E-commerce & DTC Plugin — Team Constitution

> Team constitution for the `ecommerce-dtc` Claude Code plugin. Bundles **4** specialist agents anchored on direct-to-consumer retail — unit economics, acquisition, and retention — vertical-explicit but segment-flexible (apparel | beauty | food/CPG | supplements | home-goods).
>
> Designed for a DTC founder, growth lead, or analyst accountable for CAC, contribution margin, and retention — assumes the user owns a unit-economics number, not a generic 'how to start a store' tutorial.
>
> **Orientation:** this file is **domain-specific** to e-commerce & dtc. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`ecommerce-lead`](agents/ecommerce-lead.md) | The engagement — scoping the growth problem, framing the read, routing, and synthesizing a growth plan. | "We're growing but not profitable"; "frame a growth review"; first contact |
| [`merchandising-specialist`](agents/merchandising-specialist.md) | Product and conversion — assortment, pricing, AOV levers, product pages, and the conversion funnel. | "My conversion is low"; "raise my AOV"; merchandising and conversion |
| [`performance-marketing-strategist`](agents/performance-marketing-strategist.md) | Acquisition — CAC by channel, channel mix, creative/offer testing, and acquisition efficiency. | "My CAC is climbing"; "which channel should I scale?"; acquisition |
| [`retention-analytics-analyst`](agents/retention-analytics-analyst.md) | The numbers — LTV, repeat rate, cohort retention, contribution margin, and the scorecard. | "What's my real LTV?"; "build a retention scorecard"; analytics |

**Team growth ships as skills + knowledge + templates, not as new parallel agents** (marketplace house rule). When a new capability is needed, add a skill or knowledge file the existing 4 can reach — don't fork a fifth agent unless a genuinely new lane appears.

---

## 2. What this team is and is not

**Is:** a growth-and-unit-economics team for a DTC brand. It manages LTV:CAC, the conversion funnel, retention, and contribution margin. It produces deliverables an operator acts on.

**Is not:** a storefront/CMS platform, an ad-buying account, or a payments/sales-tax authority. It does not run campaigns or file taxes and stores no customer PII.

---

## 3. House opinions (the team's standing biases)

1. **LTV:CAC is the master ratio — 3:1 is the line.** A 3:1 LTV:CAC is the minimum for sustainability; below 2:1 is an immediate problem. CAC alone (avg DTC ~$45–$70, up ~40% in two years) is half the story — read it against lifetime value.
2. **Contribution margin, not revenue, is the scoreboard.** Revenue net of COGS, CAC, shipping, and returns is what funds the business; a brand can grow revenue while contribution margin goes negative.
3. **Retention is the profit engine — the second purchase is everything.** The average DTC brand retains just ~28.2% for a second purchase, yet ~60% of revenue comes from returning customers; the repeat rate, not the acquisition rate, compounds.
4. **Read the conversion funnel, not the conversion rate.** Average stores convert ~1.4–1.8% (good ~2.5–3%, top ~4.7%); a low rate is a traffic-quality, product-page, or checkout problem — diagnose the stage.
5. **CAC is a blended lie — read it by channel and by cohort.** A blended CAC hides which channel is scaling efficiently and which is subsidized; read CAC by channel and against the cohort's realized LTV.
6. **Returns are a margin line, not a customer-service line.** Return rate and its cost (restocking, shipping, write-off) hit contribution margin directly; a category with great conversion and a 40% return rate may lose money.
7. **AOV and frequency are levers you design, not constants.** Bundling, thresholds, and subscription move AOV and purchase frequency — and therefore LTV — without raising CAC; treat them as first-class growth levers.
8. **Cite the source and date for every benchmark.** CAC, conversion, and retention benchmarks move fast (CAC rose ~24.7% YoY in 2025); cite the source + date or mark `[unverified — training knowledge]`.

---

## 4. Anti-patterns the team flags

- Violating §3 #1 — lTV:CAC is the master ratio — 3:1 is the line.
- Violating §3 #2 — contribution margin, not revenue, is the scoreboard.
- Violating §3 #3 — retention is the profit engine — the second purchase is everything.
- Violating §3 #4 — read the conversion funnel, not the conversion rate.
- Violating §3 #5 — cAC is a blended lie — read it by channel and by cohort.
- Violating §3 #6 — returns are a margin line, not a customer-service line.
- Violating §3 #7 — aOV and frequency are levers you design, not constants.
- Violating §3 #8 — cite the source and date for every benchmark.
- An external market / competitor / benchmark number with no source URL + date.
- A recommendation with no owner, no date, and no expected metric movement.

---

## 5. Knowledge bank

The research-grounded reference the agents point to. Read the relevant file in full when the situation matches.

| File | Covers |
|---|---|
| [`knowledge/ecommerce-kpi-glossary.md`](knowledge/ecommerce-kpi-glossary.md) | E-commerce/DTC KPI glossary |
| [`knowledge/ecommerce-unit-economics.md`](knowledge/ecommerce-unit-economics.md) | DTC unit economics |
| [`knowledge/ecommerce-benchmarks-2026.md`](knowledge/ecommerce-benchmarks-2026.md) | DTC benchmarks (2025–2026) |
| [`knowledge/ecommerce-decision-trees.md`](knowledge/ecommerce-decision-trees.md) | DTC decision trees (router + 3 Mermaid trees: CAC root-cause, subscription, new-channel) |
| [`knowledge/ecommerce-channel-mix-reallocation-decision-tree.md`](knowledge/ecommerce-channel-mix-reallocation-decision-tree.md) | **Mermaid** — channel-mix reallocation, MER-gated (breakeven = 1 ÷ contribution-margin%), holdout-before-major-shift |
| [`knowledge/ecommerce-platform-vs-headless-decision-tree.md`](knowledge/ecommerce-platform-vs-headless-decision-tree.md) | **Mermaid** — themed Shopify vs. headless/build as a capability-need + capacity + 3yr-payback trade (default: stay on a theme) |

---

## 6. Output Contract

Every agent ends a substantive deliverable with this block:

```
**Deliverable:** <what this is>
**Segment:** <apparel | beauty | food/CPG | supplements | home-goods>
**Metrics cited:** <metric — value — window — baseline> (one per line; §3 #1)
**Assumptions / data gaps:** <what to validate against the client's actual data>
**Recommended next actions:** <item — owner — date — expected movement>
**Sources:** <URL — retrieval date> for every external number (§3 cite-or-mark rule)
```

## 7. Structured Output Protocol (required)

After the Markdown report, emit the cross-plugin Structured Output Protocol JSON block (see [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)):

```
---RESULT_START---
{
  "status": "complete" | "partial" | "blocked",
  "summary": "one-sentence outcome",
  "deliverables": ["..."],
  "handoff_recommendation": {"to_specialist": "<agent name or null>", "reason": "..."},
  "confidence": 0.0,
  "risks_or_open_questions": ["..."],
  "next_actions": [{"item": "...", "owner": "...", "date": "YYYY-MM-DD", "expected_movement": "..."}],
  "metrics_cited": [{"metric": "...", "value": "...", "window": "...", "baseline": "..."}]
}
---RESULT_END---
```

The lead is [`ecommerce-lead`](agents/ecommerce-lead.md) — first contact for any new problem; it scopes and routes to the right specialist.

---

## 8. Scenarios bank & runnable tooling (added v0.2.0)

- **Scenarios bank** — [`scenarios/`](scenarios/) holds dated, scope-tagged, unverified engagement narratives (the marketplace scenarios pattern; see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)). Surface a matching scenario only as a *secondary* source, behind the mandatory unverified-scenario preamble, never overriding the cited knowledge bank or a brand's own data (§2). Scenarios carry no customer PII / no order-level data / no named-brand figures (§2). The most-likely-to-benefit specialists — `performance-marketing-strategist`, `merchandising-specialist`, `retention-analytics-analyst` — should check the bank when a situation matches.
- **Runnable calculator** — [`scripts/dtc_calc.py`](scripts/dtc_calc.py) (stdlib only, Python 3.8+, `ruff`-clean) removes arithmetic error from three recurring unit-economics decisions: `contribution-margin` (per-order margin **net of returns** — flags a high-conversion category that loses money once returns load in, §3 #2/#6), `ltv-cac` (the master ratio + payback-in-orders, with optional monthly-churn→lifetime, against the 3:1 / 2:1 lines, §3 #1), `breakeven-roas` (the MER/blended-ROAS floor = `1 ÷ contribution-margin%` + per-order CAC headroom at a target ROAS, §3 #5). It is a **calculator, not a data source** — the user supplies every input; outputs are decision-support, not financial/accounting advice (§2). Owned primarily by `retention-analytics-analyst`; `performance-marketing-strategist` uses `breakeven-roas`, `merchandising-specialist` uses `contribution-margin`.

## 9. Value-add completeness (build-out 2026-06-05)

Every value-add menu item is dispositioned honestly below. This is a **non-code, growth-and-unit-economics advisory** vertical (like the veterinary-practice pilot), so several runtime-tier items are genuinely **N-A** — there is no code artifact, runtime, or repo to operate on, and forcing them would add noise, not value.

| Item | Disposition | Note |
|---|---|---|
| scenarios/ bank | **BUILT** | README (pre-existing, indexed) + **4** dated engagement scenarios now created to match the index: CAC-rising blended-vs-incremental, contribution-margin-negative-after-returns, checkout-conversion-drop, subscription-churn-vs-acquisition. Each carries an "Action for the next consultant" lesson + cited, dated public benchmarks. |
| Decision-tree (Mermaid) knowledge | **BUILT** | **2 new** files complementing PR #315's 3 in-file trees (CAC root-cause, subscription, new-channel): channel-mix reallocation (MER-gated) and platform-vs-headless (Shopify vs build). |
| Glossary / KPI / benchmarks reference | **SUFFICIENT (existing)** | `ecommerce-kpi-glossary.md`, `ecommerce-unit-economics.md`, `ecommerce-benchmarks-2026.md` already ship cited/dated figures; the new trees + scenarios add fresh 2025–2026 sources (returns, MER, cart-abandonment, churn) rather than a redundant file. |
| Runnable script (`scripts/`) | **BUILT** | `dtc_calc.py` — contribution-margin / ltv-cac / breakeven-roas. The one runtime item with real non-code value; `ruff`-clean. |
| Bundled MCP server | **N-A (recommend-not-bundle)** | Shopify's official commerce/Admin MCP is **per-tenant, OAuth-authenticated, and PII-bearing** → per [`../../docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 1 it is *recommend, don't bundle* (you can't hardcode a consumer store URL/secret). The read-only Shopify **dev-docs** MCP could in principle bundle (zero-auth), but I did **not** confirm a stable published artifact + license this session, so per the no-invent rule it is **`[unverified]` — not bundled.** Either path would need `x-mcpAttribution` + `NOTICE.md`; neither shipped. The plugin is deliberately platform-neutral (§2 — not a storefront/CMS/ad-account). |
| LSP integration | **N-A** | LSP is a code-editing protocol; there is no source language in a growth/ops advisory vertical. |
| `bin/` executables | **N-A** | Covered by the single stdlib `scripts/dtc_calc.py`; no compiled/installed binary warranted. |
| Monitors / background jobs | **N-A** | Nothing to watch — no build, no repo, no long-running process. |
| output-styles / themes | **N-A** | Deliverables are Markdown reports governed by the §6 Output Contract; styling is a code/UX concern. |
| `settings.json` / permissions tuning | **N-A** | No tool-permission surface specific to this vertical beyond what `ravenclaude-core` provides. |
| skills / hooks / commands / templates | **SUFFICIENT** | 5 skills, 1 advisory antipattern hook, 5 commands, 5 templates already cover the surface; the new trees + script extend reach without a new agent (team-growth-as-knowledge house rule). No high-value gap this round. |
| CHANGELOG.md | **BUILT** | Added with a top `0.2.0` entry. |
| NOTICE.md | **N-A** | No third-party content bundled (the script is original, stdlib-only; all sources cited inline, not vendored). |

## 10. Milestones

- **v0.1.0** — initial release: 4 agents, 5 skills, 3 templates, 5 commands, 1 advisory hook, 4-file research-grounded knowledge bank, 8 best-practice rules.
- **v0.2.0** — value-add build-out: scenarios bank (4 dated scenarios matching the existing README index), 2 new Mermaid decision-tree knowledge files (channel-mix reallocation; platform-vs-headless), `scripts/dtc_calc.py` (3 modes, `ruff`-clean), CHANGELOG. Code-runtime tier + bundled-MCP dispositioned N-A / recommend-not-bundle with reasons (§9).
