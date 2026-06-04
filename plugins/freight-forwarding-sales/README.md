# freight-forwarding-sales

A Claude Code plugin for an **international freight-forwarding sales / business-development manager** — the person who sells ocean, air, and road freight + supply-chain services for a global forwarder or 3PL (DHL Global Forwarding, Kuehne+Nagel, DSV, DB Schenker, Expeditors, a regional forwarder, etc.).

It packages the recurring, judgment-heavy work of that job into a team of specialist agents, reusable skills, slash commands, and a runnable calculator — so quoting, tendering, account reviews, pipeline hygiene, and prospecting take minutes instead of hours, and come out consistent.

> Carrier-neutral by design. Nothing here is DHL-internal or DHL-confidential — it encodes **industry-standard** freight-sales practice (Incoterms 2020, IATA chargeable weight, ocean surcharge stack, RFQ/RFP norms, QBR structure) that applies to any forwarder.

## Who it's for

- Field / inside sales and business-development managers at a freight forwarder or 3PL
- Key-account managers running a book of shipper accounts
- Sales managers who coach a team and own a pipeline + forecast

## What's inside

### Agents (6)

| Agent | Owns |
|---|---|
| `freight-rate-quoter` | All-in ocean + air quotes — chargeable weight, CBM / W/M, the surcharge stack (BAF, CAF, THC, LSS, GRI, PSS, ISPS, AMS/ENS), margin, validity, customer-ready quote sheet |
| `rfq-tender-strategist` | RFQ / RFP / tender responses — qualify-or-decline, lane rate matrices, win-factor strategy, bid narrative, follow-up cadence |
| `key-account-manager` | QBRs, account plans, retention, whitespace / upsell-cross-sell, escalation handling, joint business plans |
| `pipeline-forecast-coach` | CRM hygiene, pipeline stages + coverage, sales velocity, weighted forecast, deal inspection, single-threaded-risk flags |
| `prospecting-outreach-strategist` | ICP + target lists, trigger events, multi-channel (email / call / LinkedIn) sequences, value-first messaging, objection handling |
| `trade-lane-compliance-advisor` | Incoterms 2020 selection + responsibility split, mode selection (FCL / LCL / air / express), customs & documentation basics, trade-lane intel |

### Skills (6)

`incoterms-2020`, `freight-pricing-mechanics`, `rfq-tender-response`, `qbr-account-planning`, `pipeline-forecasting`, `prospect-outreach` — veteran-level playbooks each agent consults on demand.

### Slash commands (6)

`/freight-forwarding-sales:build-freight-quote`, `:respond-to-rfq`, `:prep-qbr`, `:pipeline-review`, `:draft-prospect-outreach`, `:account-plan`.

### Knowledge bank (2)

- `freight-sales-decision-trees.md` — 4 Mermaid decision trees: **mode selection** (FCL/LCL/air/express), **quote-vs-qualify** (chase or decline an RFQ), **Incoterms selection**, **spot-vs-contract** rate strategy.
- `freight-sales-glossary.md` — the working vocabulary (Incoterms, surcharge codes, document set, charge points) so quotes and emails use the right terms.

### Runnable tool

`scripts/freight_calc.py` — a zero-dependency Python CLI:

```bash
# Air chargeable weight (IATA 1:6000 volumetric vs actual)
python3 scripts/freight_calc.py air --pieces 4 --dims 120x80x100 --weight 350

# Ocean LCL chargeable basis (CBM vs weight/measure ton)
python3 scripts/freight_calc.py ocean --dims 120x100x110 --weight 800

# Build an all-in sell price from a base rate + surcharges + margin
python3 scripts/freight_calc.py quote --base 1200 --surcharge BAF=180 --surcharge THC=210 --margin 12%
```

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project, or use the repo URL
/plugin install freight-forwarding-sales@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0` (inherited Team Lead, protocols, and structured-output contract).

## House stance

- **Quote all-in, never base-only.** A quote without its surcharge stack and validity date is a future dispute.
- **Reliability and visibility sell, not a 3% discount.** Lead with lane expertise and problem-solving; price is the last lever.
- **Margin discipline is a design constraint**, not a post-quote afterthought — every quote shows buy, sell, and margin.
- **Qualify before you quote.** Not every RFQ is winnable; chasing un-winnable bids is the silent killer of a sales week.
- **The CRM is the forecast.** A deal that isn't in the pipeline with a next step and a date doesn't exist.

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and routing rules.
