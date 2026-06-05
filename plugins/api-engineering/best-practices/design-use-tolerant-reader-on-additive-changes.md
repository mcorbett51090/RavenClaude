# Require consumers to implement the tolerant-reader pattern

**Status:** Absolute rule
**Domain:** API design / contract evolution
**Applies to:** `api-engineering`

---

## Why this exists

Additive changes — a new optional field in a response, a new enum value, a new endpoint — should not break conforming consumers. But they will break consumers that are brittle: those that fail on unknown JSON fields, that switch exhaustively over enum values without a default, or that validate response schemas so strictly they reject extension. The tolerant-reader pattern (Postel's Law for API consumers) is the contract assumption that makes additive changes non-breaking. Without it, every new field forces a version bump, crushing the lifecycle of the API.

## How to apply

State the tolerant-reader expectation in your API documentation and design guide, and validate it in contract tests.

```typescript
// Client code that is NOT tolerant (breaks on new fields):
const user = UserSchema.strict().parse(response);  // zod .strict() rejects extra fields

// Client code that IS tolerant (ignores unknown fields):
const user = UserSchema.passthrough().parse(response);  // or just z.object({...}) without .strict()
// — or — use a try/catch that extracts only known fields
const { id, name, email } = response;  // destructure known fields; ignore the rest
```

Document in the OpenAPI spec:

```yaml
# In your spec description / x-api-guidelines extension:
# Consumers MUST ignore unknown fields in response objects.
# Consumers MUST handle unknown enum values gracefully (treat as the unknown/other case).
# Consumers MUST NOT validate response bodies with a strict schema that rejects extensions.
```

**Do:**
- State in the developer portal and SDK docs that consumers must ignore unknown response fields.
- Design contract tests to include a "future field" in the response and verify the consumer still passes.
- Return unknown enum values as a safe default ("UNKNOWN") in generated client SDKs.
- Design request validation to be tolerant of unknown fields sent by clients (for forward-compatible client upgrades).

**Don't:**
- Require consumers to use strict schema validation against your response contract — that defeats Postel's Law.
- Treat an additive change (new response field) as breaking if you have stated and tested the tolerant-reader expectation.
- Add required fields to existing response objects without bumping the version — required new fields are breaking changes.

## Edge cases / when the rule does NOT apply

Security-sensitive contexts where unknown fields should be rejected for safety (e.g., a signed JWT claims object where unexpected claims could alter authorization logic) are legitimate exceptions — reject unknown fields explicitly there.

## See also

- [`../agents/api-design-architect.md`](../agents/api-design-architect.md) — owns versioning strategy and contract evolution.
- [`./design-version-only-for-breaking-changes.md`](./design-version-only-for-breaking-changes.md) — the versioning rule that tolerant-reader makes sustainable.

## Provenance

Postel's Law / Robustness Principle and Martin Fowler's "Tolerant Reader" pattern. Codifies `api-design-architect`'s contract-evolution posture from this plugin's CLAUDE.md §3 rule 10.

---

_Last reviewed: 2026-06-05 by `claude`_
