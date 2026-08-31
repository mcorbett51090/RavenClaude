# Name the denominator before you quote a completion rate

**Status:** Absolute rule — a form rate without its denominator is not a number. Completion and abandonment are complements on **one** denominator or they are two unrelated statistics.
**Domain:** Forms engineering — measurement
**Applies to:** `forms-engineering`

---

## Why this exists

Three denominators are in common use and they do not agree:

- **Page views** — everyone who loaded the page. Measures the page's traffic mix, not the form.
- **Form starts** — sessions that produced a first interaction with a field. Isolates people who tried.
- **Eligible sessions** — sessions that arrived with the intent the form serves. Rarely definable without circularity.

The gap between the first two is usually larger than any improvement anyone is arguing about, which means a team can "improve" a form by changing what it counts. Two dashboards that disagree about the same form almost always disagree about this and about nothing else.

There is a second, quieter version of the same error: quoting completion from one denominator and abandonment from another, so the two do not sum to one. That is how a form report becomes internally inconsistent while every individual number is defensible.

## How to apply

1. **Write the denominator into the plan before instrumenting**, in words a second analyst would implement identically. "Sessions in which any field of form `X` received a first interaction" is a definition. "Visitors" is not.
2. **Know what the platform means by a start.** A start event that fires on first interaction is not the same as one that fires on visibility, and a team that assumes the latter will over-report completion and then not understand why the fix did nothing.
3. **State completion and abandonment as exact complements.** `abandonment = 1 − completion`, on the one denominator.
4. **Print the denominator with the number, every time.** Not in a footnote and not in the data dictionary — next to the figure, wherever it appears. `form_metrics.py` does this by construction, which is the point of using it rather than a spreadsheet.
5. **Say what a submit does and does not mean.** A submit event is not a server acceptance. A form that posts and then fails counts as a submit on most platforms.

## The anti-pattern

A slide that says "completion improved from 42% to 61%" with no denominator on either figure and no statement that the two were computed the same way. Nobody can falsify it, which is exactly why it survives.

## Source

Definitions and the platform default are in [`../knowledge/form-telemetry-and-spc.md`](../knowledge/form-telemetry-and-spc.md) §1 (retrieved 2026-08-17). Funnel-level conversion diagnosis, which is a different question, belongs to [`../../web-design/skills/conversion-design/SKILL.md`](../../web-design/skills/conversion-design/SKILL.md).
