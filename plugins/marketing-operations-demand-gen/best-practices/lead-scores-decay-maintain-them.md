# Lead scores decay — maintain them

**Status:** Pattern
**Domain:** Lead scoring / marketing automation
**Applies to:** `marketing-operations-demand-gen`

---

## Why this exists

A lead scoring model built once and never updated is an archaeological artifact. It rewards contacts
for actions taken 18 months ago, promotes cold leads based on historical behavior that no longer
reflects current intent, and sends Sales to contacts who have long since moved to a competitor or
changed roles. The score is no longer a signal — it is a noise-amplifier.

Lead scores decay in two ways: (1) individual contact activity becomes stale as time passes and
(2) the ICP criteria and behavioral signals themselves change as the business evolves. Both decay
mechanisms require active maintenance, not passive monitoring.

## How to apply

- **Implement recency decay on behavioral scores.** Every behavioral score point has a half-life.
  Implement time-based decay natively in the MAP (Marketo Score Programs with decay Smart Campaigns,
  HubSpot Workflow-based score reduction, Pardot Automation Rules [verify-at-use]) or via a
  scheduled batch process. At minimum, reset behavioral scores to zero after 90–180 days of
  inactivity.
- **Add negative scoring for inactivity.** If a contact has not engaged with any marketing touch
  in 90 days, reduce their score. If inactive for 120+ days, reduce it further. This ensures
  long-inactive contacts cannot maintain a high composite score.
- **Run a quarterly scoring committee.** Marketing and Sales jointly review: (a) the distribution
  of MQL scores across recent leads, (b) the Sales rejection reason taxonomy from the past quarter,
  (c) the MQL→SQL conversion rate by score band, and (d) whether the demographic/firmographic fit
  criteria still match the current ICP.
- **Version the scoring model.** Document each scoring revision with a date and the rationale.
  When the ICP changes (e.g., you start selling upmarket), the scoring model must be updated to
  reflect the new firmographic criteria — not just the behavioral weights.

**Do:**

- Treat the scoring model as a living configuration, versioned like software.
- Alert the team when the MQL→SQL conversion rate drops significantly — it is an early warning
  of score model drift.
- Test any scoring change on a historical cohort before deploying to the live database.

**Don't:**

- Build a scoring model, deploy it, and never revisit it.
- Allow behavioral scores to accumulate indefinitely with no decay or cap.
- Change scoring thresholds without notifying Sales — it changes their expected lead volume.
- Rely on MAP-native scoring alone if it doesn't support decay; build the decay logic explicitly.

## Edge cases / when the rule does NOT apply

Hand-raise signals (demo request, pricing page visit with a form fill, direct sales contact
request) carry high intent regardless of recency. These bypass scoring decay and should trigger
MQL status or direct routing without waiting for the composite score. The decay rule applies to
passive engagement signals, not active hand-raises.

## See also

- [`./mql-is-a-handoff-contract-not-a-trophy.md`](./mql-is-a-handoff-contract-not-a-trophy.md)
- [`../skills/lead-scoring-and-lifecycle/SKILL.md`](../skills/lead-scoring-and-lifecycle/SKILL.md)
- [`../knowledge/marketing-ops-decision-trees.md`](../knowledge/marketing-ops-decision-trees.md) — Lead-score design tree.

## Provenance

Codifies the lead scoring maintenance discipline from Marketo's "Definitive Guide to Lead Scoring"
(Adobe), HubSpot's scoring best-practice documentation, and the B2B marketing ops practitioner
consensus (MO Pros, Demand Gen Report) that scoring decay and quarterly calibration are standard
operating practice for any mature lead scoring implementation.

---

_Last reviewed: 2026-06-08 by `claude`._
