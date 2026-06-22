# Cutover Runbook — <migration / switch-over>

> Output of the `migration-engineer`. No cutover without a tested rollback (§2 #6). Run old and new in parallel; reconcile before traffic moves.

## Headline
<what switches, when, and the rollback strategy, in one line>

## Parallel-run state (must hold before cutover)
- **Migration pattern:** dual-write / shadow-read / backfill+reconcile / expand-contract
- **Reconciliation result:** <old vs new agree to <tolerance> — evidence>

## Go / no-go gates
- [ ] Reconciliation clean to tolerance
- [ ] SLOs healthy on the new path under shadow load
- [ ] Rollback rehearsed in non-prod / canary (date: ____)
- [ ] Owner + comms + window agreed

## Cutover steps (incremental)
| # | Step | Cohort / % | Watch (reconciliation + SLO) | Rollback trigger |
|---|---|---|---|---|
| 1 | | | | |

## Rollback (rehearsed)
1. <step-by-step reversal — the exact mechanism, already exercised>
- **Last-known-good:** <what to flip back to>

## Post-cutover
- [ ] Reconciliation re-checked post-switch
- [ ] Legacy path retirement scheduled (not left running indefinitely)

## Handoffs
- Traffic-shift / deploy automation → `devops-cicd` · DDL mechanics → `database-engineering`.
