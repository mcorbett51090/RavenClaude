# Orchestrator hybrid — Phase −1 demand validation (findings)

> **Gate:** Phase −1 / Gate −1.1 of `docs/orchestrator-hybrid-BUILD-plan-2026-05-29.md`.
> **Run:** 2026-05-30. **Verdict:** ⛔ **CANNOT CLEAR IN THIS ENVIRONMENT → PARK** (pending Matt's session data).
> **No build code is written under Phase −1** (per the plan).

## What the gate requires

> Read the `Copilot bridge in active use` memory + the Contoso session logs (or whatever active
> consumer repo is the truth-source). Enumerate the **last 20 Copilot-CLI sessions**. For each, mark
> "would have benefited from Team Lead fan-out" Y/N. **Pass: ≥3 Y → proceed; else PARK.**

The plan assigns this gate **Owner: Matt** because the truth-source is real consumer usage, which
lives outside this marketplace repo.

## What was checked this session (and why it's insufficient)

| Source | Result |
|---|---|
| `docs/session-log.md` | Marketplace-development sessions (building the plugins), **not** Copilot-CLI fan-out usage. Not the truth-source. |
| User-scoped memory (`~/.claude/projects/*/memory/`) | No `Copilot bridge in active use` memory present in this container. |
| `.ravenclaude/runs/` | Only this session's `runaway/` counters — no multi-seat / fan-out run artifacts. |
| Contoso session logs / active consumer repo | **Not accessible** from this ephemeral environment. |

Conclusion: the data needed to enumerate 20 real Copilot-CLI sessions and mark fan-out benefit is
**not available here**. Producing a 20-row table would require fabricating sessions — which the
accuracy discipline forbids. The gate therefore cannot be honestly cleared in this environment.

## Verdict

Per the plan's fail action — **"PARK plan; revisit only when a real engagement surfaces the need"** —
the orchestrator hybrid is **PARKED**. It is *not* a "no": it is "not yet validated."

## To clear the gate (one of)

1. **Matt fills the table below** from the Contoso / active-consumer Copilot-CLI history (last 20
   sessions). If ≥3 are "Y", the gate passes and Phase 0 (feasibility spike) begins.
2. **Point me at the session logs** (paste, or a path I can read) and I'll enumerate + score them
   here, then build if it passes.

## The 20-row table (to be completed from real session history)

| # | Session (date / id) | Task summary | Would Team-Lead fan-out have helped? (Y/N) | One-line justification |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |
| 6 |  |  |  |  |
| 7 |  |  |  |  |
| 8 |  |  |  |  |
| 9 |  |  |  |  |
| 10 |  |  |  |  |
| 11 |  |  |  |  |
| 12 |  |  |  |  |
| 13 |  |  |  |  |
| 14 |  |  |  |  |
| 15 |  |  |  |  |
| 16 |  |  |  |  |
| 17 |  |  |  |  |
| 18 |  |  |  |  |
| 19 |  |  |  |  |
| 20 |  |  |  |  |

**Y count:** ___ / 20 → **≥3 = proceed to Phase 0; <3 = stay parked.**
