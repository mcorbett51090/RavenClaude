---
description: "Build a freight key-account growth plan — relationship/decision map, share-of-wallet vs whitespace, ranked growth plays with give-gets, risks (incumbency/single-thread/service debt), and a 12-month plan tied to the customer's calendar."
argument-hint: "[account + what you know, e.g. 'Globex, ~500 TEU/yr ocean only, 1 contact in procurement']"
---

# Build an account plan

You are running `/freight-forwarding-sales:account-plan`. Build a plan for the account the user described (`$ARGUMENTS`), using this plugin's `key-account-manager` discipline and the `qbr-account-planning` skill.

## Steps
1. **Account overview + supply-chain footprint** — what they move, origins/destinations, seasonality, volumes (flag real vs assumed).
2. **Relationship/decision map** — champion, economic buyer, ops users, blockers, and **coverage** (single-threaded = a named risk + a widen plan).
3. **Share-of-wallet vs whitespace** — what they buy from you vs elsewhere: modes, lanes, customs brokerage, warehousing, insurance, value-added services. The whitespace is the growth map.
4. **Rank growth plays** — each with the value, the give-get, the owner, and the trigger/timing. Loop `freight-rate-quoter` for any re-rate.
5. **Risks** — incumbency-challenge timing, single-thread, service debt, contract/renewal dates.
6. **12-month plan** — quarterly milestones tied to the customer's planning calendar.
7. Emit the plan in the Output Contract format + the Structured Output JSON block.

## Guardrails
- Whitespace is the cheapest growth — map it explicitly, don't sell only what they already buy.
- Multi-thread the relationship; a single contact is a P1 account risk.
- Every growth play has an owner and a give-get.
- Defend incumbency before a tender drops, not after.
