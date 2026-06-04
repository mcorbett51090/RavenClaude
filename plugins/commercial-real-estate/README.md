# Commercial Real Estate — Claude Code plugin

An acquisitions-and-asset-management team for a CRE owner, operator, or advisor — it underwrites a deal to in-place NOI, prices the cap-rate-vs-Treasury spread, reads the bifurcated vacancy, decomposes net effective rent, and stress-tests the debt and refinance wall before a board sees the IC memo.

Part of the **RavenClaude** marketplace. Inherits the domain-neutral
[`ravenclaude-core`](../ravenclaude-core/) protocols (Capability Grounding,
Structured Output, the comfort-posture permission model) and adds
commercial real estate depth on top.

## What it does

Diagnoses whether a deal pencils on real income (not pro-forma), separates the going-in cap rate from the hold-period IRR, exposes the risk premium hiding in the cap-rate-minus-Treasury spread, and reads operating expenses and lease economics as first-class underwriting inputs. Produces IC memos, underwriting models, and asset-plan deliverables an owner acts on.

## Agents

- **`cre-engagement-lead`** — The engagement — scoping a mandate, framing the IC memo, routing to the right specialist, synthesizing an investment recommendation.
- **`acquisitions-underwriter`** — The underwriting model — in-place NOI, cap-rate/IRR, the spread, lease economics, opex, debt sizing, and sensitivity tables.
- **`asset-property-manager`** — The owned asset — the business plan, leasing strategy, opex/recovery management, capex, tenant retention, and NOI growth.
- **`cre-market-analyst`** — The outside view — submarket fundamentals, cap-rate and vacancy trends, rent comps, demand drivers, and competitive supply.

## Skills

- **`underwrite-to-in-place-noi`** — Build a CRE base case on contractual in-place income before any pro-forma step-up — separating real income from assumed growth so the return rests on something sourced. Reach for this when a deal is being sold on stabilized rents.
- **`price-the-cap-rate-spread`** — Frame a cap rate as a risk premium over the 10-yr Treasury, not an absolute level, so a 'compression' is read correctly. Reach for this whenever a cap rate enters a memo.
- **`decompose-net-effective-rent`** — Convert a face rent to net effective by netting TI, free rent, and leasing commissions, so comps and underwriting use the rent the landlord actually earns. Reach for this on any rent comp.
- **`stress-the-debt-and-refi`** — Size the debt, schedule DSCR through the hold, and surface the refinance year and the rate at which the deal breaks. Reach for this before any levered return is quoted.
- **`build-the-asset-plan`** — Sequence lease rollovers, recovery improvements, and capex against a quarterly NOI target so a held asset tracks (or beats) its acquisition underwriting. Reach for this once an asset is owned.

## Slash commands

- **`/commercial-real-estate:underwrite-deal`** — Underwrite a CRE deal
- **`/commercial-real-estate:build-asset-plan`** — Build an asset business plan
- **`/commercial-real-estate:market-read`** — CRE submarket read

## Knowledge bank

4 research-grounded reference docs under [`knowledge/`](knowledge/) — figures carry a source + date, advisory numbers are marked `[ESTIMATE]`, and anything from training knowledge is marked `[unverified — training knowledge]`.

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install commercial-real-estate@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Scope & disclaimers

This plugin produces **analysis and operational deliverables**, not licensed
professional advice. It is not a broker, appraiser, or lender, and gives no investment, legal, or tax advice — it flags where those questions live and routes them. It stores no PII in deliverables — see
[`CLAUDE.md`](CLAUDE.md) §3.
