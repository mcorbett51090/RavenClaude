# Assert specific outcomes in Apex tests — never write tests that chase coverage numbers only

**Status:** Absolute rule
**Domain:** Apex testing
**Applies to:** `salesforce`

---

## Why this exists

Salesforce's 75% code-coverage requirement is a floor, not a quality metric. A test method that creates data, calls the method under test, and makes no `System.assert*` statement will pass the code-coverage gate while proving absolutely nothing. Worse, it will pass indefinitely even as the logic it exercises silently regresses. The house opinion #9 ("test for bulk (200 records); assert outcomes, not coverage") is explicit: a test's value is its assertions, not the green percentage. A test with no `System.assert*` call is dead weight that consumes org test-run time and gives engineers false confidence.

## How to apply

Every test method must assert at least one observable outcome:

```apex
@isTest
static void testOrderTotalCalculation_bulkBoundary() {
    List<Order__c> orders = TestDataFactory.createOrders(200);
    insert orders;

    Test.startTest();
    OrderService.recalculateTotals(orders);
    Test.stopTest();

    // Assert the outcome, not just that the method ran
    List<Order__c> updated = [SELECT Total__c FROM Order__c WHERE Id IN :orders];
    System.assertEquals(200, updated.size(), 'Expected 200 orders processed');
    for (Order__c o : updated) {
        System.assertNotEquals(null, o.Total__c, 'Total should not be null after recalculation');
        System.assert(o.Total__c >= 0, 'Total must be non-negative');
    }
}
```

Assertion hierarchy (use the most specific available):
1. `System.assertEquals(expected, actual, message)` — exact match
2. `System.assertNotEquals(unexpected, actual, message)` — not-null / not-zero guards
3. `System.assert(condition, message)` — boolean predicate
4. `Assert.areEqual` / `Assert.isNotNull` (new API, Salesforce Spring '23+)

**Do:**
- Include the `message` parameter on every assertion — it surfaces in the failure output and saves debugging time.
- Assert the side effects (records created, emails sent, field values changed) not just the return value.
- When testing exception paths, use `System.assert(false, 'Exception expected')` inside the try block and a `catch` to confirm the exception type.

**Don't:**
- Write a test that creates records, calls the method, and has no `System.assert*` — the compiler won't stop you, but it proves nothing.
- Assert only `results.size() > 0` when you know the exact expected count — weak assertions allow degraded correctness to pass.
- Re-query data and then assert it equals what you inserted without the method transforming it — you're just asserting round-trip serialization.

## Edge cases / when the rule does NOT apply

Integration tests that exercise a full chain may use a single high-level assertion (e.g., "no unhandled exception + final record state is X") as the outcome. The rule is that at least one assertion must be present, not that every line must be asserted.

## See also

- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns Apex test authoring and is the primary enforcer of this rule
- [`./apex-test-data-with-testfactory-not-seealldata.md`](./apex-test-data-with-testfactory-not-seealldata.md) — the complementary rule about test data isolation

## Provenance

Codifies house opinion #9 ("test for bulk (200 records); assert outcomes, not coverage") from CLAUDE.md; standard Apex testing best practice.

---

_Last reviewed: 2026-06-05 by `claude`_
