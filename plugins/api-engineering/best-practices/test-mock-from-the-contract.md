# Mock from the contract, not by hand

**Status:** Pattern — a hand-written stub drifts from the contract the moment it's written.

**Domain:** API testing / developer experience

**Applies to:** `api-engineering`

---

## Why this exists

Consumers need to build before the real API is ready, and tests need a fast, deterministic stand-in. A hand-coded stub starts wrong (someone's memory of the spec) and drifts immediately (the spec changes, the stub doesn't). Generating the mock **from the OpenAPI/AsyncAPI document** — with Prism, a Postman mock, or similar — keeps the mock honest: it serves only spec-valid responses, validates incoming requests against the spec, and updates when the spec does.

## How to apply

Run a contract mock straight off the spec; let consumers point at it.

```
# Prism — a validating mock server from the spec
prism mock openapi.yaml            # serves spec examples; validates requests against the schema

# Postman / Postman MCP — generate a collection + mock from the spec
#   (load the Postman MCP tools via ToolSearch first; treat generated artifacts as drafts)
```

**Do:**
- Serve `examples` from the spec; enable request validation so the mock rejects off-contract calls.
- Regenerate the mock from the spec in CI so it can't drift; use it as the consumer's parallel-dev target.

**Don't:**
- Hand-maintain a stub that duplicates the contract; let the mock return shapes the spec doesn't define.

## Edge cases / when the rule does NOT apply

Stateful, multi-step flows (a checkout that remembers a cart) need scripted service virtualization, not a stateless contract mock. Dynamic/example-poor specs may need example enrichment before the mock is useful — fix the spec's examples rather than hand-coding the mock.

## See also

- [`./test-consumer-driven-contract-tests.md`](./test-consumer-driven-contract-tests.md)
- [`../knowledge/api-testing-governance-decision-trees.md`](../knowledge/api-testing-governance-decision-trees.md) — mock vs stub vs virtualize
- [Prism](https://docs.stoplight.io/docs/prism/) — authoritative `[verify-at-build]`

## Provenance

Grounded in contract-driven mocking (Prism / Postman). Tool capabilities verified before quoting. Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
