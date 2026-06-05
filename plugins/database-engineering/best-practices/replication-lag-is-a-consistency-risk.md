# Monitor replication lag and route reads that require freshness to the primary

**Status:** Primary diagnostic
**Domain:** Read replicas / consistency
**Applies to:** `database-engineering`

---

## Why this exists

A read replica is eventually consistent with its primary; the lag is usually milliseconds but can grow to seconds or minutes under high load, during a streaming hiccup, or after a failover. An application that reads from the replica immediately after writing — confirmation of a submitted order, the current balance after a transfer, a user's own profile after they edited it — may see stale data. This is not a corner case; it is a predictable property of replication that must be engineered around, not discovered in a production bug.

## How to apply

```sql
-- Check replication lag from the primary
SELECT
  client_addr,
  state,
  write_lag,
  flush_lag,
  replay_lag
FROM pg_stat_replication;

-- From the replica: check how far behind it is
SELECT NOW() - pg_last_xact_replay_timestamp() AS replication_lag;
```

Application-layer routing:

```typescript
// Route reads by consistency requirement at the service layer
class UserRepository {
  async getForConfirmation(userId: string): Promise<User> {
    // Read from primary — just-written record must be present
    return this.primary.query('SELECT * FROM users WHERE id = $1', [userId]);
  }

  async listForDashboard(tenantId: string): Promise<User[]> {
    // Replica is fine — a few seconds of lag is acceptable
    return this.replica.query('SELECT * FROM users WHERE tenant_id = $1', [tenantId]);
  }
}
```

**Do:**
- Alert when replica lag exceeds your application's stated consistency tolerance (e.g., > 5 seconds).
- Route reads that must see the result of a recent write to the primary.
- Use `synchronous_commit = remote_apply` for replicas where you cannot tolerate any lag on specific paths.
- Document each read's consistency requirement explicitly in the data-access layer.

**Don't:**
- Route all reads to replicas without understanding which reads require freshness.
- Assume replica lag is "usually zero" and build the application on that assumption.
- Disable replication monitoring because "the replica caught up" — lag can return on the next high-write period.

## Edge cases / when the rule does NOT apply

A reporting/analytics replica where staleness of minutes is acceptable does not need per-query freshness routing. The rule targets transactional replicas used for application reads.

## See also

- [`../agents/db-reliability-engineer.md`](../agents/db-reliability-engineer.md) — owns replication configuration and monitoring.
- [`./choose-isolation-deliberately.md`](./choose-isolation-deliberately.md) — isolation level governs intra-primary consistency; this rule governs primary-to-replica consistency.

## Provenance

PostgreSQL documentation on streaming replication and `pg_stat_replication`. Standard read/write routing practice in high-availability database architectures. Codifies `db-reliability-engineer`'s replication monitoring responsibility.

---

_Last reviewed: 2026-06-05 by `claude`_
