# Use role selectors and test IDs, not CSS classes or XPath

**Status:** Absolute rule
**Domain:** E2E test automation
**Applies to:** `qa-test-automation`

---

## Why this exists

CSS selectors tied to styling classes (`button.btn-primary.checkout`) and brittle XPath expressions (`//div[@class='modal']//button[2]`) break whenever a designer renames a class or restructures the DOM — not because the feature changed, but because the styling or markup changed. These failures are false alarms: the feature works, but the test fails. Role-based selectors (`getByRole('button', { name: 'Place Order' })`) are stable because they reflect user-observable semantics, not implementation details. Where role selectors aren't sufficient, `data-testid` attributes provide a stable, explicit contract between the test and the UI.

## How to apply

Prefer selectors in this order:
1. **Role + accessible name** (`getByRole`, `getByLabel`) — tests what a screen reader sees; stable.
2. **Test ID** (`data-testid` attribute) — explicit contract; immune to style changes.
3. **Text content** (`getByText`) — only when the text is stable and not i18n-translated.
4. **CSS class / XPath** — last resort, never for elements that may be restyled.

```typescript
// ✅ Preferred: role selector — works even if the class changes
await page.getByRole('button', { name: 'Place Order' }).click();

// ✅ Acceptable: test ID — developer explicitly supports this selector
await page.getByTestId('checkout-submit-btn').click();

// ❌ Avoid: CSS class — breaks on every restyle
await page.locator('.btn-primary.checkout-submit').click();

// ❌ Avoid: XPath — breaks on DOM restructure
await page.locator('//form[@id="checkout"]//button[last()]').click();
```

In the component, add `data-testid` only for interactive elements that don't have a clear role/label:

```tsx
// React component — add test ID when role selector isn't available
<button
  type="submit"
  data-testid="checkout-submit-btn"
  className={styles.primaryButton}
>
  Place Order
</button>
```

**Do:**
- Discuss selector strategy with the frontend team — `data-testid` attributes are a cross-team contract.
- Remove `data-testid` attributes in production builds if your bundle optimizer supports it (or keep them — they are harmless).
- Use `aria-label` or visually-hidden text to give elements accessible names when the visible label is ambiguous.

**Don't:**
- Use `page.locator('nth=2')` to select the second button; it's purely positional and brittle.
- Select elements by placeholder text (`getByPlaceholder`) for primary navigation; placeholder text often changes.
- Use test IDs as a crutch to avoid adding proper accessible names to elements.

## Edge cases / when the rule does NOT apply

Data tables, charts, and complex visualizations sometimes cannot be meaningfully addressed by role or test ID — a positional or index selector may be acceptable for a specific cell, clearly documented and confined to the page object.

## See also

- [`../agents/e2e-automation-engineer.md`](../agents/e2e-automation-engineer.md) — owns selector strategy and test structure.
- [`./page-objects-own-selectors.md`](./page-objects-own-selectors.md) — selectors live in page objects, not in test files.

## Provenance

Codifies the Playwright selector priority guidance (playwright.dev/docs/best-practices#use-user-facing-attributes) and the Testing Library selector philosophy (testing-library.com/docs/queries/about).

---

_Last reviewed: 2026-06-05 by `claude`_
