# Map the whole buying committee and track champion-redundancy as a durable signal

**Status:** Pattern

**Domain:** Executive-sponsor mapping / Durable partner record

**Applies to:** `edtech-partner-success`

---

## Why this exists

A partner with one champion is one departure from churn — and single-threading is invisible until the champion leaves and the renewal arrives in a dead inbox. Champion-redundancy is a *durable* concern, not a current-quarter one, so it belongs in the partner profile with a status indicator, not buried in a touchpoint log. The deeper failure is mapping only the obvious seat: in K-12 the curriculum / C&I director often sets what kind of solution wins before procurement opens, so a motion threaded only through the superintendent (or only through the friendly user-champion) misses the seat that actually decides. The 6-role taxonomy — economic buyer, champion, technical buyer, user-champion, blocker, executive sponsor — exists so the PSM can see the coverage gaps before they become surprises, and the "ghost sponsor" pattern (a named buyer who left, profile never updated) exists because it recurs.

## How to apply

Maintain a standing committee map per partner with a redundancy status, and refresh it on every handoff, pre-meeting, and annual review.

```
Buying-committee map (in the durable profile, refreshed every ~90 days):
  ROLES — name a real person (or flag the GAP) for each of the 6:
    economic buyer · champion · technical buyer · user-champion · blocker · exec sponsor
    K-12 overlay: don't stop at the superintendent — the curriculum / C&I director
    often sets the winning solution shape pre-procurement.
  REDUNDANCY STATUS:
    1  = single point of failure (surface this risk early; design for it)
    2  = thin
    3+ = robust
  GHOST-SPONSOR CHECK — is each named seat confirmed alive in the role THIS quarter?
    A seat filled by someone who left = a ghost; the play arrives in a dead inbox.
  SPONSOR-HEALTH SIGNAL — QBR no-shows by the sponsor are a sponsor-health signal,
    not a scheduling nuisance. Silence 30+ days → sponsor re-engagement.
  PROTOCOLS — new sponsor arrives → rebuild context (they inherit none).
              sponsor leaves → identify successor before any commercial motion.
              sponsor sidelined → re-thread through a live seat.
```

**Do:**
- Record the map as durable canon (profile), separate from the running diary (touchpoint log) — house opinion §3 #1.
- Treat a redundancy status of 1 as a flagged risk on its own, before any score moves.

**Don't:**
- Run a renewal or expansion motion against a committee map the curator hasn't refreshed in 6 months.
- Confuse the user-champion (loves the product) with the economic buyer (signs the renewal) — they're different seats and often different people.

## Edge cases / when the rule does NOT apply

- **Very small partner** (single-school, one administrator) — the committee may genuinely be one person; then the redundancy=1 risk is structural and the mitigation is a documented second contact, not a phantom second seat.
- **Higher-ed shadow-IT motion** — the committee may sit in a department rather than central IT; map the *actual* deciding body, not the org chart.
- **Corporate L&D under M&A** — the committee can reshuffle wholesale; re-map before re-engaging rather than patching one seat.

## See also

- [`./risk-confirm-the-decision-maker-is-alive-in-the-role-every-quarter.md`](./risk-confirm-the-decision-maker-is-alive-in-the-role-every-quarter.md) — the liveness check this map feeds
- [`./expansion-pitch-only-when-the-partner-has-earned-value.md`](./expansion-pitch-only-when-the-partner-has-earned-value.md) — Gate 3 reads the committee map
- [`../skills/executive-sponsor-mapping/SKILL.md`](../skills/executive-sponsor-mapping/SKILL.md) — the 6-role taxonomy, coverage-gap grid, ghost-sponsor detection, sponsor-change protocols
- [`../templates/partner-profile.md`](../templates/partner-profile.md) — where the durable map lives
- [`../agents/partner-profile-curator.md`](../agents/partner-profile-curator.md) — owns champion-redundancy tracking

## Provenance

Distilled from `skills/executive-sponsor-mapping/SKILL.md` (6-role taxonomy, coverage-gap grid, ghost-sponsor, sponsor-change protocols, QBR-attendance-as-sponsor-health), `agents/partner-profile-curator.md` (champion-redundancy status indicator, durable-not-diary), `knowledge/renewal-pricing-conversations-edtech.md` (curriculum director as the real buyer), and house opinion §3 #1. Authored 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
