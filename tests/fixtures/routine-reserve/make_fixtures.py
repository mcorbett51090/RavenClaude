"""Builds tests/fixtures/routine-reserve/. Expected values are derived by hand from
the spec (knowledge/routine-token-reserve.md), NOT by calling the engine."""
import datetime as dt
import json
import os
import sys

root = sys.argv[1]
E = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
H = 3600

def fresh_runs(tid, cost, fired_list, prefix):
    recs = []
    for i, f in enumerate(fired_list):
        sid = f"{prefix}{i}"
        recs.append({"kind": "run", "t": f + 2 * H, "trigger_id": tid, "session_id": sid, "fired_at": f})
        # session idle since f+5min, snapshot at f+2h -> settled
        recs.append({"kind": "cost", "t": f + 2 * H, "session_id": sid, "cost_usd": cost,
                     "created_at": f, "updated_at": f + 300})
    return recs

def write(name, inp, exp):
    d = os.path.join(root, name); os.makedirs(d, exist_ok=True)
    json.dump(inp, open(os.path.join(d, "input.json"), "w"), indent=1, sort_keys=True)
    json.dump(exp, open(os.path.join(d, "expected.json"), "w"), indent=1, sort_keys=True)

# 1 — cron counting incl. day-of-week; equal-cost EWMA; ok state.
now = E("2026-09-24T12:00:00Z")  # Thursday
s = [
  {"kind": "trigger", "t": now - 600, "trigger_id": "T1", "name": "hourly", "cron": "0 * * * *", "active": True},
  {"kind": "trigger", "t": now - 600, "trigger_id": "T2", "name": "saturday", "cron": "0 7 * * 6", "active": True},
  {"kind": "trigger", "t": now - 600, "trigger_id": "T3", "name": "disabled", "cron": "0 * * * *", "active": False},
]
s += fresh_runs("T1", 0.2, [now - 10 * H, now - 9 * H, now - 8 * H], "h")
s += fresh_runs("T2", 5.0, [now - 26 * H, now - 50 * H, now - 74 * H], "w")
# T1: Thu 12:00 -> Mon 12:00 = 96 firings; T2: Sat 07:00 only = 1; T3: 0.
# reserve_usd = (96*0.2 + 1*5.0) * 1.2 = 29.04 ; k = 100/1000 = 0.1 -> 2.904%
write("01-cron-dow-weekly", {
  "now": "2026-09-24T12:00:00Z", "samples": s, "config": {"weekly_budget_usd": 1000},
  "reading": {"seven_day_pct": 40, "resets_at": E("2026-09-28T12:00:00Z"), "captured_at": now - 60}},
  {"state": "ok", "reserve_usd": 29.04, "reserve_pct_recommended": 2.9, "line_pct": 97.1,
   "reset_assumed": False, "estimated": False,
   "routines": [
     {"name": "disabled", "remaining_firings": 0},
     {"name": "hourly", "remaining_firings": 96, "avg_cost_usd": 0.2, "runs_measured": 3, "estimated": False},
     {"name": "saturday", "remaining_firings": 1, "avg_cost_usd": 5.0, "runs_measured": 3, "estimated": False}]})

# 2 — persistent session deltas; EWMA weights; cold-start median blend; override -> over.
r1, r2, r3 = E("2026-09-21T09:00:00Z"), E("2026-09-22T09:00:00Z"), E("2026-09-23T09:00:00Z")
now = r3 + 3 * H  # Wed 12:00
s = [
  {"kind": "trigger", "t": now - 600, "trigger_id": "T4", "name": "daily-persistent", "cron": "0 9 * * *", "active": True, "persistent": True},
  {"kind": "trigger", "t": now - 600, "trigger_id": "T5", "name": "new-hourly", "cron": "30 * * * *", "active": True},
]
for f in (r1, r2, r3):
    s.append({"kind": "run", "t": f + 2 * H, "trigger_id": "T4", "session_id": "p1", "fired_at": f})
s += [
  {"kind": "cost", "t": r1 - 600, "session_id": "p1", "cost_usd": 10.0, "created_at": r1 - 86400, "updated_at": r1 - 3600},
  {"kind": "cost", "t": r1 + 2 * H, "session_id": "p1", "cost_usd": 12.0, "created_at": r1 - 86400, "updated_at": r1 + 600},
  {"kind": "cost", "t": r2 + 2 * H, "session_id": "p1", "cost_usd": 13.0, "created_at": r1 - 86400, "updated_at": r2 + 600},
  {"kind": "cost", "t": r3 + 2 * H, "session_id": "p1", "cost_usd": 16.0, "created_at": r1 - 86400, "updated_at": r3 + 600},
]
s += fresh_runs("T5", 0.5, [now - 5 * H], "n")
# T4 run costs 2,1,3 at ages (days) 2.125, 1.125, 0.125, half-life 7 d:
w = [0.5 ** (a / 7) for a in (2.125, 1.125, 0.125)]
t4 = (w[0] * 2 + w[1] * 1 + w[2] * 3) / sum(w)
# T5: 1 run of 0.5; median of all runs [0.5,1,2,3] = 1.5 -> (1*0.5 + 2*1.5)/3
t5 = (0.5 + 2 * 1.5) / 3
# firings Wed 12:00 -> Fri 00:00: T4 Thu 09:00 = 1 ; T5 :30 hourly for 36 h = 36
reserve_usd = (1 * t4 + 36 * t5) * 1.2
write("02-persistent-coldstart-override", {
  "now": "2026-09-23T12:00:00Z", "samples": s, "config": {"weekly_budget_usd": 500},
  "override": {"override_pct": 50, "expires_at": E("2026-09-25T00:00:00Z")},
  "reading": {"seven_day_pct": 60, "resets_at": E("2026-09-25T00:00:00Z"), "captured_at": now - 60}},
  {"state": "over", "reserve_usd": round(reserve_usd, 2), "reserve_pct_recommended": round(0.2 * reserve_usd, 1),
   "override_pct": 50.0, "reserve_pct_effective": 50.0, "line_pct": 50.0, "estimated": True,
   "routines": [
     {"name": "daily-persistent", "remaining_firings": 1, "avg_cost_usd": round(t4, 4), "runs_measured": 3, "estimated": False},
     {"name": "new-hourly", "remaining_firings": 36, "avg_cost_usd": round(t5, 4), "runs_measured": 1, "estimated": True}]})

# 3 — no reading, no budget: unknown, reset assumed, nothing guessed.
now = E("2026-09-24T12:00:00Z")
s = [{"kind": "trigger", "t": now - 600, "trigger_id": "T1", "name": "hourly", "cron": "0 * * * *", "active": True}]
s += fresh_runs("T1", 0.2, [now - 10 * H, now - 9 * H, now - 8 * H], "h")
write("03-unknown-uncalibrated", {"now": "2026-09-24T12:00:00Z", "samples": s},
  {"state": "unknown", "reset_assumed": True, "k_source": "uncalibrated", "current_pct": None,
   "reserve_pct_recommended": None, "estimated": True})

# 4 — routines alone need more than the headroom: infeasible (warn, never ask).
# 96 hourly firings x 0.2 x 1.2 = 23.04 $ ; k = 100/100 = 1 -> 23.04% > headroom 5%
write("04-infeasible", {"now": "2026-09-24T12:00:00Z", "samples": s, "config": {"weekly_budget_usd": 100},
  "reading": {"seven_day_pct": 95, "resets_at": E("2026-09-28T12:00:00Z"), "captured_at": now - 60}},
  {"state": "infeasible", "reserve_usd": 23.04, "reserve_pct_recommended": 23.0, "headroom_pct": 5.0})

# 5 — calibration from metered spend; undercount-safe baseline; warn band.
now = E("2026-09-24T12:00:00Z"); start = E("2026-09-21T12:00:00Z")  # resets 09-28 12:00
s = [{"kind": "trigger", "t": now - 600, "trigger_id": "T1", "name": "hourly", "cron": "0 * * * *", "active": True}]
s += fresh_runs("T1", 0.2, [now - 10 * H, now - 9 * H, now - 8 * H], "h")   # created in window: base 0 -> 0.6
s += [  # a long session created BEFORE the window, first seen inside it: counts growth only
  {"kind": "cost", "t": start + 10 * H, "session_id": "old", "cost_usd": 50.0, "created_at": start - 86400, "updated_at": start + 9 * H},
  {"kind": "cost", "t": start + 20 * H, "session_id": "old", "cost_usd": 59.4, "created_at": start - 86400, "updated_at": start + 19 * H}]
# spend = 0.6 + 9.4 = 10.0 ; pct 88 -> k = 8.8 %/$ ; reserve_usd = 96*0.2*1.2 = 23.04
# margin 0 -> reserve_usd 19.2 ; current 12 vs line 100-16 = 84 -> ok
write("05-calibrated", {"now": "2026-09-24T12:00:00Z", "samples": s,
  "config": {"margin_pct": 0},
  "reading": {"seven_day_pct": 12, "resets_at": E("2026-09-28T12:00:00Z"), "captured_at": now - 60},
  "history": [{"resets_at": int(E("2026-09-21T12:00:00Z")), "k": 0.1, "pct": 50, "spend": 500}]},
  # this week: pct 12 >= 10, spend 10.0 -> k_week 1.2 ; history weights [0.5, 1] -> (0.5*0.1 + 1*1.2)/1.5
  {"k_source": "calibrated from 2 week(s)", "k_pct_per_usd": round((0.5 * 0.1 + 1.2) / 1.5, 6),
   "reserve_usd": 19.2, "reserve_pct_recommended": round(19.2 * (0.5 * 0.1 + 1.2) / 1.5, 1),
   "state": "ok"})

# 6 — warn band: k = 1 (budget 100), reserve 23.04 -> line 76.96 ; 72 >= 76.96 - 5
now = E("2026-09-24T12:00:00Z")
s = [{"kind": "trigger", "t": now - 600, "trigger_id": "T1", "name": "hourly", "cron": "0 * * * *", "active": True}]
s += fresh_runs("T1", 0.2, [now - 10 * H, now - 9 * H, now - 8 * H], "h")
write("06-warn-band", {"now": "2026-09-24T12:00:00Z", "samples": s, "config": {"weekly_budget_usd": 100},
  "reading": {"seven_day_pct": 72, "resets_at": E("2026-09-28T12:00:00Z"), "captured_at": now - 60}},
  {"state": "warn", "line_pct": 77.0, "reserve_pct_effective": 23.0})
print("fixtures written to", root)
