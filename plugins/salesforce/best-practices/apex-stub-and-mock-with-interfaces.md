# Isolate external dependencies in Apex tests using interfaces and StubProvider — not SeeAllData or live callouts

**Status:** Pattern
**Domain:** Apex / testing
**Applies to:** `salesforce`

---

## Why this exists

Apex tests that reach outside their own transaction — calling a live web service, asserting on org data they did not create, or hard-coupling to a concrete class's implementation — are brittle by design: they break when the external system is down, when another test creates conflicting data, or when an internal implementation detail changes. Two Salesforce primitives solve this: **Apex interfaces + `Test.createStub()`** (`StubProvider`) for faking the callable layer, and **`HttpCalloutMock` / `StaticResourceCalloutMock`** for faking HTTP responses. Neither requires touching the org's real data. Tests that use them verify the *interaction contract* and unit-test the calling code in isolation — which is the correct scope for a unit test.

## How to apply

### Pattern 1 — Interface + StubProvider

```apex
// 1. Define an interface for the dependency
public interface AccountService {
    List<Account> getByIndustry(String industry);
}

// 2. Real implementation (production code)
public class AccountServiceImpl implements AccountService {
    public List<Account> getByIndustry(String industry) {
        return [SELECT Id, Name FROM Account WHERE Industry = :industry LIMIT 200];
    }
}

// 3. In the test class — create a stub via StubProvider
@isTest
private class OpportunityControllerTest {
    private class AccountServiceStub implements System.StubProvider {
        public Object handleMethodCall(
            Object stubbedObject,
            String stubbedMethodName,
            Type returnType,
            List<Type> paramTypes,
            List<String> paramNames,
            List<Object> args
        ) {
            if (stubbedMethodName == 'getByIndustry') {
                Account a = new Account(Name = 'Test Co', Industry = (String) args[0]);
                return new List<Account>{ a };
            }
            return null;
        }
    }

    @isTest
    static void returnsAccountsFromService() {
        AccountService stub = (AccountService) Test.createStub(
            AccountService.class, new AccountServiceStub()
        );
        // Inject stub into class under test
        OpportunityController ctrl = new OpportunityController(stub);
        List<Account> result = ctrl.getIndustryAccounts('Technology');
        System.assertEquals(1, result.size(), 'Expected stubbed account');
        System.assertEquals('Technology', result[0].Industry, 'Industry should match');
    }
}
```

### Pattern 2 — HttpCalloutMock for callout tests

```apex
@isTest
global class MockHttpResponse implements HttpCalloutMock {
    global HTTPResponse respond(HTTPRequest req) {
        HTTPResponse res = new HTTPResponse();
        res.setHeader('Content-Type', 'application/json');
        res.setBody('{"status":"ok"}');
        res.setStatusCode(200);
        return res;
    }
}

@isTest
static void calloutReturnsOk() {
    Test.setMock(HttpCalloutMock.class, new MockHttpResponse());
    MyCalloutService svc = new MyCalloutService();
    String result = svc.ping();
    System.assertEquals('ok', result);
}
```

**Do:**
- Design callout-making and query-making classes against an interface so they can be stubbed — dependency injection at the constructor or via a `setService()` method.
- Use `Test.createStub()` for faking an interface rather than writing a hand-rolled concrete stub class per test.
- Assert the *outcome of the caller's logic* (what it does with the response), not internal implementation details of the stub.

**Don't:**
- Use `@isTest(SeeAllData=true)` as a workaround for not having a stub — the SeeAllData exemption is banned (house opinion #10); the correct answer is TestDataFactory + stubs.
- Issue live callouts in tests without `Test.setMock()` — Salesforce throws `System.CalloutException: You have uncommitted work pending` or a `WebServiceException` depending on context.
- Stub across package boundaries unless the interface is part of the public API contract — stub only what you own.

## Edge cases / when the rule does NOT apply

End-to-end integration tests that **intentionally** verify the full callout stack (deployed to a scratch org with the external system mocked at the network layer by a test setup fixture, or run in a dedicated integration sandbox) are not unit tests — the `HttpCalloutMock` pattern does not apply to them, but they must be clearly labelled and must not run in the default `RunLocalTests` gate.

## See also

- [`../agents/apex-engineer.md`](../agents/apex-engineer.md) — owns Apex test authoring and is the primary enforcer of this rule
- [`./apex-test-data-with-testfactory-not-seealldata.md`](./apex-test-data-with-testfactory-not-seealldata.md) — the complementary rule on test data isolation
- [`./apex-assert-outcomes-not-coverage.md`](./apex-assert-outcomes-not-coverage.md) — the assertion-quality rule this stub pattern enables

## Provenance

Codifies house opinion #10 ("no SeeAllData — use TestDataFactory") extended to the full dependency-isolation principle; Salesforce `Test.createStub()` + `HttpCalloutMock` developer documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
