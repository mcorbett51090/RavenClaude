# Partner Pickup Brief — `<Partner Name>`

> **5-minute read for a PSM picking up this account cold.** Vacation backfill, handoff between owners, leadership ask, pre-call refresh. Mirrors the dashboard's per-partner pickup-brief drill-down 1:1 — same shape, two surfaces. Generated from the same `bi-report/data.json` paths (called out below as `→ data.json: …`); when the dashboard updates, this brief should too.
>
> **Refresh trigger:** weekly (Mondays) or before any unscheduled handoff.
> **Last refreshed:** `<YYYY-MM-DD>`
> **By:** `<PSM name>`
>
> **Audience:** ☐ PSM of record  ☐ PSM backfilling cold  ☐ CS leadership  ☐ Cross-functional (AE / product / support)

---

## 1. Where we are right now

> → `data.json: partners[].pickup.where_we_are`

One plain-language sentence. School-year phase, days since last touch, days to renewal.

**Phase:** `<e.g., Phase 2 (Settling, weeks 4-8 — most-predictive period for partner success)>` → `data.json: school_year.current_phase` (see [`knowledge/k12-adoption-arc-fall-spring-summer.md`](../knowledge/k12-adoption-arc-fall-spring-summer.md) §"Phase model")

**Health band + score:** `<Green / Yellow / Red — score / delta vs. last period>` → `data.json: partners[].band, .score, .delta`

**Last touch:** `<YYYY-MM-DD — N days ago>` → `data.json: partners[].last_touch`

**Renewal:** `<YYYY-MM-DD — N days out>` → `data.json: partners[].renewal`

**Active play:** `<Maintain / Recovery / Expand / Adoption push / etc.>` → `data.json: partners[].play`

**One-line summary:**
> `<e.g., "Phase 2 (Settling). Last touch 4 days ago. Renewal in 165 days. Steady, green.">`

---

## 2. What's promised (open commitments)

> → `data.json: partners[].pickup.commitments[]`

What we owe the partner, with owner + due date. **Anti-pattern hook (§3 #13):** every commitment needs an owner and a due date — if either is missing, surface it.

| Commitment | Owner | Due | Source |
|---|---|---|---|
| `<item>` | `<name>` | `<YYYY-MM-DD>` | `<PH / SFDC / SNOW / ZAP / GRN>` |
| `<item>` | `<name>` | `<YYYY-MM-DD>` | `<source>` |

**Overdue commitments:** `<list, or "none">`

---

## 3. What's next (next 3 actions due)

> → `data.json: partners[].pickup.next_actions[]`

The next 3 things due, by date. A mix of CS activities (Planhat) and SFDC tasks. Use this to plan the week.

| Action | Due | Source |
|---|---|---|
| 1. `<item>` | `<YYYY-MM-DD>` | `<source>` |
| 2. `<item>` | `<YYYY-MM-DD>` | `<source>` |
| 3. `<item>` | `<YYYY-MM-DD>` | `<source>` |

---

## 4. Don't say / don't push (sensitivities + dead zones)

> → `data.json: partners[].pickup.dont_push[]`

What a backfill PSM would otherwise step on. Dead-zone overlays from [`knowledge/k12-psm-operating-cadence.md`](../knowledge/k12-psm-operating-cadence.md) §2 plus partner-specific sensitivities.

- `<e.g., "State testing window Apr 7–25 — no expansion asks during this period.">`
- `<e.g., "Champion is on partial PD leave through mid-June — keep asks light.">`
- `<e.g., "Renewal is in 88 days; do NOT raise expansion. Stabilize first.">`
- `<e.g., "Avoid jargon — new district leadership unfamiliar with product.">`

---

## 5. Who's who

> → `data.json: partners[].pickup.who_is_who[]`

Decision-makers with **confirmed alive in role** dates. Plugin rule §3 #4: every status carries the signals that drove it; named champion role-confirmation is one of them.

| Role | Name | Title | Confirmed in role | Source |
|---|---|---|---|---|
| Champion | `<name>` | `<title>` | `<YYYY-MM-DD or "(vacant)">` | `<source>` |
| Executive sponsor | `<name>` | `<title>` | `<YYYY-MM-DD>` | `<source>` |
| Economic buyer | `<name>` | `<title>` | `<YYYY-MM-DD>` | `<source>` |
| Technical buyer | `<name>` | `<title>` | `<YYYY-MM-DD>` | `<source>` |
| Blocker (if any) | `<name>` | `<title>` | `<YYYY-MM-DD>` | `<source>` |

**Champion redundancy:** `<1 (single point of failure) | 2 (thin) | 3+ (robust)>` — mirrors `templates/partner-profile.md`.

**Watch list:** `<any role that's "(vacant)" or unconfirmed > 90 days>`

---

## 6. Multi-year context (optional, expand only if relevant)

> → `data.json: partners[].history[]`

| Year | End-of-year score | Renewal outcome | ARR delta | QBR count |
|---|---|---|---|---|
| `<YYYY-YY>` | `<0–100>` | `<renewed-flat / renewed-increase / renewed-decrease / churned>` | `<+/− $>` | `<n>` |

**Trend across years:** `<one line — improving / steady / declining / volatile>`

---

## Output contract

Per the plugin's [`CLAUDE.md`](../CLAUDE.md) §6 Output Contract, when an agent generates this brief end the report with:

```
Status: ✅  |  ⚠️ partial  |  ❌ blocked
Files changed: <relative path>
Partner / segment context: <named partner + segment K-12 / higher-ed / corp L&D / mixed>
Signals cited: <fields in §1, §3, §6 cited with date / range and source system>
Followups: <commitments in §2 and next actions in §3, with owners + dates>
Open questions: <anything the Team Lead needs to decide before this can ship>
Grounding checks performed: <which data.json paths were read; which sources were stale at read time>
```

Then the JSON block per `ravenclaude-core/skills/structured-output/SKILL.md`.

---

## References

- Dashboard rendering of the same data: [`../skills/health-report-dashboard/SKILL.md`](../skills/health-report-dashboard/SKILL.md)
- Field-to-source contract: [`../skills/cs-platform-integration/SKILL.md`](../skills/cs-platform-integration/SKILL.md)
- Identity spine + failure modes: [`../knowledge/cs-stack-integration-planhat-sfdc-snowflake.md`](../knowledge/cs-stack-integration-planhat-sfdc-snowflake.md)
- School-year phase model: [`../knowledge/k12-adoption-arc-fall-spring-summer.md`](../knowledge/k12-adoption-arc-fall-spring-summer.md)
- Dead-zone calendar: [`../knowledge/k12-psm-operating-cadence.md`](../knowledge/k12-psm-operating-cadence.md) §2
- The durable partner record (the canon): [`partner-profile.md`](partner-profile.md)
- The running diary: [`touchpoint-log.md`](touchpoint-log.md)
- Sponsor / champion taxonomy: [`../skills/executive-sponsor-mapping/SKILL.md`](../skills/executive-sponsor-mapping/SKILL.md)
