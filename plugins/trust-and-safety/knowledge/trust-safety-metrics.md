# Knowledge — Trust & Safety metrics

> **Last reviewed:** 2026-06-17 · **Confidence:** High (consensus T&S measurement practice; the statistical-validity caveats route to `applied-statistics`).
> The **measurement catalogue** for the plugin: the metrics that prove enforcement is working — **prevalence** (not just volume), **enforcement precision/recall**, **time-to-action SLA**, and **appeal-overturn rate** — each with its formula, its honest denominator, and the trap it exists to prevent.
>
> **How the agents use it:** the `measure-enforcement-quality` skill assembles a scorecard from these; both agents pull the formula and the denominator choice from here. **Statistical validity** of any precision/recall figure (confidence interval, labeled-sample size, class imbalance) is the **`applied-statistics`** seam — this file defines *what* to measure; that plugin confirms a measured number is real.

---

## 1. Prevalence — the headline metric

**Question it answers:** how much violating content does a user actually *experience*?

```
prevalence = (violating impressions) / (total impressions)
```

- **Use impressions, not content counts.** A removed post nobody saw and a viral post seen 1M times are not equal harm. The honest denominator is **views/impressions**, weighting by reach.
- **Volume ("posts removed") is a vanity metric.** It rises when you enforce more *and* when abuse rises — it cannot tell you whether users are safer. Prevalence can.
- Report as a rate (e.g. violating impressions per 10,000 total impressions), trended over time, per policy category.

## 2. Enforcement precision & recall — report as a pair

**Question they answer:** when we acted, were we right (precision)? Of what we should have caught, how much did we (recall)?

```
precision = true positives / (true positives + false positives)
recall    = true positives / (true positives + false negatives)
F1        = 2 * (precision * recall) / (precision + recall)
```

- **Never quote one without the other** — precision alone hides how much slips through; recall alone hides how many users were wrongly punished.
- A **false positive** is a real user wrongly enforced against (a trust cost); a **false negative** is abuse that got through (a safety cost). The operating point is the deliberate tradeoff between them.
- Tie the pair to the **threshold / operating point** the detector runs at and the **eval set + date** it was measured on — both decay as the adversary adapts.
- **Validity caveat:** a precision/recall number from a small or imbalanced labeled eval needs a **confidence interval** and an adequate sample size to be defensible → route to **`applied-statistics`** before quoting it to leadership.

## 3. Time-to-action SLA — tiered by harm, read the tail

**Question it answers:** how fast do we act once content is detected/reported?

```
time_to_action = action_timestamp - detection_or_report_timestamp
SLA attainment = (# actions within SLA) / (total actions)   per harm tier
```

- **Tier the SLA by harm.** Critical/imminent-harm gets the tightest SLA; low-severity can wait.
- **Report the distribution (p50/p90/p99), not the mean.** The tail is where the harm lives — a good median hides a catastrophic p99.
- Pair with **queue-prioritization health**: an SLA breach usually traces to a queue ordered by arrival instead of by severity × prevalence × virality.

## 4. Appeal-overturn rate — a quality signal, not noise

**Question it answers:** how often was an enforcement action wrong (per the appeal review)?

```
appeal_overturn_rate = (appeals overturned) / (appeals decided)
appeal_rate          = (actions appealed) / (total actions)        # context for the above
```

- A **high overturn rate** means the policy category is ambiguous or the classifier is wrong — it is **feedback on enforcement quality**, not "users gaming appeals."
- Alarm above a per-category threshold; a rising overturn rate should trigger a policy-definition or threshold review.
- Watch the **appeal rate** alongside it: a near-zero appeal rate can mean the appeal path is too hard to find (a due-process failure), not that enforcement is perfect.

## 5. Putting it together — the scorecard read

| Metric | Honest denominator | The trap it prevents |
|---|---|---|
| Prevalence | total impressions | mistaking enforcement *volume* for user safety |
| Precision / recall (pair) | actioned items / truly-violating items | hiding the FP/FN tradeoff behind one number |
| Time-to-action SLA | actions per harm tier | a good mean masking a catastrophic tail |
| Appeal-overturn rate | appeals decided | treating a quality signal as user noise |

## Provenance

Codifies consensus Trust & Safety measurement practice (prevalence-as-headline; precision/recall as a pair; tiered SLA; overturn rate as quality feedback). Domain-neutral. The statistical-validity of any measured precision/recall is the **`applied-statistics`** seam — see this plugin's [`measure-enforcement-quality`](../skills/measure-enforcement-quality/SKILL.md) skill and the [`enforcement-decision-tree.md`](enforcement-decision-tree.md) that produces the actions these metrics score.

---

_Last reviewed: 2026-06-17 by `claude`_
