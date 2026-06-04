# E2E test skeleton (Playwright pattern)

```ts
test('user can check out', async ({ page }) => {
  // setup: this test's own data
  await seedCart(testUser);
  await page.goto('/cart');
  // resilient selectors
  await page.getByTestId('checkout-button').click();
  // condition-based wait, NOT sleep
  await expect(page.getByRole('heading', { name: 'Order confirmed' })).toBeVisible();
  // teardown handled by fixture
});
```
- Role/test-id selectors only.
- Await conditions, never `sleep`.
- Per-test data; isolated.
