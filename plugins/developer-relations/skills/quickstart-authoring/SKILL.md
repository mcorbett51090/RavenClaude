---
name: quickstart-authoring
description: "Write a quickstart that minimizes time-to-first-success — one happy path, a declared time target, ruthless prerequisite-cutting, and CI tests against the real SDK so it never silently rots. Used by docs-and-samples-engineer (primary)."
---

# Skill: quickstart-authoring

**Purpose:** Produce a quickstart that gets a developer to their first real success as fast as
possible — and that can't silently rot. Used by `docs-and-samples-engineer` (primary).

## When to use

- Writing the getting-started for a new SDK/API/product
- Auditing an existing quickstart whose activation rate is low
- Cutting a quickstart's time-to-first-success

## The north-star metric

**Time-to-first-success (TTFS):** the wall-clock minutes from "landed on the quickstart" to
"ran something real and saw it work." Declare a target up front ("working in under 10 minutes")
and judge every change against it.

## The shape of a great quickstart

1. **State the outcome and the TTFS target first.** "In 10 minutes you'll send your first
   message and see the response." The developer knows the payoff and the cost.
2. **One happy path.** No branches, no "you could also…", no platform matrix up front. Options
   come *after* first success.
3. **Cut every prerequisite you can.** Each "first install X / get a key / configure Y" is a
   cliff. Provide a sandbox key, a one-line installer, a hosted try-it where possible.
4. **Every code block runs as written, in order.** No hidden steps, no `# ... configure this`.
   Copy-paste the whole thing top to bottom and it works.
5. **Show the success signal.** End on the concrete thing they'll see ("you should get back
   `{...}`") so they *know* it worked.
6. **Then, and only then, branch.** "Next: auth options / production setup / other languages."

## The non-negotiable: CI test the snippets

A quickstart that drifts from the real SDK is worse than none — it burns trust at the
highest-leverage moment. Extract the snippets and run them against the real SDK on every
release; drift fails the build. This is the single most important DX practice in this skill.

```
# Pattern: a CI job that runs the quickstart end-to-end
- extract code blocks from quickstart.md
- run them in a clean environment against the published SDK
- assert the success signal appears
- fail the build on any error  (docs drift == red build)
```

## Audit checklist (for an existing quickstart)

- [ ] Is TTFS declared and measured? Walk it with a timer.
- [ ] How many prerequisites before first success? Can any be cut/deferred/sandboxed?
- [ ] Does every block run copy-paste, in order, with no hidden steps?
- [ ] Is there a single happy path, or does it branch before first success?
- [ ] Are the snippets CI-tested against the real SDK?

## Output

A quickstart (or audit) with a declared TTFS target, one happy path, minimized prerequisites,
a visible success signal, and a CI-test plan. See [`../../templates/quickstart-template.md`](../../templates/quickstart-template.md).
