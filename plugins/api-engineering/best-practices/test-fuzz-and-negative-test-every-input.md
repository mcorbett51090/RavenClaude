# Fuzz and negative-test every public input

**Status:** Pattern
**Domain:** API testing
**Applies to:** `api-engineering`

---

## Why this exists

Happy-path tests prove your API works when callers behave correctly. Negative and fuzz tests prove it stays safe and correct when they don't. A public input that has never been sent an empty string, a 10 MB payload, a negative integer, a Unicode control character, or a SQL fragment is an untested attack surface. The most common API security flaws — injection, resource exhaustion, broken input validation — are found by sending unexpected inputs, not expected ones.

## How to apply

```typescript
// Negative test cases for a user creation endpoint
const badCases = [
  { body: {},                      expect: 400, label: 'empty body' },
  { body: { name: '' },            expect: 400, label: 'empty name' },
  { body: { name: 'a'.repeat(10_001) }, expect: 400, label: 'name too long' },
  { body: { name: '<script>xss</script>' }, expect: 400, label: 'HTML in name' },
  { body: { age: -1 },             expect: 400, label: 'negative age' },
  { body: { email: 'not-an-email' }, expect: 400, label: 'invalid email' },
];

for (const tc of badCases) {
  it(`rejects: ${tc.label}`, async () => {
    const res = await request(app).post('/users').send(tc.body);
    expect(res.status).toBe(tc.expect);
    expect(res.body.type).toMatch(/^https:\/\//);  // RFC 9457 Problem Details type URI
  });
}

// Property-based / fuzz testing (fast-check)
import * as fc from 'fast-check';

it('never returns 500 for arbitrary string inputs', async () => {
  await fc.assert(fc.asyncProperty(fc.string(), async (name) => {
    const res = await request(app).post('/users').send({ name });
    expect(res.status).not.toBe(500);  // 400 and 422 are expected; 500 is a bug
  }));
});
```

**Do:**
- Test every boundary: empty string, max-length+1, negative numbers, null, wrong type.
- Assert that invalid inputs return `400 Bad Request` or `422 Unprocessable Entity` with a `problem+json` body — never `500`.
- Use a property-based testing library (fast-check, Hypothesis) to automate edge-case generation on critical endpoints.
- Include security-relevant fuzz inputs: SQL fragments, path traversal sequences, Unicode surrogates.

**Don't:**
- Treat negative tests as optional or "QA's job" — the API team owns the contract, including invalid input behavior.
- Allow a `500` internal server error to leak through for any caller-controlled input.
- Fuzz only the happy-path schema; fuzz the type boundaries too (string where number is expected).

## Edge cases / when the rule does NOT apply

Internal gRPC endpoints between trusted services with protobuf validation enforced by the framework gain less from input fuzzing at the HTTP layer — though business-logic edge cases still warrant negative tests. WebSocket streams have different fuzz tooling.

## See also

- [`../agents/api-testing-engineer.md`](../agents/api-testing-engineer.md) — owns negative and fuzz testing.
- [`./secure-limit-resource-consumption.md`](./secure-limit-resource-consumption.md) — the complementary control: even after fuzzing, resource-consumption limits are a defense-in-depth layer.

## Provenance

OWASP API Security Top 10 (2023) — API8/misconfiguration and general security testing guidance; fast-check and property-based testing practices. Codifies `api-testing-engineer`'s test-type coverage responsibility.

---

_Last reviewed: 2026-06-05 by `claude`_
