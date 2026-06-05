# Reach for Bayesian methods only with a written justification — frequentist is the spine

**Status:** Pattern
**Domain:** Bayesian / method selection
**Applies to:** `applied-statistics`

---

## Why this exists

Bayesian methods (PyMC, bambi) are powerful but operationally heavy: they require prior specification, MCMC sampling diagnostics (R-hat, effective sample size, divergences), and a stakeholder audience that may not understand posterior distributions. For most SMB consulting questions — "is this A/B winner real?", "what drives churn?", "is this metric moving?" — the frequentist methods (scipy, statsmodels, pingouin) answer the question, are faster to run, and are easier to communicate and defend. The reach for Bayesian is justified when the frequentist path genuinely can't serve: informative priors are the right way to incorporate known domain knowledge, or the question is inherently about updating a belief rather than a fixed-universe hypothesis test.

## How to apply

Before choosing a Bayesian approach, answer:

```markdown
## Bayesian justification (required before using PyMC/bambi)

1. What does the frequentist approach fail to provide here?
   [ ] Small n + informative prior is the right use case
   [ ] Full posterior distribution is needed (not just a point + CI)
   [ ] Sequential / adaptive design requires Bayesian updating
   [ ] None of the above — use frequentist

2. What prior will you use?
   [ ] Prior specified with a domain rationale (e.g., "conversion rate is typically 2-8%")
   [ ] Weakly informative (half-normal on scale parameters)
   [ ] Flat/improper — if yes, explain why the likelihood is sufficient

3. MCMC diagnostics checklist (required before trusting results):
   [ ] R-hat < 1.01 for all parameters
   [ ] Effective sample size > 400
   [ ] No divergences in NUTS sampler
   [ ] Trace plots visually converged
   [ ] Posterior predictive check run
```

**Do:**
- Run the full MCMC diagnostics — a Bayesian fit that hasn't been diagnosed is not a result.
- Report posteriors as distributions, not just posterior means — the distribution IS the result.
- Translate the posterior for a non-technical stakeholder: "There is a 92% probability the conversion rate under treatment is higher than under control."

**Don't:**
- Reach for PyMC/bambi because it "feels more sophisticated" when a t-test answers the question.
- Specify a flat prior when the likelihood is weak (small n) — flat priors with weak data produce posteriors dominated by the likelihood tails.
- Report Bayesian results without the MCMC diagnostics.

## Edge cases / when the rule does NOT apply

- Engagements explicitly scoped as "Bayesian analysis" (e.g., a client who has asked for a Bayesian update to a prior belief) are exempt from the justification requirement — the method is pre-selected. Still run the diagnostics.

## See also

- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — method-before-library discipline
- [`./check-assumptions-before-the-test.md`](./check-assumptions-before-the-test.md) — the assumption-gate rule that gates parametric methods, which Bayesian bypasses differently

## Provenance

Codifies applied-statistics CLAUDE.md §3 house opinion #8 ("Frequentist is the spine; Bayesian is the (justified) reach") and §3 house opinion #9 ("Don't over-tool a small engagement"). The justification checklist is derived from standard Bayesian workflow best practices (Gelman et al., "Bayesian Workflow", arXiv:2011.01808).

---

_Last reviewed: 2026-06-05 by `claude`_
