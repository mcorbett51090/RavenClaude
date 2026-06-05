# Player feedback during development tests the loop, not the features

**Status:** Pattern
**Domain:** Game design and playtesting
**Applies to:** `game-development`

---

## Why this exists

When internal or external playtesters give feedback during development, the default response is to fix the things they name: "the enemy AI is too hard," "I didn't understand the crafting," "the jump felt off." These are feature-level responses to what are often core-loop symptoms. A player who says "the enemy AI is too hard" may actually be telling you that the game isn't teaching them the tools they need — a loop-design problem. A player who says "I didn't understand the crafting" may be telling you that the economy loop is not surfacing the right moment to craft. Treating playtester feedback as a feature-fix list, rather than as a signal about loop design, leads to an ever-growing backlog of patch fixes on top of a loop that was never validated.

## How to apply

In playtest feedback sessions, categorize every piece of feedback as either a loop signal or a feature signal before scheduling any fix. Address loop signals first.

```
Feedback classification model:

  Feature signal (fix the specific thing named):
    — "This button doesn't respond reliably"
    — "The tooltip text is wrong"
    — "This level has a missing texture"
    → Schedule as a bug or polish item.

  Loop signal (the named thing is a symptom of a loop design question):
    — "I didn't know why I was doing X" → the goal structure of the loop isn't clear
    — "I felt stuck after doing Y" → the loop's progress signal is broken or too slow
    — "The pacing felt off" → loop-beat timing or reward cadence
    — "I kept dying to the same thing" → skill-acquisition loop isn't teaching the tool
    → Investigate the loop design question first; don't patch-fix the symptom.

  Post-playtest protocol:
    1. Collect all feedback items.
    2. Classify each as feature or loop signal.
    3. For loop signals: identify the loop design question (what the signal points to).
    4. Fix loop questions before feature patch items — in that priority order.
    5. After loop fixes are in: re-run the playtest before adding the feature fixes.
```

**Do:**
- Run a feedback classification session with the design lead before any playtest feedback enters the sprint backlog.
- Ask "why did the player experience this?" for every feedback item before assigning it as a bug.
- Re-playtest after a loop fix to validate that the original feedback signal has resolved.

**Don't:**
- Enter playtest feedback directly into the bug tracker without classification.
- Fix feature symptoms while the underlying loop design question is still open.
- Treat "the difficulty is off" feedback as a balance-tune issue without checking whether the skill-acquisition loop is teaching the player the tool they need.

## Edge cases / when the rule does NOT apply

In late-stage polish and QA (post-content-lock), the loop has been validated and feedback is genuinely feature-level. This rule applies most strongly in vertical slice, alpha, and early beta phases when the loop is still mutable. Press/influencer feedback may cover both loop and feature signals; classify before acting.

## See also

- [`../agents/game-designer.md`](../agents/game-designer.md) — owns loop design and the classification of playtest feedback against loop questions.
- [`./prove-the-fun-in-a-vertical-slice-before-the-full-build.md`](./prove-the-fun-in-a-vertical-slice-before-the-full-build.md) — the parent rule on why the vertical slice is the right moment to validate the loop with playtest feedback.

## Provenance

Codifies the loop-signal vs. feature-signal distinction in playtest analysis. The direct-feature-fix response to playtest feedback is the most common playtesting error; the classification step is the standard discipline that prevents feature-patch accumulation on an unvalidated loop.

---

_Last reviewed: 2026-06-05 by `claude`_
