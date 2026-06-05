# Finance — best-practice docs

Named, citable rules for the `finance` plugin's specialists. Each file is **one rule**, grounded in this plugin's knowledge bank and agent opinions — read, applied, and cited as a whole.

These complement, and do not restate, the cross-cutting house opinions in the team constitution ([`../CLAUDE.md`](../CLAUDE.md) §3) or the automated checks in the anti-pattern hook (§7). They take one opinion each and make it a standalone, exception-documented rule.

---

## Index

_32 rules. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`audit-classify-deficiency-severity.md`](./audit-classify-deficiency-severity.md) | Absolute rule — calling every exception a "finding" (or burying a material weakness) misstates the control environment; severity is a defined judgment. | A failed control test must be classified CD / SD / material weakness — likelihood × magnitude vs materiality — which drives remediation and disclosure. |
| [`audit-controls-need-an-owner-frequency-and-evidence.md`](./audit-controls-need-an-owner-frequency-and-evidence.md) | Absolute rule | An auditor does not accept that a control exists because someone says it does — they ask "who runs it, how often, and what proves it fired?" A control… |
| [`board-open-with-the-narrative-not-the-table.md`](./board-open-with-the-narrative-not-the-table.md) | Pattern | A board pack that opens with a table is a request to skim, and a board that skims makes worse decisions. |
| [`controller-every-journal-entry-carries-a-memo-and-reviewer.md`](./controller-every-journal-entry-carries-a-memo-and-reviewer.md) | Absolute rule | A journal entry without a memo is a number an auditor cannot trust six months later, and a recon without a reviewer signature is one person's unchecke… |
| [`controller-reconcile-the-subledger-to-the-gl.md`](./controller-reconcile-the-subledger-to-the-gl.md) | Absolute rule | The general ledger is the source of truth, but it is fed by sub-ledgers — AR, AP, fixed assets, inventory, deferred revenue, intercompany — and the mo… |
| [`controller-state-the-revenue-recognition-policy.md`](./controller-state-the-revenue-recognition-policy.md) | Absolute rule | Revenue is the most scrutinized line in the financial statements and the easiest to get subtly wrong, because *when* revenue is earned is a policy dec… |
| [`fpa-build-the-variance-bridge-price-volume-mix.md`](./fpa-build-the-variance-bridge-price-volume-mix.md) | Primary diagnostic | `reconcile-before-you-narrate.md` gates *when* commentary may be written; this doc governs *how* a revenue or unit-driven-cost variance gets decompose… |
| [`fpa-rolling-forecast-beside-the-budget.md`](./fpa-rolling-forecast-beside-the-budget.md) | Pattern | A budget and a rolling forecast do two different jobs, and collapsing them destroys both. |
| [`inputs-live-in-one-place.md`](./inputs-live-in-one-place.md) | Absolute rule | A hardcoded number buried in a formula — `=Revenue*0.21` for a tax rate, `=Q3*1.04` for a growth assumption — is invisible to the next reader and impo… |
| [`link-the-three-statements.md`](./link-the-three-statements.md) | Absolute rule | A three-statement model is only trustworthy when the P&L, balance sheet, and cash flow are **mechanically linked**, not three independently-maintained… |
| [`model-carry-an-error-check-block.md`](./model-carry-an-error-check-block.md) | Pattern | A model that *looks* right and a model that *proves* it is right are different artifacts. |
| [`model-derive-the-cash-flow-bridge-from-net-income.md`](./model-derive-the-cash-flow-bridge-from-net-income.md) | Pattern | `link-the-three-statements.md` establishes the *absolute rule* — every cash-flow line is a balance-sheet movement and the model must tie. |
| [`model-design-disclose-circular-references.md`](./model-design-disclose-circular-references.md) | Absolute rule | A circular reference in a financial model is either a deliberate, documented piece of structure or it is a bug — there is no third category. |
| [`model-drive-the-forecast-off-operational-drivers.md`](./model-drive-the-forecast-off-operational-drivers.md) | Pattern | A forecast built as `=PriorRevenue * (1 + growth%)` is a guess wearing a formula. |
| [`model-present-scenarios-driven-by-one-switch.md`](./model-present-scenarios-driven-by-one-switch.md) | Pattern | A model that emits a single number is a guess with extra decimal places. |
| [`reconcile-before-you-narrate.md`](./reconcile-before-you-narrate.md) | Absolute rule | Variance commentary written on an account that has not been reconciled describes bookkeeping noise, not business performance. |
| [`treasury-cite-the-agreement-on-every-covenant.md`](./treasury-cite-the-agreement-on-every-covenant.md) | Absolute rule | A covenant calculation is a contractual assertion to a lender, and "approximately in compliance" is not a thing — the credit agreement defines the rat… |
| [`treasury-forecast-cash-direct-method-thirteen-weeks.md`](./treasury-forecast-cash-direct-method-thirteen-weeks.md) | Pattern | Near-term liquidity is a survival question, and the indirect cash-flow statement — useful as it is inside the three-statement model — is the wrong too… |
| [`treasury-manage-the-cash-conversion-cycle.md`](./treasury-manage-the-cash-conversion-cycle.md) | Pattern | Working capital is the cheapest source of cash a company has — money trapped in receivables and inventory, or released by supplier terms, that needs n… |
| [`valuation-build-wacc-from-sourced-components.md`](./valuation-build-wacc-from-sourced-components.md) | Absolute rule | The discount rate is the single most powerful lever in a DCF — a 100 bps move in WACC can swing enterprise value by double digits, because it compound… |
| [`valuation-discipline-the-terminal-value.md`](./valuation-discipline-the-terminal-value.md) | Absolute rule | In most DCFs the **majority of present value lives in the terminal value** — the period beyond the explicit forecast — so a small over-reach in termin… |
| [`valuation-triangulate-three-methods.md`](./valuation-triangulate-three-methods.md) | Absolute rule | A valuation built on a single method is fragile: a DCF is only as good as its forecast and discount rate, comparables are only as good as the comp set… |
| [`audit-pbc-item-is-complete-only-when-evidence-is-attached.md`](./audit-pbc-item-is-complete-only-when-evidence-is-attached.md) | Absolute rule | A PBC item marked "complete" must contain the actual evidence the auditor needs, not an assertion or a pointer to a folder. |
| [`board-one-page-executive-summary-with-a-recommendation.md`](./board-one-page-executive-summary-with-a-recommendation.md) | Pattern | Every board pack opens with a one-page summary that states the key conclusion and the decision requested — before any tables or supporting slides. |
| [`controller-accruals-are-estimates-not-plugs.md`](./controller-accruals-are-estimates-not-plugs.md) | Absolute rule | An accrual must be supported by a documented calculation — not a round-number chosen to hit a target or match a prior period. |
| [`controller-intercompany-eliminate-before-you-consolidate.md`](./controller-intercompany-eliminate-before-you-consolidate.md) | Absolute rule | Intercompany transactions must be eliminated as a documented pre-consolidation step; consolidating first and cleaning up after creates audit risk. |
| [`fpa-document-the-planning-calendar-raci-and-lock-dates.md`](./fpa-document-the-planning-calendar-raci-and-lock-dates.md) | Absolute rule | Every budget or forecast cycle requires a published calendar with explicit lock dates and a RACI before any template is distributed. |
| [`fpa-saas-arr-bridge-shows-the-four-movements.md`](./fpa-saas-arr-bridge-shows-the-four-movements.md) | Absolute rule | SaaS ARR must be reported as a bridge with four movements — new, expansion, contraction, and churn — not collapsed to a net change. |
| [`model-label-every-unit-and-currency.md`](./model-label-every-unit-and-currency.md) | Absolute rule | Every input and output in a financial model carries an explicit unit label and currency designation to prevent silent unit-mismatch errors. |
| [`model-version-and-archive-every-release.md`](./model-version-and-archive-every-release.md) | Absolute rule | Every externally-shared or decision-bearing model release is version-stamped and archived before further edits begin. |
| [`treasury-fx-exposure-name-it-before-you-hedge-it.md`](./treasury-fx-exposure-name-it-before-you-hedge-it.md) | Absolute rule | Build an explicit FX exposure inventory — sign, size, tenor, certainty — before selecting any hedge instrument. |
| [`valuation-control-premium-is-not-free.md`](./valuation-control-premium-is-not-free.md) | Absolute rule | A control premium must be sourced from a current, period-specific, sector-matched precedent study and presented as a range, not a round memorized number. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — finance team constitution (§3 house opinions, §4 anti-patterns, §6 Output Contract).
- [`../knowledge/variance-root-cause-triage.md`](../knowledge/variance-root-cause-triage.md) — the variance decision tree both docs lean on.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs and the `_TEMPLATE.md` these follow.
