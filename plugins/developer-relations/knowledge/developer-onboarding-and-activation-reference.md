# Developer onboarding & activation — reference

Deep reference for the `docs-and-dx-engineer` and the onboarding-funnel skill. Companion to
[`devrel-decision-trees.md`](devrel-decision-trees.md).

---

## The activation funnel, defined

| Event | Definition | Instrument it as |
|---|---|---|
| `sign_up` | account/credential request started | form submit / signup event |
| `credential_created` | a usable API key / token exists | key-created event |
| `first_api_call` | the first authenticated request | first request from a new key |
| `first_success` | the first request that returns the intended result | 2xx + expected payload, or SDK callback |
| `recurring_use` | use on a second distinct day | DAU/WAU on the key |
| `production` | non-trivial sustained volume | volume threshold over time |

**Activation** is `first_success`. Everything before it is setup; everything after is adoption.

## Time-to-first-value (TTFV) — the north-star input

TTFV is the median wall-clock time from `sign_up` to `first_success`. It is the single best leading
predictor of activation: every minute of friction in that window costs activations. Measure median
and p90 (the p90 is where the silent failures hide).

## Hidden-step taxonomy (the silent activation killers)

1. **Undeclared prerequisite** — a runtime, version, package, or account toggle the docs assume.
2. **Stateful snippet** — copy-paste code that depends on prior state not shown.
3. **Console detour** — a dashboard step ("enable the API") missing from the written path.
4. **Version drift** — the snippet was written against an older SDK/API and silently breaks.
5. **Auth ambiguity** — unclear which key/scope/region the developer needs.

The detection method is always the same: **run the quickstart on a clean machine and log every step
the docs skipped.**

## Error-message rubric (critical-path errors)

A good first-run error message answers three questions in order:

1. **What** went wrong (the specific condition, not a generic code).
2. **Why** (the likely cause in the developer's terms).
3. **Next** (the concrete action to fix it, ideally with a link).

Audit the 3–5 errors a new developer is most likely to hit (bad key, missing param, wrong region,
rate limit, version mismatch) against this rubric.

## Quickstart construction checklist

- [ ] Prerequisites and versions declared up front
- [ ] Real, runnable commands (no pseudo-code on the happy path)
- [ ] Shortest path to first success (defer everything optional)
- [ ] A verification step the developer can run to confirm success
- [ ] The common failure-and-recovery shown, not hidden
- [ ] Ends with the next concrete step (an activation path)

## What's out of scope here (defer to `technical-writing-docs`)

The docs information architecture, the reference-writing craft, navigation, and the docs toolchain
belong to `technical-writing-docs`. This reference owns the **activation funnel** through the docs,
not the docs system itself (see the seam in [`../CLAUDE.md`](../CLAUDE.md)).
