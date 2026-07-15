# Migrations are expand-then-contract, never destructive-in-one-step

A schema change on a live database is a sequence of individually-safe, reversible
steps — not a single `ALTER`. Add the new shape (expand), move the app and data to
it, then remove the old shape (contract). Any step that both removes the old and
requires the new at once is an outage waiting for load.

**Do:** expand (additive, reversible) → dual-write → batched/throttled/idempotent
backfill → cutover reads → contract. Build indexes concurrently/online on hot
tables. Know the lock each step takes and its duration under production load; set a
`lock_timeout`.

**Don't:** run one big `UPDATE` to backfill, or take an ACCESS EXCLUSIVE lock on a
hot table "because it's usually fast." Usually-fast under test is an outage under
peak load.

**Flag:** a migration with no rollback per step, a backfill that isn't batched and
paced against replication lag, or a non-additive change to a hot table with no
online strategy.
