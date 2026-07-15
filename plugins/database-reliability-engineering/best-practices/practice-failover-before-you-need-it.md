# Practice failover before you need it

A failover path that has never been exercised will fail when it counts — a stale
DNS TTL, an app that caches the old primary, a replica too far behind to promote, a
split-brain because the fencing was never tested. The first real failover should not
be the first failover.

**Do:** rehearse failover and restore as scheduled game-days in a non-prod (or
carefully in prod during a low window): promote a replica, confirm the split-brain
guard fires, verify the app reconnects, measure the real RTO (which includes
reconnection and validation, not just promotion), and roll back.

**Don't:** treat "we have automatic failover configured" as "failover works." A
configuration is a hypothesis until it's been triggered end-to-end.

**Flag:** an HA setup whose failover has never been drilled, an unknown real-world
RTO, or a runbook step no one has actually executed.
