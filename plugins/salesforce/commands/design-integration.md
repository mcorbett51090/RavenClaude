---
description: Choose and design the right Salesforce integration pattern — Platform Events vs Change Data Capture vs callout, Bulk API vs row-by-row REST, named credentials over hardcoded endpoints, idempotent replay-aware consumers, and governor-safe async callouts.
argument-hint: "[the integration goal, e.g. 'sync orders to an ERP on update']"
---

# Design an integration

You are running `/salesforce:design-integration`. Pick the correct integration pattern for what the user described (`$ARGUMENTS`) and design it to be governor-safe, secure, and replay-aware — the `salesforce-platform-architect`'s integration discipline.

## When to use this

Salesforce needs to exchange data with an external system (ERP, data warehouse, middleware, another SaaS) and you're choosing the mechanism.

## Steps

1. **Pick the channel** (`integration-platform-events-vs-cdc-vs-callout`):
   - Salesforce → external, event-driven, decoupled → **Platform Events**.
   - "Tell me what changed on these records" → **Change Data Capture**.
   - Synchronous request/response or external → Salesforce → **REST/SOAP callout** or inbound API.
2. **Batch vs row-by-row** (`integration-bulk-api-for-batch-not-row-by-row-rest`): moving many rows → **Bulk API 2.0**, never a REST call per record.
3. **Named Credentials, not hardcoded endpoints/secrets** (`integration-named-credentials-not-hardcoded-endpoints`) — auth + URL live in metadata, not Apex strings.
4. **Governor-safe callouts** (`integration-callout-governor-and-async`): respect the callout limit per transaction; long/slow calls go **async** (`@future(callout=true)`, Queueable, or Batch) — never block a trigger on a synchronous callout.
5. **Idempotent, replay-aware consumers** (`integration-idempotent-consumers-and-replay-aware-subscribers`): events can be redelivered; design the consumer to dedupe (external ID / replay ID) so a replay doesn't double-apply.
6. Produce: the chosen pattern + why, the Named Credential to create, the Apex/Flow shape, and the failure/replay handling.

## Guardrails

- Never hardcode an endpoint, key, or token in Apex — Named Credential always.
- Never make a synchronous callout from a trigger context.
- Assume at-least-once delivery; a non-idempotent consumer is a data-corruption bug waiting to happen.
