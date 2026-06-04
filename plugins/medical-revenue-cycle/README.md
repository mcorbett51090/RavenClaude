# Medical Revenue Cycle — Claude Code plugin

A revenue-cycle team for a healthcare provider or RCM operator — it drives the clean-claim rate toward 98%, attacks denials before they happen (initial denials hit ~11.8% in 2024 and trend 12–15%), works the A/R by aging bucket, and reads net collection rate the way a CFO who lives the cash cycle does.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
medical revenue cycle depth on top.

## What it does

Raises first-pass clean-claim and resolution rates, runs denial prevention by root cause and payer, manages days-in-A/R below 30, and protects the net collection rate. Produces denial-prevention plans, A/R work-down strategies, and RCM scorecards a provider acts on.

## Agents

- **`rcm-engagement-lead`** — The engagement — scoping the cash problem, framing the read, routing, and synthesizing an action plan.
- **`medical-coding-specialist`** — Coding accuracy — CPT/ICD/HCPCS accuracy, documentation support, and coding-driven denials, as decision-support.
- **`denials-management-specialist`** — Denial prevention and A/R — root-cause categorization, front-end fixes, appeals, and the work-down.
- **`rcm-analytics-analyst`** — The metrics — clean-claim/first-pass, net collection rate, days-in-A/R, denial analytics, and the scorecard.

## Skills

- **`prevent-denials`** — Categorize denials by root cause and owner and push fixes upstream to registration and authorization, instead of only appealing. Reach for this when the denial rate is high.
- **`read-the-cash-cycle`** — Read net collection rate, first-pass resolution, and days-in-A/R together, against benchmark, so a cash problem is diagnosed correctly. Reach for this on any collections question.
- **`work-down-ar`** — Prioritize an A/R work-down by aging bucket, payer, and recoverable dollars, with timely-filing risk first. Reach for this when A/R piles up.
- **`read-coding-denials`** — Trace coding denials to documentation, code selection, or modifier use as decision-support, never to up-coding. Reach for this when coding denials rise.
- **`build-rcm-scorecard`** — Build a net-collection-led RCM scorecard with first-pass, denial-by-category, and days-in-A/R, each defined and baselined. Reach for this to instrument the cycle.

## Slash commands

- **`/medical-revenue-cycle:prevent-denials-at-the-root`** — Prevent denials at the root
- **`/medical-revenue-cycle:read-the-cash-cycle`** — Read the cash cycle
- **`/medical-revenue-cycle:work-down-aged-a-r`** — Work down aged A/R
- **`/medical-revenue-cycle:read-coding-driven-denials`** — Read coding-driven denials
- **`/medical-revenue-cycle:build-an-rcm-scorecard`** — Build an RCM scorecard

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install medical-revenue-cycle@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a clearinghouse, an EHR, or a certified-coding/legal authority — coding guidance is decision-support, and final code assignment belongs to a credentialed coder and provider. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
