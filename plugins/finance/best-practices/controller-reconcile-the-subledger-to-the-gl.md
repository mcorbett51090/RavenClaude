# Reconcile every sub-ledger to the GL each close — a difference over materiality is owned, not carried

**Status:** Absolute rule
**Domain:** Controllership / close controls
**Applies to:** `finance`

---

## Why this exists

The general ledger is the source of truth, but it is fed by sub-ledgers — AR, AP, fixed assets, inventory, deferred revenue, intercompany — and the moment a sub-ledger drifts from the GL, every downstream number (variance commentary, covenant inputs, the board pack) is built on a figure that is about to move. The `controller` rule is "sub-ledger reconciles to GL every month; differences > materiality are tracked with owner + remediation date," and "intercompany matches at the period — a net imbalance > materiality is an unclosed loop." This is the structural precondition behind [`./reconcile-before-you-narrate.md`](./reconcile-before-you-narrate.md): that rule says don't narrate an unreconciled account; *this* rule says reconcile every account, every close, and never let a difference roll forward unowned. A carried intercompany imbalance is the classic example — small each month, large by year-end, and a guaranteed audit finding.

## How to apply

For each sub-ledger, tie the sub-ledger balance to the GL control account every close; any residual gets an owner, a root cause, and a remediation date — it is never silently carried:

```
Account          Sub-ledger    GL control    Diff      Owner     Root cause              Remediate by
AR               1,204,300     1,204,300         0      —         tie                     —
Fixed assets       880,150       879,400       750      <name>    in-flight disposal JE   2026-05-06
Intercompany (net)       0        12,400    12,400      <name>    unmatched IC invoice    2026-05-05
Deferred revenue   640,000       640,000         0      —         tie (roll-forward ok)   —

Rule: any |Diff| > materiality -> owner + root cause + dated remediation. Never carried unexplained.
```

**Do:**
- Tie **every** sub-ledger to its GL control account each close — AR, AP, fixed assets, inventory, deferred revenue, intercompany, equity, suspense.
- Give any residual over materiality an **owner, a root cause, and a remediation date** — a tracked difference is acceptable; an ignored one is not.
- Match intercompany at the period and eliminate; a net IC imbalance over materiality is an open loop to close before sign-off.

**Don't:**
- Carry a sub-ledger-to-GL difference month after month with no owner (the named anti-pattern).
- Plug the GL control account to force a tie — fix the broken feed, don't mask it (the controller's no-plug stance).
- Let deferred revenue sit without a contract-liability roll-forward, or let suspense accumulate as a parking lot.

## Edge cases / when the rule does NOT apply

- **Known, documented timing differences** (a sub-ledger posting that hits the GL one day later by design) are legitimate reconciling items — they are *explained*, owned, and expected to clear, not unexplained residuals.
- **Immaterial differences below the documented threshold** may be aggregated and reviewed in bulk rather than individually root-caused — materiality governs the depth of investigation.
- **A system in mid-migration** may run a temporary parallel-tie process with a documented exception; the discipline is to date the exception and the cut-over, not to suspend the reconciliation.

## See also

- [`./reconcile-before-you-narrate.md`](./reconcile-before-you-narrate.md) — the commentary gate this reconciliation underwrites.
- [`./controller-every-journal-entry-carries-a-memo-and-reviewer.md`](./controller-every-journal-entry-carries-a-memo-and-reviewer.md) — the reviewed JE that clears a reconciling item.
- [`./controller-state-the-revenue-recognition-policy.md`](./controller-state-the-revenue-recognition-policy.md) — deferred revenue ties via its contract-liability roll-forward.
- [`../agents/controller.md`](../agents/controller.md) — "sub-ledger reconciles to GL every month"; "intercompany matches at the period"; the carried-imbalance and plug anti-patterns.

## Provenance

Codifies the `controller` agent's "sub-ledger reconciles to GL every month" and "intercompany matches at the period" opinions and the carried-imbalance / plug anti-patterns ([`../agents/controller.md`](../agents/controller.md)), plus house opinion #8 (one source of truth per metric) in [`../CLAUDE.md`](../CLAUDE.md) §3. New, adjacent to the existing reconcile-before-you-narrate rule.

---

_Last reviewed: 2026-05-30 by `claude`_
