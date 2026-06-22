# Every enforcement action carries an appeal path

**Status:** Absolute rule
**Domain:** Content moderation / due process
**Applies to:** `trust-and-safety`

---

## Why this exists

A system that can act on a user but cannot be contested is not moderation — it is arbitrary power, and it is the anti-pattern this team exists to prevent (house opinion #2). Enforcement is built on imperfect signals: classifiers have false positives, reviewers misread context, policies are ambiguous at the edges. The appeal is how those errors get corrected and how the program learns its own error rate. Due process here is concrete and minimal: **notice** (what happened), a **reason** (which policy, which tier), and a **route to contest** with a human-review SLA. The **appeal-overturn rate** that falls out is not a complaints box — it is the single best signal of where the policy or the classifier is wrong.

## How to apply

Attach an appeal path to **every** rung of the ladder — including the warn, including the ban. Wire the overturn rate back as a quality signal.

```
Every action emits:
  Notice:  "Your <content/account> was <actioned> on <date>."
  Reason:  "Policy: <category> · Tier: <severity>."
  Contest: <one route to appeal> · Human-review SLA: <24h for suspend/ban>.

Then: appeal-overturn rate is monitored per category; a rising rate triggers a
      policy-definition or classifier-threshold review.
```

**Do:**
- Give notice + reason + a findable contest route for every action.
- Set a human-review SLA on appeals, tightest for account-level penalties.
- Treat a high overturn rate as a defect in the policy/classifier — fix the source.

**Don't:**
- Ship an enforcement action with no way to contest it.
- Bury the appeal route so the appeal rate is near zero (that is a due-process failure, not success).
- Dismiss overturns as "users gaming the system" — they are feedback.

## Edge cases / when the rule does NOT apply

- **Legally-mandated removals** (e.g. CSAM-class) may not be user-appealable in the ordinary flow, but still carry the lawful process appropriate to them — the principle (a defined process, not arbitrariness) holds.
- **Obvious automated spam at scale** may use a lighter-weight appeal (a single re-review trigger) rather than a full review, but the route must still exist.

## See also

- [`../knowledge/trust-safety-metrics.md`](../knowledge/trust-safety-metrics.md) — the appeal-overturn-rate metric and how to read it.
- [`./enforcement-ladder-proportionality.md`](./enforcement-ladder-proportionality.md) — the companion rule: the action the appeal contests.
- [`../templates/content-policy-doc.md`](../templates/content-policy-doc.md) — §4 Appeal path the policy must fill in.

## Provenance

Codifies house opinion #2 (appeals are due process) in [`../CLAUDE.md`](../CLAUDE.md) §3. Consensus Trust & Safety due-process practice; domain-neutral.

---

_Last reviewed: 2026-06-17 by `claude`_
