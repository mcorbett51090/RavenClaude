# Use data factories to generate test data — not hand-crafted fixture files

**Status:** Pattern
**Domain:** Test infrastructure / test data management
**Applies to:** `qa-test-automation`

---

## Why this exists

Static fixture files (JSON dumps, SQL inserts, YAML blobs) that encode specific entity IDs, hardcoded timestamps, and interrelated FK chains become a maintenance nightmare as the schema evolves. Every schema change touches the fixture. Every test that relies on the fixture is coupled to IDs that may collide between test runs. Factories generate minimal, valid, realistic test data on demand — each test gets exactly the shape it needs, with unique IDs, and with no dependency on a pre-loaded state.

## How to apply

Use a factory library (Factory Boy for Python, factory_bot for Ruby, Fishery for TypeScript, or equivalent) to define entity shapes with sensible defaults that can be overridden per test.

```python
# Python + Factory Boy
import factory
from factory.django import DjangoModelFactory
from myapp.models import User, Order

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    is_active = True

class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    total_cents = factory.Faker("random_int", min=100, max=100000)
    status = "pending"

# In a test: create only the data the test cares about
def test_order_confirmation_email_is_sent():
    order = OrderFactory(status="placed", total_cents=5000)
    # override only the fields the test needs
    send_confirmation(order)
    assert len(mail.outbox) == 1
```

```typescript
// TypeScript with Fishery
import { Factory } from 'fishery';

const userFactory = Factory.define<User>(({ sequence }) => ({
  id: sequence,
  username: `user_${sequence}`,
  email: `user_${sequence}@example.com`,
  role: 'member',
}));

const orderFactory = Factory.define<Order>(({ sequence }) => ({
  id: sequence,
  user: userFactory.build(),
  totalCents: 5000,
  status: 'pending',
}));

// Test: override only the relevant field
const order = orderFactory.build({ status: 'placed', totalCents: 9999 });
```

**Do:**
- Define one factory per entity; use `SubFactory` / associations to build related entities.
- Use sequences for IDs and unique fields to prevent collisions between parallel test runs.
- Override only the fields a specific test cares about — let defaults handle the rest.
- Clean up factory-created data in `afterEach` or use a transaction rollback strategy.

**Don't:**
- Commit hand-crafted fixture files with hardcoded entity IDs.
- Share a factory-created entity between test cases (each test gets its own).
- Use factories for read-only reference data (country codes, currency codes) — those can be seeded once.

## Edge cases / when the rule does NOT apply

Read-only reference/lookup tables (currencies, country codes, feature-flag enums) are appropriate candidates for a one-time seed migration, not a factory per test. Use factories for anything that gets created, modified, or deleted in the course of a test.

## See also

- [`../agents/test-infrastructure-engineer.md`](../agents/test-infrastructure-engineer.md) — owns test data strategy and factory patterns.
- [`./isolate-test-data.md`](./isolate-test-data.md) — factories produce the isolated data; isolation is the design contract.

## Provenance

Codifies the Factory pattern for test data from Factory Boy documentation and Martin Fowler's "Test Data Builder" pattern. Standard practice in Django/Rails test infrastructure.

---

_Last reviewed: 2026-06-05 by `claude`_
