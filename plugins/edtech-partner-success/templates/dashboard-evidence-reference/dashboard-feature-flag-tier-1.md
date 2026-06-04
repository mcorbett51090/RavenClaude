# PSM Command Center — Feature-flag patterns (Tier 1)

> Pattern for shipping each Tier 1 widget behind a feature flag so partial deploys work. Same flag names cross Tier 1 (Evidence) and Tier 2 (Streamlit-in-Snowflake) so the rollout state is one source of truth.
>
> Source priors:
> - The four-wave staged rollout matches the spec.md §rollout cadence and is consistent with [`rendering-layer.md`](../../../../docs/research/2026-06-04-psm-dashboard-research/rendering-layer.md) §5 migration phasing (v0 → v0.5 → v1 → v2).
> - Default-OFF discipline follows the operational-console-design §2 rule ("default to neutral, escalate by exception") applied to flags: a flag flipped on is a deliberate act, never an accident.
> - The guard syntax in Evidence Markdown (`{#if features.x}`) is Evidence's first-class conditional rendering primitive; the Streamlit guard is plain Python.

---

## 1. The flag store — single source of truth

Tier 1's flag store is **`evidence.config.yaml`** at the dashboard project root. Tier 2 (SiS) reads from `feature_flags.toml` in the SiS stage. The flag NAMES are identical across both; only the file format differs.

### Tier 1 — `evidence.config.yaml` flag block

```yaml
# evidence.config.yaml — at plugins/edtech-partner-success/dashboard-evidence/
# (Drop this block into the project root Evidence config.)
title: PSM Command Center
appearance:
  default: system
  switcher: true

# ─────────────────────────────────────────────────────────────────────────────
# Feature flags — default OFF discipline.
# A flag flipped to `true` is the deliberate go-live for that widget.
# A new widget MUST land here as `false` first, get rendered+verified,
# then flip to `true` in a separate PR.
# ─────────────────────────────────────────────────────────────────────────────
features:
  # ── Wave 1: Daily Operating System (Tier 1 ships these four) ─────────────
  portfolio_summary: false # W1 — Portfolio Summary card (7 KPI tiles)
  portfolio_health_snapshot: false # W2 — averages + counts card (5 KPI tiles)
  daily_action_center: false # W3 — top-15 prioritized table with inline drivers
  upcoming_touchpoints: false # W4 — calendar countdown list with R5 tooltip

  # ── Wave 2: Drill-downs (Tier 2 ships these; reserved here for the contract) ──
  partner_360: false # /partner/[partner_id] drill page
  account_timeline: false # merged event history per partner
  lifecycle_tracking: false # phase × substage view
  renewal_command_center: false # 180/120/90/60/30 day buckets

  # ── Wave 3: Segment lenses (Tier 3) ───────────────────────────────────────
  top15_dashboard: false
  health_lens: false
  sentiment_lens: false
  family_engagement_lens: false
  school_level_lens: false
  support_lens: false

  # ── Wave 4: Business-motion lenses (Tier 4) ───────────────────────────────
  success_plan_dashboard: false
  expansion_opportunity: false
  pd_tracker: false
  contract_center: false
  relationship_mapping: false
```

### Tier 2 — `feature_flags.toml` for Streamlit-in-Snowflake

The SiS app reads the same flag names via TOML (lighter touch than YAML in Python without a dependency):

```toml
# feature_flags.toml — uploaded to the SiS stage alongside app.py
# (PUT file://feature_flags.toml @PSM_CONSOLE.LIVE_OPS.APP_STAGE OVERWRITE=TRUE)
#
# Same names as evidence.config.yaml features.* — the rollout state is one
# source of truth even though the file format differs per host.

[features]
# Wave 1
portfolio_summary = false
portfolio_health_snapshot = false
daily_action_center = false
upcoming_touchpoints = false

# Wave 2 (reserved)
partner_360 = false
account_timeline = false
lifecycle_tracking = false
renewal_command_center = false

# Wave 3 (reserved)
top15_dashboard = false
health_lens = false
sentiment_lens = false
family_engagement_lens = false
school_level_lens = false
support_lens = false

# Wave 4 (reserved)
success_plan_dashboard = false
expansion_opportunity = false
pd_tracker = false
contract_center = false
relationship_mapping = false
```

---

## 2. Guard pattern — Evidence Markdown (`{#if features.x}`)

Evidence supports `{#if …}` blocks natively in `.md` pages. The renderer reads `features.*` from `evidence.config.yaml` via the project context. Every Wave 1 widget is wrapped in its own guard, so a flag flip lights up exactly one surface.

```markdown
<!-- pages/index.md — the Home Dashboard, top-fold of the 5-second test. -->

# PSM Command Center

<FreshnessChip as_of={data.portfolio_summary[0].as_of} />

{#if features.portfolio_summary}

## Portfolio Summary

<PortfolioSummary data={data.portfolio_summary} />

{:else}

<!--
  Honest empty contract — operational-console-design §7.
  A flag that's OFF is NOT a silent gap; it's a labeled "coming soon" so the
  PSM knows what to expect and the QA pass can confirm the gap is intentional.
-->

<EmptyState
  headline="Portfolio Summary — coming in Wave 1"
  copy="Flip features.portfolio_summary to true in evidence.config.yaml to enable."
/>

{/if}

{#if features.portfolio_health_snapshot}

## Portfolio Health Snapshot

<PortfolioHealthSnapshot data={data.portfolio_health_snapshot} />

{:else}

<EmptyState
  headline="Portfolio Health Snapshot — coming in Wave 1"
  copy="Flip features.portfolio_health_snapshot to enable."
/>

{/if}

{#if features.daily_action_center}

## Daily Action Center

<DailyActionCenter data={data.daily_action_center} />

{:else}

<EmptyState
  headline="Daily Action Center — coming in Wave 1"
  copy="Flip features.daily_action_center to enable."
/>

{/if}

{#if features.upcoming_touchpoints}

## Upcoming Touchpoints

<UpcomingTouchpoints data={data.upcoming_touchpoints} />

{:else}

<EmptyState
  headline="Upcoming Touchpoints — coming in Wave 1"
  copy="Flip features.upcoming_touchpoints to enable."
/>

{/if}
```

**Why the explicit `{:else}` branch matters:** an absent widget renders the empty-state surface from `dashboard-styles.css` §4 — diagnostic-headline + copy — so the PSM never sees a silent gap. This pairs with the dashboard-acceptance-tests.md Test 3 (honest empty states).

---

## 3. Guard pattern — Streamlit `if flags["x"]:`

The SiS app loads the flag store once at startup and treats it as a dict. Each Wave 1 widget is a function gated by an `if`:

```python
# app.py — Streamlit-in-Snowflake live operational panel
# Loads feature_flags.toml from the same stage as app.py.

from __future__ import annotations

import streamlit as st
import tomllib  # Python 3.11+; for SiS warehouse runtime fall back to `tomli`
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Flag loader — runs once per session; cache survives reruns.
# Honest empty: if the file is missing, NO widget is rendered (NOT a crash).
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)  # 5-min refresh aligns with the operational cadence
def load_feature_flags() -> dict[str, bool]:
    flag_path = Path("feature_flags.toml")
    if not flag_path.exists():
        # Default-OFF discipline — absent file means every flag is False.
        return {}
    with flag_path.open("rb") as fh:
        return tomllib.load(fh).get("features", {})


flags = load_feature_flags()


# ─────────────────────────────────────────────────────────────────────────────
# Page assembly — every widget gated by its flag, paired with an honest
# empty-state surface when the flag is OFF.
# ─────────────────────────────────────────────────────────────────────────────
st.title("PSM Command Center — Live Operational Panel")

# Wave 1: Portfolio Summary
if flags.get("portfolio_summary", False):
    render_portfolio_summary()
else:
    st.info(
        "**Portfolio Summary — coming in Wave 1.** "
        "Flip features.portfolio_summary in feature_flags.toml to enable."
    )

# Wave 1: Portfolio Health Snapshot
if flags.get("portfolio_health_snapshot", False):
    render_portfolio_health_snapshot()
else:
    st.info(
        "**Portfolio Health Snapshot — coming in Wave 1.** "
        "Flip features.portfolio_health_snapshot to enable."
    )

# Wave 1: Daily Action Center
if flags.get("daily_action_center", False):
    render_daily_action_center()
else:
    st.info(
        "**Daily Action Center — coming in Wave 1.** "
        "Flip features.daily_action_center to enable."
    )

# Wave 1: Upcoming Touchpoints
if flags.get("upcoming_touchpoints", False):
    render_upcoming_touchpoints()
else:
    st.info(
        "**Upcoming Touchpoints — coming in Wave 1.** "
        "Flip features.upcoming_touchpoints to enable."
    )
```

**The `.get("x", False)` pattern is load-bearing** — an unknown or absent flag NEVER renders the widget. Default-OFF is the safe failure mode.

---

## 4. Rollback procedure

A flag flip is the *only* deploy path for going live. Rollback inverts it.

### Tier 1 (Evidence) rollback

1. **Open the offending PR** in the consumer repo (or open a new revert PR).
2. **Edit `evidence.config.yaml`:** change the offending `features.x: true` back to `false`. Do NOT delete the line — leaving it as `false` makes the rollback auditable.
3. **Commit + push to `main`.** The GitHub Actions workflow at [`dashboard-deployment-notes.md`](dashboard-deployment-notes.md#github-actions-workflow-hourly-cron) §Tier 1 rebuilds and deploys within ~5 minutes.
4. **Verify in the deployed site:** the widget is gone, the empty-state surface is back, and the rest of the page is byte-identical to pre-flip.
5. **Log the rollback** in the run artifact `.ravenclaude/runs/<flag-name>-rollback/summary.md` per the marketplace's run-artifacts standard.

**Time-to-rollback:** ≤ 10 minutes from "we have a problem" to "the widget is no longer visible."

### Tier 2 (Streamlit-in-Snowflake) rollback

1. **Edit `feature_flags.toml` locally:** flip the offending flag to `false`.
2. **Upload to the SiS stage:**
   ```sql
   PUT file://feature_flags.toml
       @PSM_CONSOLE.LIVE_OPS.APP_STAGE
       AUTO_COMPRESS = FALSE
       OVERWRITE = TRUE;
   ```
3. **Hard refresh the SiS browser tab** (Ctrl-Shift-R / Cmd-Shift-R) — the Streamlit cache reads the new flag on next page load. If `@st.cache_data` is holding the old flags, the cached function expires within `ttl=300` (5 min) OR the user clicks "Rerun" from the Streamlit menu.
4. **Verify** the widget is gone.

**Time-to-rollback:** ≤ 5 minutes; faster than Tier 1 because there's no static-site rebuild.

### Emergency kill-switch (all flags OFF)

If something catastrophic ships, the **global kill-switch** is to set every `features.*` to `false` and redeploy. The page renders four empty-state surfaces and a header — degraded but never broken. The empty-state copy still names the dashboard, the freshness chip still shows when the data was last refreshed, and the PSM can navigate to the existing `report.html` Portfolio Report below the fold.

---

## 5. Default-OFF discipline

The discipline has four rules:

1. **A new widget MUST land in `evidence.config.yaml` (and `feature_flags.toml`) with the flag set to `false` first.** The PR that adds the code is separate from the PR that flips the flag.
2. **An empty-state branch is mandatory for every gated widget.** The `{:else}` block / `else:` clause is not optional — never silent-skip. This is what makes the "is it intentionally hidden?" question answerable in the dashboard-acceptance-tests.md Test 3 pass.
3. **An unknown flag is treated as `false`.** Python uses `.get("x", False)`; the Evidence guard naturally falls through to `{:else}` because the truthy check fails on `undefined`. No widget renders against a flag the store doesn't know about.
4. **A flag is removed from the store only when the widget itself is removed.** Going-live promotes a flag from `false` → `true`; you don't delete the entry. This keeps the flag store an auditable changelog.

The discipline pairs with [`dashboard-acceptance-tests.md`](dashboard-acceptance-tests.md) Test 3 (honest empty states): the wife seeing a "Daily Action Center — coming in Wave 1" empty-state surface is a successful pass of acceptance-Test-3 / category "first-run," NOT a fail.

---

## 6. Four-wave staged rollout — spec sections → flags

Approximately 20 spec.md sections map to the four waves below. Each wave is a separate go-live PR; flags within a wave can flip independently.

### Wave 1 — Daily Operating System (Tier 1; this PR's scope)

The four flags here line up 1-to-1 with the Tier 1 build plan §0 widgets. Go-live order matches the page top-to-bottom:

| Flag | Spec section | Surface | Acceptance |
|---|---|---|---|
| `portfolio_summary` | §Home Dashboard / Portfolio Summary | W1 card, 7 KPI tiles | Test 1 + Test 2 #7, #8 |
| `portfolio_health_snapshot` | §Portfolio Health Snapshot | W2 card, 5 KPI tiles | Test 2 #2, #4, #5 |
| `daily_action_center` | §Daily Action Center | W3 table top-15 | Test 1 + Test 7 (5-day FP rate) |
| `upcoming_touchpoints` | §Calendar View / Upcoming tasks view | W4 list | Test 2 #6 + Test 8 (TZ) |

**Wave 1 done = all four flipped to `true` + dashboard-acceptance-tests.md fully signed off.**

### Wave 2 — Drill-downs (Tier 2)

Adds drill-from-the-home-view depth. Reserved here so the contract is one document.

| Flag | Spec section | Surface |
|---|---|---|
| `partner_360` | §Partner 360 | `/partner/[partner_id]` drill page |
| `account_timeline` | §Account Timeline | merged event history per partner |
| `lifecycle_tracking` | §Lifecycle Tracking | phase × substage view |
| `renewal_command_center` | §Renewal Command Center | 180/120/90/60/30 day buckets |

### Wave 3 — Segment lenses (Tier 3)

Population-level slices.

| Flag | Spec section | Surface |
|---|---|---|
| `top15_dashboard` | §Top 15 Dashboard | Community Top 15 page |
| `health_lens` | §Health Dashboard | health-band donut + drill |
| `sentiment_lens` | §Sentiment Dashboard | sentiment-band drill |
| `family_engagement_lens` | §Family Engagement | per-partner family-engagement view |
| `school_level_lens` | §School-Level | per-school drill |
| `support_lens` | §Support & Escalation | support volume + age view |

### Wave 4 — Business-motion lenses (Tier 4)

Process surfaces that wrap motion-specific work.

| Flag | Spec section | Surface |
|---|---|---|
| `success_plan_dashboard` | §Success Plan Dashboard | per-partner success plan status |
| `expansion_opportunity` | §Expansion Opportunity | expansion candidate list |
| `pd_tracker` | §Professional Development Tracker | partner PD progress |
| `contract_center` | §Contract Center | 180/120/90/60/30 day contract alerts |
| `relationship_mapping` | §Relationship Mapping | sponsor / decision-maker map |

---

## 7. Cross-tier consistency

The flag NAMES are identical across `evidence.config.yaml` and `feature_flags.toml`. The rollout state is one source of truth in `git` even though the file formats differ per host.

A flag is "live" when it's `true` in **both** files (if both tiers are deployed) — go-live for a widget means flipping both, in the same PR, with a coordinated cache-bust:

- Evidence rebuild via the hourly cron (manual `workflow_dispatch` for immediate)
- SiS hard refresh (or wait for `@st.cache_data` TTL)

If only Tier 1 is deployed (the single-PSM today reality), only `evidence.config.yaml` matters; `feature_flags.toml` is reserved for when Tier 2 ships.

---

## 8. CI guards (recommended; out of scope for this Tier 1 PR)

A future CI gate (Gate 5X, after the Tier 1 render gate ships at Gate 53) should:

1. **Schema-check** every flag in `evidence.config.yaml` `features.*` against a closed list of approved flag names (no typos = no widget silently disabled).
2. **Cross-check** that every flag mentioned in a guard (`{#if features.x}` in any `pages/**.md` OR `flags.get("x", …)` in `app.py`) appears in the flag store.
3. **Reject** any committed file with all Wave-1 flags set to `true` AND no `dashboard-acceptance-tests.md` sign-off block updated in the same PR.

Not implemented in Tier 1 — Tier 2 owns this as part of the rollout-maturation work.
