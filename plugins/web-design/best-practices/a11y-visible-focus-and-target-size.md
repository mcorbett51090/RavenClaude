# Keep focus visible and pointer targets large enough (WCAG 2.2 additions)

**Status:** Absolute rule — `:focus-visible` is shaped to the design system but never removed, and interactive targets meet the WCAG 2.2 minimum size.

**Domain:** Accessibility / Focus & Pointer

**Applies to:** `web-design`

---

## Why this exists

WCAG 2.2 added two success criteria that older codebases routinely fail: **SC 2.4.11 Focus Not Obscured (Minimum, AA)** and **SC 2.5.8 Target Size (Minimum, AA, 24×24 CSS px)** [verify-at-build — WCAG 2.2 SC numbers/thresholds]. The most common violation predates them: `outline: none` with no replacement, which leaves keyboard users with no idea where they are. The team's stricter house default is **44×44 CSS px** touch targets (SC 2.5.5 Enhanced / AAA, the mobile-first norm), so meeting it satisfies both the AA floor and the team bar. Visible focus and adequate target size are also the two cheapest a11y wins — they cost a few lines of CSS and prevent the most-reported real-world complaints.

## How to apply

Replace the default focus ring with a design-system ring via `:focus-visible` (so it shows for keyboard, not on mouse click), and size every tap target.

```css
/* Never bare outline:none. Shape the ring; keep it visible. */
:focus-visible {
  outline: 2px solid var(--color-focus-ring);
  outline-offset: 2px;
}
button:focus:not(:focus-visible) {
  outline: none;
} /* suppress ring on mouse-click only */

/* Target size: team default 44px; WCAG 2.2 AA floor is 24px. */
.btn,
.icon-button,
a.nav-link {
  min-block-size: 44px;
  min-inline-size: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
```

**Do:**

- Use `:focus-visible` so keyboard users see the ring and mouse users don't get a click-flash.
- Ensure the focused element isn't hidden behind a sticky header/footer (SC 2.4.11) — add `scroll-margin` or offset.
- Give icon-only buttons real hit area (padding counts) even if the glyph is small.

**Don't:**

- Ship `outline: none` (or `outline: 0`) without an equally-clear replacement.
- Rely on `:focus` alone for the ring — it fires on mouse click too, which trained a generation of devs to remove it.
- Pack interactive targets closer than the minimum with no spacing exception.

## Edge cases / when the rule does NOT apply

- **Inline targets** (a link inside a sentence) are exempt from SC 2.5.8 — you cannot make body text 44px tall. The criterion has an inline exception.
- **Equivalent control available** — a small target is allowed if the same action has a compliant-sized alternative on the page.
- **User-agent default focus** that is already clearly visible against the design can be kept; the rule is "visible," not "custom."

## See also

- [`./a11y-keyboard-operability-every-interactive-surface.md`](./a11y-keyboard-operability-every-interactive-surface.md) — focus visibility is meaningless without keyboard reachability
- [`./visual-color-contrast-is-a-constraint.md`](./visual-color-contrast-is-a-constraint.md) — the focus ring itself needs 3:1 contrast against adjacent colors
- [`../agents/accessibility-auditor.md`](../agents/accessibility-auditor.md) (target size ≥ 44×44, focus removed = anti-pattern); [`../agents/visual-designer.md`](../agents/visual-designer.md)

## Provenance

From the `accessibility-auditor` surface area (target size ≥ 44×44 CSS px per WCAG 2.5.5; focus indicator removed = flagged anti-pattern) and the WCAG 2.2 section of `web-platform-capabilities-2026.md` (retrieved 2026-05-28). WCAG 2.2 SC 2.4.11 / 2.5.8 added in the 2023 recommendation.

---

_Last reviewed: 2026-05-30 by `claude`_
