# Benefits Program — Brief

> Output of `benefits-advisor` / the `benefits-plan-design` skill. **Educational scaffolding, not legal, tax, or
> actuarial advice** — a licensed broker and ERISA counsel sign off. An empty "Coverage gaps" or "Funding rationale"
> section means the package isn't scoped as a system yet.

## 1. The group (who we're covering)

| Attribute | Value |
|---|---|
| Headcount / FTE | <n> |
| ALE status (50+ FTE)? | <yes / no — `[verify-at-build]`> |
| Workforce profile (age / family mix / income) | |
| Budget / current spend | |
| Current pain | |

## 2. Plan design per line

| Line | Recommended plan | Mechanics (deductible / coinsurance / OOP-max) | Why for this population |
|---|---|---|---|
| Medical | <HMO / PPO / HDHP+HSA> | | |
| Dental | | | |
| Vision | | | |
| Group life + AD&D | | | |
| Short-term disability | | | |
| Long-term disability | | | <flag if absent — most under-bought line> |

## 3. Funding recommendation

- **Recommended model:** <fully-insured / level-funded / self-funded>
- **Rationale (risk, group size, cash-flow tolerance, stop-loss need):**
- **Conditions that would change the call:**
- **If self-funded:** specific & aggregate stop-loss attachment, ASO vs carrier, cash cushion

## 4. Contribution & eligibility structure

| Tier | Employer share | Employee share | Waiting period |
|---|---|---|---|
| Employee only | | | |
| + dependents | | | |

- **ACA affordability check:** <self-only premium vs the indexed % — `[verify-at-build]`>
- **Minimum value met?** <yes / no — `[verify-at-build]`>

## 5. ACA / ERISA obligations triggered

- <ALE / employer-shared-responsibility — `[verify-at-build]`>
- <ERISA plan documents / SPD>
- <Section 125 cafeteria-plan framing; non-discrimination concerns for counsel>

## 6. Handoff

| What | Routed to |
|---|---|
| Rate adequacy / renewal projection | `underwriting-and-actuarial-analyst` |
| Open enrollment + 1095 / 5500 / COBRA filings | `enrollment-and-compliance-lead` |
| Ongoing HR administration | `people-ops-hr` |
| Binding legal / tax / actuarial opinion | licensed broker / actuary / ERISA counsel |

---

```
Status: ...
Files changed: ...
Not advice: ...
Coverage gaps flagged: ...
Verify-at-build: ...
Handoff: ...
Open questions: ...
Grounding checks performed: ...
```
