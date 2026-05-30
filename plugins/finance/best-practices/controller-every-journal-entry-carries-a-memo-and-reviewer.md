# Every journal entry carries a memo and a reviewer — "adj per analysis" is not a memo

**Status:** Absolute rule
**Domain:** Controllership / close controls
**Applies to:** `finance`

---

## Why this exists

A journal entry without a memo is a number an auditor cannot trust six months later, and a recon without a reviewer signature is one person's unchecked assertion. The `controller` agent writes JE memos "as if an auditor is going to read them six months later — because they are," and the rule is "every JE has a memo: 'adj per analysis' is not a memo — the memo names the driver, the source doc, the period, and the basis," plus "recons have a reviewer: preparer signs, reviewer signs, both before close declares done." This is the close-side expression of house opinion #6 (audit trail in every workpaper). The failure mode is concrete: an unexplained entry surfaces in fieldwork, nobody remembers the basis, and it becomes an audit adjustment or a control deficiency — when a two-line memo at the time would have closed it.

## How to apply

Give every JE a memo that names driver + source + period + basis, and route every recon through a preparer and a separate reviewer before close signs off:

```
JE #2026-04-118   Accrue April legal fees
  Dr  Legal expense        45,000
      Cr  Accrued liabilities    45,000
  Memo:   Accrue 3 unbilled April matters per outside-counsel estimate email 2026-04-28
          (Acme LLP). Basis: hours-to-date × blended rate. True up on receipt of May invoice.
  Source: counsel estimate email (attached), engagement letter rate schedule §3.
  Prepared: <name> 2026-05-02   Reviewed: <different name> 2026-05-03

Recon (AR): preparer signs + dates, reviewer signs + dates — both BEFORE close is declared done.
```

**Do:**
- Name the **driver, source doc, period, and basis** in every memo — enough that a reviewer reconstructs the entry without asking.
- Require a **separate reviewer** signature on every recon and every non-trivial JE — preparer ≠ reviewer.
- Give round-number accruals (`$50,000.00`) a second look — round numbers are usually un-refined estimates, not facts (the agent's instinct).

**Don't:**
- Write "to record," "adj," or "per analysis" as a memo — that is the named anti-pattern.
- Mark a reconciliation complete with no reviewer signature (constitution §4 anti-pattern).
- Post a "plug" or "true-up" entry that ties to nothing — every reconciling item is a real timing difference or a bug, never a plug.

## Edge cases / when the rule does NOT apply

- **Fully automated, system-generated standard JEs** (recurring depreciation from the fixed-asset module) carry their basis in the system configuration rather than a per-entry memo — but the *configuration* is documented and a manual override of it needs its own memo.
- **Immaterial entries below a documented threshold** may use a standardized short-form memo — but they still carry a basis and a preparer; materiality governs depth, not existence.
- **A genuine prior-period restatement** is *not* a quiet reclass — it carries an explicit policy, a memo, and often auditor notification (the agent's restatement discipline).

## See also

- [`./reconcile-before-you-narrate.md`](./reconcile-before-you-narrate.md) — the reconciliation this rule's reviewer signs off must clear before commentary.
- [`./controller-reconcile-the-subledger-to-the-gl.md`](./controller-reconcile-the-subledger-to-the-gl.md) — the monthly sub-ledger-to-GL tie the reviewer attests.
- [`./audit-controls-need-an-owner-frequency-and-evidence.md`](./audit-controls-need-an-owner-frequency-and-evidence.md) — the preparer/reviewer split is the segregation-of-duties control auditors test.
- [`../agents/controller.md`](../agents/controller.md) — "every JE has a memo"; "recons have a reviewer"; the plug-entry and round-number anti-patterns.

## Provenance

Codifies the `controller` agent's "every JE has a memo" and "recons have a reviewer" opinions and its plug-entry / round-number / no-reviewer anti-patterns ([`../agents/controller.md`](../agents/controller.md)), plus house opinion #6 (audit trail in every workpaper) and the §4 anti-patterns "reconciliations without a reviewer signature" and "'we'll just adjust … to make it tie' without an explicit reclassification entry" ([`../CLAUDE.md`](../CLAUDE.md)). New.

---

_Last reviewed: 2026-05-30 by `claude`_
