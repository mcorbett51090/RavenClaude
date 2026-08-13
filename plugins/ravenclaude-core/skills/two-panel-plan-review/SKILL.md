---
name: two-panel-plan-review
description: "Two fresh-independent expert panels review a strategic plan, fill its gaps, author a tactical build plan, then a different panel cold-reviews the build plan and emits P0/P1 recommendations. Includes an upfront advisory routing analysis recommending Ultraplan (cloud) vs. local for the task."
---

# Skill: two-panel-plan-review

> **This is a workflow TEMPLATE, not a script to execute verbatim.** The bundled
> [`two-panel-plan-review.js`](./two-panel-plan-review.js) is a
> [dynamic-workflow](../../knowledge/dynamic-workflows.md) harness — a reference shape.
> Claude **adapts** it to the task at hand; it does **not** run the file byte-for-byte.
> Read the `.js` for the orchestration shape (panel lenses, severity rubric, the Args
> contract near the top), then produce the version this task actually needs.

## What it does

A **fan-out-and-synthesize + adversarial-verification** plan-review harness. Given a strategic
plan (a "what/why" doc), it:

1. **Route** — one advisory agent weighs plan size/scope, web-research need, and privacy to
   recommend **Ultraplan (cloud)** vs. **local** execution.
2. **Panel 1** — a fresh expert panel (default lenses: architect / security / ops /
   devil's-advocate) stress-tests the strategic plan.
3. **Synthesize 1** — gap-fills the plan body and authors a tactical **build plan** (a "how" doc).
4. **Panel 2** — a *different*, fresh panel (default: tester-QA / project-manager /
   deep-researcher / prompt-engineer) **cold-reviews** the build plan — independent context, so
   it never saw Panel 1's reasoning.
5. **Synthesize 2** — appends a **P0/P1 recommendations** section to the build plan.

The two panels are deliberately independent (different lenses, fresh context) so the build-plan
review can't inherit the strategic-plan panel's blind spots. Its lens / severity / routing rubric
lives **here**, in this workflow's own consts, and is **not** shared with the
[`/forge`](../forge-pipeline/SKILL.md) pipeline — the two have different input contracts (this one
reviews a *pre-written* plan with a specialist panel; FORGE turns a *raw idea* into a plan), so the
rubric deliberately does not transfer. `[corrected 2026-07-15 — the prior "shares its rubric with
/forge" claim was false: these consts are module-private and FORGE carries none of them. See
forge-pipeline's provenance reference for the full ruling.]` Bundling it as a skill
means a consumer who installs `ravenclaude-core` gets a runnable `/two-panel-plan-review` (or
invokes it via the `ultracode` keyword) without copying files out of the marketplace.

## Args contract

The harness reads a structured `args` object — see the **Args contract** comment block near the
top of [`two-panel-plan-review.js`](./two-panel-plan-review.js) for the required
(`inputPlanPath`, `outputBuildPlanPath`, `contextSummary`) and optional (panel lenses, severity
rubric, extra axes) fields, each with a baked-in default.

## Runtime facts (re-verify at use — research-preview feature)

- Dynamic workflows: Claude Code v2.1.154+, all paid plans. Saved under `.claude/skills` /
  `.claude/workflows`; invoked as a `/<name>` command or via the `ultracode` keyword.
- Caps: ≤16 concurrent agents, 1,000 total per run, no mid-run user input, resumable in-session.
- The script coordinates agents; it does **not** touch the filesystem or shell — the agents do the IO.

Authoritative guidance + the orchestration-shape decision aid:
[`knowledge/dynamic-workflows.md`](../../knowledge/dynamic-workflows.md).
