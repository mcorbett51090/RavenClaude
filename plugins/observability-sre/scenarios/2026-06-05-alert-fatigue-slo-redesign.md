---
scenario_id: 2026-06-05-alert-fatigue-slo-redesign
contributed_at: 2026-06-05
plugin: observability-sre
product: prometheus-alertmanager
product_version: "unknown"
scope: likely-general
tags: [alert-fatigue, slo, burn-rate, symptom-alerting, on-call, runbook]
confidence: high
reviewed: false
---

## Problem

An on-call rotation for a payments API was getting ~45 pages per 24h shift and acknowledging most of them within seconds without taking any action — the textbook alert-fatigue signature. The team's instinct was to "tune the thresholds" (raise the CPU alert from 80% to 90%, etc.). The real failure surfaced when a genuine customer-facing outage paged at 02:14 and sat un-actioned for 19 minutes because the engineer had muted the rotation channel two nights earlier to sleep.

## Constraints context

- Alerting stack was Prometheus + Alertmanager; ~120 alert rules, most authored cause-based (CPU, memory, disk, pod-restart-count, queue-depth) over two years with no deletion discipline.
- No SLOs existed — "availability" was an after-the-fact spreadsheet number, not an alerting input.
- Roughly 30 of the 120 rules accounted for ~90% of the page volume; none of those 30 had a runbook, and post-hoc analysis showed none had ever preceded a customer-visible incident.
- Leadership wanted the page count down but was nervous about "going blind" by deleting alerts.

## Attempts

- Tried: raising thresholds on the noisiest cause-based rules (CPU 80→90%, restart-count 3→5). Page volume dropped ~20% for two weeks, then crept back as load grew — and a real memory-leak incident was now *also* suppressed because its early CPU signal was under the new threshold. Threshold-tuning a cause-based alert just moves the noise floor; it doesn't fix the symptom-vs-cause error.
- Tried: routing the noisy rules to a "warnings" Slack channel instead of paging. Cut pages but created a 200-message/day channel nobody read — the noise moved, the actionability problem didn't.
- Tried (the move that worked): defined SLOs first (availability + p99 latency at the user boundary), then replaced the alerting model wholesale. Every cause-based pager was demoted to a dashboard or a ticket; the only things that *page* are **multi-window multi-burn-rate alerts on the two SLOs** (fast window 1h @ 14.4x burn AND-ed with a 5m confirmation; slow window 6h @ 6x) plus a short list of "the system is on fire and can't self-report" alerts (the SLI scrape itself failing). Each surviving page got a one-runbook-per-alert link before it was allowed to page.

## Resolution

**Delete the cause-based pages and alert on SLO burn rate — but define the SLO first, or you have nothing to burn against.** The order is the whole lesson: you cannot quiet alert fatigue by tuning thresholds on the wrong *kind* of alert. The sequence that worked:

1. **Define the user-facing SLIs and SLO targets** (availability + latency at the boundary the customer feels). This is the thing worth waking someone for.
2. **Demote every cause-based alert.** CPU/memory/disk/restart-count → dashboards (look when investigating) or tickets (act soon). They are diagnostic context, not pages. A cause only earns a page if it *reliably precedes* user pain AND there's no symptom signal available — rare.
3. **Page on multi-window multi-burn-rate.** Fast-burn (budget burning fast, short window) AND-ed with a confirmation window catches real fast outages and suppresses one-off blips; a slow-burn window catches the quiet steady bleed. This is the Google SRE Workbook pattern.
4. **Gate every surviving page on a runbook.** If you can't write "when this fires, do X," it isn't pageable — delete it.

Result over the next two rotations: pages dropped from ~45/shift to ~3/shift, every remaining page was acted on, and the next real fast-burn incident paged-and-was-acknowledged-and-acted in under 4 minutes because the channel was no longer muted-by-survival.

**Action for the next engineer:** when a team asks you to "tune the noisy alerts," do **not** start with thresholds. Audit which rules actually page, check how many have ever preceded a real incident (usually few), define the SLOs, then rebuild alerting as burn-rate-on-SLO + a tiny "can't self-report" set. The page count falls out of the redesign; you don't chase it directly.

Cross-reference: the canonical traversal is [`../knowledge/observability-sre-decision-trees.md`](../knowledge/observability-sre-decision-trees.md) `## Decision Tree: Should this be an alert (and how)?` and `## Decision Tree: On-call — page, ticket, or dashboard?`, plus the new [`alerting-threshold-strategy-decision-tree.md`](../knowledge/alerting-threshold-strategy-decision-tree.md). SLI/SLO design is `sre-reliability-engineer`'s lane; the instrumentation that produces the SLI is `observability-engineer`'s.

**Sources for the cited pattern:** Google SRE Workbook, "Alerting on SLOs" (multi-window multi-burn-rate) — https://sre.google/workbook/alerting-on-slos/ (retrieved 2026-06-05). The page-count figures are illustrative for this engagement; validate against the team's own Alertmanager history before a deliverable.
