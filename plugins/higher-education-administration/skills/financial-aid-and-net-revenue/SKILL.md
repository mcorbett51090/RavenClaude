---
name: financial-aid-and-net-revenue
description: "Optimize financial aid as a yield lever against net tuition revenue — compute gross-to-net tuition and discount rate, find where added aid stops paying for itself, and separate need-based from merit leveraging with Title IV compliance flagged."
---

# Financial Aid & Net Revenue

**Purpose:** treat institutional aid as a leveraging tool measured by net tuition revenue, not as a
discount race — and know where the next dollar of aid stops buying enrolled net revenue.

---

## Steps

### 1. Compute net tuition revenue, not gross

Net tuition revenue = gross tuition − institutional aid/discount. Use
[`../../scripts/higher_ed_calc.py`](../../scripts/higher_ed_calc.py) `net_tuition_revenue` and
`discount_rate`. The headline sticker price funds nothing; net revenue funds the institution.

### 2. Distinguish the two aid jobs

| Aid type | Job | Optimized for |
|---|---|---|
| Need-based | Access / mission | Affordability for eligible students |
| Merit / leveraging | Yield | Enrolled net revenue per aid dollar |

Conflating them produces a single blunt discount that over-pays fit-sensitive students and
under-serves need-sensitive ones.

### 3. Find the diminishing-returns point

Model net tuition revenue across discount scenarios. As discount rises, yield rises but net revenue
per student falls; the optimum is where the marginal aid dollar stops adding net enrolled revenue.
Past that point, more discount buys volume that loses money.

### 4. Segment leveraging by price-sensitivity

Direct leveraging aid at price-sensitive admits who would otherwise melt; don't spend it on
fit-sensitive admits who would enroll anyway. A flat discount does both jobs badly.

### 5. Flag Title IV and compliance points

Federal aid mechanics, packaging rules, and disclosure requirements change and carry compliance
risk. State the mechanic, date it, and flag it for verification against current federal rules and
institutional financial-aid counsel.

---

## Output

A net-tuition-revenue model across discount scenarios, the diminishing-returns point, and a
segmented leveraging recommendation — with Title IV points flagged for verification.
