# Add data-testid attributes to interactive elements — they are engineering, not optional

**Status:** Absolute rule
**Domain:** Testability
**Applies to:** `frontend-engineering`

---

## Why this exists

End-to-end tests that select elements by text content, CSS class, or DOM position are fragile: a copy change, a style refactor, or a layout tweak breaks them even when the feature is working correctly. `data-testid` attributes are stable, semantically neutral, and explicitly contract-tested — they don't appear in production CSS, they don't affect styling, and they make test intent readable. Adding them is part of implementing a component, not an afterthought for the QA team.

## How to apply

```tsx
// Good: stable selectors for interactive elements
function LoginForm() {
  return (
    <form data-testid="login-form">
      <input
        data-testid="login-email"
        type="email"
        name="email"
        placeholder="Email"
      />
      <input
        data-testid="login-password"
        type="password"
        name="password"
        placeholder="Password"
      />
      <button data-testid="login-submit" type="submit">
        Sign in
      </button>
    </form>
  );
}

// E2E test (Playwright)
await page.getByTestId('login-email').fill('user@example.com');
await page.getByTestId('login-submit').click();
```

**Do:**
- Add `data-testid` to every form, interactive control, key list item, modal, and navigation element.
- Use kebab-case, scoped names: `{component}-{role}` (e.g., `checkout-submit`, `product-card-title`).
- Add `data-testid` to container elements that E2E tests need to scope within (forms, modals, list containers).
- Prefer accessible queries (`getByRole`, `getByLabel`) in unit tests (Testing Library); use `getByTestId` in E2E tests where role queries are too ambiguous.

**Don't:**
- Use CSS classes as test selectors — classes change with design refactors.
- Use text content as the primary E2E selector — copy changes break the test.
- Add `data-testid` to every leaf element — focus on testable units (forms, interactive controls, key landmarks).

## Edge cases / when the rule does NOT apply

Pure presentational or decorative elements (icons, dividers, decorative images) do not need `data-testid`. Server-rendered static pages without interactive elements have nothing to test-id.

## See also

- [`../agents/react-implementation-engineer.md`](../agents/react-implementation-engineer.md) — owns testable markup in component implementation.
- [`./forms-are-controlled-and-validated-at-the-edge.md`](./forms-are-controlled-and-validated-at-the-edge.md) — form components are high-priority targets for test IDs.

## Provenance

Testing Library best practices and the `data-testid` convention used by React Testing Library, Playwright, and Cypress. Codifies `react-implementation-engineer`'s testable-markup responsibility from this plugin's CLAUDE.md.

---

_Last reviewed: 2026-06-05 by `claude`_
