# Charge Capture Lag Is a Hidden Revenue Leak

**Status:** Primary diagnostic
**Domain:** Charge capture / revenue integrity
**Applies to:** `medical-revenue-cycle`

---

## Why this exists

Charge capture lag — the delay between when a service is delivered and when the charge is posted for billing — is one of the most underappreciated revenue leaks in a medical practice or hospital. Each day of lag is a day of delayed cash, and for high-volume services, uncaptured charges compound quickly. Worse, charges that lag beyond 5–7 days are at risk of never being captured at all — they slip through the charge review workflow, providers forget the encounter detail, and documentation is not reviewed. In a typical group practice, 1–3% of charges may be lost to capture failures. [unverified — training knowledge] At $5M revenue, that is $50–$150k per year in permanently lost revenue.

## How to apply

Instrument charge capture lag as a revenue-cycle KPI with a defined tolerance window.

```
Charge capture lag metrics:
Definition: date of service → date charge is posted for billing (in business days)
Target: ≤2 business days for professional charges; ≤3 business days for facility charges
         [unverified — verify against your payer contract timely-filing windows]

Red flags:
  - Any charge >7 days lag: investigate before timely-filing window at risk
  - Same provider consistently lags >3 days: workflow or documentation issue
  - Missing charge report: compare scheduled visits to posted charges — gap is lost revenue

Daily reconciliation (minimum for high-volume practices):
  [ ] Run same-day charge query: visits yesterday vs. charges posted today
  [ ] Missing charges flagged to provider within 24 hours
  [ ] Provider acknowledgment required before close of business next day

Monthly lag report:
  - Average lag by provider and service line
  - % of charges captured within 24 hours vs. 2 days vs. >5 days
  - Late charges reversed or adjusted: dollar value and category
  - Timely-filing write-offs: charges lost because the filing window closed
```

**Do:**
- Set up a daily missing-charge reconciliation report that runs automatically from the PM/EHR system — don't rely on staff to remember to check.
- Train every provider that charge lag is a revenue and compliance responsibility, not just a billing team problem.
- Run timely-filing write-off analysis monthly — if charges are being written off for timely filing, the lag problem is already at critical.

**Don't:**
- Accept "the doctor is busy" as an explanation for chronic charge lag — the workflow fix is earlier in the encounter (point-of-care charge capture, charge capture mobile tools), not asking the doctor to document faster.
- Treat charge lag as a billing-office metric in isolation; the root cause is usually a clinical workflow or documentation step, not the billing team's performance.
- Allow charge review rounds to fall more than 48 hours behind — a 72-hour-old charge review pile means yesterday's charges are already approaching the lag threshold.

## Edge cases / when the rule does NOT apply

Pathology, radiology, and other read-based services have a different charge cycle (read happens asynchronously); lag measurement must account for the read turnaround time as a separate component. The principle still applies — the lag must be measured and managed — but the baseline is different.

## See also

- [`../agents/rcm-analytics-analyst.md`](../agents/rcm-analytics-analyst.md) — owns charge capture metrics and revenue integrity analytics.
- [`../agents/rcm-engagement-lead.md`](../agents/rcm-engagement-lead.md) — charge capture lag analysis is a first-order item in an RCM engagement scope.

## Provenance

Standard RCM and revenue integrity practice; grounded in HFMA revenue cycle benchmarks and MGMA practice management data; charge capture loss estimates are [unverified — training knowledge] and should be validated against the practice's own charge reconciliation data.

---

_Last reviewed: 2026-06-05 by `claude`_
