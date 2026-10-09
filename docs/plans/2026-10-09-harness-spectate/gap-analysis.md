# Harness Spectate — Multi-model gap analysis log

**Plan:** `BUILD-PLAN.md` + `design-system-spec.md` + `SURFACE-DECISION.md`  
**Rule:** Iterate gap analysis with a *different* model each pass; close gaps; continue until **3 consecutive** passes return `NO_GAPS`.

| Pass | Model | Scope | Verdict | Closed in |
|---|---|---|---|---|
| Surface A | claude-opus-5-5-high (product-strategist) | Surface only | LOCKED (agree) | SURFACE-DECISION + BUILD-PLAN |
| Surface B | gpt-5.6-sol-high (ux-designer) | Surface only | LOCKED (agree; IDE panel deferred by C) | SURFACE-DECISION |
| Surface C | grok-4.7-high (web-architect) | Surface only | LOCKED | SURFACE-DECISION + BUILD-PLAN Task 3b |
| Plan G1 | gpt-5.6-sol-high (code-reviewer) | Full BUILD-PLAN | GAPS_FOUND (15) | BUILD-PLAN + design-system-spec |
| Plan G2 | claude-opus-5-5-high (code-reviewer) | Full BUILD-PLAN after G1 | GAPS_FOUND (20) | BUILD-PLAN + design-system-spec + SURFACE §3 |
| Plan G3 | TBD (≠ G1/G2 models) | Full plan after G2 closes | — | — |

## Surface lock (done)

> Spectate is one loopback page. `rc spectate` and `/spectate` open it on the current session. The Activity tab is a link, not a home. IDE panels, ACP, and a TUI do not get their own UI.

## Plan gap Pass G1 — CLOSED

Agent: [Gap analysis pass 1](bc-7d73d562-a471-55e4-a837-070c83d5c280). Fifteen gaps closed (capability unknown, nested scrub, reducer, correlation, path, cursor, `/spectate` map, source UI, denied-harness, Payload override, a11y, filter/legend, headers, tests, no dashboard.html commit).

## Plan gap Pass G2 — CLOSED

Agent: [Plan G2 gap analysis](bc-0373c006-2c42-5361-8ebc-b0a3dad88927). Twenty gaps closed into plan + design + SURFACE:

| ID | Severity | Title |
|---|---|---|
| G2-1 | blocker | Gate 242 inventory + commit concepts-doc |
| G2-2 | blocker | `--no-reclaim` + attach probe |
| G2-3 | major | `--open-path` + detach `rc spectate` |
| G2-4 | blocker | Serve `/spectate` (not 302); SURFACE amended |
| G2-5 | major | `_read_spectate_*` parity + MH-33 |
| G2-6 | major | CLAUDE_SESSION_ID honesty + harness filter |
| G2-7 | blocker | available seed map + deny.by |
| G2-8 | major | source/connection axes + unterminated |
| G2-9 | major | rail multi-harness; columns = agent_id |
| G2-10 | major | target derivation + value scrub |
| G2-11 | major | visibility-gated polling |
| G2-12 | major | corr_id = tool_use_id |
| G2-13 | major | light-theme contrast tokens |
| G2-14 | major | design-system relationship recorded |
| G2-15 | major | stub-DOM gate + manual a11y |
| G2-16 | major | UI polls nodes only; bounds |
| G2-17 | minor | explicit Content-Type |
| G2-18 | minor | event-file symlink refuse |
| G2-19 | minor | follow=latest pin semantics |
| G2-20 | minor | CSP, kind split, Gate 142 plugin, glyph/handoff |

## Next

1. ~~Close G1 / G2.~~  
2. Re-run plan gap analysis with a model **different from** G1 (`gpt-5.6-sol-high`) and G2 (`claude-opus-5-5-high`).  
3. Repeat until 3 consecutive `NO_GAPS`.  
4. Implement v0.1.
