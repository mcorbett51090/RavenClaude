#!/usr/bin/env python3
"""Synthetic data generator for the Partner Success Command Center dashboard.

This is the REFERENCE implementation of Prompt 1 (see ../codex-build-prompts.md).
It proves the data contract the dashboard reads against and gives a known-good
fixture so the dashboard can be built/verified without spending Codex credits.

- Fully SYNTHETIC + FERPA-safe: generated district names, aggregate counts only,
  never any student-level or personal data.
- Reproducible: seeded with 42 AND pinned to a fixed REFERENCE_TODAY so the output
  is byte-identical across runs. In a live build you'd swap REFERENCE_TODAY for
  datetime.date.today() (the only line that makes output non-reproducible).

Run:  python3 synthesize.py    # writes ./data.json next to this file
"""

import json
import os
import random
from datetime import date, datetime, timedelta

# Pinned so reruns are byte-identical. Swap for date.today() in a live build.
REFERENCE_TODAY = date(2026, 6, 4)
SEED = 42
N_PARTNERS = 25

WEIGHTS = {
    "renewal_timing": 25,
    "health_decline": 20,
    "sentiment_decline": 15,
    "days_since_touchpoint": 12,
    "open_escalations": 10,
    "ticket_volume": 5,
    "arr": 5,
    "top15_bonus": 5,
    "usage_decline": 3,
}
BANDS = {"green_min": 70, "yellow_min": 50}

SEGMENTS = ["Enterprise", "Mid", "SMB"]
STATES = ["TX", "CA", "FL", "NY", "OH", "WA", "GA", "NC", "AZ", "CO", "MI", "PA"]
FUNDING = ["Title I", "ESSER", "General Fund", "Grant"]
LIFECYCLE = {
    "Deployment": ["Kickoff", "Data Mapping", "Go-Live"],
    "BOI": ["Onboarding", "Early Adoption"],
    "MOI": ["Steady State", "Expansion Review"],
    "Renewal": ["Renewal Planning", "Renewal Outreach"],
}
PSMS = ["Dana Whitfield", "Priya Nair", "Marcus Bell"]
PRODUCTS = ["Core Platform", "Family Messaging", "Insights", "Translate", "PD Suite"]
ROLES = [
    "champion",
    "exec_sponsor",
    "superintendent",
    "tech_lead",
    "family_engagement",
    "stakeholder",
]
TICKET_THEMES = ["SSO / rostering", "messaging delivery", "data sync", "billing", "training gap"]
EVENT_TYPES = [
    "closed_won", "kickoff", "go_live", "training", "qbr", "checkin",
    "success_plan_review", "escalation", "sentiment_change",
    "renewal_conversation", "expansion_conversation",
]

ADJ = ["Maple", "Riverbend", "Oakridge", "Cedar", "Granite", "Willow", "Summit", "Harbor",
       "Prairie", "Lakeside", "Birchwood", "Stonebridge", "Foxhill", "Clearwater", "Brookfield",
       "Redwood", "Silvercreek", "Northgate", "Meadowlark", "Pinehurst", "Ironwood", "Glenmoor",
       "Ashford", "Crestview", "Fairhaven"]
SUFFIX = ["USD", "School District", "Public Schools", "County Schools", "Unified District"]


def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def iso(d):
    return d.isoformat()


def iso_ts(d):
    return datetime(d.year, d.month, d.day, 9, 0, 0).isoformat() + "Z"


def main():
    rng = random.Random(SEED)

    # Renewal buckets: guarantee >=2 partners at each of 180/120/90/60/30 days out.
    forced_renewal_offsets = [180, 180, 120, 120, 90, 90, 60, 60, 30, 30]
    # Health bands: guarantee >=3 green / >=3 yellow / >=3 red.
    forced_health = [82, 88, 75, 60, 65, 55, 42, 35, 48]  # 3 green, 3 yellow, 3 red

    arr_values = [rng.choice([45000, 60000, 90000, 120000, 180000, 240000, 320000])
                  for _ in range(N_PARTNERS)]
    max_arr = max(arr_values)

    partners, contacts, timeline_events, usage_daily = [], [], [], []
    success_plans, contracts, tickets, calendar_events = [], [], [], []

    for i in range(N_PARTNERS):
        uid = f"acct_{i + 1:04d}"
        name = f"{ADJ[i % len(ADJ)]} {rng.choice(SUFFIX)}"
        segment = rng.choice(SEGMENTS)
        arr = arr_values[i]

        # Renewal timing
        if i < len(forced_renewal_offsets):
            days_to_renewal = forced_renewal_offsets[i]
        else:
            days_to_renewal = rng.choice([240, 300, 150, 75, 45, 200, 110])
        renewal = REFERENCE_TODAY + timedelta(days=days_to_renewal)
        term_years = rng.choice([1, 2, 3])
        contract_start = renewal - timedelta(days=365 * term_years)

        # Health
        if i < len(forced_health):
            health = forced_health[i]
        else:
            health = rng.randint(38, 92)
        # Health components average back to ~health
        comps = {
            "adoption": clamp(health + rng.randint(-8, 8)),
            "touchpoint": clamp(health + rng.randint(-12, 6)),
            "outcome": clamp(health + rng.randint(-6, 10)),
            "sentiment": clamp(health + rng.randint(-10, 10)),
        }
        health_score = round(sum(comps.values()) / 4)
        sentiment_score = comps["sentiment"]
        engagement_score = clamp(round((comps["adoption"] + comps["touchpoint"]) / 2))

        top15 = i < 8 or rng.random() < 0.15
        lifecycle_stage = rng.choice(list(LIFECYCLE.keys()))
        if days_to_renewal <= 120:
            lifecycle_stage = "Renewal"
        substage = rng.choice(LIFECYCLE[lifecycle_stage])
        stage_entered = REFERENCE_TODAY - timedelta(days=rng.randint(20, 160))

        days_since_touch = rng.choice([3, 14, 27, 45, 62, 80, 95, 110])
        last_touch = REFERENCE_TODAY - timedelta(days=days_since_touch)
        next_touch = REFERENCE_TODAY + timedelta(days=rng.choice([7, 14, 21, 30, 45]))

        open_esc = rng.choice([0, 0, 0, 1, 1, 2])
        open_tk = rng.choice([0, 0, 1, 1, 2, 3, 4])
        ticket_aging = rng.randint(0, 40) if open_tk else 0
        usage_decline_signal = clamp(rng.randint(0, 100))

        # ── Priority breakdown: raw 0-100 strength of each signal ──
        breakdown = {
            "renewal_timing": clamp(round(100 * (1 - days_to_renewal / 365))),
            "health_decline": clamp(100 - health_score),
            "sentiment_decline": clamp(100 - sentiment_score),
            "days_since_touchpoint": clamp(days_since_touch),  # 0-110 capped at 100
            "open_escalations": clamp(open_esc * 50),
            "ticket_volume": clamp(open_tk * 18),
            "arr": clamp(round(arr / max_arr * 100)),
            "top15_bonus": 100 if top15 else 0,
            "usage_decline": usage_decline_signal,
        }
        priority_score = clamp(round(sum(breakdown[k] * WEIGHTS[k] for k in WEIGHTS) / 100))

        # Top contributing signal → reason + recommended action
        top_signal = max(WEIGHTS, key=lambda k: breakdown[k] * WEIGHTS[k])
        reason_map = {
            "renewal_timing": ("Renewal approaching", "Schedule renewal planning call"),
            "health_decline": ("Health score declining", "Run a health-recovery play"),
            "sentiment_decline": ("Sentiment slipping", "Book a relationship check-in"),
            "days_since_touchpoint": ("Overdue for a touchpoint", "Reach out this week"),
            "open_escalations": ("Open escalation", "Resolve the open escalation today"),
            "ticket_volume": ("Elevated support volume", "Review open tickets with support"),
            "arr": ("High-value account", "Protect this account proactively"),
            "top15_bonus": ("Top 15 partner", "Keep cadence tight"),
            "usage_decline": ("Usage trending down", "Drive an adoption push"),
        }
        action_reason, recommended_action = reason_map[top_signal]

        partners.append({
            "account_uid": uid,
            "name": name,
            "segment": segment,
            "state": rng.choice(STATES),
            "arr": arr,
            "contract_start": iso(contract_start),
            "contract_end": iso(renewal),
            "renewal_date": iso(renewal),
            "funding_source": rng.choice(FUNDING),
            "owner_psm": rng.choice(PSMS),
            "top15_status": top15,
            "lifecycle_stage": lifecycle_stage,
            "lifecycle_substage": substage,
            "stage_entered_at": iso_ts(stage_entered),
            "last_touchpoint_at": iso_ts(last_touch),
            "next_required_touchpoint_at": iso_ts(next_touch),
            "health_components": comps,
            "health_score": health_score,
            "sentiment_score": sentiment_score,
            "engagement_score": engagement_score,
            "priority_score": priority_score,
            "priority_breakdown": breakdown,
            "open_escalations": open_esc,
            "open_tickets": open_tk,
            "ticket_aging_days": ticket_aging,
            "recommended_action": recommended_action,
            "action_reason": action_reason,
        })

        # ── Contacts (2-6) ──
        n_contacts = rng.randint(2, 6)
        chosen_roles = ["champion", "exec_sponsor"] + rng.sample(
            ROLES, k=min(n_contacts - 2, len(ROLES)))
        for c, role in enumerate(chosen_roles[:n_contacts]):
            contacts.append({
                "contact_uid": f"{uid}_c{c + 1}",
                "account_uid": uid,
                "name": f"{rng.choice(['Alex','Jordan','Sam','Casey','Riley','Morgan','Taylor','Jamie'])} "
                        f"{rng.choice(['Reyes','Cole','Nguyen','Patel','Brooks','Okafor','Diaz','Hahn'])}",
                "title": {
                    "champion": "Curriculum Director",
                    "exec_sponsor": "Assistant Superintendent",
                    "superintendent": "Superintendent",
                    "tech_lead": "Director of Technology",
                    "family_engagement": "Family Engagement Lead",
                    "stakeholder": "Principal",
                }[role],
                "role": role,
                "influence_level": rng.choice(["high", "med", "low"]),
                "sentiment": rng.choice(["green", "green", "yellow", "red"]),
                "last_interaction_at": iso_ts(
                    REFERENCE_TODAY - timedelta(days=rng.randint(5, 90))),
            })

        # ── Timeline events (4-10) ──
        n_events = rng.randint(4, 10)
        for e in range(n_events):
            etype = rng.choice(EVENT_TYPES)
            timeline_events.append({
                "event_uid": f"{uid}_e{e + 1}",
                "account_uid": uid,
                "type": etype,
                "ts": iso_ts(REFERENCE_TODAY - timedelta(days=rng.randint(1, 300))),
                "source": rng.choice(
                    ["salesforce", "planhat", "support", "snowflake", "calendar", "manual"]),
                "summary": {
                    "sentiment_change": "Sentiment moved after a leadership change",
                    "escalation": "Escalation opened on rostering sync",
                    "qbr": "Quarterly business review completed",
                    "renewal_conversation": "Opened renewal timeline discussion",
                    "expansion_conversation": "Discussed adding two schools",
                }.get(etype, f"{etype.replace('_', ' ').title()} logged"),
            })

        # ── Usage daily (~30 days) ──
        base_users = rng.randint(200, 4000)
        fam_invited = rng.randint(500, 6000)
        fam_activated = round(fam_invited * rng.uniform(0.25, 0.8))
        for d in range(30):
            day = REFERENCE_TODAY - timedelta(days=29 - d)
            drift = 1 - (usage_decline_signal / 100) * (d / 60)
            active = max(0, round(base_users * drift * rng.uniform(0.9, 1.05)))
            usage_daily.append({
                "account_uid": uid,
                "date": iso(day),
                "active_users": active,
                "active_teachers": round(active * 0.18),
                "active_admins": round(active * 0.03),
                "family_invited": fam_invited,
                "family_activated": fam_activated,
                "family_engagement_rate": round(fam_activated / fam_invited, 3),
            })

        # ── Success plans (1-3) ──
        for p in range(rng.randint(1, 3)):
            success_plans.append({
                "plan_uid": f"{uid}_sp{p + 1}",
                "account_uid": uid,
                "goal": rng.choice([
                    "Reach 70% teacher adoption", "Launch family messaging district-wide",
                    "Complete PD for all schools", "Improve 2-way family response rate"]),
                "owner": rng.choice(PSMS),
                "due_date": iso(REFERENCE_TODAY + timedelta(days=rng.randint(15, 180))),
                "progress_pct": rng.randint(0, 100),
                "status": rng.choice(["on_track", "on_track", "at_risk", "complete", "overdue"]),
            })

        # ── Contract (1) ──
        pd_purchased = rng.choice([0, 5, 10, 20])
        contracts.append({
            "contract_uid": f"{uid}_ct1",
            "account_uid": uid,
            "start": iso(contract_start),
            "end": iso(renewal),
            "arr": arr,
            "multi_year": term_years > 1,
            "schools_included": rng.randint(1, 24),
            "licensed_users": rng.randint(500, 12000),
            "products_purchased": rng.sample(PRODUCTS, k=rng.randint(1, 4)),
            "pd_purchased_sessions": pd_purchased,
            "pd_completed_sessions": round(pd_purchased * rng.uniform(0, 1)) if pd_purchased else 0,
        })

        # ── Tickets (0-4) ──
        for t in range(open_tk):
            tickets.append({
                "ticket_uid": f"{uid}_t{t + 1}",
                "account_uid": uid,
                "opened_at": iso_ts(REFERENCE_TODAY - timedelta(days=rng.randint(1, 45))),
                "status": rng.choice(["open", "pending", "closed"]),
                "severity": rng.choice(["low", "med", "high"]),
                "theme": rng.choice(TICKET_THEMES),
                "age_days": rng.randint(1, 45),
                "is_escalation": t < open_esc,
            })

        # ── Calendar events (2-5) ──
        for k in range(rng.randint(2, 5)):
            calendar_events.append({
                "event_uid": f"{uid}_cal{k + 1}",
                "account_uid": uid,
                "type": rng.choice([
                    "qbr", "checkin", "renewal_meeting", "strategic",
                    "pd_session", "success_plan_review", "health_check"]),
                "scheduled_at": iso_ts(REFERENCE_TODAY + timedelta(days=rng.randint(3, 120))),
                "duration_min": rng.choice([30, 45, 60]),
                "status": rng.choice(["scheduled", "scheduled", "completed", "missed"]),
            })

    data = {
        "schema_version": "1.0",
        "generated_at": iso_ts(REFERENCE_TODAY),
        "bands": BANDS,
        "priority_weights": WEIGHTS,
        "partners": partners,
        "contacts": contacts,
        "timeline_events": timeline_events,
        "usage_daily": usage_daily,
        "success_plans": success_plans,
        "contracts": contracts,
        "tickets": tickets,
        "calendar_events": calendar_events,
    }

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"Wrote {out}: {len(partners)} partners, {len(contacts)} contacts, "
          f"{len(timeline_events)} events, {len(usage_daily)} usage rows.")


if __name__ == "__main__":
    main()
