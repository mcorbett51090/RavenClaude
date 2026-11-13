# Settings copy is a label and a caption, with more info on demand

**Status:** Pattern — strong default. Deviate only with a written reason.

**Domain:** Web Design — content, forms and settings controls

**Applies to:** `web-design`

---

## Why this exists

Pages that explain each control in a paragraph make people read to find the control. A short label, one caption line and an opt-in "more info" are faster to scan. The budgets below are house defaults `[inference]`; no study in this repository measures comprehension or conversion for shorter copy. The same marketplace has a case where removing fields lowered conversion ([`forms-engineering` scenario](../../forms-engineering/scenarios/2026-08-17-we-removed-fields-and-conversion-fell.md)), so cut by *moving* text, and test the cut.

## How to apply

| Layer | Budget `[inference]` | Visible? |
|---|---|---|
| Page title | ≤ 4 words | always |
| Page lede | none or one sentence | always |
| Group heading | ≤ 3 words | always |
| Control label | ≤ 4 words / ~28 characters | always |
| Caption | ≤ 1 line (~80 characters) | always |
| More info | ≤ 2 sentences + one "Learn more" link | on demand |

1. **Caption = consequence, unit or limit.** If it restates the label, delete it.
2. **Anything needed to decide stays visible:** cost, irreversibility, limits, errors. Never put it only in a tooltip.
3. **"More info" is a toggletip, not a tooltip or `title=`:** a `<button type="button">` named "More about <label>" that fills an adjacent `role="status"` region. Tooltips stay for naming an icon-only control or expanding an abbreviation, and must meet WCAG 1.4.13 (dismissible, hoverable, persistent; Level AA, read 2026-11-05).
4. **Primary navigation keeps visible labels.** A tooltip is not a substitute (solid rule in the 2026-11-04 standing bar).
5. **Real copy in the mock,** including the longest label at 320 px.

**Don't:**
- Open a settings page with a paragraph that repeats the headings.
- Make the label change with state ("Enable…" / "Disable…").
- Cite a shorter-copy gain without a denominator and a test.

## Edge cases / when the rule does NOT apply

- Legal, consent and safety text: its wording is not yours to shorten; keep it visible.
- First-run or rarely used settings may carry a longer caption; say why in the PR.
- Inclusive Components calls tooltips "a last resort" and is a single-author secondary source; APG's tooltip page is marked work in progress (both read 2026-11-05). Treat both as guidance, not settled standards.

## See also

- [`../knowledge/settings-and-choice-controls-2026.md`](../knowledge/settings-and-choice-controls-2026.md) §6 — budgets, before/after example, sources
- [`content-microcopy-cta-and-errors.md`](./content-microcopy-cta-and-errors.md), [`content-readability-and-hierarchy.md`](./content-readability-and-hierarchy.md)
- [`../../accessibility-engineering/knowledge/settings-controls-markup-and-keyboard-2026-11.md`](../../accessibility-engineering/knowledge/settings-controls-markup-and-keyboard-2026-11.md) — toggletip and tooltip markup
