# Use Pub/Sub for async event-driven integration between GCP services

**Status:** Pattern
**Domain:** GCP integration / event-driven
**Applies to:** `gcp-cloud`

---

## Why this exists

Direct service-to-service calls over HTTP create tight coupling: the caller waits for the receiver, the receiver's failure is the caller's failure, and scaling either side independently requires careful orchestration. Pub/Sub decouples producers from consumers — a Cloud Run service publishes an event to a topic, and one or more Cloud Run services (or Cloud Functions) subscribe via push subscriptions without the producer knowing about them. This enables independent scaling, retry (dead-letter topics), and fan-out without changing the producer.

## How to apply

```hcl
# Terraform — Pub/Sub topic with dead-letter
resource "google_pubsub_topic" "orders" {
  name    = "orders-${var.env}"
  project = var.project_id

  message_retention_duration = "86400s"   # 1 day — default 7 days max
}

resource "google_pubsub_topic" "orders_dlq" {
  name    = "orders-dead-letter-${var.env}"
  project = var.project_id
}

resource "google_pubsub_subscription" "orders_processor" {
  name    = "orders-processor-${var.env}"
  topic   = google_pubsub_topic.orders.id
  project = var.project_id

  # Push to Cloud Run
  push_config {
    push_endpoint = "https://order-processor-${var.env}.run.app"
    oidc_token {
      service_account_email = google_service_account.pubsub_invoker.email
    }
  }

  ack_deadline_seconds = 60
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.orders_dlq.id
    max_delivery_attempts = 5
  }
}
```

**Do:**
- Always configure a dead-letter topic — a message that fails 5+ times should not silently disappear.
- Use OIDC authentication on push subscriptions to Cloud Run or Cloud Functions — the push endpoint should not accept unauthenticated calls.
- Monitor dead-letter topic message count — messages landing in the DLQ are a signal, not a silent discard.
- Use `ack_deadline_seconds` matched to the expected processing time — too short causes redelivery of messages still in flight.

**Don't:**
- Pull-subscribe from Cloud Run without understanding pull subscription costs (per-byte billing); push is simpler and lower-cost for most Cloud Run patterns.
- Use Pub/Sub for synchronous request-response patterns — the caller does not get a response; use HTTP/gRPC for synchronous calls.
- Publish to a topic without a subscription — messages sit on the topic consuming retention until the retention window expires.

## Edge cases / when the rule does NOT apply

- **Synchronous API calls** where the caller needs the result inline: use HTTP/gRPC directly.
- **High-throughput streaming ingestion** (logs, telemetry, millions of events/second): Cloud Pub/Sub handles this, but evaluate Dataflow + BigQuery streaming inserts or Pub/Sub + Dataflow for analytics pipelines.

## See also

- [`../agents/gcp-data-and-compute-engineer.md`](../agents/gcp-data-and-compute-engineer.md) — owns Pub/Sub event-driven integration design.
- [`./cloud-run-as-the-default.md`](./cloud-run-as-the-default.md) — Cloud Run push subscriptions are the standard Pub/Sub consumer pattern.

## Provenance

Derives from the `gcp-data-and-compute-engineer` remit in `CLAUDE.md` §1: "Pub/Sub event-driven integration." Standard GCP event-driven architecture pattern from the Pub/Sub documentation and the Cloud Architecture Center.

---

_Last reviewed: 2026-06-05 by `claude`_
