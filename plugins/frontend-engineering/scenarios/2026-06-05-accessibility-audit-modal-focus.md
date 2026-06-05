---
scenario_id: 2026-06-05-accessibility-audit-modal-focus
contributed_at: 2026-06-05
plugin: frontend-engineering
product: react
product_version: "unknown"
scope: likely-general
tags: [accessibility, focus-trap, aria, keyboard, modal, wcag]
confidence: medium
reviewed: false
---

## Problem

An accessibility audit (from the design side / `web-design`'s WCAG review) flagged the app's custom modal dialog as failing keyboard and screen-reader users. Concrete failures: opening the modal left keyboard focus behind on the trigger button, `Tab` could walk *out* of the open modal into the page behind it, `Esc` didn't close it, screen readers didn't announce the dialog or read its title, and on close, focus dropped to the top of the page (the user lost their place). The component was a `<div>` with an `onClick` overlay and a `className="modal"` — visually a modal, semantically nothing. The team's first instinct was to "add some `aria-*` attributes."

## Constraints context

- The audit (the *what's wrong* / WCAG verdict) is `web-design`'s lane; the *in-code remediation* is this team's (the seam in CLAUDE.md §3).
- The modal was a non-semantic `<div>` soup: no `role`, no managed focus, no keyboard handlers — sprinkling ARIA on top of broken semantics would have made it *announce* better while still being a keyboard trap.
- The app already had React; a battle-tested headless dialog primitive was available and not yet used.
- "Accessible" here meant the WAI-ARIA Authoring Practices dialog pattern: focus moves in on open, is trapped while open, returns to the trigger on close, `Esc` closes, and the dialog is labelled.

## Attempts

- Tried: adding `role="dialog"` + `aria-label` to the existing `<div>`. Made screen readers *announce* a dialog but left every behavioral failure (focus not moved/trapped/restored, no `Esc`). ARIA describes; it does not implement behavior. A labelled keyboard trap is still a keyboard trap.
- Tried: a hand-rolled focus trap (query all focusables, wrap `Tab`/`Shift+Tab` at the edges). Worked for the simple case but missed edge cases — dynamically added content, disabled elements, nested focusables, `contenteditable` — and didn't handle focus *restoration* on close. Re-implementing a solved primitive, badly.
- Tried (the fix): replaced the `<div>` soup with a **headless, accessible dialog primitive** (e.g. Radix UI / React Aria Dialog) that implements the WAI-ARIA dialog pattern correctly, then styled it. Specifically it gave us, for free: focus moved to the dialog on open, focus trapped within while open, focus **restored to the trigger** on close, `Esc` to close, `aria-modal` + the labelling wiring, and the inert/`aria-hidden` treatment of the background.

## Resolution

**Accessibility is implementation, not attributes — semantic behavior first, ARIA only to fill the gaps.** The failures here were behavioral (focus management, keyboard), and ARIA attributes don't supply behavior; they supply *names and roles*. The remediation order:

1. **Use the right primitive / semantics first.** A dialog has a specified interaction pattern (WAI-ARIA APG dialog pattern). Reach for native elements where they exist and a vetted headless primitive for composite widgets — don't rebuild focus-trapping by hand. The first rule of ARIA is "don't use ARIA if a native/semantic solution exists."
2. **Manage focus explicitly for dynamic content.** On open, move focus *into* the dialog; while open, trap it; on close, **restore** it to the element that opened the dialog. Lost focus = a lost user.
3. **Keyboard-operate everything.** `Esc` closes, `Tab`/`Shift+Tab` cycle within, the trigger is a real `<button>`. A mouse-only modal is broken for keyboard and screen-reader users.
4. **Add ARIA last, to label and relate** — `aria-modal`, an accessible name (`aria-labelledby` to the title), and hiding the background — *after* the semantics and behavior are right, not as a substitute for them.
5. **Confirm with the audit owner.** The `web-design` WCAG review verifies the fix; we implement it. (The seam: they audit, we remediate in code.)

**Action for the next engineer:** when an audit flags a custom interactive widget (modal, menu, combobox, tabs, tooltip), don't patch it with `aria-*` — check whether a vetted headless primitive implements the WAI-ARIA pattern and adopt it, then style and label. Hand-rolled focus traps are a recurring source of subtle a11y bugs.

Cross-reference: this is the field-note complement to [`../best-practices/accessibility-is-implementation.md`](../best-practices/accessibility-is-implementation.md) and [`../best-practices/focus-management-for-dynamic-content.md`](../best-practices/focus-management-for-dynamic-content.md); the skill is [`../skills/accessibility-audit-and-fix/SKILL.md`](../skills/accessibility-audit-and-fix/SKILL.md). The WCAG *audit* is `web-design`'s lane; this is in-code remediation (CLAUDE.md §3 seam). Pattern reference: WAI-ARIA Authoring Practices — Dialog (Modal) Pattern, https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ (retrieved 2026-06-05).
