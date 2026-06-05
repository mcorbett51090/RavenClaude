# Feature flags have a lifecycle — create, use, and retire them explicitly

**Status:** Pattern
**Domain:** Release engineering / progressive delivery
**Applies to:** `devops-cicd`

---

## Why this exists

Feature flags let you deploy code dark and release behavior separately — a powerful progressive-delivery tool. But flags accumulate: a codebase with dozens of permanent-feeling flags becomes a combinatorial testing nightmare, a source of confusion about what's actually on in prod, and a hiding place for technical debt. Every flag that outlives its purpose adds a conditional branch that will eventually be wrong. Flags are ephemeral by design; treating them as permanent is the anti-pattern.

## How to apply

Give every feature flag an explicit lifecycle with an owner and a retirement date. Use a structured flag catalog (in code, a feature-flag service, or a config file) that captures intent and TTL.

```python
# Example: typed flag definition with explicit TTL and owner
@dataclass
class Flag:
    name: str
    description: str
    owner: str            # team or individual responsible for cleanup
    expires: date         # mandatory — no flag without an expiry
    default_off: bool = True

# Feature flag catalog
CHECKOUT_V2_ROLLOUT = Flag(
    name="checkout_v2_rollout",
    description="Gradual rollout of v2 checkout flow — 0% -> 100%",
    owner="checkout-team",
    expires=date(2026, 9, 1),   # retire after full rollout confirmed
    default_off=True,
)
```

Flag retirement checklist:
- [ ] Flag is 100% on in prod for at least one stable release cycle.
- [ ] Old code path (flag=off branch) has no callers in any running version.
- [ ] Flag removed from code and feature-flag service.
- [ ] PR removes the conditional — the code is now unconditional.

**Do:**
- Assign every flag an owner and an expiry at creation time.
- Add a linter or CI check that fails on flags past their expiry date.
- Track flags in code review — a new flag is a new short-term debt item.
- Remove the flag AND the old code path together; half-cleanup is worse than none.

**Don't:**
- Use flags for permanent configuration (those are env vars or config files, not flags).
- Leave a flag at 100% in prod "just in case" — that's a permanent conditional that buys nothing.
- Let flag cleanup become a separate project; retire flags in the same sprint you finish the rollout.

## Edge cases / when the rule does NOT apply

Kill switches (circuit breakers for a feature that must be disabled fast without a deploy) can be longer-lived than rollout flags, but still need an owner and a review cadence.

## See also

- [`../agents/release-engineer.md`](../agents/release-engineer.md) — owns progressive delivery strategy, including flag-based rollouts.
- [`./deploy-separate-deploy-from-release.md`](./deploy-separate-deploy-from-release.md) — feature flags are the mechanism that separates deploy from release.

## Provenance

Codifies the feature flag lifecycle practices from LaunchDarkly's "Feature Flag Best Practices" and Martin Fowler's "Feature Toggles" article, grounded in the `release-engineer`'s progressive-delivery mandate.

---

_Last reviewed: 2026-06-05 by `claude`_
