# Referral & revenue cycle — reference

Deep reference for the `referral-and-patient-access-strategist` and the `pt-practice-lead`. Companion
to [`pt-practice-decision-trees.md`](pt-practice-decision-trees.md).

> **Compliance note:** direct-access scope, payer authorization rules, and visit limits vary by state
> and payer. Treat specifics as `[verify against current state practice act and payer policy]`.

---

## The front-of-pipeline funnel

```
referral source → referral received → scheduled → arrived → evaluated → plan-of-care started
```

Each arrow is a conversion. Referrals that never become evaluations are lost revenue *and* a
frustrated referral source. Use [`../scripts/pt_calc.py`](../scripts/pt_calc.py)
`referral_conversion_rate`.

## Referral sources as a pipeline

Track volume and trend by source like a sales pipeline. The failure mode that hurts most is a
high-volume physician source quietly going cold — it can outweigh any marketing spend, and it's
invisible unless source trend is monitored. A declining source is an alert.

## Speed-to-contact — the dominant conversion lever

Referral → scheduled conversion drops sharply with each day of delay. Calling a new referral within
hours rather than days is usually the single highest-leverage conversion improvement available, ahead
of any acquisition spend.

## Closing the loop with referrers

Send outcome/status updates back to referring physicians. A source that sees good outcomes and clear
communication refers more — the loop *is* the relationship, and outcome data (from the outcomes
analyst) is what makes the loop credible.

## Intake verification prevents downstream denials

The cheapest place to prevent an authorization or coverage denial is at intake: verify eligibility and
benefits, obtain and track authorization and visit limits, and track the therapy threshold. A denial
traced to intake was preventable before the visit.

## Reimbursed-visit economics

The clinic's revenue unit is the **reimbursed** visit — delivered, documented, coded, and collected.
Booked visits, gross fee schedule, and even delivered visits overstate it. Plan-of-care adherence
(completed episodes) is the multi-visit revenue engine; the front-of-pipeline work exists to feed it
with verified, converted patients.

## Point-of-service expectations

Communicating copay/coinsurance and visit-limit reality at intake protects both collections and
plan-of-care adherence — surprise cost is a top driver of mid-episode dropout.
