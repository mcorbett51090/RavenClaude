# Expensive-test front-loading — when a test costs a human action or a long run, validate exhaustively first

**Status:** Pattern
**Domain:** Agent behavior / Verification discipline / Cost & latency

**Applies to:** `ravenclaude-core` (every agent); the worked instrument is `power-platform/dataverse-payload-preflight`.

---

## Why this exists

The default failure loop is **hypothesize → act → fail → fix one thing → act again**. That loop is
cheap when a test is cheap (a local `bash -n`, a unit test). It is **ruinously expensive when each
test costs a scarce resource** — a **human re-fire**, a **long run**, a **paid API turn**, a
**deploy**. There, every "act again" spends the scarce thing to discover *one* more defect, and a
five-defect payload becomes five round-trips.

The fix is to **invert the loop**: when the *test* is expensive, spend cheap static-validation tokens
to make each expensive test exercise a **fully-validated** change — so the scarce resource is spent
once on a payload you already know is complete, not N times discovering defects one at a time.

> **Worked case (Contoso extraction pipeline, 2026-06-24).** A `Create_BalanceSheet` failed **four times
> in a row, each on a different field** — empty lookup bind `/accounts()` → invalid `sourcechannel`
> option value → undeclared `extractionrun` columns → "Owner was not provided" — every failure costing
> a human re-fire. A single metadata-vs-payload sweep would have surfaced **all four at once**. When a
> comprehensive audit was finally dispatched, it found every remaining issue in one pass. The 5-way
> parallel fan-out that ultimately unblocked the session is the same principle: validate everything in
> one sweep instead of crawling a serial fix-and-retry.

## The rule

Before spending an **expensive test**, ask: *what is the scarce resource this test consumes, and have
I validated everything that this test could surface, in one pass?*

1. **Name the scarce resource.** A human re-fire / a multi-minute run / a billed turn / an irreversible
   deploy. If the test is cheap and reversible, this rule does not apply — just run it.
2. **Front-load all the static validation the expensive test would otherwise discover serially.** Pull
   the real source of truth (live schema, the proven reference, the actual error envelope) and check
   **every** dimension at once — not the first one that fails.
3. **One expensive test per fully-validated change.** Never fix-one-field-and-retrigger when each
   trigger costs the scarce resource.
4. **Prefer a tool over a reminder.** A deterministic validator (run it) beats "remember to validate"
   (skipped). For Dataverse create/update that tool is
   [`power-platform/dataverse-payload-preflight`](../../power-platform/skills/dataverse-payload-preflight/SKILL.md)
   — `{entity, payload}` → *all* field-level violations vs live metadata in one shot.

## Composition

This is the cost-side complement of the verification protocols: the [Capability Grounding /
"Verify the load-bearing assumption before a high-impact activity" / "Verify a reference before you
mirror it"](../CLAUDE.md) clauses say *read the live source of truth instead of assuming*; this says
**when reading-then-testing is expensive, read EXHAUSTIVELY before the test.** The retro's own finding:
those clauses already existed and were *non-applied* — which is why the highest-leverage fix is a
**deterministic tool + an advisory hook nudge**, not another prose rule. This best-practice records the
principle; the validator skill + the `nudge-dataverse-preflight.sh` PreToolUse hook are the teeth.

## Anti-patterns
- Fixing one field and asking the user to re-fire, then hitting the next field. (Contoso #2/#3.)
- Designing *around* a claimed limitation without one live capability test. (Contoso #4 — a policy/memory
  doc is a hypothesis, not a fact; test the privilege live.)
- Reasoning about a mechanism repeatedly when a proven reference exists to diff against exhaustively.
  (Contoso #1 — diff the working temp flow across host + params + **input schema/type** before variant N+1.)
