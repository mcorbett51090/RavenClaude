# Manage focus explicitly when content changes dynamically

**Status:** Absolute rule
**Domain:** Accessibility
**Applies to:** `frontend-engineering`

---

## Why this exists

Single-page applications render content dynamically: a modal opens, a drawer slides in, a route changes, a form submits and shows a success message. The browser's built-in focus management handles none of this — the focus stays wherever it was before the DOM update. A keyboard user or screen-reader user completing a form whose result appears somewhere else on the page has no idea anything happened. Focus management is what makes dynamic UIs navigable for users who cannot see the DOM change.

## How to apply

```tsx
import { useEffect, useRef } from 'react';

// Pattern 1: move focus to new content when it appears
function Modal({ isOpen, children }: { isOpen: boolean; children: React.ReactNode }) {
  const firstFocusableRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) {
      firstFocusableRef.current?.focus();  // move focus into the modal
    }
  }, [isOpen]);

  return isOpen ? (
    <div role="dialog" aria-modal="true">
      <button ref={firstFocusableRef}>Close</button>
      {children}
    </div>
  ) : null;
}

// Pattern 2: announce the result and move focus after a form submit
function ContactForm() {
  const statusRef = useRef<HTMLDivElement>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await submitForm();
    statusRef.current?.focus();  // focus the success/error message
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* fields */}
      <div ref={statusRef} tabIndex={-1} role="status">
        {/* success/error message rendered here */}
      </div>
    </form>
  );
}
```

**Do:**
- Move focus to the first interactive element when a modal or drawer opens.
- Return focus to the trigger element when a modal or drawer closes.
- Move focus to the success/error message after form submission.
- Use `tabIndex={-1}` on non-interactive containers you want to focus programmatically.
- Trap focus inside a modal (`Tab` cycles within the dialog, `Escape` closes it).

**Don't:**
- Use `document.getElementById(...).focus()` without a null check — the element may not be in the DOM yet.
- Set `tabIndex={0}` on non-interactive elements (div, span) — use a semantic button or link instead.
- Trigger focus changes before the DOM update has committed — use `useEffect` or `setTimeout(0)`, not inline.

## Edge cases / when the rule does NOT apply

Client-side route changes in a SPA need a different focus strategy: move focus to the route's `<h1>` or a skip-nav target rather than the first focusable element. This is route-navigation-specific and handled by the routing library or a page-level `useEffect`.

## See also

- [`../agents/react-implementation-engineer.md`](../agents/react-implementation-engineer.md) — owns accessibility in component implementation.
- [`./accessibility-is-implementation.md`](./accessibility-is-implementation.md) — the foundational accessibility rule this extends for focus specifically.

## Provenance

WCAG 2.2 SC 2.1.1 (Keyboard), SC 2.4.3 (Focus Order), and ARIA Authoring Practices Guide (Modal Dialog Pattern). Codifies `react-implementation-engineer`'s accessibility-in-code responsibility.

---

_Last reviewed: 2026-06-05 by `claude`_
