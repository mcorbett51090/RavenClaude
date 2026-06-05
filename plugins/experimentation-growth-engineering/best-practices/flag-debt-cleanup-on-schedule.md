# Clean up feature flags on a scheduled cadence, not someday

**Status:** Absolute rule
**Domain:** Feature flags / technical debt
**Applies to:** `experimentation-growth-engineering`

---

## Why this exists

A feature flag that shipped the feature and was never removed is dead configuration
code that still runs on every request. After a few quarters, a codebase with 50+
stale flags has a combinatorial config-space that no one can reason about, a risk
surface from flags that could accidentally be toggled, and a maintenance burden
that grows monotonically. Teams that say "we'll clean up when we get time" never
get time. The only working approach is a scheduled, enforced removal deadline
baked into the flag's creation event.

## How to apply

**At flag creation:** record the owner, the expected removal date, and the
removal condition in the flag's metadata.

**At removal date:** the flag owner gets an automated reminder (most flag
platforms support this natively `[verify-at-use]`). If the flag is still needed,
the owner explicitly extends the deadline — the extension is a conscious act,
not a default.

**Periodic audit (monthly):** a script lists all flags past their removal date
and reports them to the team.

```yaml
# Example flag metadata (LaunchDarkly / Flagsmith / etc. — field names vary)
name: "new-checkout-flow"
key: "new_checkout_flow"
owner: "eng-growth"
created: "2026-06-05"
removal_deadline: "2026-09-05"   # 90 days: typical release flag TTL
removal_condition: "experiment concluded AND treatment shipped to 100%"
tags: ["release", "checkout"]
```

```bash
# Stale flag audit (pseudo — adapt to your platform's API)
flags=$(launchdarkly_api list_flags)
today=$(date +%Y-%m-%d)
echo "$flags" | jq -r \
  --arg today "$today" \
  '.[] | select(.removal_deadline < $today) | "\(.key)\t\(.owner)"'
```

**Do:**
- Set a removal deadline at flag creation, not retroactively.
- Make deadline extension a deliberate action with a logged reason.
- Gate on `removal_deadline` in CI: fail the build if code still references a
  flag past its deadline.

**Don't:**
- Leave flags with no removal date ("permanent" flags should be config, not
  feature flags, with very rare exceptions).
- Use "someday cleanup sprint" as the removal strategy — it never arrives.
- Remove flags without checking for all references in the codebase first.

## Edge cases / when the rule does NOT apply

- Ops flags (circuit breakers, kill switches) and permission flags (feature
  gating by tenant/plan): these are long-lived by design. Document them as
  permanent ops/permission flags explicitly; they are not release/experiment
  flags and don't need a removal deadline.

## See also

- [`../agents/feature-flag-engineer.md`](../agents/feature-flag-engineer.md) — owns flag lifecycle
- [`./every-flag-has-a-kill-switch-and-a-lifecycle.md`](./every-flag-has-a-kill-switch-and-a-lifecycle.md) — the upstream rule this cleanup discipline completes

## Provenance

Codifies the flag-debt management section of house opinion #2 from `CLAUDE.md`
§2 ("every flag has a lifecycle and a removal date — stale flags are a
combinatorial config-space nightmare"). Standard feature-flag engineering practice.

---

_Last reviewed: 2026-06-05 by `claude`_
