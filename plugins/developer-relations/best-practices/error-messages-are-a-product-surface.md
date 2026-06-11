# Error messages are a product surface

**Status:** Pattern.

**Rule:** The errors a developer hits in the first hour are a product surface, not log noise. Each
critical-path error message must say what went wrong, why, and the next action. A cryptic error at
first-success is an activation lost.

## Why

During onboarding, a developer's relationship with the product is mediated almost entirely by what
happens when something goes wrong — and something always goes wrong. A clear, actionable error keeps
the developer on the path: they read it, fix it, and continue. A cryptic stack trace or generic code
ends the session and often the evaluation. Error quality is therefore an activation lever as direct
as the quickstart itself, and it's frequently the difference at the `first_call → first_success` step
where funnels leak most.

## What it looks like in practice

- The 3–5 most likely first-run errors (bad key, missing param, wrong region, rate limit, version
  mismatch) are audited against the what/why/next rubric.
- Error messages link to the relevant fix in the docs where possible.
- Error-driven support tickets and community questions are treated as error-message defects to fix at
  the source.

## Anti-pattern

Treating error text as an engineering afterthought ("it returns a 400, that's correct") while the
developer who hit it has no idea what to do next. Correct-but-cryptic is still an activation failure.
