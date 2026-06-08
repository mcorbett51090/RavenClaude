# Behavioral Health Practice Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/behavioral_health_practice_calc.py`](../scripts/behavioral_health_practice_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. No-show is lost revenue AND lost access (§3 #1)

```
lost_slots    = scheduled_visits * no_show_rate
lost_revenue  = lost_slots * avg_visit_revenue
recovered     = lost_revenue * reminder_lift   # lift = fraction of no-shows a reminder program recovers
```

An empty slot is two losses at once — the practice's revenue and a patient who didn't get seen. A reminder program plus waitlist backfill recovers a measurable fraction; quantify it against the baseline rate, never as a per-patient anecdote.

## 2. Caseload fits under capacity (§3 #4)

```
capacity_sessions = clinician_ftes * target_weekly_billable_hours / avg_session_hours
utilization        = demand_sessions / capacity_sessions
gap                = demand_sessions - capacity_sessions
```

Staff against measured demand and the no-show-adjusted fill rate. A capacity guessed from a fixed headcount ratio either starves access or burns margin on idle clinician time.

## 3. Payer mix is the margin lever (§3 #5)

```
blended_reimb = sum(volume_p * reimb_p for p in payers) / total_volume
margin_per_visit = reimb_p - variable_cost_p          # per payer
mix_shift_delta  = new_blended_margin - current_blended_margin
```

Read margin by payer, not blended only — a flush commercial book can mask a payer billing below variable cost. Mental-health parity gaps (behavioral rates lagging medical-equivalent services) are a margin signal you flag and route to counsel, never rule on.

## 4. Documentation is a revenue control (§3 #3)

```
at_risk_revenue = visits_with_late_or_incomplete_note * reimbursement_per_visit
```

A note that's late, unsigned, or missing medical-necessity language is both unbillable and a clawback exposure. Treat note timeliness and content as one revenue-and-compliance control — but the clinical and medical-necessity judgment is the licensed clinician's, never the team's.
