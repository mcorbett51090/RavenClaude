# Moderation runbook — <surface / queue name>

> The operating manual for the human-review layer: how content arrives, how the queue is
> prioritized, who escalates what, how reviewers are protected, and how the program is measured.

**Owner:** <name> · **Version:** <x.y> · **Updated:** <YYYY-MM-DD> · **Queue:** <name>

## 1. Intake & routing
- **Sources:** <user reports / rule matches / classifier scores>.
- **Auto-action band:** scores ≥ <threshold> (precision ≥ <floor>) are auto-actioned; everything else enters the queue.
- **Gray zone → queue:** <score range> routes to human review.

## 2. Queue prioritization (by harm, not arrival)
> Order = **severity × prevalence × virality**, never FIFO.

| Priority | Criteria | Time-to-action SLA |
|---|---|---|
| P0 — critical / imminent harm | <…> | <e.g. 1h> |
| P1 — high severity / high virality | <…> | <e.g. 4h> |
| P2 — medium | <…> | <e.g. 24h> |
| P3 — low / borderline | <…> | <e.g. 72h> |

## 3. Reviewer decisions → enforcement
- Map each decision to a proportional action via
  [`../knowledge/enforcement-decision-tree.md`](../knowledge/enforcement-decision-tree.md).
- Every action emits **notice + reason + appeal route** (due process).
- Reviewer decisions are **labels** — feed them back to recalibrate detector thresholds.

## 4. Escalation
| Trigger | Escalate to | SLA |
|---|---|---|
| Critical / imminent-harm class | Specialist queue + (where required) legal | <…> |
| Novel abuse pattern / suspected campaign | T&S policy lead + `abuse-detection-engineer` | <…> |
| Account-takeover / coordinated accounts | `security-engineering` | <…> |
| Ambiguous policy call | Policy lead (may trigger a policy revision) | <…> |

## 5. Reviewer wellness (a design constraint)
- **Exposure limits:** <max time / volume on the worst-content queues per shift>.
- **Rotation:** <how reviewers rotate off high-severity queues>.
- **Tooling:** <grayscale / blur / muting that reduces unnecessary exposure>.
- **Support:** <access to wellness resources>.

## 6. Measurement (program health)
| Metric | Current | Target | Owner |
|---|---|---|---|
| Prevalence (violating impressions / 10k) | <…> | <…> | <…> |
| Enforcement precision / recall | <…> | <…> | <…> |
| Time-to-action p90 (per tier) | <…> | <…> | <…> |
| Appeal-overturn rate | <…> | <…> | <…> |

> Definitions + formulas: [`../knowledge/trust-safety-metrics.md`](../knowledge/trust-safety-metrics.md).
> Validate any precision/recall figure with `applied-statistics` before reporting it.

## 7. On-call / incident
- **Surge handling:** <what happens when the queue floods>.
- **Contact:** <on-call rotation / pager>.
