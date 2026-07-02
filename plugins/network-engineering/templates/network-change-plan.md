# Network Change Plan — <change>

## Change
- **What + why:** <...>
- **Requested by / date / target window:** <...>

## Blast radius
- **Touches:** <devices/segments/services> · **Depends on it:** <who>
- **Worst case:** <...> → **change-control rigor:** <low | standard | high/CAB>

## Baseline / pre-checks (capture BEFORE touching anything)
- [ ] Config backup of <devices>
- [ ] Routing table / neighbor / interface snapshot
- [ ] Reachability tests (the ones you'll re-run after): <list>
- [ ] Out-of-band/console access confirmed

## Steps (staged, expand/contract where possible)
1. <step> — **verification gate:** <confirm X before proceeding>
2. <step> — **verification gate:** <...>
3. <...>

## Rollback (reverse of each step + trigger)
- **Trigger:** if <verification gate N fails> → execute rollback.
1. <reverse of step N>
2. <...>

## Post-checks (success = baseline re-run + compare)
- [ ] Re-run reachability tests; compare to baseline
- [ ] Neighbors/routes/interfaces match expected
- [ ] Capture the diff + rationale; codify in IaC (terraform-iac) where applicable
