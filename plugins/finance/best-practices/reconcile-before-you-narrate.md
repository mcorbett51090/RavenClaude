# Reconcile before you narrate a variance

**Status:** Absolute rule
**Domain:** FP&A / variance analysis
**Applies to:** `finance`

---

## Why this exists

Variance commentary written on an account that has not been reconciled describes bookkeeping noise, not business performance. The `variance-root-cause-triage` decision tree puts reconciliation at the **root node** for exactly this reason: if the subledger does not tie to the GL, or open recon items remain, every driver you name downstream is built on a number that is about to move. The cost is concrete — you tell a stakeholder "opex ran hot" and name an owner, the controller closes the recon next week, the variance halves, and your commentary (and credibility) flips. Reconciliation is a **precondition**, not a parallel task.

## How to apply

When a material variance lands (per the engagement's declared threshold — typically the greater of $50K or 5%), traverse the first node of [`../knowledge/variance-root-cause-triage.md`](../knowledge/variance-root-cause-triage.md) before writing a single word of commentary:

```
Q1: Was the underlying account reconciled AND the subledger tied to the GL?
  NO  -> STOP. Route to controller for recon. Commentary is deferred, not drafted.
  YES -> proceed to the TIMING / ONE-TIME / FX / PVM / DECISION / FORECAST leaves.
```

**Do:**
- Confirm the recon is signed off (preparer + reviewer) before drafting the variance walk.
- If recon is incomplete, ship the deliverable as `⚠️ partial` with an open question routed to `controller`, not a narrated cause.
- State the reconciliation status in the workpaper's audit-trail line.

**Don't:**
- Write "we missed plan by $X because Y" on an account with open recon items.
- Treat recon and commentary as work that can proceed in parallel to hit a deadline.
- Let a stakeholder's pre-offered explanation ("sales said the deal slipped") substitute for tying the account first.

## Edge cases / when the rule does NOT apply

- **Immaterial variances below the declared threshold** — no commentary is owed at all, so the recon gate is moot (house opinion #5: materiality is a design constraint).
- **A reconciled account where the variance is purely a known timing reclass** — recon is done; you proceed straight to the TIMING leaf. The rule gates on recon completeness, not on the eventual driver.
- **Pre-close flash/estimate decks explicitly labelled "unreconciled, directional only"** — permitted, *provided* the unreconciled status is stated on the face of the deliverable so no reader mistakes it for closed commentary.

## See also

- [`../knowledge/variance-root-cause-triage.md`](../knowledge/variance-root-cause-triage.md) — the decision tree whose root node this codifies (RECON leaf).
- [`../agents/fpa-analyst.md`](../agents/fpa-analyst.md) — owns variance commentary; traverses the tree top-to-bottom.
- [`../agents/controller.md`](../agents/controller.md) — owns the reconciliation the gate depends on.

## Provenance

Codifies the RECON root node and "reconcile before commentary" discipline in [`../knowledge/variance-root-cause-triage.md`](../knowledge/variance-root-cause-triage.md) (last reviewed 2026-05-22; sourced from CFI's variance framework and Numeric's 2025 variance guide), and house opinion #3 in the finance team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3).

---

_Last reviewed: 2026-05-30 by `claude`_
