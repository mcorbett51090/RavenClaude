---
description: Design a sample app or SDK quickstart as production-grade, runnable code — demonstrate the real value path, handle real errors, pin versions, and use no hardcoded secrets (sample code is copied verbatim into real codebases).
argument-hint: "[the product/SDK + value path, e.g. 'a webhook-processing sample for our events SDK']"
---

# Design sample app

You are running `/developer-relations:design-sample-app`. Spec the sample for
`$ARGUMENTS` using the `devrel-content-engineer` discipline: sample code is
production code.

## Steps

1. **Pick the value path, not a toy** — the real reason a developer would use the
   product, including the hard parts.
2. **Scope it to run from a clean checkout** with documented, minimal setup.
3. **Handle real errors** — rate limits, auth expiry, bad input.
4. **Secure by default** — **no hardcoded secrets** (env vars / secret manager),
   teach the secure pattern; route deep auth questions to `security-engineering`.
5. **Pin dependency versions** so the sample doesn't rot.
6. **Mark any product friction** for `developer-advocate` to file, and capture the
   spec in the [`sample-app-spec`](../templates/sample-app-spec.md) template.

## Guardrails

- A sample with a hardcoded API key or an empty `catch {}` is not done.
- If it doesn't compile and run from clean, it isn't done.
