# Size the Sprint Commitment to Demonstrated Capacity, Not Aspiration

**Status:** Absolute rule
**Domain:** Project Management — Agile / Scrum
**Applies to:** `project-management`

---

## Why this exists

An over-committed sprint is a broken one before it starts. Teams that pad velocity, ignore known absences, or carry forward the "we can do better" story end every sprint with partial delivery, carry-over creep, and a velocity signal that cannot be used for planning. The sprint commitment is a *forecast*, not a stretch goal. Credible forecasts are built on what the team has demonstrated it can complete at sustainable pace — not on what the team believes it *should* be able to do.

## How to apply

**Capacity-based sprint sizing process:**

1. **Establish available hours** for the sprint window:
   ```
   Team capacity = Σ (person-days available) × focus factor
   focus factor = typically 0.6–0.7 (accounts for meetings, interruptions, non-sprint work)
   ```
2. **Anchor to recent velocity**: use the average of the last 3–5 sprints (story points or story count). Do not use the single highest sprint.
3. **Adjust for this sprint's known variances**: vacations, on-call duty, tech-debt items, sprint ceremonies.
4. **Size the commitment to the *adjusted* capacity**: stop before the capacity ceiling, not at or above it.
5. **Maintain a prioritized buffer list**: 1–2 items below the commitment line that can be pulled in if the team finishes early — these are never in the sprint commitment itself.

**Do:**
- Document the capacity calculation in the sprint plan for auditability.
- Flag a sprint where historical velocity is unavailable (new team, new tech) as an estimate, not a forecast.
- Update the team's definition of "done" before sizing if the scope of a point has changed.

**Don't:**
- Add velocity buffer for a milestone ("we're only two sprints from launch, let's push harder").
- Accept mid-sprint injection of new stories without explicit trade-off (remove something of equal size).
- Use the theoretical maximum capacity (ignoring focus factor) as the basis for the commitment.

## Edge cases / when the rule does NOT apply

- **First sprint of a new team**: no historical velocity exists; use a rough sizing exercise (team's estimate of what is feasible) and treat the result as a learning sprint, not a contractual commitment.
- **Hardened-scope milestone with a known fixed date**: the `delivery-lead` must flag the capacity gap to the sponsor; the scrum-master still sizes to demonstrated capacity and surfaces the risk — they do not inflate the velocity to meet the date.

## See also

- [`../agents/scrum-master.md`](../agents/scrum-master.md) — the agent that runs sprint planning
- [`./commitments-have-one-owner-and-one-date.md`](./commitments-have-one-owner-and-one-date.md) — the parallel rule that each commitment in the sprint plan has a named owner

## Provenance

Codifies house opinion #6 ("Capacity, not aspiration") from `CLAUDE.md` §3. Capacity-based sprint sizing is standard Scrum practice (Scrum Guide 2020; Mike Cohn, "Agile Estimating and Planning"). _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
