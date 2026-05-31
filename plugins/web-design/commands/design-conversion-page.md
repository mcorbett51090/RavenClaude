---
description: Design a conversion-focused page or form mobile-first — one dominant CTA per screen, all five screen states (default/empty/loading/error/success) designed, forms with real labels validated on blur with fix-oriented inline errors, real copy in the mocks, and accessibility built in from wireframe.
argument-hint: "[the page/form + goal, e.g. 'a signup page' or 'fix this form's conversion']"
---

# Design a conversion page

You are running `/web-design:design-conversion-page`. Design (or remediate) the conversion surface the user described (`$ARGUMENTS`), following this plugin's `ux-designer` + `content-strategist` discipline. Conversion design is choosing what to remove, not what to add.

## When to use this

A landing page, signup/checkout form, pricing page, or a low-converting flow being redesigned. Not for an information-architecture / sitemap pass (that's a different workflow) and not for pure visual theming (use the token scaffold).

## Steps

1. **One dominant CTA per screen** (`ux-one-cta-and-state-coverage`): pick the single primary action, give it visual dominance, and demote secondary actions to subordinate weight (two CTAs max). Five competing equal-weight CTAs split attention and lower all of them; navigation menus aren't CTAs.
2. **Design all five screen states** (`ux-one-cta-and-state-coverage`): default, empty, loading, error, and success are each real surfaces. Treat the empty state as a conversion moment ("here's how to start" + one CTA), use skeleton screens that match the final layout over blocking spinners, and design the error state — never ship only the happy path.
3. **Design forms for completion** (`ux-form-design-and-error-handling`): every input pairs with a real `<label>` (never placeholder-as-label); mark required *and* optional explicitly; validate on blur not keystroke; on submit, focus the first error and show all errors inline via `aria-describedby`. The disabled-submit pattern is dead — show it enabled, validate on click, surface the error.
4. **Write microcopy that names the fix** (`ux-form-design-and-error-handling`, `content-readability-and-hierarchy`): CTAs are verbs with destination context (never "click here"); error messages name the fix ("Add the @ — e.g. name@company.com"), not just "invalid"; lead each section with its point at one held reading level.
5. **Use real copy, mobile-first, a11y from the start** (`frontend-fluid-type-and-space`, `reach-for-semantic-html-before-aria`): real copy in the mocks (lorem ipsum hides layout problems realistic text lengths cause); design narrowest-first and expand up; native form semantics and keyboard operability designed in from wireframe, not bolted on.

## Guardrails

- Don't give a destructive action the same visual weight as cancel; confirm irreversible submits with distinct CTA weight, not a disabled button.
- Use the right `type`/`inputmode`/`autocomplete` so mobile keyboards and autofill help; never rely on color alone for the error state (pair icon + text).
- Pull the conversion measurement plan and trust-signal placement from the `conversion-design` skill; route any auth / user-data handling through `ravenclaude-core/security-reviewer`.
