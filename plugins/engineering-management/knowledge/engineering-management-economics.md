# Engineering Management — the economics behind the house opinions

> The unit economics the house opinions (CLAUDE.md §3) rest on. Formulas here are reproduced in [`../scripts/engineering_management_calc.py`](../scripts/engineering_management_calc.py) so the arithmetic is checkable. Every figure a manager plugs in must be validated against their real situation; benchmark constants are `[unverified — training knowledge]` until a dated source is attached (§3 #8). Outputs are decision-support, not HR/comp/legal advice (§2).

## 1. The cost of regretted attrition (§3 #2 #4 — why retention beats heroics)

Losing an engineer you wanted to keep is expensive in ways a backfill req hides:

```
attrition_cost ≈ replacement_cost + ramp_loss + team_drag
  replacement_cost = (recruiting + hiring-manager + interviewer time)  [org-specific]
  ramp_loss        = months_to_full_productivity × monthly_loaded_cost × avg_ramp_fraction
  team_drag        = morale/onboarding tax on the rest of the team       [estimate]
```

Industry rules of thumb put the fully-loaded cost of replacing a software engineer at a large fraction of, to multiples of, annual salary — but the number is `[unverified — training knowledge]` and org-specific. The point is not the constant; it's that **a held 1:1 and a real growth path are cheap against this** (§3 #2). The `attrition-cost` mode sizes it from the manager's own inputs.

## 2. On-call load (§3 — humane operations)

On-call sustainability is a load calculation, not a willpower test:

```
pages_per_engineer_per_week = total_actionable_pages_per_week ÷ rotation_depth
off_hours_burden            = off_hours_pages ÷ total_pages
```

Sustained load above a few actionable pages per shift — especially off-hours — predicts burnout and attrition (feeding §1's cost). The fix order is: **cut the pages (reduce toil/false alarms) before deepening the rotation or adding people.** The `oncall-load` mode computes per-engineer load and flags an off-hours-heavy rotation.

## 3. Tech-debt as a carrying cost (§3 #7)

Debt is not a moral failing; it's a loan whose interest is paid in slower future work:

```
carrying_cost_per_period = extra_lead_time_fraction × work_volume × loaded_cost_per_unit
paydown_payback_periods  = paydown_cost ÷ carrying_cost_per_period_saved
```

A paydown is worth doing when its **payback period is short relative to the code's remaining life** and it sits on a **hotspot** (high churn × complexity). A rewrite is the highest-risk, longest-payback option — prefer incremental (strangler-fig) paydown traded against roadmap value. The `tech-debt` mode computes carrying cost and payback so the trade-off is sized, not argued (§3 #7).

## 4. Span of control (§3 #8 — context-dependent, not a magic number)

Too-wide a span starves 1:1s and growth (§3 #2); too-narrow over-manages and inflates cost. The "right" number varies with seniority of reports, role complexity, and how much IC work the manager still carries — so it's a **reasoning input, not a rule**. Treat any quoted range as `[unverified — training knowledge]` and decide against the team's reality.

## The rule

Every constant here is the manager's to supply and validate (§2). The calculator does the arithmetic and shows the formula; it never fetches a benchmark or makes the call. Route comp/HR/legal determinations to the qualified authority (§2).
