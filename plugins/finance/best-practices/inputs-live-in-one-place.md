# Keep every model input in exactly one labelled, sourced place

**Status:** Absolute rule
**Domain:** Financial modeling / auditability
**Applies to:** `finance`

---

## Why this exists

A hardcoded number buried in a formula — `=Revenue*0.21` for a tax rate, `=Q3*1.04` for a growth assumption — is invisible to the next reader and impossible to audit. When the rate changes, you must hunt every formula that embedded it, and you will miss one. The `financial-modeler` agent treats inputs as **sacred**: labelled, sourced, and living in exactly one place, so a reviewer can change one cell and trust the whole model re-flows. Inputs without sources rot fastest — six months on, nobody remembers whether the 21% was the statutory rate, a blended effective rate, or a guess.

## How to apply

Structure the model **inputs tab → mechanics in between → outputs tab**, with one scenario switch driving the whole model. Every driver is a labelled cell on the Inputs sheet with a source and a refresh date.

```
Inputs sheet:
  TaxRate        21.0%   src: US federal statutory, IRC §11 (2026)   refreshed 2026-05-30
  RevGrowth_Base  4.0%   src: mgmt rolling forecast, base case        refreshed 2026-05-30

Mechanics:  =Revenue * (1 - TaxRate)        # references the label, never the literal
            =PriorRev * (1 + RevGrowth_Base)
```

Color conventions make a violation visible: **blue = hardcoded input, black = formula, green = link to another sheet.** A black formula cell containing a literal rate is a smell.

**Do:**
- Promote every literal rate/growth/margin to a labelled Inputs cell with a source citation and refresh date.
- Drive scenarios from a single switch cell, not scattered `IF`s.
- Carry a Documentation/Assumptions tab: source per input, owner, version, last-refresh date.

**Don't:**
- Embed `*0.21`, `*1.25`, or any literal multiplier inside a calculation formula.
- Wrap a broken formula in `IFERROR(formula, 0)` — that hides the bug instead of fixing it.
- Leave a key driver (WACC, growth, margin) on the Inputs sheet with no source citation.

## Edge cases / when the rule does NOT apply

- **True mathematical constants** (days-in-year 365, months-per-quarter 3, a unit conversion) are not assumptions and need not be promoted — though a labelled constant still reads better.
- **Designed, disclosed circulars** (interest-on-cash-sweep) legitimately reference calc cells in a loop; document them on the Documentation tab. The rule bans *undisclosed* circulars and *buried* literals, not intentional designed structure.
- **A genuinely one-off scratch calc** thrown away after a single answer — but the moment it feeds a deliverable or gets re-run, it inherits the rule.

## See also

- [`../agents/financial-modeler.md`](../agents/financial-modeler.md) — "Inputs are sacred"; the anti-pattern list this codifies.
- [`../knowledge/variance-root-cause-triage.md`](../knowledge/variance-root-cause-triage.md) — the FORECAST leaf, where a broken model input is named and refreshed.

## Provenance

Codifies the `financial-modeler` agent's "treats inputs as sacred" / "no hardcodes in formulas" opinions and anti-patterns ([`../agents/financial-modeler.md`](../agents/financial-modeler.md)), plus finance house opinion #2 ("No hardcoded numbers in model mechanics") and #11 ("Models age" — version + assumptions + refresh date) in [`../CLAUDE.md`](../CLAUDE.md) §3. The hardcoded-rate pattern is also the first mechanical check in the plugin's anti-pattern hook (§7).

---

_Last reviewed: 2026-05-30 by `claude`_
