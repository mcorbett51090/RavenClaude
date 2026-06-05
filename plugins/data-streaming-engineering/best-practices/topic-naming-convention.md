# Use a consistent, machine-parseable topic naming convention

**Status:** Absolute rule
**Domain:** Kafka / topic design
**Applies to:** `data-streaming-engineering`

---

## Why this exists

A Kafka cluster without a naming convention becomes a sprawl of topics named `orders`, `orders2`, `orders-dev`, `orders_v2`, `orders_new` within six months. Operators cannot determine topic ownership, environment, or data type from the name. Automated tooling (schema registry lookup, ACL generation, monitoring dashboards) cannot pattern-match against inconsistent names. A naming convention is the cheapest governance investment in a Kafka deployment.

## How to apply

Use the pattern: `<domain>.<environment>.<entity>.<event-type>` (all lowercase, dots as separators):

```
commerce.prod.order.placed
commerce.prod.order.cancelled
commerce.prod.payment.charged
analytics.prod.user.pageview
iam.prod.account.created
iam.staging.account.created
```

**Convention elements:**
- `<domain>`: bounded context or team (e.g., `commerce`, `iam`, `analytics`)
- `<environment>`: `prod`, `staging`, `dev`, `local` — keeps environments strictly separate
- `<entity>`: the aggregate root (e.g., `order`, `user`, `payment`)
- `<event-type>`: past-tense event verb (e.g., `placed`, `cancelled`, `charged`)

**Schema registry subject naming:** use the `TopicNameStrategy` — the subject is `<topic-name>-value` (and `-key` for keyed schemas). This ties the schema to the topic name automatically.

**Do:**
- Enforce the convention in CI with a topic-name lint script before any new topic is created.
- Use the same convention for DLQ topics: `commerce.prod.order.placed.dlq`
- Document the convention in the team runbook with approved domain names.

**Don't:**
- Allow freeform topic names — even "internal" topics should follow the convention.
- Use camelCase or mixed separators (`orders-v2` alongside `iam.account`).
- Create environment-specific topics by appending a suffix (`orders_dev`) — use the environment segment instead.

## Edge cases / when the rule does NOT apply

- Confluent Cloud's managed connector topics and internal Kafka system topics (`__consumer_offsets`, `_schemas`) follow platform conventions and are exempt.
- Legacy topics in an existing cluster can be migrated to the convention on a rename-with-dual-produce window rather than an immediate rename.

## See also

- [`../agents/kafka-pipeline-engineer.md`](../agents/kafka-pipeline-engineer.md) — owns topic design and naming
- [`./govern-schemas-with-a-registry.md`](./govern-schemas-with-a-registry.md) — the schema registry rule that topic naming enables

## Provenance

Standard Apache Kafka operational practice. The `domain.environment.entity.event-type` pattern is widely used in enterprise Kafka deployments (Confluent, Uber, LinkedIn). Grounded in data-streaming-engineering CLAUDE.md §2 house opinion #5 ("Schemas evolve; govern them").

---

_Last reviewed: 2026-06-05 by `claude`_
