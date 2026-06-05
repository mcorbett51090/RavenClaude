# Soft launch is a tuning gate, not a slow rollout

**Status:** Pattern
**Domain:** Game production and live-ops
**Applies to:** `game-development`

---

## Why this exists

Many studios treat a soft launch as a geographic rollout that will eventually become global — something that happens slowly while the team finishes content. This misunderstands what a soft launch is for. A soft launch is a data-collection and tuning gate: you are measuring D1/D7/D30 retention, ARPDAU, conversion, and tutorial completion against specific thresholds. You do not go global until those metrics cross the threshold. If you treat it as a slow rollout, you push marketing spend before the game is ready to retain players — and you spend CAC on players who churn in the first session. The soft-launch metrics are the gate. The gate is what makes the global launch safe to scale.

## How to apply

Define the global-launch gate criteria before the soft launch begins. Do not schedule the global launch date until the gate is passed.

```
Soft-launch gate criteria template (adjust to genre and segment):

  Tier 1 — MUST pass before global launch (hard gate):
    D1 retention: >= 40% [ESTIMATE — benchmark varies significantly by genre]
    Tutorial completion: >= 70%
    Crash-free rate: >= 99%

  Tier 2 — SHOULD pass before global launch (soft gate — waiver requires written decision):
    D7 retention: >= 20% [ESTIMATE]
    ARPDAU trend: flat or positive over last 14 days (not declining)
    Top review topics: no dominant refund / content-depth complaint pattern

  Gate decision rule:
    Tier 1 not met → do not go global. Fix the issue. Re-measure.
    Tier 1 met, Tier 2 not met → document the specific waiver with the known risk.
    Both tiers met → proceed to global launch.

Soft-launch market selection:
  Choose markets with similar player behavior to your target global market but lower CPM
  (common choice: Canada, Australia, New Zealand for English-language games) [ESTIMATE].
  Avoid markets where demographic differences make metrics unrepresentative of the global target.
```

**Do:**
- Write the gate criteria and thresholds before the soft launch, not during.
- Keep the soft launch small enough to tune quickly; over-indexing on scale before the gate is passed wastes marketing spend.
- Treat a missed Tier 1 gate as a "stop and fix" signal, not a "launch and patch" signal.

**Don't:**
- Schedule the global launch date before the soft launch begins (it creates schedule pressure that overrides the gate).
- Use soft-launch marketing spend to drive volume before D1/D7 thresholds are met.
- Skip the soft launch for a "small indie" game — the gate applies regardless of budget; the stakes scale but the principle doesn't.

## Edge cases / when the rule does NOT apply

Premium (paid) games launching on PC/console typically have different pre-launch validation paths (press embargo, review period) rather than a soft launch; the gate-criteria concept applies but the mechanism is different. Very small indie games launching on itch.io or similar low-stakes platforms may use a soft launch as a genuine slow rollout with less rigorous gate criteria.

## See also

- [`../agents/gamedev-producer.md`](../agents/gamedev-producer.md) — owns the production plan and milestone gates where the soft-launch gate criteria must be embedded.
- [`./retention-before-monetization-d1-d7-d30-are-the-vital-signs.md`](./retention-before-monetization-d1-d7-d30-are-the-vital-signs.md) — the companion rule on why D1/D7/D30 gates the monetization push.

## Provenance

Codifies standard mobile/F2P soft-launch practice. The slow-rollout misunderstanding is the most common soft-launch failure mode; the gate-criteria discipline is the standard prevention used by experienced mobile studios.

---

_Last reviewed: 2026-06-05 by `claude`_
