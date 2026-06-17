# Optimize for time-to-first-hello-world — it gates activation

**Status:** Absolute rule
**Domain:** Developer experience / activation
**Applies to:** `developer-relations`

---

## Why this exists

Time-to-first-hello-world (TTFHW) is the elapsed time from a developer's first step to their first *real* runnable result. It is the single most leveraged number in DevRel because it gates **activation**, and activation gates retention, revenue, and referral downstream (the AAARRP funnel in [`../knowledge/devrel-metrics.md`](../knowledge/devrel-metrics.md)). A developer who hits a 40-minute setup before their first success bounces before any talk, post, or community can reach them. No amount of awareness work fixes a TTFHW problem — it pours water into a leaky bucket. Shrinking TTFHW moves activation more than any campaign.

## How to apply

Measure TTFHW **on a clean machine**, end-to-end, the way a new developer experiences it — never from your already-configured laptop. Then cut everything before first hello-world that doesn't gate the result:

```
TTFHW = t(first runnable result) − t(first step)        # lower is better

Before:  signup → email verify → create API key → install → configure → first call   (~12 min)
After:   install → first call against a pre-provisioned sandbox key                   (~90 sec)
         (signup deferred PAST first hello-world)
```

**Do:**
- Define first hello-world as the *smallest real* result (a returned response, a rendered output), and make the quickstart reach it in the fewest steps.
- Defer signup / API-key creation past first hello-world wherever possible (sandbox or demo keys).
- Report TTFHW with the path that produced it ("90s with a sandbox key; 12 min if account creation is required first").

**Don't:**
- Measure TTFHW from your own configured environment — that hides the real friction.
- Gate first hello-world on account creation, email verification, or manual config that could be deferred.
- Prescribe more awareness content for an activation (TTFHW) problem.

## Edge cases / when the rule does NOT apply

- **Genuinely security-sensitive products** may not be able to offer an unauthenticated sandbox — then minimize the *auth* TTFHW (one-click key, not a multi-step form), don't pretend it's zero.
- **Enterprise/on-prem products** have an irreducible setup floor — measure TTFHW from the realistic starting point and optimize within it; don't claim a SaaS-style 90 seconds.

## See also

- [`../knowledge/devrel-metrics.md`](../knowledge/devrel-metrics.md) — §2 TTFHW definition and the activation-rate formula.
- [`./sample-apps-must-run-unmodified.md`](./sample-apps-must-run-unmodified.md) — the companion rule that keeps the fast path actually runnable.
- [`../skills/author-quickstart-and-sample-app/SKILL.md`](../skills/author-quickstart-and-sample-app/SKILL.md) — the procedure that produces a low-TTFHW quickstart.

## Provenance

Codifies house opinion "TTFHW is the single most leveraged number in DevRel" in [`../CLAUDE.md`](../CLAUDE.md) §3 and the §2 metric definition in [`../knowledge/devrel-metrics.md`](../knowledge/devrel-metrics.md). Field-standard activation framing (last reviewed 2026-06-17).

---

_Last reviewed: 2026-06-17 by `claude`_
