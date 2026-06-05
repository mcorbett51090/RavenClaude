# Expose a structured health endpoint for every service

**Status:** Absolute rule
**Domain:** Observability / reliability
**Applies to:** `backend-engineering`

---

## Why this exists

A load balancer, container orchestrator, or deployment system cannot route traffic away from a broken instance without a health signal it can query. Without a `/health` endpoint, a restarted container that fails to connect to its database will silently receive live traffic and return 500s to every user. A structured health endpoint exposes liveness (is the process alive?) and readiness (is the service ready to serve traffic?) as separate signals, allowing the orchestrator to restart dead instances without removing healthy-but-warming instances.

## How to apply

Implement two endpoints. Keep the liveness check trivially cheap (no I/O). Make the readiness check verify critical dependencies.

```typescript
// GET /health/live — is the process up?
// Used by the orchestrator to decide "restart or not"
app.get('/health/live', (_req, res) => {
  res.json({ status: 'ok' });
});

// GET /health/ready — can this instance accept traffic?
// Used by the load balancer to decide "route to or not"
app.get('/health/ready', async (_req, res) => {
  const checks = await Promise.allSettled([
    db.query('SELECT 1'),           // database reachable?
    redis.ping(),                   // cache reachable?
  ]);
  const failed = checks.filter(c => c.status === 'rejected');
  if (failed.length > 0) {
    return res.status(503).json({ status: 'degraded', details: failed });
  }
  res.json({ status: 'ok' });
});
```

**Do:**
- Return `200` for healthy, `503` for not-ready — the standard orchestrator contract.
- Keep liveness checks free of I/O; a liveness probe that calls the DB will take the instance out of rotation when the DB is slow, causing cascading restarts.
- Include a machine-readable JSON body with per-check status for operational dashboards.
- Protect the readiness endpoint from rate limiting — orchestrators call it frequently.

**Don't:**
- Use a single `/health` endpoint for both liveness and readiness — they are semantically different.
- Include sensitive configuration or internal stack traces in the health response body.
- Let liveness and readiness checks share a slow I/O call — they fire at different cadences for different decisions.

## Edge cases / when the rule does NOT apply

CLI tools, batch jobs, and one-shot workers have no persistent listener; they signal health via exit code, not an HTTP endpoint. Serverless functions use platform-specific health mechanisms (e.g., Lambda provisioned concurrency warm-up, not HTTP probes).

## See also

- [`../agents/backend-reliability-engineer.md`](../agents/backend-reliability-engineer.md) — owns service observability and reliability contracts.
- [`./graceful-degradation-not-total-failure.md`](./graceful-degradation-not-total-failure.md) — defines what "degraded" means at the application layer; health endpoints report that state.

## Provenance

Kubernetes liveness/readiness probe pattern (kubernetes.io docs), extended to any orchestrated service. Codifies `backend-reliability-engineer`'s responsibility for making service health observable to the infrastructure layer.

---

_Last reviewed: 2026-06-05 by `claude`_
