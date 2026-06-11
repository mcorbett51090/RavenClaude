---
name: enrollment-funnel-and-yield
description: "Model the admissions funnel and optimize yield against net tuition revenue — instrument inquiry → applicant → admit → deposit → enroll, find the leaking stage, and pull non-aid yield levers before the discount lever."
---

# Enrollment Funnel & Yield

**Purpose:** turn a pile of admissions activity into a measured funnel, localize the leak, and lift
yield without defaulting to a discount race — every move judged by net tuition revenue.

---

## Steps

### 1. Instrument the funnel

Define the funnel with concrete, countable stages:

```
inquiry → applicant → admit → deposit → enroll → (melt) → matriculated
```

Each arrow is a conversion. Use [`../../scripts/higher_ed_calc.py`](../../scripts/higher_ed_calc.py)
`funnel_conversion` to compute every step and flag the steepest drop. "Melt" (deposited students who
don't show) is a stage, not an afterthought.

### 2. Localize the leak

| Leak at… | Likely driver | Lever |
|---|---|---|
| inquiry → applicant | weak engagement / unclear fit | nurture, segmented outreach |
| applicant → admit | policy / capacity | review process, admit criteria |
| admit → deposit | price perception / competing offers | yield events, aid timing, fit messaging |
| deposit → enroll (melt) | summer melt, doubts | melt-prevention outreach, onboarding |

### 3. Segment by price- vs. fit-sensitivity

A blended yield rate hides two different students. Price-sensitive admits respond to aid; fit-sensitive
admits respond to engagement and belonging. Pull the lever that matches the segment.

### 4. Exhaust non-aid levers before discounting

Admit timing, personalized engagement, faculty/student contact, and melt-prevention move yield
without eroding net revenue. Reach for additional discount only after these are exhausted — and then
size it against net tuition revenue, not gross.

### 5. Tie every lever to net tuition revenue

Use `net_tuition_revenue` and `discount_rate` from the calculator. A yield gain bought with discount
that lowers net revenue is not a win.

---

## Output

A funnel model (each stage's conversion + the leak), a segmented yield plan, and the net-revenue
effect of each lever. Use the
[`../../templates/enrollment-funnel-model.md`](../../templates/enrollment-funnel-model.md) template.
