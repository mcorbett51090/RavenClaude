---
name: accessibility-audit-and-fix
description: "Actionable checklist and fix patterns for WCAG 2.1 AA compliance in React apps — automated scanning, keyboard navigation, focus management, ARIA usage, color contrast, and the most common component-level failures."
---

# Accessibility Audit and Fix

## When to invoke

Use when reviewing a React component or page for accessibility correctness, remediating audit findings, or adding accessibility checks to CI. Note the boundary: the WCAG *design audit* (color palettes, visual design) belongs to `web-design`; this skill covers the **implementation** side — semantic HTML, ARIA, keyboard, and focus in code.

## Step 1 — Automated scanning baseline

Run automated tools first — they catch ~30–40% of WCAG issues with zero manual effort:

```bash
# In CI (axe-core via jest-axe)
npm install --save-dev jest-axe

# In component tests
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

it('has no accessibility violations', async () => {
  const { container } = render(<MyComponent />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

Also run [axe DevTools browser extension](https://www.deque.com/axe/) on the running page for full-page context.

## Step 2 — Keyboard navigation audit

Tab through every interactive element on the page. Check:

| Check | Pass condition |
|---|---|
| Every interactive element is reachable by Tab | No focusable elements skipped |
| Tab order follows visual reading order | No surprising jumps |
| Custom components (dropdowns, modals) support Escape | Modal closes, dropdown collapses |
| Arrow keys work in composite widgets | Listbox, menubar, tabs use arrow keys, not Tab |
| No keyboard trap | User can always leave the component |

**Common fix — custom button built from `<div>`:**
```tsx
// Wrong
<div onClick={handleClick}>Submit</div>

// Right — use a real button
<button type="button" onClick={handleClick}>Submit</button>
```

If you must use a non-button element (rare): add `role="button"`, `tabIndex={0}`, and a `onKeyDown` handler for Enter/Space.

## Step 3 — Focus management

When content changes dynamically, focus must follow:

```tsx
// Dialog open — move focus to first focusable element
const firstFocusableRef = useRef<HTMLButtonElement>(null);
useEffect(() => {
  if (isOpen) firstFocusableRef.current?.focus();
}, [isOpen]);

// Dialog close — return focus to the trigger
const triggerRef = useRef<HTMLButtonElement>(null);
useEffect(() => {
  if (!isOpen) triggerRef.current?.focus();
}, [isOpen]);
```

**Focus trap in modals:** use `focus-trap-react` or manually cycle through `querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])')`.

## Step 4 — ARIA: when to use, when not to

| Situation | Right approach |
|---|---|
| Simple button, link, input | Native HTML element — no ARIA needed |
| Icon-only button | `<button aria-label="Close dialog">` |
| Live region (toast, status) | `<div role="status" aria-live="polite">` |
| Custom select/listbox | `role="listbox"`, `role="option"`, `aria-selected` |
| Error message linked to input | `aria-describedby="error-id"` on the input |
| Loading state | `aria-busy="true"` on the container |
| Decorative image | `alt=""` (empty alt, not missing) |

**First rule of ARIA:** don't use ARIA if a native HTML element does the job. Adding `role="button"` to a `<div>` is always worse than using `<button>`.

## Step 5 — Form accessibility checklist

- Every `<input>` has an associated `<label>` (via `htmlFor`/`id` or wrapping) — placeholder is not a label.
- Required fields: `aria-required="true"` or the native `required` attribute.
- Error states: `aria-invalid="true"` on the input + `aria-describedby` pointing to the error message element.
- Fieldsets group related inputs; `<legend>` describes the group.

```tsx
<div>
  <label htmlFor="email">Email address</label>
  <input
    id="email"
    type="email"
    aria-required="true"
    aria-invalid={hasError}
    aria-describedby={hasError ? "email-error" : undefined}
  />
  {hasError && <span id="email-error" role="alert">Enter a valid email</span>}
</div>
```

## Step 6 — Color and contrast (implementation checks)

Automated contrast checks in code:
- `eslint-plugin-jsx-a11y` catches hardcoded hex/rgb values with low contrast.
- For dynamic/themed color: run [Lighthouse accessibility audit](https://developers.google.com/web/tools/lighthouse) on the running app.

WCAG AA minimums: 4.5:1 for normal text, 3:1 for large text (18pt+ or 14pt bold) and UI components.

## Pitfalls

- **`aria-label` on a container div wrapping visible text** — the ARIA label overwrites the visible label for screen readers; only use `aria-label` when there is no visible text.
- **`role="presentation"` on interactive elements** — removes the element from the accessibility tree while keeping it visually interactive; users on assistive technology can't reach it.
- **Focus outline removed globally** — `*:focus { outline: none }` fails keyboard users; use `:focus-visible` to remove outlines only for mouse users.
- **Toast/alert not announced** — a toast that appears visually but has no `aria-live` region is invisible to screen readers.
- **Testing only with axe** — automated tools miss 60%+ of issues; keyboard tab-through and screen reader smoke test (NVDA/VoiceOver) are required for a real pass.
