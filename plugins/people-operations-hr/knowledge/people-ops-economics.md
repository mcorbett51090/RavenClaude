# People-Ops Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/people_calc.py`](../scripts/people_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. The cost of attrition (§3 #1)

```
replacement_cost = recruiting_cost
                 + onboarding_cost
                 + ramp_loss            (productivity_gap × ramp_months)
                 + vacancy_loss         (daily_role_value × days_open)

annual_attrition_cost = regretted_separations × replacement_cost_per_role
```

**Why it's the headline:** a turnover percentage is abstract; the dollar figure funds the retention investment. A 2-point reduction in regretted attrition on a 500-person org with a meaningful per-head replacement cost is a six- or seven-figure line — but only the *regretted* share is a loss to recover (§3 #1). Always split regretted from non-regretted before costing.

## 2. The hiring plan ties to the budget (§3 #6)

```
required_offers   = target_hires ÷ offer_accept_rate
required_onsites  = required_offers ÷ onsite_to_offer_rate
required_screens  = required_onsites ÷ screen_to_onsite_rate
required_sourced  = required_screens ÷ source_to_screen_rate

recruiter_capacity = required_sourced ÷ sourced_per_recruiter_per_period
comp_envelope      = sum(target_hires_by_level × band_midpoint_by_level)
```

The hiring plan is a *pipeline* problem and a *budget* problem at once. The leaking-stage logic (§3 #3) says: if accept rate is the constraint, more sourcing just fills the top of a leaking funnel — fix the leak first. The `comp_envelope` is the comp analyst's handoff (§3 #6).

## 3. Comp band mechanics (§3 #2)

```
compa_ratio        = salary ÷ band_midpoint
range_penetration  = (salary − band_min) ÷ (band_max − band_min)
band_spread        = (band_max − band_min) ÷ band_min
```

**Compression cost of the counteroffer:** paying a retention counteroffer above the band raises that person's compa-ratio but drags every tenured peer's *relative* position down — the fix for one exit creates inequity for five who stayed, and the precedent recurs. Pay to the band; if the band is wrong, fix the band (§3 #2).

## 4. Pay equity — raw vs residual (§3 #5)

```
raw_gap      = mean_pay(group_A) − mean_pay(group_B)
residual_gap = gap remaining after controlling for
               level, role, tenure, location, performance
```

The raw gap is mostly *composition* (which groups hold which levels/roles), not *pay discrimination*. The residual gap — what remains for like-for-like work — is the actionable number. **But** `people_calc.py pay-equity` computes an *illustrative* controlled gap via simple stratified means, **not** a regression; a defensible audit uses a proper model and a privileged legal review (§2). Report the residual as a *signal to investigate*, never as a legal conclusion.

## 5. Cost of vacancy → the urgency math

```
cost_of_vacancy = daily_value_of_role × days_open
daily_value_of_role ≈ (fully_loaded_salary × value_multiplier) ÷ working_days
```

This converts "time-to-fill" from an HR stat into a finance number the hiring manager feels — and justifies the recruiter capacity in §2.
