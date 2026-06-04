# Build plan for Codex — Partner Success Command Center, Tier 4 (motion lenses)

**Audience:** a fresh **Codex (GPT-5.5) session running in GitHub Copilot CLI**, in a Codespace with RavenClaude installed. Codex is the engineer; this file is the engineer's brief. **Self-contained — do not ask Matt to clarify what's already in here.**

**Scope:** Tier 4 of [`plan.md`](./plan.md) — the **5 motion-lens pages** that organize partners by business motion (success-plan progress, expansion opportunity, PD utilization, contract lifecycle, relationship mapping) rather than by audience segment. Each lens REUSES Tier 2's `openPartner360(account_uid)` drill-down + Tier 3's `renderLens` primitive; no new drill-downs, no new shared primitives.

**Pre-build gate:** Tier 2 ([`build-plan-tier-2-drill-downs.md`](./build-plan-tier-2-drill-downs.md)) merged. **Tier 3 strongly recommended but not strictly required** — Tier 4 can ship in parallel because both consume `lens-shared.js`; if Tier 4 ships first, `lens-shared.js` becomes a Tier 4 deliverable instead and Tier 3 reuses it. The cross-section-consistency gate (Gate 53) must pass at all times.

**Pattern-replication tier.** Each motion lens shares the `renderLens` skeleton from Tier 3 but adds **deterministic business-rule logic** (auto-flag criteria, alert bucket logic, expiration thresholds). The business rules are the load-bearing part — Codex MUST cite the source knowledge files for each rule, not invent thresholds.

---

## 0. Dependencies

- **Tier 0** ([`build-plan-for-codex.md`](./build-plan-for-codex.md)) — schema + fixture. Frozen.
- **Tier 2** — `openPartner360`, `resolveSourceRef`, lifecycle threshold CONST table, **Renewal Command Center bucket logic** (180/120/90/60/30). **Reused for Contract Center.**
- **Tier 3 (or shipped here if Tier 3 unlanded)** — `lens-shared.js` with `renderLens(config)` primitive.
- **Knowledge files that constrain this tier** — re-read before writing code:
  - `plugins/edtech-partner-success/knowledge/k12-renewal-motion-90-60-30.md` — **source of truth for Contract Center alert buckets.** The 180/120/90/60/30 cadence + per-checkpoint meaning. The Planhat doctrine quoted in §3 of the knowledge file is the language the Contract Center hover-tooltips MUST cite.
  - `plugins/edtech-partner-success/knowledge/k12-superintendent-turnover-as-renewal-event.md` — **source of truth for Relationship Mapping risk flags.** 23% YoY top-500 superintendent turnover (EdWeek/AASA); "map the cabinet, not the chair" (Pedagogue); positions-not-people durability. Drives the "champion seat at risk" badge in §4.5.
  - `plugins/edtech-partner-success/knowledge/k12-psm-operating-cadence.md` §"Dead zones" — Success Plan "overdue" alerts suppressed during dead zones; PD-expiration urgency adjusted when expiration falls inside a dead zone.
  - `plugins/edtech-partner-success/skills/expansion-play-design/SKILL.md` — **3-gate eligibility model** (top-quartile health AND demonstrable adoption AND organizational readiness). Auto-flag criteria for the Expansion Opportunity Dashboard MUST match this gate exactly; the dashboard is a thin UI over the SKILL.
  - `plugins/edtech-partner-success/skills/success-plan-authoring/SKILL.md` — the "what makes a good success plan" rules that drive the at-risk / overdue classification logic.
  - `plugins/edtech-partner-success/knowledge/k12-pd-norms-and-constraints.md` — PD-credit constraints + state PD hour requirements drive the PD Tracker "underutilized" criteria.
  - `docs/research/2026-06-04-psm-dashboard-research/dashboard-ux.md` §4 (color discipline, alarm-fatigue mitigation — PD-expiration alerts MUST be calibrated to ≤5% false-positive rate, NOT default-red-everything), §6 (empty states), §8 (URL state).
- **Substrate (do NOT re-author):**
  - 3-gate expansion eligibility — owned by `expansion-play-design` SKILL.
  - Champion / cabinet anchor durability rules — owned by `k12-superintendent-turnover-as-renewal-event.md`.
  - 180/120/90/60/30 cadence — owned by `k12-renewal-motion-90-60-30.md`.

---

## 1. Pre-flight

| # | Action | Command | Confirm |
|---|---|---|---|
| 1 | Sync main | `git fetch origin main && git checkout origin/main` | tip is latest main |
| 2 | New branch | `git checkout -b feat/psm-dashboard-tier-4-motion-lenses` | switched |
| 3 | Verify Tier 2 surface present | `grep -q 'function openPartner360' plugins/edtech-partner-success/bi-report/dashboard.js` | match found |
| 4 | Verify `lens-shared.js` present (from Tier 3) OR plan to ship it here | `test -f plugins/edtech-partner-success/bi-report/lenses/lens-shared.js` | exit 0 OR add to §2 |
| 5 | Verify Tier 0 fixture | `python3 -m jsonschema -i plugins/edtech-partner-success/bi-report/data.json plugins/edtech-partner-success/bi-report/data.schema.json` | exit 0 |
| 6 | Verify Gate 53 passes | `python3 scripts/check-psm-cross-section-consistency.py` | exit 0 |
| 7 | Read spec §"Success Plan Dashboard", "Expansion Opportunity Dashboard", "Professional Development Tracker", "Contract Center", "Relationship Mapping" | open file | all 5 |
| 8 | Re-read `k12-renewal-motion-90-60-30.md` + `k12-superintendent-turnover-as-renewal-event.md` + `expansion-play-design/SKILL.md` | open files | all 3 |

---

## 2. Deliverables — exactly these files

| # | File | Action | Purpose |
|---|---|---|---|
| 1 | `plugins/edtech-partner-success/bi-report/dashboard.html` | EDIT | Mount 5 new lens routes in left-nav. |
| 2 | `plugins/edtech-partner-success/bi-report/lenses/success-plan.js` | CREATE | Success Plan Dashboard. |
| 3 | `plugins/edtech-partner-success/bi-report/lenses/expansion.js` | CREATE | Expansion Opportunity Dashboard. |
| 4 | `plugins/edtech-partner-success/bi-report/lenses/pd-tracker.js` | CREATE | Professional Development Tracker. |
| 5 | `plugins/edtech-partner-success/bi-report/lenses/contract-center.js` | CREATE | Contract Center. |
| 6 | `plugins/edtech-partner-success/bi-report/lenses/relationship-mapping.js` | CREATE | Relationship Mapping. |
| 7 | `plugins/edtech-partner-success/bi-report/motion-rules.js` | CREATE | Pure-function module containing the deterministic business rules: `isExpansionEligible(partner, usage, contacts) → {flag, reason}`, `pdAlertBucket(contract, as_of) → 'on-track'|'expiring-90'|'expiring-30'|'expired'`, `contractAlertBucket(contract, as_of) → '180'|'120'|'90'|'60'|'30'|null`, `championSeatRisk(contacts, partner) → 'green'|'yellow'|'red'`, `successPlanStatus(plan, as_of) → 'on-track'|'at-risk'|'overdue'|'complete'`. |
| 8 | `plugins/edtech-partner-success/bi-report/dashboard.css` | EDIT (append) | Motion-lens-specific layout (relationship-mapping grid, contract-center timeline). |
| 9 | `scripts/generate-bi-report.py` | EDIT | Mount 5 lens HTML scaffolds. |
| 10 | `scripts/check-psm-cross-section-consistency.py` | EDIT (extend) | Add motion-lens invariants per §4. |
| 11 | `plugins/edtech-partner-success/.claude-plugin/plugin.json` | EDIT (version bump) | Semver minor. |
| 12 | `.claude-plugin/marketplace.json` | EDIT (version mirror) | Lockstep. |
| 13 | `plugins/edtech-partner-success/CLAUDE.md` | EDIT | 5-line Tier 4 milestone. |

**Nothing else.** No new schema, no new fixture data, no new drill-down.

---

## 3. The 5 motion-lens specifications

### 3.1 Success Plan Dashboard (`lenses/success-plan.js`)

**Spec §"Success Plan Dashboard"** — tracks goals + owners + due dates + progress + status.

**KPI strip:**
- Total active success plans (count of `success_plans[]` where `status != complete`)
- Goals completed in last 30 days (sum of `goals[]` with `status = complete AND due_date >= as_of - 30d`)
- Goals at risk (sum of `goals[]` with `status = at_risk`)
- Goals overdue (sum of `goals[]` with `due_date < as_of AND status != complete`)

**Table columns per spec:**
- Partner name (click → drill-down with `tab=timeline` filtered to type `success_plan_milestone`)
- Plan name (= `success_plans[].name`)
- Goal description (= `goals[].description` — one row per goal, so partners with multiple goals span multiple rows; group by partner via visual indentation)
- Goal owner (= `goals[].owner`)
- Due date (with countdown chip)
- Progress % (rendered as a horizontal bar gauge per `dashboard-ux.md` §2 — Few's bullet-graph pattern, NOT a pie / donut / gauge dial)
- Current status (derived via `motion-rules.js` `successPlanStatus()`)

**Status derivation rule** (lives in `motion-rules.js`):

```
successPlanStatus(goal, as_of):
  if goal.status == 'complete':       return 'complete'
  days_to_due = (goal.due_date - as_of).days
  if days_to_due < 0:                 return 'overdue'    # past due
  if goal.progress_pct < expected_progress(goal, as_of):
                                      return 'at-risk'
  else:                               return 'on-track'

expected_progress(goal, as_of):
  # Linear expectation: 0% at plan start, 100% at due_date
  # In dead zones, freeze the clock per k12-psm-operating-cadence.md
  ...
```

**Dead-zone discipline:** suppress 'overdue' classification for goals where due_date falls inside an active dead zone for the partner's state. The goal renders as 'at-risk-deferred' with tooltip "due date in dead zone (e.g., winter break); re-evaluating Jan 6."

**Filter chips:** status (multi-select), owner (multi-select), due-date range.

**Highlight per spec:** goals completed (green check), goals at risk (yellow), upcoming milestones (count chip per partner).

### 3.2 Expansion Opportunity Dashboard (`lenses/expansion.js`)

**Spec §"Expansion Opportunity Dashboard"** — auto-flags accounts with high adoption + high usage + high sentiment + strong engagement.

**THE auto-flag criteria — single source of truth via `motion-rules.js isExpansionEligible()`:**

```
isExpansionEligible(partner, usage_daily, contacts) → {flag: bool, reason: str|null, gates_passed: [str]}:
  # The 3-gate model from expansion-play-design/SKILL.md:
  gate_health = partner.health_score >= 80 AND partner.band == 'green'
  gate_adoption = (
      partner.components.adoption >= 80 AND
      partner.components.usage >= 70 AND
      latest(usage_daily[partner]).active_users / partner.licensed_users >= 0.7
  )
  gate_readiness = (
      partner.sentiment_score >= 75 AND
      partner.components.champion >= 70 AND
      has_role(contacts, 'champion') AND
      has_role(contacts, 'exec_sponsor') AND
      partner.lifecycle_phase IN ('moi', 'renewal')
  )

  if gate_health AND gate_adoption AND gate_readiness:
    return { flag: True, reason: <derived from highest-signal gate>, gates_passed: [...] }
  else:
    return { flag: False, reason: None, gates_passed: [...] }  # partial gates still reportable
```

**Cite the SKILL** in a help-icon tooltip on the page header: "Auto-flag criteria: `skills/expansion-play-design/SKILL.md` § 3-gate eligibility model. Failing any gate disqualifies."

**The 'don't pitch to bottom-quartile' rule from the SKILL is enforced HERE in the dashboard, not just in the play.** Partners failing ANY gate are EXCLUDED from the eligibility list, not displayed-as-yellow.

**KPI strip:**
- Eligible partners (count where all 3 gates pass)
- Total potential opportunity ARR (sum of estimated expansion value across eligible partners)
- Partners at gate 2 of 3 (close-but-not-yet — surfaces "near misses")
- Partners flagged in last 30 days (newly-eligible)

**Table columns per spec:**
- Partner name (click → drill-down)
- Potential opportunity type (= derived from segment + product mix; e.g. "Additional school" if partner has < 5 schools in district vs district school count from external data — Tier 0.5 dependency, render `—` in Tier 0; "Additional product" if `contracts.products_purchased` count < portfolio average; "Multi-year" if current contract is single-year)
- Estimated value (computed as % of current ARR — 25-50% expansion uplift typical; render with caveat tooltip "directional estimate; RM confirms in pricing conversation per `knowledge/renewal-pricing-conversations-edtech.md`")
- Reason flagged (= `isExpansionEligible().reason`)
- Gates passed (3 dots — green/red per gate; per `dashboard-ux.md` §4 redundant encoding: shape + color, not color alone)
- Owner PSM
- Recommended play (= reference to `expansion-play-design` SKILL)

**Default sort:** estimated value descending.

### 3.3 Professional Development Tracker (`lenses/pd-tracker.js`)

**Spec §"Professional Development Tracker"** — pulls from `contracts[].pd_purchased_sessions / pd_completed_sessions / pd_expiration_date`.

**KPI strip:**
- Total PD sessions purchased (sum across current contracts)
- Total PD sessions completed
- Total PD remaining
- Sessions expiring in 90 days (count where `pd_expiration_date - as_of <= 90 AND remaining > 0`)
- Expired PD (sum of unconsumed sessions past `pd_expiration_date`)

**Table columns per spec:**
- Partner name
- PD purchased (= `pd_purchased_sessions`)
- PD completed (= `pd_completed_sessions`)
- PD remaining (= purchased - completed)
- Upcoming sessions (count of `calendar_events[]` with `type=pd_session AND status=scheduled` for this partner)
- Expiring sessions (= sessions expiring in next 90 days)
- PD expiration date

**Alert bucket derivation** (lives in `motion-rules.js`):

```
pdAlertBucket(contract, as_of):
  remaining = contract.pd_purchased_sessions - contract.pd_completed_sessions
  if remaining <= 0:                                       return 'on-track'  # all consumed
  days_until_expiry = (contract.pd_expiration_date - as_of).days
  if days_until_expiry < 0:                                return 'expired'
  if days_until_expiry <= 30 AND remaining > 0:            return 'expiring-30'
  if days_until_expiry <= 90 AND remaining > 0:            return 'expiring-90'
  return 'on-track'
```

**Dead-zone calibration** (per `dashboard-ux.md` §4 alarm-fatigue mitigation): if `pd_expiration_date` falls inside a dead zone, the alert renders as 'expiring-30-deferred' with tooltip "expiration in dead zone; PSM should schedule pre-dead-zone session by [date]." Prevents the dashboard from firing 25 useless alerts every December.

**Highlight per spec:**
- Unscheduled PD (= remaining > 0 AND no upcoming `calendar_event` of type `pd_session`)
- Expiring PD (= bucket is `expiring-30` or `expiring-90`)
- Underutilized PD (= `completed / purchased < 0.5 AND days_into_contract_period > 180` — partner is past mid-year of contract and < 50% consumed)

**Cite knowledge** in page header tooltip: "PD utilization norms: `knowledge/k12-pd-norms-and-constraints.md` — state PD hour requirements + district PD allocation patterns."

### 3.4 Contract Center (`lenses/contract-center.js`)

**Spec §"Contract Center"** — contract documents + details + alerts.

**KPI strip:**
- Active contracts count
- Total ARR under contract
- Contracts in renewal window (≤ 180 days to renewal)
- Contracts with alert bucket fired (any of 180/120/90/60/30 active)
- Multi-year contract count

**Layout: TWO views toggled via tab:**

**View A — Contract list** (default):
Table columns per spec §"Contract Details":
- Partner name (click → drill-down)
- Contract kind (= `kind` enum: current / previous / amendment / renewal_quote / order_form)
- Contract start
- Contract end
- Renewal date
- ARR
- Multi-year (bool badge)
- Schools included
- Licensed users
- Products purchased (rendered as chips)
- PD purchased / completed
- Doc link (= `resolveSourceRef(doc_ref, tenantConfig, ...)` → renders as "Open in CPQ / Ironclad / DocuSign" per the doc_ref scheme; disabled in synthetic Tier 0 per Tier 2 rules)

**View B — Alert buckets** (the spec's §"Contract Alerts" 180/120/90/60/30 + PD expiration):

Six columns / card groups: 180 / 120 / 90 / 60 / 30 / PD-expiration. Same bucket-assignment rule as Tier 2's Renewal Command Center — **reuse the Tier 2 function**, do not re-implement.

**Per-bucket meaning labels** (cite `k12-renewal-motion-90-60-30.md` §3 in tooltip — SAME tooltips as Tier 2's Renewal Command Center because both surfaces share the doctrine):

- **180 Days** — "Internal review; refresh champion map (assume superintendent turnover until verified — 23% YoY top-500 districts); YTD usage pull; expansion go/no-go"
- **120 Days** — "Year-end impact deck drafting; SETDA-aligned evidence pack"
- **90 Days** — "Decisive EBR / value-realization meeting (Planhat: 'secure verbal yes by proving undeniable value')"
- **60 Days** — "Proposal delivered; procurement starts; RM owns from here (Planhat: 'CS owns Value Realization, Adoption, Health; AM owns Commercial Contract, Procurement, Negotiation')"
- **30 Days** — "Commercial execution only; PSM in support mode"
- **PD-expiration** — "PD sessions expire by [date]; partner should schedule remaining before expiry"

**Cross-section invariant:** the 30/60/90/120/180 bucket assignment in Contract Center MUST match the assignment in Tier 2's Renewal Command Center for the same `account_uid`. Same function, same result. Asserted in §4.

**Filter chips:** kind, status, alert bucket, multi-year, segment.

### 3.5 Relationship Mapping (`lenses/relationship-mapping.js`)

**Spec §"Relationship Mapping"** — stakeholder grid: name / title / role / influence_level / sentiment / last_interaction_date.

**KPI strip:**
- Total tracked stakeholders
- Champions confirmed (count of role=champion across all partners)
- Exec sponsors confirmed (count of role=exec_sponsor)
- Partners missing a champion (= partners where `contacts[]` has no role=champion entry — should be 0 per Tier 0 integrity check #12; if non-zero, that's a data-quality flag)
- Partners with a champion seat at risk (per `championSeatRisk()` rule below — see `k12-superintendent-turnover-as-renewal-event.md`)

**Layout: matrix view + per-partner detail.**

**Matrix view:** rows = partners (filtered to top-15 by default, expandable to full portfolio), columns = the 5 role types per spec §"Contacts" (champion / exec_sponsor / superintendent / tech_lead / family_engagement). Each cell shows: contact name + influence dot + sentiment dot, or `—` if role missing.

**Per-partner detail (expanded row):** the full Tier 2 Partner 360 contacts grid, inline (NOT a drawer — for this lens, the contacts ARE the content, so an inline expansion is preferred over a drill-down; partner name click still opens the drawer for full 360 context).

**Champion seat risk rule (`motion-rules.js championSeatRisk()`):**

Per `k12-superintendent-turnover-as-renewal-event.md` ("23% YoY top-500 superintendent turnover; map the cabinet, not the chair; positions-not-people durability"):

```
championSeatRisk(contacts, partner):
  # Per the knowledge file: assume turnover until verified.
  champion = contacts.find(c => c.role == 'champion')
  exec_sponsor = contacts.find(c => c.role == 'exec_sponsor')

  # No champion → red (worst case).
  if !champion: return 'red'

  # Last interaction > 90 days → champion ghosted; yellow.
  # > 180 days → likely turnover; red.
  days_since_champion_interaction = (as_of - champion.last_interaction_at).days
  if days_since_champion_interaction > 180: return 'red'
  if days_since_champion_interaction > 90:  return 'yellow'

  # Champion confirmed but no exec sponsor → yellow (single-thread risk per SKILL).
  if !exec_sponsor: return 'yellow'

  # All checks pass.
  return 'green'
```

Cite the knowledge file in tooltip on every red/yellow seat-risk badge: "Source: `knowledge/k12-superintendent-turnover-as-renewal-event.md` — assume turnover until verified; map the cabinet, not the chair."

**Highlight per spec:** stakeholders with no interaction in 90+ days (yellow row tint), seat-at-risk partners (red left-border per `dashboard-ux.md` §4 pattern #4).

**Filter chips:** role, influence_level, sentiment, "seat at risk" toggle.

---

## 4. Cross-section invariants (Gate 53 extension)

`scripts/check-psm-cross-section-consistency.py` gets new motion-lens invariants. **Same number on N pages renders identical bytes.**

| # | Invariant | How enforced |
|---|---|---|
| C13 | The Contract Center 30/60/90/120/180 bucket assignment for a given partner matches the Tier 2 Renewal Command Center bucket assignment. | Script asserts: same `bucketForRenewal(partner.renewal_date, as_of)` function called from both surfaces. |
| C14 | The Expansion Opportunity Dashboard's eligibility list contains ONLY partners passing all 3 gates per `isExpansionEligible()`. No bottom-quartile partners appear. | Script enumerates partners with `health_score < 70 OR adoption < 70`; asserts none appear in the expansion lens output. |
| C15 | The PD Tracker's "Expiring in 90 days" KPI = sum of contracts where `pdAlertBucket() == 'expiring-90'`. Same function, same result. | Script computes from `motion-rules.js` rules; compares to displayed KPI. |
| C16 | The Success Plan Dashboard's overdue count for a partner matches the Partner 360 drill-down's open-risks list — overdue success plans are open risks. | Script asserts the open-risks computation in `openPartner360` (Tier 2) and the overdue computation in success-plan lens (Tier 4) are consistent for the same `account_uid`. |
| C17 | The Relationship Mapping "Partners missing a champion" KPI = 0 in the Tier 0 fixture (because integrity check #12 enforces exactly-one-champion-per-partner). Non-zero is a data-quality regression. | Script asserts == 0 in synthetic mode; in production mode, surfaces it as a warning. |
| C18 | The Contract Center Alert Bucket view and the Renewal Command Center (Tier 2) display the SAME per-partner bucket label. | Same labels, same colors, same partner ordering within bucket (by ARR descending). |

---

## 5. Verification

| # | Command | Expected |
|---|---|---|
| 1 | `npx prettier --write . && npx prettier --check .` | exit 0 |
| 2 | `python3 -m jsonschema -i plugins/edtech-partner-success/bi-report/data.json plugins/edtech-partner-success/bi-report/data.schema.json` | exit 0 |
| 3 | `python3 scripts/check-psm-data-integrity.py` | exit 0 |
| 4 | `python3 scripts/check-psm-cross-section-consistency.py` | exit 0 (C1–C18 all pass) |
| 5 | `grep -rE 'function (open\|render)Partner360' plugins/edtech-partner-success/bi-report/lenses/` | empty (no lens re-authors drill-down) |
| 6 | `grep -rE 'function bucketForRenewal' plugins/edtech-partner-success/bi-report/` | exactly `1` match (Tier 2 location; Tier 4 imports it) |
| 7 | `grep -rE 'function isExpansionEligible' plugins/edtech-partner-success/bi-report/` | exactly `1` match (`motion-rules.js`) |
| 8 | `bash scripts/audit-gates.sh` | clean |
| 9 | Open `dashboard.html?lens=expansion` → only partners passing all 3 gates appear; row-click → drill-down opens. Verify no red-band partner ever appears. | Confirmed. |
| 10 | Open `dashboard.html?lens=contract-center&view=alerts` → 6-bucket view (180/120/90/60/30/PD-expiration) — same partner appears in the same renewal bucket as Tier 2 Renewal Command Center. | Confirmed via Gate 53 C13/C18. |
| 11 | Open `dashboard.html?lens=relationship-mapping` → matrix view; champion-seat-risk badges colored per `championSeatRisk()`; tooltip cites `k12-superintendent-turnover-as-renewal-event.md`. | Confirmed. |
| 12 | Open `dashboard.html?lens=pd-tracker` with a fixture partner whose `pd_expiration_date` lands in winter break dead zone → alert renders 'expiring-30-deferred' not 'expiring-30'. | Confirmed via dead-zone discipline. |
| 13 | Open `dashboard.html?lens=success-plan` → goal-status derivation matches `successPlanStatus()` rule for every visible goal. | Confirmed. |
| 14 | Visual diff: Tier 0/1/2/3 surfaces unchanged. | Confirmed. |
| 15 | Layout snippet (Tier 0 brief §6) | "Layout OK" |

---

## 6. PR shape

```sh
git add plugins/edtech-partner-success/bi-report/dashboard.html \
        plugins/edtech-partner-success/bi-report/dashboard.css \
        plugins/edtech-partner-success/bi-report/lenses/success-plan.js \
        plugins/edtech-partner-success/bi-report/lenses/expansion.js \
        plugins/edtech-partner-success/bi-report/lenses/pd-tracker.js \
        plugins/edtech-partner-success/bi-report/lenses/contract-center.js \
        plugins/edtech-partner-success/bi-report/lenses/relationship-mapping.js \
        plugins/edtech-partner-success/bi-report/motion-rules.js \
        scripts/generate-bi-report.py \
        scripts/check-psm-cross-section-consistency.py \
        plugins/edtech-partner-success/CLAUDE.md \
        plugins/edtech-partner-success/.claude-plugin/plugin.json \
        .claude-plugin/marketplace.json

git commit -m "feat(edtech-partner-success): PSM dashboard Tier 4 — 5 motion lenses + deterministic business rules"
git push -u origin feat/psm-dashboard-tier-4-motion-lenses
```

Open as draft PR.

---

## 7. Wall-handling

1. Re-read priors in §1 — especially the 3 knowledge files in §0 (`k12-renewal-motion-90-60-30.md`, `k12-superintendent-turnover-as-renewal-event.md`, `expansion-play-design/SKILL.md`). Any threshold not documented there is OUT OF SCOPE — propose extending the knowledge file in a *separate* PR.
2. If a column or metric in the spec requires Tier 0.5 connector data (e.g. "Additional school opportunity" needs district-school count from external SIS), render `—` + footer note "Data from Tier 0.5 connector — not in synthetic fixture."
3. If a business rule is silent in this brief AND silent in the cited knowledge files, `AskUserQuestion`. Do NOT invent thresholds.

---

## 8. What Codex MUST NOT do

- Add new fields to `data.schema.json` or `data.json`. Tier 0's schema is frozen.
- Author a per-lens drill-down. Every lens reuses `openPartner360(account_uid)`. Invariant C4.
- Re-author the Renewal Command Center bucket assignment. Reuse Tier 2's function via import. Invariant C13/C18.
- Re-author the expansion eligibility gates. They live in `expansion-play-design/SKILL.md`. Codify them once in `motion-rules.js isExpansionEligible()` and reference that single source.
- Show bottom-quartile partners in the Expansion lens, even as "near misses." The SKILL is explicit: don't pitch to bottom-quartile (credibility burn + misallocation). The dashboard enforces this by exclusion.
- Re-author champion-seat-risk thresholds. They come from `k12-superintendent-turnover-as-renewal-event.md`. Cite in tooltip.
- Re-author the 180/120/90/60/30 bucket meanings. They come from `k12-renewal-motion-90-60-30.md` §3.
- Skip the dead-zone suppression for Success Plan overdue / PD expiration alerts. Alarm-fatigue mitigation per `dashboard-ux.md` §4 — calibrate to ≤ 5% false-positive rate.
- Use a pie chart, donut, or speedometer gauge for any metric. Per Stephen Few + `dashboard-ux.md` §2 — "all listed in *Common Pitfalls* as anti-patterns." Use bullet graphs, sparklines, bars.
- Hardcode a `30%` / `50%` expansion uplift estimate without a tooltip caveat. Pricing conversations are RM-owned per the Planhat doctrine; the dashboard's estimate is directional.
- Render an LLM-generated reason in the Expansion lens "reason flagged" column. Tier 5 (AI features) is out of scope per spec; Tier 4 is deterministic only.
- Skip the `motion-rules.js` extraction. Business rules go in one place; lens files consume the rules. Architectural rule prevents per-lens drift.
- Render an alert at the highest severity level (red + icon + motion) for any check whose false-positive rate is > 5%. Per `dashboard-ux.md` §4 #5 PPV-not-recall design rule.
- Author a per-lens dead-zone suppression rule. Single source of truth = `dashboard-dead-zones.md` (Tier 0).
- Add per-entity `console.log` debug paths.
- Render real district names or real stakeholder names. All names in Tier 0 fixture are synthetic with `Demo:` prefix per Tier 0 integrity check #16.
- Open the PR as ready-for-review without Matt's say-so.
- Force-push, amend, or rewrite history.
- Author a 6th motion lens. Five lenses per spec, no more.
- Change Tier 1/2/3 surfaces. Additive only.
- Add a CLAUDE.md milestone entry longer than 5 lines.
- Skip Gate 53 invariants C13–C18. They prove the dashboard's deterministic business rules are consistent across all surfaces — the architectural promise of the build kit.
- Use a chart library (Chart.js, D3, Plotly, Highcharts, ApexCharts). Inline SVG only, matching `bi-report/report.html`.
- Mix the matrix-view inline expansion (§3.5) with the side-panel drill-down. The inline expansion shows contacts; the side panel shows full Partner 360. Both are reachable; they don't conflict.

End of Tier 4 brief.
