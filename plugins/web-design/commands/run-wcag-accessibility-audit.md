---
description: Run a WCAG 2.2 AA accessibility audit the way it's actually tested — tab the whole page with the mouse unplugged, check semantic-HTML-before-ARIA, verify contrast against the displayed background, confirm visible focus and 44px targets, and check reduced-motion and forced-colors fallbacks.
argument-hint: "[the page/component, e.g. 'the checkout flow' or a path; omit for the current page]"
---

# Run a WCAG accessibility audit

You are running `/web-design:run-wcag-accessibility-audit`. Audit the page or component the user named (`$ARGUMENTS`), following this plugin's `accessibility-auditor` discipline. WCAG 2.2 AA is the floor, not the ceiling — and a Lighthouse-100 page can still be unusable on a keyboard.

## When to use this

A pre-launch a11y gate, remediation prioritization, or ongoing review. Not for purely visual polish that doesn't touch interaction, semantics, or contrast.

## Steps

1. **Tab the whole page with the mouse unplugged** (`a11y-keyboard-operability-every-interactive-surface`): every interactive control must be reachable, operable (Enter/Space/Esc/Arrows), and escapable; focus order follows DOM order (never `tabindex > 0`); a skip link is the first focusable element, visible on `:focus`. A keyboard trap with no return is a SC 2.1.2 failure.
2. **Check semantic HTML before ARIA** (`reach-for-semantic-html-before-aria`): the first rule of ARIA is don't — a `<div onClick>` reinventing a `<button>` is a defect; reach for native `<dialog>` / the Popover API before a bespoke widget. ARIA is correct only where no native element exists (combobox, tree, tablist) — then lean on an APG-accurate primitive.
3. **Verify contrast against the displayed background** (`visual-color-contrast-is-a-constraint`): 4.5:1 normal text, 3:1 large text and UI/focus boundaries — checked over gradients, hover/active states, and image overlays, not just flat white. Color is never the only signifier; pair status with icon + text.
4. **Confirm visible focus and target size** (`a11y-visible-focus-and-target-size`): never bare `outline: none` — shape a `:focus-visible` ring; interactive targets meet the team's 44x44 CSS px default (WCAG 2.2 AA floor is 24px), and the focused element isn't obscured by sticky chrome (SC 2.4.11).
5. **Check motion and forced-colors fallbacks** (`a11y-respect-motion-and-forced-colors-preferences`): every animation/transition/autoplay has a `prefers-reduced-motion: reduce` fallback (gate the View Transitions API too), and the UI survives `forced-colors` mode using system color keywords.
6. **Confirm forms and headings** (`ux-form-design-and-error-handling`, `seo-semantic-structure-and-metadata`): every input has a real `<label>` (placeholder-as-label fails), errors associate via `aria-describedby` and name the fix; one clean heading tree with no level skips.

## Guardrails

- Report findings by severity against WCAG 2.2 AA; an open AA failure past 30 days is a flagged anti-pattern. Don't manufacture findings — if a surface is clean, say so.
- Decorative images take `alt=""` (empty, not omitted); a missing `alt` is a real failure the hook flags.
- Roving tabindex (composite widgets) is the APG-sanctioned exception to "everything reachable by Tab" — don't flag it as a bug.
