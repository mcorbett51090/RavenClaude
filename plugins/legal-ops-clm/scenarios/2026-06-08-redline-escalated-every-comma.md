---
scenario_id: 2026-06-08-redline-escalated-every-comma
contributed_at: 2026-06-08
plugin: legal-ops-clm
product: generic
product_version: "unknown"
scope: likely-general
tags: [redline, clause-library, material-deviation, risk-tier, approval-routing, key-clauses]
confidence: high
reviewed: false
---

> Not legal advice — an operational field note. A qualified lawyer owned the legal judgement throughout.

## Problem

A legal team's first clause-library rollout produced redline summaries that flagged everything: a notices-address change, a defined-term capitalization fix, and a struck limitation-of-liability cap all came back as "DEVIATION — review." Business teams got a 40-line flag list per contract with no tiers, couldn't tell which lines mattered, and started rubber-stamping the whole list to keep deals moving. Two months in, a counterparty-favorable indemnity expansion sailed through inside one of those lists because it looked like all the rest. The review existed but had stopped discriminating.

## Constraints context

- ~30 contracts/month going through the new library; reviewers were paralegals, not lawyers.
- The library had standard positions for the key clauses but no fallback or walk-away lines — so the tool treated every change as binary "matches / doesn't match standard."
- "Flags raised" was being reported as a productivity metric, which rewarded over-flagging.

## Attempts

- Tried: telling reviewers to "use judgement" on which flags to escalate. Failed — without encoded fallback bounds, judgement varied per reviewer and the inconsistency was its own risk; a non-lawyer guessing materiality is the thing the library was supposed to remove.
- Tried: only flagging the five key clauses and suppressing everything else. Failed — it missed a material payment-terms change that wasn't on the key-clause list; "key clause" and "material" overlap but aren't identical.
- Tried: encoding standard / fallback / walk-away per clause, then tiering each flag — within-fallback (note + named approver), beyond-fallback (escalate to a named approver), walk-away (stop, lawyer decides) — and routing each tier to a specific approver. This worked.

## Resolution

Tiering collapsed the 40-line lists to a handful of real flags, each with a tier and a named approver, and the noise dropped into a "noted, not escalated" appendix. The struck-cap and indemnity-expansion cases now surface as walk-away/beyond-fallback at the top, not buried. The reported metric moved from "flags raised" to "material flags by tier + approver turnaround," which stopped rewarding over-flagging. The lawyers set every bound once; the paralegals applied them consistently.

## Lesson

Flag material deviations, not every comma — surface what changes risk and note the rest. Every flag needs a risk tier (within-fallback / beyond-fallback / walk-away) and a named approver, and the standard/fallback/walk-away bounds must be decided once by a lawyer so a non-lawyer can apply them. Review the key clauses first and hardest, but don't assume "material" stops at the key-clause list. Not legal advice — the lawyers owned every materiality bound.
