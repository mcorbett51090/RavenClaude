# Page objects own the selectors — test logic never queries the DOM directly

**Status:** Pattern
**Domain:** E2E test automation
**Applies to:** `qa-test-automation`

---

## Why this exists

When E2E tests scatter `page.locator('.checkout-btn')` calls across dozens of test files, a single UI refactor that renames a class or restructures a component produces 30 simultaneous failures. The page-object pattern (or its modern equivalent: component/fixture wrappers) centralizes all selector knowledge in one place. When the DOM changes, you update one file; all tests that use it keep passing.

## How to apply

Create a page-object (or Playwright component fixture) class for each significant page or UI region. Expose named actions (`checkout.placeOrder()`) and state queries (`checkout.orderTotal()`) — not selectors. Tests call actions; page objects call selectors.

```typescript
// playwright/pages/CheckoutPage.ts — the page object
export class CheckoutPage {
  constructor(private page: Page) {}

  // Selectors are private — never leak to tests
  private orderButton = () => this.page.getByRole('button', { name: 'Place Order' });
  private orderTotal = () => this.page.getByTestId('order-total');
  private successBanner = () => this.page.getByRole('alert').filter({ hasText: 'Order placed' });

  async placeOrder() {
    await this.orderButton().click();
    await this.successBanner().waitFor();
  }

  async getOrderTotal(): Promise<string> {
    return this.orderTotal().innerText();
  }
}

// playwright/tests/checkout.spec.ts — test uses actions, not selectors
test('places an order with valid card', async ({ page }) => {
  const checkout = new CheckoutPage(page);
  await checkout.placeOrder();
  expect(await checkout.getOrderTotal()).toMatch(/\$\d+\.\d{2}/);
});
```

**Do:**
- Keep selectors private to the page object — expose only named actions and assertions.
- One page object per page or major UI region, not one per test file.
- Name actions after user intent (`login()`, `addToCart()`) not after DOM mechanics (`clickButton()`).
- Use Playwright fixtures to inject page objects into tests — avoids construction boilerplate.

**Don't:**
- Let test files import Playwright locators or call `page.locator()` directly.
- Create a single mega-page-object for the whole application — one per meaningful UI region.
- Put assertions inside page-object actions (the test decides what to assert; the page object navigates).

## Edge cases / when the rule does NOT apply

Very small test suites (< 5 E2E tests) with a single UI page may not warrant page objects — inline locators are acceptable until the suite grows. Add page objects at the first sign of selector duplication.

## See also

- [`../agents/e2e-automation-engineer.md`](../agents/e2e-automation-engineer.md) — owns E2E test structure and the page-object pattern.
- [`./test-ids-over-css-selectors.md`](./test-ids-over-css-selectors.md) — page objects should use test IDs or role selectors, not CSS classes.

## Provenance

Codifies the Page Object pattern from Martin Fowler's original 2013 article and its modern expression in Playwright's recommended fixture pattern (playwright.dev/docs/pom).

---

_Last reviewed: 2026-06-05 by `claude`_
