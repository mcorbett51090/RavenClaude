# Test restores on a schedule — a backup never tested is not a backup

**Status:** Absolute rule
**Domain:** Database reliability
**Applies to:** `database-engineering`

---

## Why this exists

A backup that has never been successfully restored is a file of unknown recoverability. The backup process can silently produce corrupt dumps, incomplete streams, or snapshots that are missing WAL segments required for a consistent restore. A recovery procedure that has never been executed in production-equivalent conditions will have errors when executed under incident pressure for the first time. The only way to know a backup works is to restore it.

## How to apply

Schedule automated restore tests. Run them in an isolated environment with a clock comparison against the production point-in-time.

```bash
#!/usr/bin/env bash
# Automated restore test — runs on a schedule (weekly minimum)
set -euo pipefail

BACKUP_S3_URI="s3://myapp-backups/pg/$(date -d 'yesterday' +%Y-%m-%d)/"
RESTORE_HOST="restore-test.internal"

# 1. Download and restore the backup
pg_restore --host="$RESTORE_HOST" --clean --if-exists \
  --dbname=postgres "$BACKUP_S3_URI"

# 2. Run a smoke-test query
psql --host="$RESTORE_HOST" --command="SELECT COUNT(*) FROM orders;" | \
  grep -E '^[[:space:]]+[0-9]+'

# 3. Check the restored database's max timestamp
MAX_TS=$(psql --host="$RESTORE_HOST" -t --command="SELECT MAX(created_at) FROM orders;")
echo "Restored up to: $MAX_TS"

# 4. Alert if the test fails — page on-call
echo "Restore test PASSED for backup $BACKUP_S3_URI"
```

**Do:**
- Run automated restore tests weekly at minimum; daily for high-RPO databases.
- Test PITR (point-in-time recovery) by restoring to a target time, not just the latest snapshot.
- Verify row counts and spot-check critical table data post-restore.
- Measure and record restore duration — this is your RTO; if it exceeds your target, fix it now.

**Don't:**
- Consider a backup "tested" because the backup job returned exit 0.
- Run restore tests against the production database — use an isolated, throwaway instance.
- Skip the restore test when the backup is compressed/encrypted — those are the highest-risk scenarios.

## Edge cases / when the rule does NOT apply

Databases that are fully reproduced from event sourcing or migrations on every deploy (seed-only, stateless test DBs) may not need scheduled restore testing. All production databases with user data are in scope.

## See also

- [`../agents/db-reliability-engineer.md`](../agents/db-reliability-engineer.md) — owns backup, restore, and HA strategy.
- [`./a-backup-is-only-real-if-restored.md`](./a-backup-is-only-real-if-restored.md) — the foundational rule; this doc provides the operational implementation of it.

## Provenance

Standard database operations practice. Codifies `db-reliability-engineer`'s backup/restore responsibility from CLAUDE.md §2.

---

_Last reviewed: 2026-06-05 by `claude`_
