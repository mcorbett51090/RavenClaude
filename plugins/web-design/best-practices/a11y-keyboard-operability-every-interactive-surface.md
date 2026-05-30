# Every interactive surface must be fully keyboard-operable

**Status:** Absolute rule — keyboard operability is a P1 surface, equal to mouse/touch. A control a keyboard user cannot reach, activate, or escape is a WCAG 2.1.1 failure, not a polish gap.

**Domain:** Accessibility / Keyboard

**Applies to:** `web-design`

---

## Why this exists

Mouse-only UIs silently exclude keyboard users, screen-reader users, and anyone with a motor impairment. The failure is invisible in design review because the designer uses a mouse — it only surfaces when someone tabs through the page. WCAG 2.2 SC 2.1.1 (Keyboard) and SC 2.1.2 (No Keyboard Trap) are Level A — the lowest bar, the one the EU Accessibility Act treats as legally non-negotiable [verify-at-build — WCAG version / EAA scope]. Reaching for the native element (see [`./a11y-semantic-html-before-aria`](./reach-for-semantic-html-before-aria.md)) gives you Tab/Enter/Space/Esc handling for free; the moment you hand-roll a control on a `<div>`, you own all of it.

## How to apply

Tab through the whole page with the mouse unplugged. Every interactive control must be reachable, operable, and (if it traps focus) escapable. DOM order is focus order — fix the source order, never `tabindex` your way out.

```html
<!-- Skip link: first focusable element, visible ON focus (not permanently hidden) -->
<a href="#main" class="skip-link">Skip to content</a>

<!-- A control built on a div needs role + tabindex + key handling re-implemented by hand.
     Prefer <button>; if you must, wire ALL of it: -->
<div role="button" tabindex="0" id="toggle"
     onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();toggle()}"
     onclick="toggle()">Toggle</div>
```

```css
.skip-link {
  position: absolute;
  inset-block-start: -3rem; /* off-screen until focused */
}
.skip-link:focus {
  inset-block-start: 0;
} /* visible the instant it receives focus */
```

**Do:**

- Test every flow with Tab / Shift+Tab / Enter / Space / Esc / Arrow keys before declaring done.
- Provide a skip link as the first focusable element; reveal it on `:focus`.
- Match focus order to reading order via DOM order; use `tabindex="0"` (reachable) and `tabindex="-1"` (programmatically focusable) only.

**Don't:**

- Use `tabindex` greater than `0` to "fix" focus order — it creates an unmaintainable parallel tab sequence.
- Trap focus anywhere except an intentional modal (and there, provide Esc-to-close + return focus).
- Bind behavior to `mouseover`/`click` only — keyboard users never fire those.

## Edge cases / when the rule does NOT apply

- **Genuinely non-interactive content** (static text, decorative images) is not in the tab order and must not be — adding `tabindex="0"` to a `<p>` is noise for screen-reader users.
- **Roving tabindex** (one `tabindex="0"`, siblings `-1`, arrows move focus) is the correct pattern for composite widgets (toolbars, radio groups, tablists) — that is the APG-sanctioned exception to "everything reachable by Tab."

## See also

- [`./reach-for-semantic-html-before-aria.md`](./reach-for-semantic-html-before-aria.md) — native elements give keyboard handling for free
- [`./a11y-visible-focus-and-target-size.md`](./a11y-visible-focus-and-target-size.md) — the focus must also be _visible_ and the target big enough
- [`../knowledge/web-design-decision-trees.md`](../knowledge/web-design-decision-trees.md) — "Native element vs ARIA widget" tree
- [`../agents/accessibility-auditor.md`](../agents/accessibility-auditor.md) — enforces this; [`../agents/frontend-implementer.md`](../agents/frontend-implementer.md) — implements it

## Provenance

Distilled from the `accessibility-auditor` agent's "keyboard navigation as a P1 surface" stance + anti-pattern list (focus trap without return, `tabindex > 0`, skip link broken on first tab) and constitution house opinion #5, cross-checked against the WCAG 2.2 notes in `web-platform-capabilities-2026.md` (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
