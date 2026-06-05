---
scenario_id: 2026-06-05-schema-evolution-break
contributed_at: 2026-06-05
plugin: data-streaming-engineering
product: confluent
product_version: "7.x"
scope: likely-general
tags: [schema-registry, compatibility, avro, breaking-change, new-topic]
confidence: high
reviewed: false
---

## Problem

A producer team shipped what they thought was a harmless schema change to an Avro event — they **renamed** a field (`customer_id` → `customerId`) and changed another field's type from `string` to `long`. The schema registry accepted the registration in dev (compatibility had been left at the registry default), the producer deployed, and within minutes every downstream consumer in prod started throwing deserialization errors and falling off the topic. A real-time fraud-scoring consumer stopped scoring; lag on the consumer groups climbed to the retention edge. The producer team's position was "we registered the schema, the registry said OK, so consumers should handle it."

## Constraints context

- Confluent Schema Registry with Avro; **compatibility mode was the registry-wide default**, which the team believed was `BACKWARD` but had been switched to `NONE` during an earlier migration and never reset — so the registry enforced *nothing*.
- Multiple independent consumer teams read the topic; producers deployed on their own cadence, ahead of consumers (so the upgrade order was producer-first).
- No CI check on schema compatibility — registration happened at producer runtime, first seen in dev where there were no real consumers to break.

## Attempts

- Tried: **rolling the producer back** to the old schema. Stopped *new* bad messages, but the topic now had a run of messages in the new (incompatible) schema that consumers still couldn't read — the poison was already on the log, and consumers were stuck on the first un-deserializable offset.
- Tried: **forcing consumers to skip the bad offsets** (`kafka-consumer-groups --reset-offsets` past the poison run). Got consumers moving again but **silently dropped** the events in the gap — unacceptable for the fraud-scoring path, which needed every event.
- Tried: **treating the breaking change as a new topic version + dual-write + consumer migration**, and **fixing the registry to enforce `BACKWARD` (or `FULL`) so this can't recur**, plus a **CI compatibility check** before any registration. This is the resolution.

## Resolution

**A field rename or type change is a breaking change, not an evolution — and a registry set to `NONE` is not governing anything.** Avro resolves a rename as "drop the old field, add a new one," so old consumers lose the field and new data is unreadable by the old schema; a `string`→`long` type change has no resolution rule at all. Neither is backward-compatible.

1. **Set and enforce a real compatibility mode.** `BACKWARD` (new schema can read old data — consumers upgrade first, the common safe default) or `FULL` (both directions) — never leave it `NONE`. With `BACKWARD` enforced, the registry would have *rejected* the rename + type change at registration time, in CI, before a single bad message hit prod. The registry is only a guardrail if it's actually configured to guard.
2. **Add a CI compatibility check, don't rely on runtime registration.** Validate the candidate schema against the registry's current version (`mvn schema-registry:test-compatibility` / the Gradle plugin / a registry API call) in the producer's pipeline. Catch the break at PR time, where the cost is a failed build, not at runtime where the cost is a prod outage.
3. **A genuinely breaking change is a new topic/subject version + a migration, never an in-place edit.** When you truly must rename or retype, produce to a `v2` topic (or a new subject), dual-write `v1`+`v2` during a migration window, move consumers to `v2`, then retire `v1`. The old consumers keep reading `v1` the whole time — no poison run, no skipped offsets.
4. **Additive-and-optional is the only safe in-place change.** Adding a new field *with a default* is backward-compatible (old consumers ignore it, new consumers get the default for old data). That's the change you can make in place under `BACKWARD`. Renames, type changes, and removing-a-required-field are not.

The two traps compounded: a registry that enforced nothing let a breaking change through, and the absence of a CI gate meant the first real consumers to see it were in prod. Either guardrail alone would have caught it.

**Action for the next engineer:** before touching an event schema, confirm the subject's compatibility mode is actually `BACKWARD`/`FULL` (not `NONE`), and run the compatibility check in CI. If the change is a rename or type change, stop — it's a new topic version + migration, not an evolution. Adding an optional field with a default is the only change you make in place.

Cross-reference: complements [`../best-practices/govern-schemas-with-a-registry.md`](../best-practices/govern-schemas-with-a-registry.md), [`../best-practices/schema-breaking-change-is-a-new-topic.md`](../best-practices/schema-breaking-change-is-a-new-topic.md), the [`../knowledge/data-streaming-engineering-decision-trees.md`](../knowledge/data-streaming-engineering-decision-trees.md) `## Decision Tree: Which schema-compatibility mode?`, and the [`../skills/schema-evolution-playbook/SKILL.md`](../skills/schema-evolution-playbook/SKILL.md) skill. The AsyncAPI/event-contract documentation of the change → `api-engineering`.
