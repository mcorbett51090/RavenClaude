# Recovery starts with diagnosis, not features

**Status:** Primary diagnostic
**Domain:** EdTech partner recovery
**Applies to:** `edtech-partner-success`

---

## Why this exists

When a partner flips to Red, the PSM's instinct is to respond with offers: a feature they haven't tried, a training session, a new integration. This is the wrong first move. Most partner-health declines have a root cause in one of four hypothesis buckets — product fit, implementation health, sponsorship, or external pressure — and the right recovery play depends on knowing which. Offering a feature training to a partner whose real problem is that the district IT director who owned the implementation left in October wastes the relationship credit and delays the actual fix. The diagnosis must precede the intervention; the recovery play is chosen because of what the diagnosis found, not instead of it.

## How to apply

When a partner enters recovery, run the 4-hypothesis parallel diagnostic before selecting or executing any play.

```
4-hypothesis recovery diagnostic:

  Run all four hypotheses in the first recovery conversation. They are not mutually exclusive.

  Hypothesis 1 — Product fit
    Signals: "We're not sure this is the right tool for us," low adoption across user types,
             consistent support tickets about the same limitation, prior-year usage always low
    Diagnostic: Pull usage by feature area. Map to the original success plan.
    If confirmed: recovery play focuses on re-scoping use case to where the product DOES fit.

  Hypothesis 2 — Implementation health
    Signals: "The data isn't right," inconsistent user access, teachers report login issues,
             low usage concentrated in first weeks and then drops
    Diagnostic: Rostering pre-flight. SIS/SSO integration check. Trainer-the-trainer cascade check.
    If confirmed: escalate to engineering / IT; recovery play is technical, not relational.

  Hypothesis 3 — Sponsorship
    Signals: "Our champion just left," no response from prior contacts, new decision-maker
             was not in the original onboarding, silence since a personnel change
    Diagnostic: Confirm decision-maker liveness. Map the new org chart.
    If confirmed: sponsor-mapping play before any other recovery motion.

  Hypothesis 4 — External pressure
    Signals: "Budget is being cut across the board," competing tool just purchased,
             superintendent turnover, state policy change affecting the program
    Diagnostic: Direct question to the district's main contact. Partner profile review.
    If confirmed: adjust the renewal posture (recovery-and-renew or graceful-exit), not
                 the product pitch.
```

**Do:**
- Run all four hypotheses before selecting a recovery play.
- Document the diagnostic in the partner profile and in the escalation memo if escalating.
- Select the recovery play that addresses the confirmed root cause, not the one the PSM is most comfortable executing.

**Don't:**
- Lead a recovery conversation with a product demo or feature offer before the diagnostic.
- Treat the hypotheses as mutually exclusive — two or more often co-occur.
- Skip the rostering pre-flight (Hypothesis 2) even if the partner hasn't complained about data.

## Edge cases / when the rule does NOT apply

If the partner is in active contract-cancellation or legal-dispute mode, the recovery-play framework is superseded by the legal/executive escalation path — the PSM is not the right lead in that scenario. For partners in their first 60 days (Stage 1), implementation issues are expected, not a recovery signal; use the onboarding diagnostic, not the recovery diagnostic.

## See also

- [`../agents/success-playbook-designer.md`](../agents/success-playbook-designer.md) — selects and designs the recovery play after the diagnostic identifies the root cause.
- [`./risk-early-warning-fire-the-save-play-while-it-still-saves.md`](./risk-early-warning-fire-the-save-play-while-it-still-saves.md) — the companion rule on timing: the diagnostic must run while recovery is still possible.

## Provenance

Codifies the 4-hypothesis diagnostic from the plugin's `recovery-play-design` skill. The feature-offer-first recovery error is the most common PSM mistake under pressure; the diagnostic-first discipline is the standard prevention.

---

_Last reviewed: 2026-06-05 by `claude`_
