# Treat flag targeting rules as code: version, review, and test them

**Status:** Pattern
**Domain:** Feature flags / targeting
**Applies to:** `experimentation-growth-engineering`

---

## Why this exists

A feature flag with a complex targeting rule (role AND country AND plan tier
AND NOT beta-opt-out) is logic that executes on every request. Teams that
configure targeting rules as ad-hoc UI clickops have no audit trail for "when
did this rule change?", no review process for "is this rule correct?", and no
test for "did we accidentally exclude 40% of users?". A targeting rule error
silently mis-assigns users to the wrong experience — exactly the class of
plumbing bug that SRM checks are designed to detect.

## How to apply

Define targeting rules in code (JSON/YAML config committed to the repo) or in
the flag platform's Infrastructure-as-Code integration, not only in the GUI.

```yaml
# flags/new-checkout-flow.yaml (committed to repo)
key: new-checkout-flow
targeting_rules:
  - description: "10% of Pro users in US/CA, not in beta-opt-out list"
    clauses:
      - attribute: plan
        op: in
        values: ["pro", "enterprise"]
      - attribute: country
        op: in
        values: ["US", "CA"]
      - attribute: beta_opt_out
        op: is
        values: [false]
    rollout_percentage: 10
  - description: "Everyone else gets control"
    rollout_percentage: 0
```

Code-review the targeting rule change like any feature code. Add a targeting
rule unit test that asserts inclusion/exclusion for representative user profiles.

**Do:**
- Commit targeting rules to version control and review them in pull requests.
- Write unit tests for non-trivial rules (> 2 clauses).
- Run SRM checks after any targeting rule change to verify the intended split
  actually materialized.

**Don't:**
- Configure targeting rules only through the platform UI with no audit trail.
- Change a targeting rule mid-experiment (it changes who gets assigned and
  breaks the analysis).
- Use more than ~5 clauses in a single rule without a review for logic errors —
  complex rules have subtle exclusion bugs.

## Edge cases / when the rule does NOT apply

- Ops flags and kill switches that need instant configuration by an on-call
  engineer during an incident: UI-based emergency toggle is correct; the rule
  is "allow toggle, but the default state and intended audience should still
  be in code."

## See also

- [`../agents/feature-flag-engineer.md`](../agents/feature-flag-engineer.md) — owns flag targeting and SDK integration
- [`./check-srm-before-trusting-a-result.md`](./check-srm-before-trusting-a-result.md) — a targeting rule error produces SRM; SRM is the diagnostic
- [`./deterministic-assignment-server-side.md`](./deterministic-assignment-server-side.md) — determinism requires that rules are stable and reviewed

## Provenance

Standard software engineering discipline (infrastructure-as-code) applied to
feature-flag configuration. Targeting-rule code-review is documented best
practice in LaunchDarkly, Unleash, and similar platform documentation
`[verify-at-use]`.

---

_Last reviewed: 2026-06-05 by `claude`_
