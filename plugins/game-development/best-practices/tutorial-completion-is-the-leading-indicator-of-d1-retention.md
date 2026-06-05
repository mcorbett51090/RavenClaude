# Tutorial completion is the leading indicator of D1 retention

**Status:** Primary diagnostic
**Domain:** Game retention and onboarding
**Applies to:** `game-development`

---

## Why this exists

D1 retention is the vital sign that determines whether the game has a pulse. But by the time you're reading D1, the onboarding moment that set the outcome is already in the past. Tutorial completion rate — measured in the first session — is the leading indicator for D1 and is actionable in real time. A game with 65% tutorial completion predicts a D1 retention problem before you wait 24 hours to see the D1 number. The tutorial completion funnel also shows you exactly where the drop-off happens, which makes it a diagnostic tool: a 30% drop at the first combat tutorial means the combat feel or the instructions failed; a 20% drop at the first economy decision means the game's core loop isn't landing. These are fixable before global launch if you're measuring them.

## How to apply

Instrument the tutorial funnel at discrete checkpoints — not just "started" and "completed," but at each decision point or new mechanic introduction. Measure and review during soft launch before global.

```
Tutorial funnel instrumentation:

  Event log at each checkpoint:
    — TUTORIAL_STARTED
    — TUTORIAL_STEP_[N]_COMPLETED (one per meaningful mechanic or decision)
    — TUTORIAL_COMPLETED
    — TUTORIAL_SKIPPED (if you allow it — usually a mistake for new players)

  Funnel analysis:
    step_N_completion_rate = players reaching step N+1 / players reaching step N
    overall_completion_rate = TUTORIAL_COMPLETED / TUTORIAL_STARTED

  Target [ESTIMATE — calibrate to your genre]:
    Mobile F2P: overall completion >= 70%
    Mid-core / PC: overall completion >= 60%
    No single step drop > 15% (a drop > 15% at one step is a fix priority)

  D1 prediction rule:
    tutorial_completion_rate × expected post-tutorial D1 retention ≈ overall D1
    Example: 75% tutorial completion × 60% post-tutorial D1 ≈ 45% overall D1
    → use this model to predict D1 range during soft launch before the 24-hour wait

  Diagnostic: pull the step with the highest single-step drop and play it yourself
  with a first-time player mindset before any A/B test or rewrite.
```

**Do:**
- Instrument tutorial completion checkpoints on the first day of soft launch, not as a post-launch add-on.
- Review the tutorial funnel weekly during soft launch.
- Fix any step with > 15% drop before optimizing any later-game retention lever.

**Don't:**
- Use tutorial completion as a binary (started/completed) — the step-level funnel is the diagnostic value.
- Allow players to skip the tutorial without tracking that separately.
- Wait for D1 to evaluate whether the tutorial is working — the funnel is the leading signal.

## Edge cases / when the rule does NOT apply

Games with experienced or returning player bases (sequels, returning players from a beta) may have different tutorial completion dynamics because experienced players often skip or race through tutorials. Separate the new-player funnel from the returning-player funnel when analyzing. Hardcore strategy games where the tutorial is intentionally opaque (e.g., Dwarf Fortress genre) have a different audience expectation; the standard completion-rate thresholds don't apply.

## See also

- [`../agents/live-ops-analyst.md`](../agents/live-ops-analyst.md) — reads the retention and onboarding funnel metrics.
- [`./retention-before-monetization-d1-d7-d30-are-the-vital-signs.md`](./retention-before-monetization-d1-d7-d30-are-the-vital-signs.md) — the parent rule on why D1 is the first gate; tutorial completion is the upstream signal.

## Provenance

Codifies the tutorial-completion-as-D1-leading-indicator relationship standard in mobile/F2P analytics. The binary start/complete measurement is the most common instrumentation gap; the step-level funnel is what makes the signal actionable before global launch.

---

_Last reviewed: 2026-06-05 by `claude`_
