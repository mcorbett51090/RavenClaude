# No change without a rollback

**Rule:** Every change to a running network ships a captured baseline, a change window sized to the blast radius, staged steps with verification gates, and a *tested* rollback with a trigger condition.

**Why:** a network change with no rollback is a gamble against uptime. The baseline is what lets you prove success and return cleanly; the verification gates localize a failure to the step that caused it.

**Anti-pattern:** a big-bang cutover at peak hours with no pre-change snapshot and "we'll figure out rollback if it breaks." Prefer expand/contract + parallel-run; keep out-of-band access to anything you're changing the path through.
