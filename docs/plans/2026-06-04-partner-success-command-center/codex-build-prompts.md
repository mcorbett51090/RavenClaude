# Codex Build Prompts — Partner Success Command Center

**Audience:** the PSM (Matt's wife) building the dashboard in a **fresh GitHub repo** with **Codex desktop** on a **limited credit budget**.
**Goal:** ship a working daily-operating-system dashboard in the fewest Codex turns possible.

> **Companion documents** (open in a new tab):
> - <a href="./build-plan.html" target="_blank" rel="noopener">📋 Interactive Build Plan</a> — the whole plan + every prompt below, point-and-click with copy buttons.
> - <a href="./process-flow.html" target="_blank" rel="noopener">🔀 Dashboard Process Flow</a> — Mermaid diagrams of how the dashboard works end-to-end.
>
> These two `.html` files sit next to this markdown. Double-click either to open it in your browser — no server needed.

---

## How to spend the fewest credits

Codex charges roughly per turn and per token it reads/writes. Five rules cut the bill hard:

1. **One prompt = one complete deliverable.** Each prompt below is self-contained: it carries the full file list, the schema, and the acceptance criteria. Paste it, let Codex produce everything in a single response. Don't trickle requirements in.
2. **Don't let it explore.** Every prompt ends with a "Constraints" block that says *don't ask clarifying questions, don't run the app, don't install dependencies, produce the files directly.* Exploration and tool-running is where credits evaporate.
3. **Go in order, stop when it's enough.** Prompts 1 → 2 give you a dashboard you can actually use every morning. Prompts 3–6 are bonus depth. You do **not** need all six.
4. **Paste the schema, don't make it re-derive.** Prompt 1 prints the data schema. Later prompts say "the schema from `data.json` already in the repo" so Codex reads one file instead of reasoning it out again.
5. **Accept the synthetic data first.** The dashboard is fully usable on fake data. Wiring real Salesforce/Planhat/Snowflake (the "Tier 0.5" connector work) is a separate, much larger effort — do it only once the layout is proven and you've decided it's worth it.

**Recommended minimum to be useful every morning: Prompt 1 + Prompt 2.** That's two turns.

---

## The build, at a glance

| Prompt | Builds | Essential? | Roughly |
|---|---|---|---|
| **0** | Repo conventions + folder skeleton | optional (saves drift later) | tiny |
| **1** | `data.json` schema + `synthesize.py` + sample data | ✅ yes — foundation | medium |
| **2** | `dashboard.html` — **Daily Operating System** (4 widgets) | ✅ yes — the thing you use | large |
| **3** | Partner 360 drill-down + Timeline + Lifecycle + Renewal | bonus depth | large |
| **4** | Segment lenses (Top 15 / Health / Sentiment / Family / School / Support) | bonus depth | large |
| **5** | Motion lenses (Success Plan / Expansion / PD / Contract / Relationships) | bonus depth | large |
| **6** | Provenance + color-discipline polish pass | optional polish | small |

Everything is **plain static files** — HTML + a `data.json` + a Python generator. No framework, no build step, no server. Open `dashboard.html` in a browser and it works.

---

## Prompt 0 — Project setup (optional, run once)

*Send first if you want Codex to keep the repo tidy across the later prompts. Skip it to save a turn — Prompt 1 also creates the folders it needs.*

```text
You are setting up a fresh repo for a single-tenant "Partner Success Command Center"
dashboard for a K-12 edtech Partner Success Manager. It is a STATIC site: plain HTML +
a data.json + a Python generator. No framework, no bundler, no server.

Create this skeleton and nothing else:

  /data/data.json            # (empty placeholder {} for now)
  /data/synthesize.py        # (empty placeholder, just a top comment)
  /dashboard.html            # (empty placeholder <!doctype html>)
  /README.md                 # how to regenerate data and open the dashboard
  /.gitignore                # python + os cruft

README.md must say, in 6 lines or fewer:
  - run `python3 data/synthesize.py` to (re)generate data/data.json
  - open dashboard.html directly in a browser (no server needed)
  - dashboard.html reads data/data.json via fetch
  - all partner data is SYNTHETIC — never commit real student or partner data

Constraints: Do not ask clarifying questions. Do not run anything. Do not install
anything. Produce all five files in one response, then stop.
```

---

## Prompt 1 — Data foundation (ESSENTIAL)

*This is the contract every later prompt reads against. It prints the schema once so nothing downstream has to re-derive it.*

```text
Build the data foundation for a single-tenant K-12 edtech Partner Success dashboard.
Produce TWO files in one response: data/synthesize.py and a freshly generated data/data.json.

data/synthesize.py generates a realistic, fully SYNTHETIC, FERPA-safe sample of 25
partner districts. Requirements:
  - Reproducible: seed the RNG with 42 so output is byte-identical across runs.
  - No real names. Use generated district names like "Maple Grove USD", "Riverbend School District".
  - Only aggregate counts — NEVER any student-level or personal data.
  - Spread the sample so it exercises the dashboard:
      * >=3 partners in each health band: green (>=70), yellow (50-69), red (<50)
      * >=2 partners in each renewal bucket: 180 / 120 / 90 / 60 / 30 days to renewal
      * a mix of segments and a handful flagged top15_status = true
  - Write the result to data/data.json (pretty-printed, 2-space indent).

The JSON shape (this is the contract — emit EXACTLY these blocks and field names):

{
  "schema_version": "1.0",
  "generated_at": "<ISO8601>",
  "bands": { "green_min": 70, "yellow_min": 50 },
  "priority_weights": {
    "renewal_timing": 25, "health_decline": 20, "sentiment_decline": 15,
    "days_since_touchpoint": 12, "open_escalations": 10, "ticket_volume": 5,
    "arr": 5, "top15_bonus": 5, "usage_decline": 3
  },
  "partners": [{
    "account_uid": "acct_0001", "name": "...", "segment": "Enterprise|Mid|SMB",
    "state": "TX", "arr": 120000, "contract_start": "2024-08-01",
    "contract_end": "2026-07-31", "renewal_date": "2026-07-31",
    "funding_source": "Title I|ESSER|General Fund|Grant", "owner_psm": "...",
    "top15_status": true, "lifecycle_stage": "Deployment|BOI|MOI|Renewal",
    "lifecycle_substage": "...", "stage_entered_at": "ISO", "last_touchpoint_at": "ISO",
    "next_required_touchpoint_at": "ISO",
    "health_components": { "adoption": 0-100, "touchpoint": 0-100, "outcome": 0-100, "sentiment": 0-100 },
    "health_score": 0-100, "sentiment_score": 0-100, "engagement_score": 0-100,
    "priority_score": 0-100,
    "priority_breakdown": { "<weight_key>": <0-100 contribution before weighting>, ... },
    "open_escalations": 0, "open_tickets": 0, "ticket_aging_days": 0,
    "recommended_action": "short imperative string", "action_reason": "which signal drove it"
  }],
  "contacts": [{ "contact_uid": "...", "account_uid": "...", "name": "...",
    "title": "...", "role": "champion|exec_sponsor|superintendent|tech_lead|family_engagement|stakeholder",
    "influence_level": "high|med|low", "sentiment": "green|yellow|red", "last_interaction_at": "ISO" }],
  "timeline_events": [{ "event_uid": "...", "account_uid": "...",
    "type": "closed_won|kickoff|go_live|training|qbr|checkin|success_plan_review|escalation|sentiment_change|renewal_conversation|expansion_conversation",
    "ts": "ISO", "source": "salesforce|planhat|support|snowflake|calendar|manual", "summary": "..." }],
  "usage_daily": [{ "account_uid": "...", "date": "ISO", "active_users": 0,
    "active_teachers": 0, "active_admins": 0, "family_invited": 0, "family_activated": 0,
    "family_engagement_rate": 0.0 }],
  "success_plans": [{ "plan_uid": "...", "account_uid": "...", "goal": "...",
    "owner": "...", "due_date": "ISO", "progress_pct": 0, "status": "on_track|at_risk|complete|overdue" }],
  "contracts": [{ "contract_uid": "...", "account_uid": "...", "start": "ISO", "end": "ISO",
    "arr": 0, "multi_year": true, "schools_included": 0, "licensed_users": 0,
    "products_purchased": ["..."], "pd_purchased_sessions": 0, "pd_completed_sessions": 0 }],
  "tickets": [{ "ticket_uid": "...", "account_uid": "...", "opened_at": "ISO",
    "status": "open|pending|closed", "severity": "low|med|high", "theme": "...",
    "age_days": 0, "is_escalation": false }],
  "calendar_events": [{ "event_uid": "...", "account_uid": "...",
    "type": "qbr|checkin|renewal_meeting|strategic|pd_session|success_plan_review|health_check",
    "scheduled_at": "ISO", "duration_min": 30, "status": "scheduled|completed|missed" }]
}

priority_score math: priority_score = sum(priority_breakdown[k] * priority_weights[k]) / 100,
rounded to an integer, clamped 0-100. priority_breakdown[k] is the raw 0-100 strength of
each signal (e.g. a 30-day renewal scores ~95 on renewal_timing). Keep it deterministic.

Generate 2-6 contacts, 4-10 timeline_events, ~30 days of usage_daily, 1-3 success_plans,
1 contract, 0-4 tickets, and 2-5 calendar_events per partner.

Constraints: Do not ask clarifying questions. Do not install packages (standard library only:
json, random, datetime). Run synthesize.py mentally and emit a real, valid data/data.json —
do not leave it as a stub. Produce both files in one response, then stop.
```

**You get:** `data/synthesize.py` and a populated `data/data.json`. Open the JSON to sanity-check it looks like 25 districts. This file is now the single source of truth the dashboard renders.

---

## Prompt 2 — The Daily Operating System dashboard (ESSENTIAL)

*This is the dashboard you open every morning. It answers "who do I call today and why" in under 15 seconds.*

```text
Build dashboard.html — a self-contained, single-page "Partner Success Command Center"
that fetches ./data/data.json and renders the daily operating system for a K-12 edtech PSM.
Plain HTML + CSS + vanilla JS in ONE file. No framework, no CDN except the system font stack.
It must open directly in a browser (use fetch on ./data/data.json; degrade with a friendly
message if the file can't load).

Visual style: calm, professional, Intercom-like. Cool near-white canvas (#f5f6f8), white
cards with a 1px hairline border and very soft shadow, teal accent (#1f7f78), Inter/system
sans. Health colors: green >=70 (#1f7a3f), yellow 50-69 (#9a7010), red <50 (#b03f3f) — read
the thresholds from data.bands, never hardcode them.

Render these FOUR widgets, top to bottom, each in its own card:

1. PORTFOLIO SUMMARY — a row of stat tiles, each a count derived from partners[]:
   Total · Active · Top 15 · In Renewal Window (renewal_date within 120 days) ·
   At Risk (health_score < 50) · Open Escalations (sum) · Need Outreach
   (last_touchpoint_at older than 90 days).

2. PORTFOLIO HEALTH SNAPSHOT — average health_score, average sentiment_score, average
   engagement_score (big numbers, colored by band), plus "X partners with declining usage"
   and "X partners with no touchpoint in 90+ days".

3. DAILY ACTION CENTER — the heart of it. A table of ALL partners sorted by priority_score
   descending. Columns: Partner · Priority (the score as a colored chip) · Why (action_reason
   plus the TOP contributing signal from priority_breakdown shown as "renewal_timing 38%") ·
   Recommended Action (recommended_action) · Due (next_required_touchpoint_at as a date).
   The top 5 rows are visually emphasized. Every "Why" cell must name the signal that drove
   the score — never show a score without its reason.

4. CALENDAR / UPCOMING TOUCHPOINTS — a countdown list derived from each partner's
   renewal_date and next_required_touchpoint_at: e.g. "Maple Grove USD — 30 days until
   renewal outreach", "Riverbend SD — 14 days until next check-in". Sort soonest-first,
   show the next ~15. Add a small note that these countdowns are derived from contract dates
   and cadence rules, not synced calendar invites.

Also include a compact top bar with the title "Partner Success Command Center", the
data.generated_at timestamp, and a one-line legend for the green/yellow/red bands.

Make it responsive (stat tiles wrap on narrow screens) and keep all numbers honest —
if a value is missing in the data, show "—", not a guess.

Constraints: Do not ask clarifying questions. Do not run a server or install anything.
Read field names from the data/data.json already in the repo. Produce the single
dashboard.html file in one response, then stop.
```

**You get:** a working `dashboard.html`. Double-click it (or open in your browser). If `data/data.json` exists from Prompt 1, the four widgets light up. **This is the minimum viable deliverable — you can stop here and use it every morning.**

---

## Prompt 3 — Partner 360 drill-down (bonus depth)

*Send when the at-a-glance view is solid and you want to click into a single partner.*

```text
Extend dashboard.html (the existing single-file static dashboard that reads ./data/data.json).
Add a Partner 360 drill-down. Do NOT rebuild the four existing widgets — keep them and add to them.

When the user clicks any partner name anywhere (Daily Action Center row, calendar item, etc.),
open a slide-over / modal panel showing that one partner, built from the existing data blocks
joined on account_uid:

  - Header: name, segment, state, ARR, lifecycle_stage + lifecycle_substage badge, health/
    sentiment/engagement scores as colored chips.
  - CONTACTS: from contacts[] for this account — name, title, role, influence, sentiment,
    last interaction. Highlight the champion and exec sponsor.
  - ACCOUNT TIMELINE: from timeline_events[] for this account, newest first, with a small
    source label (salesforce/planhat/support/...) and the event type as a colored dot.
    Let the user filter by source and by type.
  - LIFECYCLE: current stage badge, date entered stage, days in stage, and next required
    activity (from next_required_touchpoint_at). Color the badge yellow if days-in-stage looks
    stale for the stage (e.g. > 90 days in MOI).
  - RENEWAL: renewal_date, days remaining, ARR, health, sentiment, and a simple renewal-risk
    read (red if health < 50 or sentiment red within 120 days of renewal).
  - OPEN ESCALATIONS / TICKETS: from tickets[] (open ones), with age and theme.

One drill-down implementation, reused for every partner. Esc closes it; clicking the backdrop
closes it.

Constraints: Do not ask clarifying questions. Do not run or install anything. Reuse the
existing styles and the data already loaded in the page. Produce the updated dashboard.html
in one response, then stop.
```

---

## Prompt 4 — Segment lenses (bonus depth)

```text
Extend dashboard.html with a left-hand nav that switches between "lens" views. Keep the
existing Daily Operating System as the default "Home" view and the Partner 360 drill-down.
Add these segment lenses, each a filtered/columned view over the same data/data.json:

  - TOP 15: partners where top15_status = true — health, sentiment, renewal countdown,
    last touchpoint, next touchpoint, open risks, success-plan status. Color-coded.
  - HEALTH: every partner's health_components (adoption/touchpoint/outcome/sentiment),
    health_score, plus declining-usage and escalation flags. Sortable by score.
  - SENTIMENT: sentiment_score + the latest timeline_events.type = "sentiment_change"
    summary as the reason/notes, sorted worst-first.
  - FAMILY ENGAGEMENT: from usage_daily aggregated per partner — family_invited,
    family_activated, activation %, family_engagement_rate. Flag low activation.
  - SCHOOL LEVEL: for partners with multiple schools, per-school active_users and a
    usage level (if the data has school detail; otherwise show a graceful "single-school"
    note).
  - SUPPORT & ESCALATIONS: open tickets, escalations, aging, themes. Highlight partners
    with multiple open tickets or any is_escalation = true.

Cross-view consistency matters: a partner's health_score must read identically on the Home
view, the Health lens, and the Top 15 lens. Don't recompute — read the same field.

Constraints: Do not ask clarifying questions. Do not run or install anything. Reuse existing
styles and loaded data. Produce the updated dashboard.html in one response, then stop.
```

---

## Prompt 5 — Motion lenses (bonus depth)

```text
Extend dashboard.html with these business-motion lenses in the same left-hand nav. All
deterministic (no AI) — read straight from data/data.json:

  - SUCCESS PLANS: from success_plans[] — goal, owner, due_date, progress_pct, status.
    Group by status; surface at_risk and overdue first.
  - EXPANSION OPPORTUNITIES: auto-flag partners with high adoption AND high usage AND high
    sentiment AND strong engagement. Show why flagged and a rough opportunity note. Pure rule,
    no model.
  - PROFESSIONAL DEVELOPMENT: from contracts[] — pd_purchased_sessions vs pd_completed_sessions,
    remaining, and a flag for underutilized PD (e.g. < 50% used with renewal approaching).
  - CONTRACT CENTER: from contracts[] — start/end, ARR, multi_year, schools_included,
    licensed_users, products_purchased, plus a renewal alert bucket (180/120/90/60/30 days).
  - RELATIONSHIP MAPPING: from contacts[] — a stakeholder grid per partner (name/title/role/
    influence/sentiment/last interaction), so gaps (e.g. no exec sponsor) are obvious.

Constraints: Do not ask clarifying questions. Do not run or install anything. Reuse existing
styles and loaded data. Produce the updated dashboard.html in one response, then stop.
```

---

## Prompt 6 — Provenance & polish pass (optional)

```text
Polish dashboard.html without changing what it shows. Three things only:

  1. PROVENANCE TOOLTIPS: every number gets a hover title naming its source field and the
     data.generated_at refresh time (e.g. "from partners[].health_score · data refreshed
     2026-06-04"). The dashboard should never show a number with no stated origin.
  2. COLOR DISCIPLINE: confirm every green/yellow/red decision reads thresholds from
     data.bands, and that red is reserved for genuine "act now" states (never decorative).
  3. EMPTY/ERROR STATES: a clean message if data/data.json is missing or a block is empty,
     and "—" for any missing field instead of blanks or zeros that imply real data.

Constraints: Do not ask clarifying questions. Do not run or install anything. Do not add new
widgets or change the layout. Produce the updated dashboard.html in one response, then stop.
```

---

## After the synthetic build: wiring real data (much later)

The dashboard renders on `data/data.json`. To go from synthetic to **real** partner data you
replace that one file — nothing in `dashboard.html` changes. That replacement is the big
"connector" effort (Salesforce + Planhat + Snowflake + support tool + contracts + calendar),
and it should wait until:

- the layout is proven and you actually use it daily, **and**
- you've answered six setup questions (see the plan): which **support tool**, **contract
  system**, and **calendar** you use; where the **Top 15 list** lives today; whether scoping is
  **just you or your team**; and whether **sentiment** is Planhat-native or you set it.

Until then, every morning is: `python3 data/synthesize.py` → open `dashboard.html`. When real
data lands, it's: export real data → `data/data.json` → open `dashboard.html`. Same file, same
dashboard.

---

*Full strategic context, tier breakdown, risks, and the data contract live in
[`plan.md`](./plan.md) and the `build-plan-*.md` files in this folder. The two HTML companions
linked at the top of this document present the same material visually.*
