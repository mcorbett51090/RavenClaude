# Maker-checker is two people — a return signed off by one person has no second set of eyes

**Status:** Absolute rule
**Domain:** Regulatory reporting — sign-off controls
**Applies to:** `regulatory-compliance`

---

## Why this exists

Maker-checker is the single most relied-on control over filing accuracy, and it collapses the instant the same person fills both roles. The trap is procedural: a preparer who is also the only available reviewer signs both lines, or a reviewer who "trusts" the preparer rubber-stamps without re-walking the work. Either way the firm has one set of eyes on a regulator-facing submission, and the control exists only on paper. Maker-checker is binary — preparer and reviewer are different people, both sign off, both in writing — because the whole point is independent re-verification, not a second signature on the same act. A return filed without a genuine maker-checker chain is a plugin-wide flagged anti-pattern, and it is one of the first things an examiner tests by asking who prepared and who reviewed a given schedule.

## How to apply

Record a real two-person chain with the checker independently re-walking the load-bearing work:

```
Preparer (maker)    named + dated; built the return, owns the lineage
Reviewer (checker)  DIFFERENT named person + dated; re-walks lineage, variances, methodology — not a glance
Approver            named + dated; accountable for submission (may be a third role for material returns)
Walkthrough         pre-submission review by someone OUTSIDE the prep team
Recorded            all sign-offs in writing — verbal sign-off does not exist for regulator-facing matters
```

The checker re-derives the load-bearing cells from the lineage and confirms the prior-period variances are explained — checking is re-verification, not endorsement.

**Do:**
- Make the checker a different person from the maker, every time, both signing in writing (house opinion #6).
- Have the checker independently re-walk the data lineage and the variance explanations, not just sign.
- Run a pre-submission walkthrough with someone outside the prep team for material returns.

**Don't:**
- Let one person sign both maker and checker lines because the reviewer was unavailable — that is no control.
- Treat the checker's signature as a formality; a rubber-stamp review is the same as no review.
- Skip the chain on a "small" or "rolled-forward" return — rolled-forward is exactly where stale errors hide.

## Edge cases / when the rule does NOT apply

- **Very small firms** with genuine segregation-of-duties constraints document a compensating control (e.g., an outsourced reviewer, or board-level review) — the *constraint* is recorded, not waived silently `[verify-at-build — some regimes mandate specific sign-off roles]`.
- **Automated/system-generated returns** still need a human checker on the inputs and the output reasonableness — automation moves the maker, it doesn't remove the checker.
- **Legal-opinion gate** — a restatement-disclosure or deadline-waiver question routes to counsel; the maker-checker on the figures themselves continues.

## See also

- [`./filing-source-trace-every-load-bearing-cell.md`](./filing-source-trace-every-load-bearing-cell.md) — what the checker re-walks.
- [`./filing-explain-the-variance-before-you-submit.md`](./filing-explain-the-variance-before-you-submit.md) — the variance review the checker confirms.
- [`../agents/regulatory-reporting-analyst.md`](../agents/regulatory-reporting-analyst.md) — "Maker-checker is binary. Preparer and reviewer are different people, both sign off, both in writing."

## Provenance

Codifies the `regulatory-reporting-analyst` opinion "Maker-checker is binary" and the anti-patterns "maker-checker with the same person signing both roles" and "return prepared without a pre-submission walkthrough by someone outside the prep team" ([`../agents/regulatory-reporting-analyst.md`](../agents/regulatory-reporting-analyst.md)), plus house opinion #6 (default to written) and the plugin-wide anti-pattern "a regulatory return filed without a maker-checker sign-off chain" in [`../CLAUDE.md`](../CLAUDE.md) §3–§4.

---

_Last reviewed: 2026-05-30 by `claude`_
