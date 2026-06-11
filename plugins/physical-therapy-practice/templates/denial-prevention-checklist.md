# Denial-Prevention Checklist — <clinic>

> Fix denials at the point they originate, not at the back end. Work each cluster to its source.
> Verify all coding/payer specifics against current CMS/payer policy and a certified coder.

## 1. Denial cluster summary

| Reason code cluster | % of denials | Origin | Owner |
|---|---|---|---|
| Medical necessity | `<%>` | documentation | clinician / documentation specialist |
| Units / 8-minute rule | `<%>` | point-of-care minutes | clinician / billing |
| Authorization | `<%>` | front desk | front office |
| Modifier (KX / threshold) | `<%>` | threshold tracking | billing |
| Coding (wrong CPT) | `<%>` | coded from target, not note | billing |

## 2. Point-of-origin controls

### Before the visit (front desk)

- [ ] Insurance & benefits verified
- [ ] Authorization obtained / visits remaining tracked
- [ ] Cumulative therapy amount checked vs. threshold

### During care (clinician)

- [ ] Skilled service + medical necessity documented
- [ ] Progress toward measurable goals noted
- [ ] Total timed minutes recorded (units basis)
- [ ] Certification/recert in date

### At billing (billing/RCM)

- [ ] Units match documented timed minutes (8-minute rule) — verify with `pt_calc.py`
- [ ] CPT codes match documented care (coded forward, not to a target)
- [ ] KX / threshold modifier applied with supporting documentation
- [ ] Untimed codes billed per service, kept distinct from timed

## 3. Tracking

| Metric | Current | Target |
|---|---|---|
| First-pass clean-claim rate | `<%>` | `<%>` |
| Denial rate | `<%>` | `<%>` |
| Net collection per visit | `<$>` | `<$>` |
