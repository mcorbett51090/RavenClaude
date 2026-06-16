# Time-to-first-success is the activation metric

**Status:** Absolute rule
**Domain:** Developer experience / activation
**Applies to:** `developer-relations`

---

## Why this exists

A developer decides whether your product is worth their time in the first session. The metric
that captures that decision is **time-to-first-success (TTFS)** — the wall-clock minutes from
"landed on the quickstart" to "ran something real and saw it work." Every minute and every
prerequisite before that moment is a cliff a developer can fall off, and most do silently. A
quickstart with no declared TTFS target is optimized for nothing; teams polish prose while the
real leak — a setup step that takes 40 minutes — goes unmeasured.

## How to apply

1. Declare the target at the top of every quickstart: "working in under 10 minutes."
2. Walk the quickstart with a timer (or estimate per step) to get the real number.
3. Judge every quickstart change by whether it shortens TTFS.

**Do:**
- State the outcome and the TTFS target before the first step.
- Cut, defer, or sandbox every prerequisite you can.
- Measure TTFS the way a brand-new developer would experience it, not the way the author does.

**Don't:**
- Ship a quickstart with no success target.
- Bury the activation event behind account setup, key provisioning, and config before first success.
- Treat "the docs read well" as a substitute for "a developer got working fast."

## Edge cases / when the rule does NOT apply

- A product whose genuine value *requires* substantial setup (e.g. on-prem infra) can't hit a
  10-minute TTFS — but it should still declare an honest target and a hosted/sandbox fast-path.
- Deep reference docs aren't quickstarts and aren't held to TTFS — that's `technical-writing-docs`.

## See also

- [`../skills/quickstart-authoring/SKILL.md`](../skills/quickstart-authoring/SKILL.md)
- [`../agents/docs-and-samples-engineer.md`](../agents/docs-and-samples-engineer.md)

## Provenance

Codifies house opinion #1 ("Time-to-first-success is the north star of activation") in
[`../CLAUDE.md`](../CLAUDE.md), and the `docs-and-samples-engineer` agent's mission. The
no-TTFS-target case is the first mechanical check in the plugin's advisory hook.

---

_Last reviewed: 2026-06-16 by `claude`_
