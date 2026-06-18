# Measure developer activation, not vanity metrics

**Status:** Absolute rule
**Domain:** DevRel strategy & measurement
**Applies to:** `developer-relations`

---

## Why this exists

GitHub stars, follower counts, impressions, and cumulative "registered developers" only ever go up
and never force a decision. They make a DevRel program *look* successful while the activation stage
silently leaks. A program reported in vanity metrics is the first budget line cut in a downturn,
because nobody can tie it to an outcome. The spine metric is **time-to-first-success** and the
**activation rate** — signed-up developers who reached a first working result.

## How to apply

**The vanity tell:** if a metric can't go *down*, it isn't measuring anything. A real metric can get
worse, and when it does you change something.

**The scorecard:**
- **Headline:** time-to-first-success (median + step count) and activation rate, trended over time.
- **Retention:** returning developers (WAU/MAU of the SDK/API).
- **Community:** resolution rate / unanswered-question rate.
- **Context (below the line):** reach, stars, event count — kept for color, never the headline.

**Do:**
- Lead every report with an activation metric.
- Demote stars/followers to context, not deletion — they're a weak awareness signal.
- Make every number ownable by a *funnel stage*, not a person.

**Don't:**
- Put GitHub stars or "registered developers" at the top of a board deck.
- Report cumulative counts that can't decrease.
- Treat a metric movement as an advocate's performance score (it's a program signal — house opinion #7).

## Edge cases / when the rule does NOT apply

- **Very early awareness stage** with no product to activate into yet — reach is legitimately the
  near-term signal, but say so explicitly and set the date you'll switch to activation.
- A genuinely **awareness-bound** goal (e.g. a brand launch) can headline reach for that campaign —
  but the *program* scorecard still leads with activation.

## See also

- [`../knowledge/devrel-funnel-and-metrics.md`](../knowledge/devrel-funnel-and-metrics.md) — the funnel + the vanity-vs-real table
- [`./optimize-time-to-first-success.md`](optimize-time-to-first-success.md) — the metric to improve first

## Provenance

Codifies developer-relations CLAUDE.md §3 house opinion #1. The vanity-vs-actionable-metric
distinction is standard analytics practice (Ries, *Lean Startup*, 2011); the awareness→activation→
advocacy funnel is the standard DevRel adaptation of pirate-metrics (AARRR).

---

_Last reviewed: 2026-06-18 by `claude`_
