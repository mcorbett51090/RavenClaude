# Report Net of Reinsurance, But Show the Gross First

**Status:** Absolute rule
**Domain:** Portfolio analytics / reinsurance
**Applies to:** `insurance-pc`

---

## Why this exists

Reporting only net-of-reinsurance combined ratios conceals the risk that sits in the gross book and the cost of the reinsurance protecting it. A carrier with a 95 NCR net may have a 115 NCR gross — and if the reinsurance treaty renews at higher rates or with higher retentions, the net result deteriorates materially without any change in the underlying book. Equally, showing only the gross result understates the protection actually in force. Both numbers are needed: the gross shows the book's inherent risk profile; the net shows the economic result after the protection structure. Management that only sees one is flying with one instrument.

## How to apply

Present combined ratio and loss ratio at three levels for any portfolio-level analysis.

```
Combined Ratio Presentation — Three Levels
──────────────────────────────────────────────────────
                        Gross          Ceded         Net (NER)
Loss ratio              XX.X%         (X.X%)         XX.X%
LAE ratio               XX.X%         (X.X%)         XX.X%
Expense ratio (written) XX.X%          n/a            XX.X%
─────────────────────────────────────────────────────────
Combined ratio          XXX.X%                       XXX.X%

Reinsurance cost (ceded premium as % of GWP): X.X%

Key disclosures alongside this table:
  - Reinsurance structure: type (quota share / XL / cat / agg stop-loss)
  - Treaty year and renewal date
  - Significant changes since prior year (retention, rate, coverage)
  - Counterparty rating on material ceded balances
```

**Do:**
- Flag when the gross vs. net divergence is widening — it signals either growing cat accumulation or deteriorating attritional loss experience that the XL is catching.
- Include the ceded premium cost ratio in the management report; reinsurance cost often rises faster than the benefit it buys, eroding the economic value of the program.
- When presenting YOY changes, show gross and net separately — a treaty restructuring can make the net result look better or worse without any change in underwriting quality.

**Don't:**
- Present a board or management report that shows only the net combined ratio — it buries the reinsurance dependency.
- Allow a favorable net result to mask deteriorating gross loss experience for more than one reporting period without an explicit discussion of the reinsurance program's adequacy.
- Omit the reinsurance counterparty credit quality from any report that includes material ceded recoverables on the balance sheet.

## Edge cases / when the rule does NOT apply

- **MGAs without a balance sheet** — if the MGA cedes 100% to a capacity provider and retains no risk, the "gross" position is the carrier's view, not the MGA's; the MGA reports on the gross written premium and ceding commission economics, not the loss triangle.
- **Proportional quota-share books** where the MGA owns a share — the presentation still applies, proportionally, to the MGA's retained share.

## See also

- [`../agents/underwriting-lead.md`](../agents/underwriting-lead.md) — the engagement lead who synthesizes the gross/net picture for management.
- [`./isolate-the-catastrophe-load.md`](./isolate-the-catastrophe-load.md) — cat load on the gross book is one of the primary drivers of gross-vs-net divergence; isolating it is a prerequisite for understanding the reinsurance dependency.

## Provenance

Codifies the underwriting-lead's portfolio presentation discipline from the insurance-pc plugin's CLAUDE.md §3 #4 (isolate the catastrophe load) and §3 #6 (line-of-business mix drives the portfolio result). The gross/net/ceded presentation structure is standard P&C management reporting practice (NAIC, Lloyd's, BMA insurance reporting conventions).

---

_Last reviewed: 2026-06-05 by `claude`_
