# Build test data with a TestDataFactory — never `@isTest(SeeAllData=true)`

**Status:** Absolute rule — `SeeAllData=true` is banned; tests create their own data.

**Domain:** Apex / testing

**Applies to:** `salesforce`

---

## Why this exists

`@isTest(SeeAllData=true)` lets a test read whatever records happen to live in the org. That makes the test **non-deterministic and non-portable**: it passes in the dev sandbox where someone left the right data, then fails in a clean scratch org, in CI, or after a sandbox refresh — for reasons unrelated to the code under test. It also couples your suite to org state you don't control. A `TestDataFactory` creates exactly the records the test needs, in test context, so the test is hermetic and reproducible. This is house opinion #10.

## How to apply

Centralize record creation in a reusable factory, insert only what the test asserts on, and prove behavior at bulk scale (200 records) — assert outcomes, not coverage.

```apex
@isTest
public class TestDataFactory {
    public static List<Account> accounts(Integer n) {
        List<Account> rows = new List<Account>();
        for (Integer i = 0; i < n; i++) {
            rows.add(new Account(Name = 'Test Acct ' + i));
        }
        return rows;   // caller inserts — factory builds, test controls DML/assertions
    }
}

@isTest
private class AccountRollupTest {
    @isTest
    static void rollupHandlesBulk() {
        List<Account> accts = TestDataFactory.accounts(200);   // bulk, not 1
        insert accts;

        Test.startTest();
        // ...exercise the trigger/handler...
        Test.stopTest();

        // assert the OUTCOME, not just that code ran
        for (Account a : [SELECT Number_Of_Contacts__c FROM Account WHERE Id IN :accts]) {
            System.assertEquals(0, a.Number_Of_Contacts__c, 'fresh account has no contacts');
        }
    }
}
```

**Do:**
- Create all test data in a `@isTest` `TestDataFactory` (or `@testSetup` method) — fresh every run.
- Test with **200 records** to prove bulk-safety, not a single happy-path row.
- Assert on **outcomes** (field values, record counts, error messages), never on coverage alone.
- Wrap the code under test in `Test.startTest()` / `Test.stopTest()` to get a fresh limit context.

**Don't:**
- Use `@isTest(SeeAllData=true)` to borrow org data — a clean org has none.
- Ship a green-bar test with zero `System.assert*` calls; coverage is not a test.
- Hard-code record/RecordType IDs in test data — query by DeveloperName or use the factory.

## Edge cases / when the rule does NOT apply

A handful of object types are **not** insertable in test context and are visible even with `SeeAllData=false` — e.g. `User`, `Profile`, `RecordType`, `Organization`, and some setup/metadata objects. Querying *those* in a test is unavoidable and is not a `SeeAllData` violation. Where a feature genuinely depends on org-managed data that can't be created in a test (rare), scope `SeeAllData=true` to the **single method** that needs it and document why — never the whole class. Standard pricebook access uses `Test.getStandardPricebookId()` rather than a `SeeAllData` read.

## See also

- [`../templates/apex-test-class.md`](../templates/apex-test-class.md) — the bulk test class + factory skeleton
- [`./apex-one-trigger-per-object-handler.md`](./apex-one-trigger-per-object-handler.md) — the handler these tests exercise at bulk scale
- [`./bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — what the 200-record test proves
- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns the Salesforce bulk/assert discipline; generic scaffolding escalates to `ravenclaude-core/test-author`

## Provenance

Codifies house opinions #9 and #10 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the `apex-engineer` discipline #6 and [`../templates/apex-test-class.md`](../templates/apex-test-class.md). The `SeeAllData` portability failure and the test-context object-visibility list are documented Salesforce platform behaviors.

---

_Last reviewed: 2026-05-30 by `claude`_
