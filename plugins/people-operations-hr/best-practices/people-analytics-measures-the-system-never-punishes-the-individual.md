# People analytics measures the system — never punishes the individual

**Status:** Absolute rule
**Domain:** People analytics / data ethics
**Applies to:** `people-operations-hr`

---

## Why this exists

People data is uniquely dangerous because it describes individual human beings — their
attendance, sentiment, performance, compensation, and behaviors. Used well, aggregate people
data reveals organizational dynamics: high attrition in a team, engagement drop after a
leadership change, headcount gaps in a function. Used badly, people data becomes surveillance:
individual productivity scores shared with managers, per-employee flight-risk scores used in
retention decisions, attendance records used to discipline remote workers.

The line between analytics and surveillance is not the data — it is the **unit of analysis**
and the **use of the output**. Measuring that Team X has 40% turnover in their first 12 months
is organizational analytics. Measuring that Employee Y's keystrokes dropped 30% this week is
surveillance of an individual. Using attrition models to identify which team deserves more
manager investment is analytics. Using an attrition model to flag specific employees for
"risk mitigation" conversations they didn't consent to is surveillance by another name.

The ethical and practical consequences of getting this wrong are severe: trust destruction when
employees learn they're being individually scored, legal exposure under GDPR Article 22
(automated decision-making), and CCPA equivalents, and the likelihood of discriminatory proxy
effects in any predictive model built on historical people data.

## How to apply

**The individual-vs-system measurement boundary:**

| Analytics question | Unit | Acceptable? |
|-------------------|------|-------------|
| "What is our annualized attrition rate?" | Organization | Yes |
| "Which team has the highest 0-12mo attrition?" | Team | Yes |
| "What manager-level factors predict team attrition?" | Manager-team aggregate | Yes — informs manager development |
| "Which specific employees are likely to leave?" | Individual | No — individual flight risk |
| "What is our engagement score trend?" | Organization / team (n≥5) | Yes |
| "What does Employee Y's engagement survey say?" | Individual | No — breaks anonymity |
| "What are the top themes from exit interviews?" | Themes (qualitative aggregate) | Yes |
| "Employee Y said in their exit interview that…" | Individual | No — unless Y consented |

**Anonymization threshold:** Never report a people data cell with n < 5. Below 5, the data
is traceable to individuals. Many organizations use n ≥ 10 for sensitive data. Set the
threshold explicitly in the analytics governance policy; never leave it implicit.

**Do:**

- Define the minimum reporting unit before building any people analytics dashboard.
- Set and document the anonymization threshold (n ≥ 5 default; n ≥ 10 recommended for
  sentiment / performance data).
- Use aggregate and trend data for manager and leader coaching; never per-employee scores.
- Require a use-case approval step for any new people analytics: "What organizational question
  does this answer? What decision will it inform? Who sees it and in what form?"
- Conduct a bias review on any predictive model built on people data before deployment —
  attrition models trained on historical data will encode historical bias.

**Don't:**

- Build or surface per-employee flight-risk scores to managers, even with good intentions.
- Report team-level engagement results for teams of <5 — the scores are attributable.
- Use people analytics outputs to initiate adverse employment actions (PIPs, terminations)
  without independent documentation of the performance issue through the normal performance
  management process.
- Allow productivity monitoring tools (keylogging, screen capture, focus-time tracking) to
  feed into performance records or manager reports without explicit employee consent and legal
  review.

## Edge cases / when the rule does NOT apply

Forensic investigations of specific misconduct (fraud, harassment investigation, security
incident) involve individual-level data by design — but they require separate legal authorization,
operate under different data-handling rules, and are never conducted under the "people analytics"
banner. These are HR investigations, governed by HR investigation protocols and employment counsel,
not by the analytics function.

## See also

- [`./comp-and-pii-are-need-to-know.md`](./comp-and-pii-are-need-to-know.md) — the parallel
  rule for comp and PII handling.
- [`../agents/people-analytics-engineer.md`](../agents/people-analytics-engineer.md) — full
  ethics framing for the analytics function.
- `applied-statistics` — for significance tests and regression on people data, route there
  with the ethical framing already established.

## Provenance

Reflects the people analytics ethics literature (Tomas Chamorro-Premuzic's "I Human",
the SHRM people analytics guidelines), GDPR Article 22 (automated individual decision-making
protections), the EU AI Act's requirements for high-risk AI in employment contexts, and the
broader algorithmic-fairness research on bias amplification in HR predictive models. The
anonymization threshold of n ≥ 5 is a common survey-science and HR-analytics standard;
some organizations use n ≥ 10 for especially sensitive data.

---

_Last reviewed: 2026-06-08 by `claude`._
