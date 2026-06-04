"""
Streamlit-in-Snowflake (SiS) — PSM Live Operational Panel
==========================================================

The "live operational panel" companion to the Evidence.dev static site.
Evidence handles the narrative/snapshot pages (hourly rebuild); SiS handles
the sub-hour / "I want fresh-now" widgets like the Daily Action Center
and open-escalations queue.

Architecture rationale: /tmp/research-rendering-layer.md §6 recommendation —
   "keep Evidence for the narrative/snapshot pages and add
    Streamlit-in-Snowflake for the live operational panels.
    SiS handles auth via Snowflake RBAC for free, no separate hosting,
    and the Codex-buildability is best-in-class."

Cache discipline (research §1.5):
   - @st.cache_data(ttl=300)   — 5-min refresh for KPI cards (cheap warehouse queries)
   - @st.cache_data(ttl=60)    — 1-min for the action-center queue (the page the PSM scans)
   - @st.fragment(run_every=…) — avoids full-app rerun (research §1.5 cited Soputro Feb 2026)

Session-state filter persistence:
   - Two-tier: URL params via `st.query_params` are the source of truth for shareable view
     state (UX research §8); st.session_state mirrors them for in-app interaction.
   - Saved-view names persist to a Snowflake table keyed by current_user.

Snowflake session:
   - `get_active_session()` — caller-rights execution per the deployment notes.
     Owner-rights apps run as the *owner's* role (not the caller's) — fine for v0
     single-PSM, problematic for multi-tenant. See deployment-notes.

Run target: Snowflake's Streamlit-in-Snowflake. Local dev with `streamlit run`
also works once SNOWFLAKE_CONNECTION env vars are set.

Required Snowflake packages (declare in environment.yml or the SiS UI):
   streamlit >=1.40
   pandas
   snowflake-snowpark-python
   altair
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Optional

import pandas as pd
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import Session


# ---------------------------------------------------------------------------
# Page setup — has to come before any other Streamlit call.
# `wide` layout because the Daily Action Center is the focal element.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PSM — Live Operational Panel",
    page_icon=":satellite:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Snowflake session.
#   In SiS: get_active_session() returns the caller's session (owner-rights
#   apps run as owner; caller-rights apps run as the caller — see deployment
#   notes for the difference and when each is appropriate).
#   In local dev: falls back to a connection built from environment vars.
# ---------------------------------------------------------------------------
def _get_session() -> Session:
    try:
        return get_active_session()
    except Exception:
        # Local dev fallback. Requires SNOWFLAKE_* env vars set in .env.
        from snowflake.snowpark import Session as LocalSession

        return LocalSession.builder.configs(
            st.secrets.get("snowflake", {})
        ).create()


session = _get_session()


# ---------------------------------------------------------------------------
# URL-state <-> session-state synchronisation.
#
# UX research §8: URL is the source of truth for shareable view state.
# st.query_params is the Streamlit API for URL params (since 1.30).
# Two-tier persistence:
#   - URL params       -> filters, sort, drill target          (shareable)
#   - st.session_state -> user preference (saved view name)    (per-session)
# ---------------------------------------------------------------------------
def _read_filters_from_url() -> dict:
    qp = st.query_params
    return {
        "segment": qp.get("segment", "all"),
        "psm": qp.get("psm", "all"),
        "band": qp.get("band", "all"),
        "min_priority": int(qp.get("min_priority", "0")),
        "saved_view": qp.get("view", ""),
    }


def _write_filters_to_url(filters: dict) -> None:
    # Drop "all"/empty/0 defaults so the URL stays clean.
    cleaned = {
        k: str(v)
        for k, v in filters.items()
        if v not in ("", "all", 0, None)
    }
    st.query_params.from_dict(cleaned)


if "filters" not in st.session_state:
    st.session_state["filters"] = _read_filters_from_url()


# ---------------------------------------------------------------------------
# Cached queries.
#
# ttl=300  (5 min) — KPI cards: cheap, can lag a few minutes
# ttl=60   (1 min) — Action center queue: this is the page the PSM scans
#                    and reload-then-stale would be misleading.
# Research §1.5 cited Soputro Feb 2026: SiS's "full-app rerun on every
# interaction" is the most-common SiS performance pitfall. The cache_data
# + st.fragment combination mitigates it.
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner="Loading portfolio KPIs…")
def load_portfolio_kpis() -> pd.DataFrame:
    """Mirrors pages/index.md / portfolio_summary.sql in the Evidence app.

    Snowflake-flavored: COUNT_IF, DATEDIFF, QUALIFY. See evidence-home-page.md
    for the full SQL; here we accept a Snowpark DataFrame.
    """
    df = session.sql(
        """
        WITH base AS (
            SELECT
                p.partner_id, p.is_active, p.is_top15,
                h.health_band,
                c.renewal_date,
                e.open_escalations,
                DATEDIFF('day', t.last_touchpoint_at, CURRENT_DATE())
                    AS days_since_touch
            FROM core.partner            p
            LEFT JOIN core.partner_health h ON h.partner_id = p.partner_id
                                            AND h.is_current
            LEFT JOIN core.contract       c ON c.partner_id = p.partner_id
                                            AND c.is_current
            LEFT JOIN core.escalation_agg e ON e.partner_id = p.partner_id
            LEFT JOIN core.touchpoint_agg t ON t.partner_id = p.partner_id
            WHERE p.is_active
        )
        SELECT
            COUNT(*)                                            AS total_partners,
            COUNT_IF(is_top15)                                  AS top15_count,
            COUNT_IF(renewal_date <= DATEADD('day', 180,
                                             CURRENT_DATE()))   AS renewal_window,
            COUNT_IF(health_band = 'red')                       AS at_risk,
            COUNT_IF(open_escalations > 0)                      AS escalations_open,
            COUNT_IF(days_since_touch >= 7)                     AS outreach_needed,
            COUNT_IF(health_band IN ('red','yellow')
                     OR open_escalations > 0)                   AS needing_attention
        FROM base;
        """
    ).to_pandas()
    return df


@st.cache_data(ttl=60, show_spinner="Loading Daily Action Center…")
def load_action_center(
    segment: str,
    psm: str,
    band: str,
    min_priority: int,
) -> pd.DataFrame:
    """Filtered, prioritized action queue.

    Cite: spec § Daily Action Center + § Dashboard Priority Ranking Logic.
    Filters arrive from the sidebar and round-trip through URL params.
    """
    where_clauses = ["p.is_active"]
    if segment != "all":
        where_clauses.append(f"p.segment = '{segment}'")
    if psm != "all":
        where_clauses.append(f"p.psm_owner = '{psm}'")
    if band != "all":
        where_clauses.append(f"h.health_band = '{band}'")

    where_sql = " AND ".join(where_clauses)

    sql = f"""
        WITH scored AS (
            SELECT
                p.partner_id, p.partner_name, p.segment, p.psm_owner,
                h.health_score, h.health_band,
                DATEDIFF('day', t.last_touchpoint_at, CURRENT_DATE())
                    AS days_since_touch,
                DATEDIFF('day', CURRENT_DATE(), c.renewal_date)
                    AS days_to_renewal,
                e.open_escalations,
                (
                    IFF(DATEDIFF('day', CURRENT_DATE(), c.renewal_date)
                          BETWEEN 0 AND 30, 40,
                    IFF(DATEDIFF('day', CURRENT_DATE(), c.renewal_date)
                          BETWEEN 31 AND 90, 25,
                    IFF(DATEDIFF('day', CURRENT_DATE(), c.renewal_date)
                          BETWEEN 91 AND 180, 15, 0))) +
                    IFF(e.open_escalations > 0, 20, 0) +
                    IFF(DATEDIFF('day', t.last_touchpoint_at,
                                 CURRENT_DATE()) >= 14, 15, 0) +
                    IFF(p.is_top15, 15, 0)
                )                                                AS priority_score
            FROM core.partner            p
            LEFT JOIN core.partner_health h ON h.partner_id = p.partner_id
                                             AND h.is_current
            LEFT JOIN core.contract       c ON c.partner_id = p.partner_id
                                             AND c.is_current
            LEFT JOIN core.escalation_agg e ON e.partner_id = p.partner_id
            LEFT JOIN core.touchpoint_agg t ON t.partner_id = p.partner_id
            WHERE {where_sql}
        )
        SELECT *
        FROM scored
        WHERE priority_score >= {min_priority}
        ORDER BY priority_score DESC
        LIMIT 100;
    """
    return session.sql(sql).to_pandas()


@st.cache_data(ttl=300)
def load_psm_owners() -> list[str]:
    return (
        session.sql(
            "SELECT DISTINCT psm_owner FROM core.partner "
            "WHERE is_active ORDER BY psm_owner"
        )
        .to_pandas()["PSM_OWNER"]
        .tolist()
    )


# ---------------------------------------------------------------------------
# Sidebar — filter controls. Round-trip via URL params.
# UX research §8: chips at top of view + Clear all link.
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Filters")

    filters = st.session_state["filters"]

    psm_options = ["all"] + load_psm_owners()
    filters["psm"] = st.selectbox(
        "PSM owner",
        psm_options,
        index=psm_options.index(filters["psm"])
        if filters["psm"] in psm_options
        else 0,
    )

    filters["segment"] = st.selectbox(
        "Segment",
        ["all", "k12", "higher-ed", "corp-ld", "mixed"],
        index=["all", "k12", "higher-ed", "corp-ld", "mixed"].index(
            filters["segment"]
        ),
    )

    filters["band"] = st.selectbox(
        "Health band",
        ["all", "red", "yellow", "green"],
        index=["all", "red", "yellow", "green"].index(filters["band"]),
    )

    filters["min_priority"] = st.slider(
        "Min priority score", 0, 100, value=filters["min_priority"], step=5
    )

    if st.button("Clear all filters", use_container_width=True):
        st.session_state["filters"] = {
            "segment": "all",
            "psm": "all",
            "band": "all",
            "min_priority": 0,
            "saved_view": "",
        }
        st.query_params.clear()
        st.rerun()

    st.divider()
    st.caption("URL is the source of truth — share this URL to share the view.")

    # Persist any changes back to URL so the address bar is shareable.
    _write_filters_to_url(filters)
    st.session_state["filters"] = filters


# ---------------------------------------------------------------------------
# Header — title + freshness chip + manual refresh.
# UX research §7: always show freshness; manual refresh button is non-negotiable.
# ---------------------------------------------------------------------------
header_left, header_right = st.columns([3, 1])
with header_left:
    st.title(":satellite: PSM — Live Operational Panel")
    st.caption(
        "Sub-hour refresh for the widgets that need it. "
        "For narrative + history, see the Evidence dashboard."
    )

with header_right:
    if st.button(":arrows_counterclockwise: Refresh now",
                 use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    cache_age_min = 0  # populated below by the fragment
    st.caption(f"Cache TTL: KPIs 5 min · Action center 1 min")


# ---------------------------------------------------------------------------
# Top: portfolio KPI row.
# ---------------------------------------------------------------------------
kpis = load_portfolio_kpis().iloc[0]

st.subheader("Portfolio at a glance")

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Needing attention", int(kpis["NEEDING_ATTENTION"]))
k2.metric("At risk (red)",     int(kpis["AT_RISK"]))
k3.metric("Renewal ≤ 180d",    int(kpis["RENEWAL_WINDOW"]))
k4.metric("Open escalations",  int(kpis["ESCALATIONS_OPEN"]))
k5.metric("Outreach this wk",  int(kpis["OUTREACH_NEEDED"]))
k6.metric("Total partners",    int(kpis["TOTAL_PARTNERS"]))


# ---------------------------------------------------------------------------
# Daily Action Center — the live widget.
#
# Wrapped in st.fragment so it can refresh independently of the rest of the
# app. Research §1.5 / Soputro Feb 2026: fragments fix SiS's "full-app rerun
# on every interaction" pitfall.
# ---------------------------------------------------------------------------
@st.fragment(run_every="60s")
def daily_action_center_widget():
    st.subheader("Daily Action Center")

    f = st.session_state["filters"]
    df = load_action_center(
        segment=f["segment"],
        psm=f["psm"],
        band=f["band"],
        min_priority=f["min_priority"],
    )

    if df.empty:
        # UX research §6: distinguish first-run / filter-emptied / healthy-empty.
        is_filtered = any(
            v not in ("all", 0) for k, v in f.items() if k != "saved_view"
        )
        if is_filtered:
            st.info(
                ":mag: **Your filters excluded every partner.** "
                "Try widening the band or PSM filter."
            )
            if st.button("Clear filters"):
                st.session_state["filters"] = {
                    "segment": "all", "psm": "all", "band": "all",
                    "min_priority": 0, "saved_view": "",
                }
                st.query_params.clear()
                st.rerun()
        else:
            st.success(
                ":white_check_mark: **Nothing needs your attention right now.** "
                f"Last checked {datetime.now(timezone.utc).strftime('%H:%M UTC')}."
            )
        return

    # Live table — st.dataframe keeps responsiveness; column_config gives
    # the colored band badge + click-through.
    st.dataframe(
        df.rename(columns={
            "PARTNER_NAME": "Partner",
            "PRIORITY_SCORE": "Priority",
            "HEALTH_SCORE": "Health",
            "HEALTH_BAND": "Band",
            "DAYS_TO_RENEWAL": "Days to renewal",
            "DAYS_SINCE_TOUCH": "Days since touch",
            "OPEN_ESCALATIONS": "Open escalations",
            "PSM_OWNER": "PSM",
            "SEGMENT": "Segment",
        }),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Priority":  st.column_config.ProgressColumn(
                "Priority",
                min_value=0, max_value=160, format="%d",
            ),
            "Band":      st.column_config.TextColumn(
                "Band", help="green / yellow / red",
            ),
            "Health":    st.column_config.NumberColumn(
                "Health", format="%d",
            ),
        },
    )

    st.caption(
        f"Showing {len(df)} of up to 100 prioritized partners. "
        f"Refreshes every 60 s. "
        f"Cache populated at {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}."
    )


daily_action_center_widget()


# ---------------------------------------------------------------------------
# Saved views — name the current URL state and store per-user.
# UX research §8 closing: "Saved views — 'My morning view,' 'Pre-standup view'
# — a named URL preset."
# ---------------------------------------------------------------------------
with st.expander("Save / load named view"):
    new_name = st.text_input("Name this view")
    if st.button("Save view", disabled=not new_name):
        url_state = json.dumps(st.session_state["filters"])
        session.sql(
            "MERGE INTO core.psm_saved_view t "
            "USING (SELECT CURRENT_USER() AS owner, "
            f"             '{new_name}'    AS view_name, "
            f"             PARSE_JSON('{url_state}') AS view_state, "
            "              CURRENT_TIMESTAMP() AS saved_at) s "
            "ON t.owner = s.owner AND t.view_name = s.view_name "
            "WHEN MATCHED THEN UPDATE SET t.view_state = s.view_state, "
            "                             t.saved_at  = s.saved_at "
            "WHEN NOT MATCHED THEN INSERT (owner, view_name, view_state, saved_at) "
            "                      VALUES (s.owner, s.view_name, s.view_state, s.saved_at)"
        ).collect()
        st.success(f"Saved '{new_name}'.")

    saved = session.sql(
        "SELECT view_name FROM core.psm_saved_view "
        "WHERE owner = CURRENT_USER() ORDER BY saved_at DESC"
    ).to_pandas()["VIEW_NAME"].tolist()

    if saved:
        chosen = st.selectbox("Load a saved view", [""] + saved)
        if chosen and st.button(f"Load '{chosen}'"):
            state_json = session.sql(
                f"SELECT view_state FROM core.psm_saved_view "
                f"WHERE owner = CURRENT_USER() AND view_name = '{chosen}'"
            ).to_pandas()["VIEW_STATE"].iloc[0]
            st.session_state["filters"] = json.loads(state_json)
            _write_filters_to_url(st.session_state["filters"])
            st.rerun()


# ---------------------------------------------------------------------------
# Footer.
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Streamlit-in-Snowflake · Caller's role: "
    f"`{session.sql('SELECT CURRENT_ROLE()').to_pandas().iloc[0, 0]}`. "
    "Multi-tenant deployments require caller-rights configuration — see "
    "dashboard-deployment-notes.md § Tier 2."
)
