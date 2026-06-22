---
name: sample-app-design
description: "Spec a sample app or SDK quickstart that demonstrates the real value path as production-grade, runnable code — it runs from a clean checkout, handles errors, pins versions, and has no hardcoded secrets. Use when designing or reviewing sample code that developers will copy verbatim."
---

# Skill: Sample-app design

Design sample code that a developer can copy into production without learning a bad
habit. Sample code is production code — it's copied verbatim into real codebases.

## When to use

- You need a sample app or SDK quickstart to show off the product's value path.
- A snippet/sample is about to be published and needs a production-grade review.
- A toy example is setting developers up for a cliff when they hit the hard parts.

## Procedure

1. **Pick the value path, not a toy.** The sample demonstrates the real reason a
   developer would use the product — including the parts that are genuinely hard.
   Hiding the hard parts is a future support ticket.
2. **Scope it to runnable.** It compiles and runs from a clean checkout with a
   documented, minimal setup. If it doesn't run from clean, it isn't done.
3. **Handle errors.** Show the real failure modes (rate limits, auth expiry, bad
   input) and the correct handling — not a happy-path-only snippet that breaks the
   moment reality intrudes.
4. **Secure by default.** **No hardcoded secrets** — env vars or a secret manager,
   never a literal key. Teach the secure pattern, because everyone who copies it
   inherits it. Route auth/secret deep dives to `security-engineering`.
5. **Pin versions** so the sample doesn't rot when a dependency ships a breaking
   change.
6. **Mark any product friction** for `developer-advocate` to file — don't bury it in
   prose. Capture the spec in the
   [`sample-app-spec`](../../templates/sample-app-spec.md) template.

## Output

A sample-app spec (value path, runnable scope, error handling, secure patterns,
pinned versions) ready for the content-engineer to build.

## Anti-patterns (the hook flags these)

- A sample with a **hardcoded secret/API key** (teaches a vulnerability at scale).
- A sample that **swallows errors** (empty catch / ignored failure).
- A toy that hides the hard parts and sets up a cliff.
