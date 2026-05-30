# Reach for the semantic element before adding ARIA

**Status:** Absolute rule — semantic-HTML-first is a P1 design constraint, not a polish item.

**Domain:** Accessibility / Semantic HTML

**Applies to:** `web-design`

---

## Why this exists

The first rule of ARIA is: **don't.** Most "wrong" ARIA is worse than no ARIA — a `role` or state that drifts out of sync with the visible UI breaks the accessible-name calculation and confuses every screen reader differently (NVDA / JAWS / VoiceOver / TalkBack each behave differently for hand-rolled widgets). Native elements ship keyboard handling, focus, and roles for free; re-implementing them in `<div>` + ARIA is how teams ship a Lighthouse-100 page that is still unusable on a keyboard. WCAG 2.2 AA is the floor (house opinion #1), and the EU Accessibility Act made this a legal requirement, not just a quality one.

## How to apply

Prefer the element that already carries the role. Use the modern platform primitives (`<dialog>`, the Popover API) before a JS widget library.

```html
<!-- Don't: a div pretending to be a button, reinventing what semantics give free -->
<div class="btn" onclick="submit()">Submit</div>

<!-- Do: the real element — keyboard, focus, and role come for free -->
<button type="submit">Submit</button>

<!-- Do: native dialog handles focus-trap + Esc + return-focus; no ARIA needed -->
<dialog id="confirm">
  <form method="dialog"><button>Close</button></form>
</dialog>
```

**Do:**
- Use the landmark / heading / list / form / table element that matches the meaning.
- Reach for native `<dialog>` + the Popover API before a bespoke modal/menu component.
- When ARIA is unavoidable, make `aria-label` match the accessible-name calculation — never `aria-label` away the visible text.

**Don't:**
- Use `<div onClick>` as an interactive surface.
- Remove the focus indicator (`outline: none`) with no replacement.
- Use `tabindex > 0` to "fix" focus order — fix the DOM order instead.

## Edge cases / when the rule does NOT apply

- **No native element exists** (combobox, tree, tablist) — then ARIA is correct. Lean on an accessible primitive (Radix / React Aria / Fluent) that already implements the APG pattern rather than re-deriving roles, states, and keyboard handling.
- **Augmenting, not replacing** — `aria-describedby` to associate a form error with its field is additive and correct; it is not a substitute for a `<label>`.

## See also

- [`../knowledge/web-platform-capabilities-2026.md`](../knowledge/web-platform-capabilities-2026.md) — native `<dialog>` / Popover API; WCAG 2.2 + EU Accessibility Act
- [`../knowledge/design-systems-and-component-architecture-2026.md`](../knowledge/design-systems-and-component-architecture-2026.md) — a11y-built-in primitives, polymorphism (`as`/`asChild`) for semantic correctness
- [`../agents/accessibility-auditor.md`](../agents/accessibility-auditor.md) — the agent that enforces this
- [`./budget-core-web-vitals-before-build.md`](./budget-core-web-vitals-before-build.md)

## Provenance

Distilled from the `web-design` plugin constitution house opinions #1 and #5, the `accessibility-auditor` agent's "first rule of ARIA: don't" stance and anti-pattern list, and the platform-features section of `web-platform-capabilities-2026.md` (retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
