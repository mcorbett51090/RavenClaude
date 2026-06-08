---
name: rc-deep-research
description: "Deep research harness — fan-out web searches, fetch sources, adversarially verify claims, synthesize a cited report. Includes an inline substrate adapter that reads .ravenclaude/run-config.json once at startup; when enabled:false (the default) all agent() calls are byte-identical to the pre-port baseline (Gate 51)."
---

# Skill: rc-deep-research

> **This is a workflow TEMPLATE, not a script to execute verbatim.** The bundled
> [`rc-deep-research.js`](./rc-deep-research.js) is a [dynamic-workflow](../../knowledge/dynamic-workflows.md)
> harness — a reference shape. Claude **adapts** it to the task at hand (it is intelligent
> enough to write the tailored harness on the fly); it does **not** run the file byte-for-byte.
> Treat the `.js` the way you'd treat a worked example: read it for the orchestration shape,
> then produce the version this task actually needs.

## What it does

A **fan-out-and-synthesize + adversarial-verification** research harness. Given a research
question, it:

1. **Scope** — decomposes the question into ~5 distinct search angles.
2. **Search** — runs one `WebSearch` agent per angle in parallel.
3. **Fetch** — URL-dedups, fetches the top sources, extracts *falsifiable* claims.
4. **Verify** — adversarially checks each claim with a separate agent (votes weighted by
   source quality), so the verifier never saw the work it judges (defeats self-preferential bias).
5. **Synthesize** — merges semantic duplicates, ranks by confidence, and emits a **cited** report.

This is the same pattern the [`/forge`](../forge-pipeline/SKILL.md) pipeline and the Researcher
meta-skill reach for; bundling it as a skill means a consumer who installs `ravenclaude-core`
gets a runnable `/rc-deep-research` (or invokes it via the `ultracode` keyword) without copying
files out of the marketplace.

## Substrate adapter (consumer-safe by default)

The harness carries an inline adapter that reads `.ravenclaude/run-config.json` **once at startup**
for per-phase model-tier / reasoning routing. **It is disabled and safe when that file is absent**
— with no `run-config.json` (or `enabled:false`, the default) `adapterOpts()` returns `{}` on every
call, so every `agent()` invocation is byte-identical to the unconfigured baseline (Gate 51 invariant).
A consumer who never creates the file pays nothing and sees the plain harness.

## Runtime facts (re-verify at use — research-preview feature)

- Dynamic workflows: Claude Code v2.1.154+, all paid plans. Saved under `.claude/skills` /
  `.claude/workflows`; invoked as a `/<name>` command or via the `ultracode` keyword.
- Caps: ≤16 concurrent agents, 1,000 total per run, no mid-run user input, resumable in-session.
- The script coordinates agents; it does **not** touch the filesystem or shell — the agents do the IO.

Authoritative guidance + the orchestration-shape decision aid:
[`knowledge/dynamic-workflows.md`](../../knowledge/dynamic-workflows.md).
