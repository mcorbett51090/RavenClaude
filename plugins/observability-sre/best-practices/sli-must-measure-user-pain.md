# SLIs must measure user-visible pain, not system internals

**Status:** Absolute rule
**Domain:** SRE / SLO design
**Applies to:** `observability-sre`

---

## Why this exists

An SLI that measures CPU utilization, connection pool size, or queue depth measures system health, not user experience. A system can be at 90% CPU with users having a perfect experience, or at 10% CPU while silently returning wrong data to every request. The SLO built on an internal-metric SLI will page you on harmless conditions and miss the outages users actually feel. SLIs that measure what users observe (did the request succeed? was it fast enough? was the data correct?) are the only ones worth building SLOs on.

## How to apply

Map each SLO to a concrete user interaction and express the SLI as a ratio of good events to total events, where "good" is defined from the user's perspective.

| Service type | Good SLI | Bad SLI |
|---|---|---|
| HTTP API | 2xx+3xx / total requests in < 300ms | CPU utilization < 70% |
| Background job | Jobs completed without error / total started | Queue depth < 1000 |
| Streaming pipeline | Records processed without drop or corruption / total ingested | Consumer lag < 5s |
| Search | Queries returning relevant results within 1s / total queries | Index size growth |
| Auth service | Logins completed successfully / total attempts | Token cache hit rate |

```yaml
# Prometheus: a good SLI for an HTTP API
# Ratio: fast successful requests / all requests (excludes health-check paths)
- record: sli:http_availability:rate5m
  expr: |
    sum(rate(http_server_request_duration_count{
      status!~"5..",
      path!~"/health|/ready"
    }[5m]))
    /
    sum(rate(http_server_request_duration_count{
      path!~"/health|/ready"
    }[5m]))

- record: sli:http_latency_p99:rate5m
  expr: |
    histogram_quantile(0.99,
      sum(rate(http_server_request_duration_bucket{
        path!~"/health|/ready"
      }[5m])) by (le)
    )
```

**Do:**
- Write the user story before writing the SLI query: "A user experiences good service when their checkout request completes in under 500ms with a 2xx response."
- Exclude health/readiness probes and internal synthetic checks from SLI denominators.
- Validate the SLI against a real incident: would a past outage have consumed budget?

**Don't:**
- Use infrastructure metrics (CPU, memory, disk) as primary SLIs.
- Include health-check or synthetic traffic in the total request count — they inflate availability.
- Set the latency SLI threshold at the average; use a percentile (P95 or P99) that represents real user experience.

## Edge cases / when the rule does NOT apply

Infrastructure SLOs (the cluster's control plane, the database's replication lag) are legitimate when the infra service has users that are other services. Even then, express the SLI as "can a dependent service operation complete?" not "is CPU below threshold?"

## See also

- [`../agents/sre-reliability-engineer.md`](../agents/sre-reliability-engineer.md) — owns SLI/SLO design and the target-setting process.
- [`./error-budget-is-the-decision-rule.md`](./error-budget-is-the-decision-rule.md) — the budget is only meaningful if the SLI measures real pain.

## Provenance

Codifies the SLI definition from Google SRE Book Chapter 4 ("Service Level Objectives") and the CRE (Customer Reliability Engineering) guidance that SLIs should map to user journeys.

---

_Last reviewed: 2026-06-05 by `claude`_
