# Harness Spectate — Multi-model gap analysis log

**Plan:** `BUILD-PLAN.md` + `design-system-spec.md` + `SURFACE-DECISION.md`  
**Rule:** Iterate gap analysis with a *different* model each pass; close gaps; continue until **3 consecutive** passes return `NO_GAPS`.

| Pass | Model | Scope | Verdict | Closed in |
|---|---|---|---|---|
| Surface A | claude-opus-5-5-high (product-strategist) | Surface only | LOCKED | SURFACE-DECISION |
| Surface B | gpt-5.6-sol-high (ux-designer) | Surface only | LOCKED | SURFACE-DECISION |
| Surface C | grok-4.7-high (web-architect) | Surface only | LOCKED | SURFACE-DECISION |
| Plan G1 | gpt-5.6-sol-high (code-reviewer) | Full plan | GAPS_FOUND (15) | closed |
| Plan G2 | claude-opus-5-5-high (code-reviewer) | Full after G1 | GAPS_FOUND (20) | closed |
| Plan G3 | grok-4.7-high (code-reviewer) | Full after G2 | GAPS_FOUND (12) | closed |
| Plan G4 | gpt-5.6-terra-high (code-reviewer) | Full after G3 | GAPS_FOUND (5) | closed |
| Plan G5 | TBD (≠ prior plan models) | Full after G4 | — | — |

## Surface lock (done)

> Spectate is one loopback page. `rc spectate` and `/spectate` open it on the current session. The Activity tab is a link, not a home. IDE panels, ACP, and a TUI do not get their own UI.

## Plan gap Pass G4 — CLOSED

Agent: [Plan G4 gap analysis](bc-7fe0fa51-f2b6-506f-bf26-409fab4ee5aa). Five gaps closed: Spectate loopback peer policy on LAN bind; one harness per stream + per-harness demo dirs; session-summary reducer; mkdir before log redirect; SURFACE upgrade-coexistence second-port exception.

## Next

1. ~~Close G1–G4.~~  
2. Re-run with a model different from G1–G4.  
3. Repeat until 3 consecutive `NO_GAPS`.  
4. Implement v0.1.
