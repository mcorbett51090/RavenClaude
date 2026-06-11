# Denials are prevented at the source, not appealed at the end

**Status:** Pattern.

**Rule:** Every denial has an origin — documentation, point-of-care minutes, intake authorization, or
threshold tracking. Fix the cause where it originates. An appealed denial is rework; a prevented one
is margin.

## Why

Working denials at the back end is the most expensive way to run a revenue cycle: staff time to appeal,
delayed cash, and a portion that never gets recovered. Yet each denial reason maps cleanly to an
upstream origin — a necessity denial to a documentation gap, a units denial to unrecorded minutes, an
auth denial to intake. Closing the cause at its source prevents the entire class of denial going
forward, while appealing one claim recovers (maybe) one claim. The leverage is enormously in favor of
prevention.

## What it looks like in practice

- Denials are clustered by reason code and each cluster traced to its origin (documentation / minutes /
  intake / threshold / coding).
- The fix is applied at the origin step so the next claim doesn't repeat it.
- First-pass clean-claim rate is tracked as the prevention metric, not just denial-recovery rate.

## Anti-pattern

A busy appeals operation that reworks the same denial types month after month because the upstream
cause (intake verification, point-of-care minute capture) was never fixed. Verify coding/payer
specifics against current policy and a certified coder.
