# Cite the agreement section on every covenant calculation, and show the headroom math

**Status:** Absolute rule
**Domain:** Treasury / debt covenants
**Applies to:** `finance`

---

## Why this exists

A covenant calculation is a contractual assertion to a lender, and "approximately in compliance" is not a thing — the credit agreement defines the ratio, the inputs, and the test date with precision, and the lender computes it the same way. The `treasury-analyst` rule is exact: "a covenant calculation cites the agreement section — 'Per Section 7.2(a) of the Credit Agreement dated YYYY-MM-DD,'" and "covenant math runs every month, not every quarter; surprises are unforgivable when the answer is in the GL." The traps are definitional: the agreement's *defined* EBITDA (with its specific add-backs) is rarely the same as reported EBITDA; the borrowing base excludes ineligible receivables (aged, foreign, concentrated) that a naive calculation includes; and "springing" covenants that only test under a condition get forgotten until they spring. Reading the actual agreement — not a summary — is the discipline.

## How to apply

Compute the covenant exactly as the agreement defines it, cite the section, and always show the headroom (the distance to the threshold), not just a pass/fail:

```
Covenant:        Total Net Leverage ≤ 3.50×   — per §7.2(a), Credit Agreement dated 2026-01-15
Defined EBITDA = reported EBITDA + permitted add-backs per §1.1 definition   (list each add-back + source)
Net debt       = total debt − unrestricted cash, capped per §1.1
Calculation:     Net debt 245.0 / Defined EBITDA 78.5 = 3.12×
Headroom:        3.50 − 3.12 = 0.38× ; EBITDA could fall ~$8.5M before breach
Borrowing base:  eligible AR only — exclude aged > 90d, foreign, single-obligor concentration > cap (§ defn)
```

**Do:**
- Quote the **section number and the agreement date** on every covenant figure (the agent's mandatory output-contract line).
- Use the agreement's **defined** terms (defined EBITDA with its add-backs, the net-debt cap, eligible-AR rules) — not the reported financial-statement figure.
- Show the **headroom math** — how far the metric can move before breach — and run it monthly so a springing or tightening covenant never surprises.

**Don't:**
- State "we're well inside" without the headroom number (the named anti-pattern).
- Compute leverage off reported EBITDA when the agreement defines a different EBITDA — the difference is the whole point of the definition.
- Include ineligible receivables in the borrowing base, or leave a springing covenant undisclosed in management reporting.

## Edge cases / when the rule does NOT apply

- **Covenant-lite facilities** may have only an incurrence test (tested on an action, not periodically) rather than a maintenance test — cite which it is; the section-reference discipline still holds.
- **A waiver or amendment in force** changes the applicable threshold — cite the amendment, not the original section, and date it.
- **Pre-financing scenario modelling** (testing a hypothetical structure) is directional, but the moment it becomes a lender deliverable it inherits the full citation + headroom discipline.

## See also

- [`./treasury-forecast-cash-direct-method-thirteen-weeks.md`](./treasury-forecast-cash-direct-method-thirteen-weeks.md) — the covenant-headroom line in the cash forecast.
- [`./controller-reconcile-the-subledger-to-the-gl.md`](./controller-reconcile-the-subledger-to-the-gl.md) — covenant inputs come from the closed, reconciled GL.
- [`../agents/treasury-analyst.md`](../agents/treasury-analyst.md) — "a covenant calculation cites the agreement section"; "covenant math runs every month"; the headroom and borrowing-base anti-patterns.

## Provenance

Codifies the `treasury-analyst` agent's covenant opinions ("cites the agreement section," "runs every month") and anti-patterns ("'we're well inside' without the headroom math," undisclosed springing covenants, ineligible receivables in the borrowing base) in [`../agents/treasury-analyst.md`](../agents/treasury-analyst.md), plus house opinion #1 (source-cite every number) in [`../CLAUDE.md`](../CLAUDE.md) §3. New.

---

_Last reviewed: 2026-05-30 by `claude`_
