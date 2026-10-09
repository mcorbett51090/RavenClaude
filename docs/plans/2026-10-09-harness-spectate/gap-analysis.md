# Harness Spectate — Multi-model gap analysis log

**Plan:** `BUILD-PLAN.md` + `design-system-spec.md` + `SURFACE-DECISION.md`  
**Rule:** Iterate until **3 consecutive** `NO_GAPS` on different models.

| Pass | Model | Verdict | Closed |
|---|---|---|---|
| Surface A/B/C | opus / gpt-5.6 / grok | LOCKED | SURFACE-DECISION |
| Plan G1 | gpt-5.6-sol-high | GAPS_FOUND (15) | closed |
| Plan G2 | claude-opus-5-5-high | GAPS_FOUND (20) | closed |
| Plan G3 | grok-4.7-high | GAPS_FOUND (12) | closed |
| Plan G4 | gpt-5.6-terra-high | GAPS_FOUND (5) | closed |
| Plan G5 | claude-sonnet-5-5-high | GAPS_FOUND (13) | closed |
| Plan G6 | TBD (≠ G1–G5 models) | — | — |

## Surface lock

> Spectate is one loopback page. `rc spectate` and `/spectate` open it on the current session. The Activity tab is a link, not a home.

## G5 — CLOSED

Agent: [Plan G5](bc-d1f1b3fb-1933-5f2c-91c6-a1a9a5c5dd66). Thirteen gaps closed in BUILD-PLAN § G5 closes + design-system token fixes (version rebase, bind helper/span, peer_ok, open ownership, input validation, probe range, kind→step, nodes shape, deny join, read cache, demo first-sight, test homes, available≠teal).

## Next

1. Plan G6 with a new model.  
2. Repeat until 3 consecutive `NO_GAPS`.  
3. Implement v0.1.
