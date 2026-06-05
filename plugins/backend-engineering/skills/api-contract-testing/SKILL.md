---
name: api-contract-testing
description: "Playbook for implementing consumer-driven contract tests (Pact) between backend services so API contract breaks surface in CI before they reach integration environments."
---

# API Contract Testing

## When to invoke

Use when two or more services communicate over HTTP/messaging and you want to catch contract breaks (missing fields, changed types, removed endpoints) in the individual service's CI pipeline rather than in a shared integration environment.

## Concepts in 30 seconds

| Term | Meaning |
|---|---|
| Consumer | The service that calls the API |
| Provider | The service that serves the API |
| Pact | A JSON file of recorded interactions the consumer depends on |
| Pact Broker | Central registry that matches consumers to providers |
| Verification | Provider re-runs each pact interaction against its real code |

## Step 1 — Consumer writes the pact

In the consumer's test suite (using the Pact SDK for your language):

```python
# Python example (pact-python)
pact = Consumer("order-service").has_pact_with(Provider("inventory-service"))

(pact
 .given("item SKU-99 exists in inventory")
 .upon_receiving("a stock-check request")
 .with_request(method="GET", path="/inventory/SKU-99")
 .will_respond_with(
     status=200,
     body={"sku": "SKU-99", "quantity": Like(10)},  # Like = type-only match
 ))
```

Key matchers:
- `Like(value)` — type only (any integer, not exactly 10)
- `EachLike(template)` — non-empty array of matching elements
- `Term(regex, example)` — value matches regex

Commit the generated `pact.json` to the Pact Broker in the consumer CI job.

## Step 2 — Provider verifies

In the provider's test suite, replay every known pact against the real application (started in-process or via Docker):

```python
# provider verification (pytest-pact)
@pytest.fixture
def provider_opts():
    return {
        "provider": "inventory-service",
        "pact_broker_url": os.environ["PACT_BROKER_URL"],
        "publish_verification_results": True,
        "provider_version": os.environ["GIT_SHA"],
    }
```

The provider CI job fetches all consumer pacts, runs each interaction, and publishes a pass/fail result. **A failed verification blocks the provider's deploy.**

## Step 3 — Can-I-Deploy gate

Before any deploy, query the Broker:

```bash
pact-broker can-i-deploy \
  --pacticipant inventory-service \
  --version $GIT_SHA \
  --to-environment production
```

Returns exit 0 only if every consumer whose pact is marked "required for production" has a passing verification against this provider version. Wire this as a required CI step before the deploy job.

## Step 4 — Provider states (test data setup)

Provider state handlers set up the preconditions described in `given(...)`:

```python
@provider_state("item SKU-99 exists in inventory")
def setup_sku99():
    db.seed(sku="SKU-99", quantity=10)

@provider_state("item SKU-99 is out of stock")
def setup_sku99_oos():
    db.seed(sku="SKU-99", quantity=0)
```

Keep states minimal — only what the consumer interaction needs, not a full fixture set.

## Decision: Pact vs schema sharing vs integration tests

| Approach | Catches contract break in | Team coupling |
|---|---|---|
| Pact (consumer-driven) | Each service's CI | Consumer drives the spec |
| Shared OpenAPI schema | PR lint | Both teams must coordinate |
| Integration environment | Shared test run | Slowest, most flaky |

Use Pact when teams deploy independently. Use schema sharing as a complement (not a replacement) — the schema documents intent; the pact proves the consumer's actual usage.

## Pitfalls

- **Over-specifying the pact body** — using exact-match on every field means any additive change by the provider fails the pact, even though the consumer doesn't care. Use `Like` and `EachLike` for fields the consumer doesn't depend on.
- **Skipping provider states** — without state setup, the provider can't reproduce the scenario and the test is meaningless noise.
- **Not publishing verification results** — the can-i-deploy gate only works when results are in the Broker; a provider that verifies locally but doesn't publish blocks nothing.
- **One monolith pact** — a single pact for an entire consumer tests too much; split by interaction group so a single-field change shows exactly what broke.
