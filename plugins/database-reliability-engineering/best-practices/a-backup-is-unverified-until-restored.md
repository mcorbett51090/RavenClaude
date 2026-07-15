# A backup is unverified until it's restored

The most common backup failure is discovering, mid-disaster, that the backups were
never restorable — wrong scope, silent corruption, an expired credential, a restore
that takes 10× the RTO. A backup you have never restored is a hope, not a recovery
plan.

**Do:** schedule restore-verification — restore to an isolated instance, validate
row counts / checksums / a smoke query, measure actual restore time against RTO, and
alert when verification goes stale. Periodically rehearse the *full* DR path
(restore-and-promote), not just the file restore.

**Don't:** treat "the backup job succeeded" as "we can recover." A green backup job
proves bytes were written, not that they restore to a working database within RTO.

**Flag:** any database whose backups have no scheduled restore test, or whose
measured restore time is unknown or exceeds the stated RTO.
