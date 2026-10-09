# Harness Spectate — Multi-model gap analysis log

**Plan:** `BUILD-PLAN.md` + `design-system-spec.md` + `SURFACE-DECISION.md`  
**Rule:** Iterate gap analysis with a *different* model each pass; close gaps; continue until **3 consecutive** passes return `NO_GAPS`.

| Pass | Model | Scope | Verdict | Closed in |
|---|---|---|---|---|
| Surface A | claude-opus-5-5-high (product-strategist) | Surface only | LOCKED (agree) | SURFACE-DECISION + BUILD-PLAN |
| Surface B | gpt-5.6-sol-high (ux-designer) | Surface only | LOCKED (agree; IDE panel deferred by C) | SURFACE-DECISION |
| Surface C | grok-4.7-high (web-architect) | Surface only | LOCKED | SURFACE-DECISION + BUILD-PLAN Task 3b |
| Plan G1 | gpt-5.6-sol-high (code-reviewer) | Full BUILD-PLAN | GAPS_FOUND (15) | BUILD-PLAN + design-system-spec (2026-10-09) |
| Plan G2 | TBD (≠ gpt-5.6-sol-high) | Full BUILD-PLAN after G1 closes | — | — |

## Surface lock (done)

> Spectate is one loopback page. `rc spectate` and `/spectate` open it on the current session. The Activity tab is a link, not a home. IDE panels, ACP, and a TUI do not get their own UI.

## Plan gap Pass G1 — CLOSED

Agent: [Gap analysis pass 1](bc-7d73d562-a471-55e4-a837-070c83d5c280) (code-reviewer). All 15 closed into BUILD-PLAN (+ design-system-spec for G1-9/G1-10):

| ID | Severity | Title | Close |
|---|---|---|---|
| G1-1 | blocker | Undocumented → unavailable-harness | Capability states `supported\|partial\|unsupported\|unknown`; only `unsupported` → `unavailable-harness` |
| G1-2 | blocker | Nested schema privacy smuggling | Nested `additionalProperties: false` + recursive sensitive-key scrub + fixtures |
| G1-3 | blocker | Reducer transition/conflict missing | Full reducer table + precedence + sticky terminals |
| G1-4 | blocker | Correlation identities | Composite uniqueness + `corr_id`; no heuristic deny join |
| G1-5 | blocker | Session-ID path traversal | Reject dots/separators; resolve under runs root; tests |
| G1-6 | major | Cursor/stream/sessions bounds | Snapshot cursor, partial lines, truncate, paginated sessions |
| G1-7 | blocker | Asset URL root vs plugin | Guarded `/spectate` maps to plugin assets on both servers |
| G1-8 | blocker | Observe-only / disconnected UI | Source-mode state machine + badges |
| G1-9 | major | `denied-harness` design incomplete | First-class tokens + hexagon in design-system-spec |
| G1-10 | blocker | Payload vs no-raw-args | Wireframe override; scrubbed fields only |
| G1-11 | major | Keyboard / a11y acceptance | Interaction contracts + breakpoint checks |
| G1-12 | minor | Filter / legend / panel ratios | localStorage axes + safe defaults |
| G1-13 | major | Cache-Control / CSP deferred | Required in v0.1 on `/__spectate` + spectate assets |
| G1-14 | major | Test / gate coverage holes | Behavioral parity, unwired canary, full audit-gates |
| G1-15 | major | Commit generated dashboard.html | Generator source only; no committed regen in feature PR |

## Next

1. ~~Close G1-* into BUILD-PLAN + design-system-spec.~~  
2. Re-run plan gap analysis with a *different* model than G1 (`gpt-5.6-sol-high`).  
3. Repeat until 3 consecutive `NO_GAPS`.  
4. Implement v0.1.
