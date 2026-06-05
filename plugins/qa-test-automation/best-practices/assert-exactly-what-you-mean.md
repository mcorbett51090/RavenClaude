# Assert exactly the property you mean — not a superset or a proxy

**Status:** Pattern
**Domain:** Test authoring
**Applies to:** `qa-test-automation`

---

## Why this exists

An assertion that checks more than it needs to becomes a maintenance burden on every unrelated change. Asserting the entire serialized JSON body when you only care about the `status` field means every schema addition breaks the test. Conversely, an assertion that checks a proxy (the response is non-empty) instead of the property (the response contains the expected order ID) produces false passes. Precise assertions catch the defects you care about without triggering on the changes you don't.

## How to apply

For each test, identify the minimum property that, if wrong, would mean the behavior is broken. Assert that property and nothing more. Avoid snapshot assertions for anything other than intentional UI regression tests.

```python
# ❌ Over-asserting: breaks whenever any field is added to the response
def test_place_order():
    response = client.post("/orders", json=order_payload)
    assert response.json() == {
        "id": 42,
        "status": "placed",
        "total_cents": 5000,
        "created_at": "2026-06-05T10:00:00Z",  # brittle timestamp
        "user": {"id": 1, "username": "alice"},  # not the point of this test
    }

# ✅ Assert exactly the properties this test cares about
def test_place_order():
    response = client.post("/orders", json=order_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "placed"
    assert body["total_cents"] == order_payload["total_cents"]
    assert "id" in body  # an order was created; the specific ID is not the point
```

```typescript
// ✅ Playwright: assert the specific user outcome, not all page content
test('displays order confirmation message', async ({ page }) => {
  await checkout.placeOrder();
  // assert the specific outcome; ignore unrelated page content
  await expect(page.getByRole('alert')).toContainText('Order placed');
  await expect(page.getByTestId('order-id')).not.toBeEmpty();
});
```

**Do:**
- Before writing an assertion, ask: "If this breaks, is the feature broken?"
- Use `toMatchObject` / `expect.objectContaining` (partial match) instead of `toEqual` for complex objects when only some fields matter.
- Assert outcome state, not intermediate state — test that the order was placed, not that a specific function was called.

**Don't:**
- Use snapshot tests for API responses that will change as the schema evolves.
- Assert timestamps, generated IDs, or monotonically-increasing counters — use `expect.any(Number)` or a pattern match.
- Use `toBeTruthy` when you mean `toBe(true)` — the former passes for any non-empty string or non-zero number.

## Edge cases / when the rule does NOT apply

Intentional snapshot testing for UI components (visual regression, rendered HTML) is a legitimate use of full-body assertions — but only when the intent is to detect any unintended change, not to verify a specific property.

## See also

- [`../agents/e2e-automation-engineer.md`](../agents/e2e-automation-engineer.md) — owns assertion patterns in E2E tests.
- [`./test-behavior-not-implementation.md`](./test-behavior-not-implementation.md) — precise assertions are the intersection of behavioral testing and minimal coupling.

## Provenance

Codifies the "assert the minimum necessary" principle from Kent Beck's "Test Driven Development: By Example" and the Playwright assertion best-practices guide.

---

_Last reviewed: 2026-06-05 by `claude`_
