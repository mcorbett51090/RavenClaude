# Set Cloud Run minimum instances for latency-sensitive services

**Status:** Pattern
**Domain:** GCP compute / Cloud Run
**Applies to:** `gcp-cloud`

---

## Why this exists

Cloud Run's scale-to-zero is a cost feature, not a latency feature. A cold start (first request after idle) adds 1–10+ seconds for JVM/Python services with heavy initialization. For user-facing APIs, this latency spike surfaces as a degraded first-request experience or a timeout. Setting `minimum-instances = 1` (or more) keeps at least one warm instance available, eliminating cold starts for prod services while scaling down to that floor in quiet periods. The cost difference between 0 and 1 minimum instance is minimal for a low-utilization service; the latency benefit is immediate.

## How to apply

```hcl
# Terraform — Cloud Run service with minimum instances
resource "google_cloud_run_v2_service" "this" {
  name     = "my-service-${var.env}"
  location = var.region

  template {
    scaling {
      min_instance_count = var.is_prod ? 1 : 0   # 0 for dev; 1+ for prod
      max_instance_count = 10
    }

    containers {
      image = var.image
      resources {
        limits   = { cpu = "1", memory = "512Mi" }
        # CPU always allocated when min > 0 (needed for startup probes)
        cpu_idle = false   # keep CPU allocated when min_instance_count > 0
      }

      startup_probe {
        http_get { path = "/healthz" }
        initial_delay_seconds = 5
        period_seconds        = 3
        failure_threshold     = 10
      }
    }
  }
}
```

**Guidance by service tier:**

| Tier | min_instance_count | Rationale |
|---|---|---|
| Dev/test | 0 | Cost; cold starts acceptable |
| Non-prod but latency-tested | 0–1 | Use 1 if testing cold-start behavior |
| Prod user-facing API | 1–3 | 1 eliminates most cold starts; 3 for peak concurrency floor |
| Prod background worker | 0–1 | Cold starts usually acceptable; 1 if job latency matters |

**Do:**
- Set `cpu_idle = false` when `min_instance_count > 0` — otherwise the kept instance doesn't get CPU and can't handle a request until CPU is re-allocated (defeating the purpose).
- Add a startup probe — Cloud Run waits for it before routing traffic, so the instance is genuinely ready.
- Monitor cold-start rate via Cloud Run metrics (`container/startup_latencies`) to calibrate the setting.

**Don't:**
- Set `min_instance_count = 0` for prod user-facing APIs unless cold-start latency has been tested and accepted.
- Set `min_instance_count` higher than max concurrency can justify — you're paying for idle instances.
- Confuse `min_instance_count` with concurrency setting — `concurrency` controls how many requests a single instance handles; `min_instance_count` controls how many instances are always warm.

## Edge cases / when the rule does NOT apply

- **Batch/async Pub/Sub consumers**: cold starts are usually acceptable since messages sit in the queue until an instance starts.
- **Cost-constrained dev projects**: `min_instance_count = 0` is the right default for dev; the concern is prod.

## See also

- [`../agents/gcp-data-and-compute-engineer.md`](../agents/gcp-data-and-compute-engineer.md) — owns Cloud Run scaling configuration.
- [`./cloud-run-as-the-default.md`](./cloud-run-as-the-default.md) — the rule that establishes Cloud Run as the GCP compute default.

## Provenance

Derives from the `gcp-data-and-compute-engineer` remit in `CLAUDE.md` §1 and the Cloud Run best practices documentation on minimizing cold starts. Standard GCP production readiness pattern.

---

_Last reviewed: 2026-06-05 by `claude`_
