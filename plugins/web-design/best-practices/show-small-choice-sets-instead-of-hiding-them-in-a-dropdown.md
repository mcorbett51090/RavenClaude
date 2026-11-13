# Show small choice sets instead of hiding them in a dropdown

**Status:** Pattern — strong default. Deviate only with a written reason (a long, typeable list; a mobile picker that helps).

**Domain:** Web Design — forms and settings controls

**Applies to:** `web-design`

---

## Why this exists

A `<select>` hides every option behind a click, so the person can't compare them without opening it. GOV.UK says a select "should only be used as a last resort in public-facing services" because "research shows that some users find selects very difficult to use" (GOV.UK Design System, Select, read 2026-11-05; GOV.UK's own claim, not independently verified here). GOV.UK gives no option-count threshold, so the numbers below are house defaults `[inference]`. No study in this repository shows that tiles outperform dropdowns; test the change before reporting a gain.

## How to apply

**The rule:** pick the lightest *visible* control the choice shape allows. Full ladder, tree and per-control rules: [`../knowledge/settings-and-choice-controls-2026.md`](../knowledge/settings-and-choice-controls-2026.md).

| Shape | Use |
|---|---|
| On/off, applies now | Switch in a grouped card |
| 2–5 short options | Segmented control (native radios) |
| 3–7 options needing detail or a price | Radio tiles |
| Money/quantity presets | Amount tiles + "Other" |
| Continuous or ≥6 ordered steps, exact value unimportant | Native range slider with live preview, visible value and `aria-valuetext` |
| 8+ typeable options | Combobox (native `select` allowed for country-style lists) |

```html
<fieldset class="segmented">
  <legend>Email digest</legend>
  <label><input type="radio" name="digest" value="instant"> Instant</label>
  <label><input type="radio" name="digest" value="daily" checked> Daily</label>
  <label><input type="radio" name="digest" value="weekly"> Weekly</label>
</fieldset>
```

**Do:**
- Keep native radios/checkboxes/range under the styling so keys, names and state come free.
- Pre-select the current value for a *setting*; don't pre-select for a *question* (see the knowledge file §1).
- Hide the native input visually (clip), never with `display:none`.

**Don't:**
- Use a `<select>` for ≤ 5 options in settings or checkout.
- Restyle a `<select>` into a custom listbox to make it "look modern".
- Build a segmented control from `div`s or `role="tablist"` when it does not switch panels.

## Edge cases / when the rule does NOT apply

- Long, well-known lists (country, timezone, year of birth) where the native mobile picker is the better control.
- Data-driven options whose count is unbounded or changes per user; use a combobox.
- Dense admin filters where space is the constraint and the audience is expert. Write the reason in the PR.

## See also

- [`../knowledge/settings-and-choice-controls-2026.md`](../knowledge/settings-and-choice-controls-2026.md) — the ladder, sources and limits
- [`../../accessibility-engineering/knowledge/settings-controls-markup-and-keyboard-2026-11.md`](../../accessibility-engineering/knowledge/settings-controls-markup-and-keyboard-2026-11.md) — markup, keys, WCAG 2.5.7
- [`reach-for-semantic-html-before-aria.md`](./reach-for-semantic-html-before-aria.md), [`form-labels-are-not-placeholders.md`](./form-labels-are-not-placeholders.md), [`a11y-visible-focus-and-target-size.md`](./a11y-visible-focus-and-target-size.md)
