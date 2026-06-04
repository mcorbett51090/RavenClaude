# Consumer-driven contract tests — the consumer's expectations gate the provider

**Status:** Pattern — strong default for any API with more than one team consuming it.

**Domain:** API testing

**Applies to:** `api-engineering`

---

## Why this exists

A provider's own test suite passing says nothing about whether a change broke a *consumer*. Consumer-driven contract testing inverts this: each consumer publishes the subset of the API it actually depends on (a Pact contract, or schema assertions), and the **provider's CI** verifies it still satisfies every published contract. A change that breaks a known consumer fails the *provider's* build — before it ships — instead of surfacing as a production incident on the consumer's side.

## How to apply

Consumer publishes expectations; provider verifies them in CI; a broker shares them.

```
1. Consumer test runs against a Pact mock, records its expectations -> a pact file
2. Pact file published to a broker (or committed)
3. Provider CI runs "provider verification": replays each consumer's expectations
   against the real provider -> fails the build if any expectation is no longer met
4. can-i-deploy gate: provider may deploy only if all consumer contracts pass
```

**Do:**
- Let consumers own their contracts (only the fields/shapes they use), so the provider can change everything else freely.
- Run provider verification on every provider PR; use a broker to track which versions are compatible.

**Don't:**
- Confuse this with the provider writing its own "contract tests" (that's schema validation); the *consumer* drives it.
- Assert on fields a consumer doesn't use (over-specified contracts block legitimate provider changes).

## Edge cases / when the rule does NOT apply

A single-team API with one in-repo consumer can use schema-validation tests instead of a full Pact broker. Public APIs with unknown consumers can't do consumer-driven contracts — there, the *published spec* is the contract and schema-validation + deprecation discipline carry the load.

## See also

- [`./test-mock-from-the-contract.md`](./test-mock-from-the-contract.md)
- [`../knowledge/api-testing-governance-decision-trees.md`](../knowledge/api-testing-governance-decision-trees.md)
- [Pact](https://docs.pact.io/) — authoritative `[verify-at-build]`

## Provenance

Grounded in the consumer-driven contract-testing pattern (Pact). Tool capabilities verified before quoting. Retrieved/verified 2026-06-04.

---

_Last reviewed: 2026-06-04 by `claude`_
