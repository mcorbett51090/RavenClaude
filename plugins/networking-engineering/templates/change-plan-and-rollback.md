# Network Change Plan & Rollback — <change title>

> One change, one plan. No production network change ships without the rollback section
> filled in. Ties to best-practice [`../best-practices/no-change-without-a-rollback-path.md`](../best-practices/no-change-without-a-rollback-path.md).

## Summary

- **What changes:** <one sentence>
- **Why:** <driver / ticket>
- **Devices affected:** <list>
- **Blast radius / shared failure domain:** <what else could be impacted>
- **Window:** <date/time, duration> — **Approver:** <name>

## Success criteria (validate against these)

- [ ] <e.g. prefix X reachable from site Y>
- [ ] <e.g. BGP neighbor Z established>
- [ ] <e.g. east-west flow A→B denied as intended>

## Pre-change state capture

```
# commands / outputs to capture BEFORE the change (routing table, adjacencies,
# interface + ACL counters, the specific flows affected)
```

## Change steps

1. <step>
2. <step>

> Apply behind commit-confirm / rollback timer where supported.

## Validation (post-change, from a SECOND path)

1. <re-run success-criteria checks from a device you did NOT change>
2. <compare counters/flows to the pre-change capture>

## Rollback

- **Trigger:** <what result means "roll back">
- **Method:** <commit-confirm auto-revert / apply saved rollback config / reload-to-rollback>
- **Rollback validation:** <how you confirm service is restored>
- **Max time before auto-revert fires:** <N minutes>

## Post-change

- [ ] Back-port any manual fix into config-as-code / source of truth
- [ ] Update drift baseline
- [ ] Close ticket with the validation evidence
