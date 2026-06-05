# Never Use Color as the Only Signifier

**Status:** Absolute rule
**Domain:** Web Design — Accessibility / visual design
**Applies to:** `web-design`

---

## Why this exists

Approximately 8% of men and 0.5% of women have color vision deficiency. An error state shown only in red, a chart whose lines are distinguished only by hue, or a form field whose "required" status is indicated only by a red label — all are invisible to a meaningful fraction of users. WCAG 1.4.1 (Use of Color, Level A) is one of the most commonly failed criteria in automated audits. The anti-pattern "Color used as the *only* signifier (error states, status indicators)" is in `CLAUDE.md` §4.

## How to apply

**The rule stated precisely (WCAG 1.4.1):**

> Color must not be the *only* visual means of conveying information, indicating an action, prompting a response, or distinguishing a visual element.

**Repair patterns by use case:**

| Use case | Color-only (bad) | Color + secondary signifier (good) |
|---|---|---|
| Error state | Red border on input | Red border + error icon + error message text below |
| Required field | Red label | Red label + asterisk (*) + "Required" in the label |
| Chart / graph lines | Different colors only | Different colors + different dash patterns or shapes |
| Status badge | Green = active, red = inactive | Green badge labeled "Active", red badge labeled "Inactive" |
| Link vs body text | Blue text | Blue text + underline (or other visible distinction) |
| Selected state | Blue highlight | Blue highlight + checkmark icon or bold type |

**Implementation checklist:**

- [ ] Every error state has an icon + text in addition to the color change.
- [ ] Every chart has a pattern or shape redundancy in addition to color.
- [ ] Required form fields are indicated with a text cue ("Required") or an asterisk, not only a color change.
- [ ] Status indicators (badges, dot indicators) have a visible label.

**Do:**
- Test with a color-blindness simulator (Sim Daltonism, Chrome DevTools accessibility emulation, or Figma plugins).
- Use `aria-describedby` or `aria-live` regions to surface error states to screen readers in addition to the visual redundancy.

**Don't:**
- Remove the redundant signifier after a design review says "the red is obvious enough."
- Treat color-blindness simulation as a pass/fail gate — use it to reveal, then apply the repair.
- Use color as the only state indicator in interactive UI (selected, focused, active, disabled) — these all need a non-color signal.

## Edge cases / when the rule does NOT apply

- **Decorative color-coded elements** where the color carries no information that matters to the task (e.g., a purely aesthetic background gradient) — color-only is fine when it is genuinely decorative and no information depends on it.
- **Text on a light background** — the contrast rule (`visual-color-contrast-is-a-constraint`) applies; the use-of-color rule does not (no information is conveyed solely by the color).

## See also

- [`../agents/accessibility-auditor.md`](../agents/accessibility-auditor.md) — audits for WCAG 1.4.1 failures
- [`./visual-color-contrast-is-a-constraint.md`](./visual-color-contrast-is-a-constraint.md) — the companion rule: contrast ratios are checked at design time

## Provenance

Codifies the anti-pattern "Color used as the *only* signifier (error states, status indicators)" from `CLAUDE.md` §4. WCAG 2.2 Success Criterion 1.4.1 Use of Color (Level A). _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
