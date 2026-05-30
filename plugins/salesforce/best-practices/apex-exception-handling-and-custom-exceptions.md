# Catch deliberately, throw typed custom exceptions, never swallow

**Status:** Pattern — strong default; an empty or over-broad `catch` is a defect, not a style choice.

**Domain:** Apex / error handling

**Applies to:** `salesforce`

---

## Why this exists

Apex exception handling fails in two opposite directions, both common. The first is **swallowing**: a bare `catch (Exception e) {}` that hides a real failure, so a partial-success DML or a failed callout silently corrupts data with no log and no user feedback. The second is **over-catching**: wrapping a whole method in one `try/catch (Exception e)` that turns a `NullPointerException` (a bug to fix) and a `DmlException` (a recoverable validation failure) into the same generic message. Typed custom exceptions and narrow catches make failures **observable, classifiable, and testable** — and they let a trigger surface a clean `addError` to the user instead of an unhandled stack trace.

## How to apply

Define a domain `class … extends Exception`, throw it for expected business-rule failures, catch the *specific* system exceptions you can actually handle, and always either re-throw, `addError`, or log — never nothing.

```apex
// Define a typed exception per domain — the name IS the documentation.
public class InsufficientCreditException extends Exception {}

public with sharing class OrderService {
    public void submit(List<Order__c> orders) {
        for (Order__c o : orders) {
            if (o.Amount__c > availableCredit(o.Account__c)) {
                // expected business failure — typed, catchable, assertable in tests
                throw new InsufficientCreditException(
                    'Order ' + o.Name + ' exceeds available credit');
            }
        }
        try {
            insert orders;
        } catch (DmlException e) {                 // catch the SPECIFIC type you handle
            for (Integer i = 0; i < e.getNumDml(); i++) {
                // attribute the failure back to the offending row
                orders[e.getDmlIndex(i)].addError(e.getDmlMessage(i));
            }
            throw e;                               // re-throw if the caller must also know
        }
        // NO bare catch (Exception e) {} — never swallow
    }
}
```

**Do:**
- Throw a **typed** `extends Exception` for expected business-rule failures; assert on the type in tests.
- Catch the **narrowest** system exception you can actually recover from (`DmlException`, `CalloutException`, `QueryException`).
- In triggers, translate a caught failure into `record.addError(...)` so the user sees a clean, row-scoped message.
- Use `Database.insert(records, false)` + `getErrors()` when you need **partial success** instead of all-or-nothing.

**Don't:**
- Write a bare `catch (Exception e) {}` — it converts a failure into silent data corruption.
- Catch `Exception` broadly when you mean to catch one specific kind — you'll mask real bugs.
- Catch and re-throw with the original lost; chain it or include `e.getMessage()` + `e.getStackTraceString()`.

## Edge cases / when the rule does NOT apply

A top-level **boundary** (a Queueable/Batch `execute`, a `@AuraEnabled` controller method, a scheduled job) legitimately catches broadly to log-and-continue or to return a controlled error to the client — but it logs (Platform Event, custom object, or `System.debug` with `LoggingLevel.ERROR`), it does not swallow. Some exceptions are **uncatchable** by design — `System.LimitException` (governor limits) cannot be caught to "retry past the limit," which is the platform telling you to fix the design, not handle the symptom. Assertion failures from `System.assert` in tests are also not meant to be caught.

## See also

- [`./apex-soql-in-loops-is-a-defect.md`](./apex-soql-in-loops-is-a-defect.md) — the uncatchable LimitException that means "redesign, don't catch"
- [`./apex-test-data-with-testfactory-not-seealldata.md`](./apex-test-data-with-testfactory-not-seealldata.md) — test the throw path, asserting the typed exception
- [`../knowledge/apex-async-patterns.md`](../knowledge/apex-async-patterns.md) — async boundaries are where log-and-continue belongs
- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns server-side error handling
- Salesforce Apex Developer Guide — "Exception Handling in Apex" (custom exceptions, `DmlException` methods) `[unverified — training knowledge; verify-at-build]`

## Provenance

Reflects the `apex-engineer` server-side discipline in [`../CLAUDE.md`](../CLAUDE.md). The `extends Exception` custom-exception mechanism, the `DmlException.getDmlIndex/getDmlMessage` accessors, the `Database.insert(.., false)` partial-success contract, and the uncatchable nature of `LimitException` are documented Apex platform behaviors; specific method signatures are tagged `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
