# Do not put three-sigma limits on a low-volume form series

**Status:** Absolute rule — below the stated minimum, or on a series with a weekday signature, three-sigma limits manufacture signals that are not there, and a team that reacts to them is adding variation rather than removing it.
**Domain:** Forms engineering — measurement / the SPC seam
**Applies to:** `forms-engineering`

---

> [NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not established practice. We found no published work joining web-form telemetry to SPC/DMAIC (open-web search, 2026-08-17); the negative finding is bounded by that method and is not proof of universal absence.]

⛔ **That marker is why this rule ships before the method it constrains.** Charting a form metric is our idea. The hazard is the first thing anyone applying it will hit, and putting the hazard in a footnote after the technique is how a hazard gets skipped.

## Why this exists

Statistical process control assumes observations that are independent and identically distributed while the process is in control. A small-business form series violates both assumptions in ways that are structural rather than incidental:

- **Volume.** A form receiving a handful of submissions a week produces a series where a single unusual day moves the computed limits. The chart then describes the noise it was built from.
- **Weekday autocorrelation.** Business-hours forms have a weekday shape. Monday is not Saturday, and treating consecutive observations as exchangeable produces limits that are too tight and a chart that alarms on the calendar.
- **Campaign autocorrelation.** Traffic mix changes when a campaign starts. The population submitting the form changed; the process did not.

The consequence is specific: **false special-cause signals**. A team that investigates each one is doing the classic tampering error — responding to common-cause variation as though it had an assignable cause, and increasing variation in the process by doing so.

⛔ And the tool will not stop you. `lss_calc.py imr` accepts a series of two observations and will happily print control limits for it. **A gate that computes a number is not a gate that says the number means anything.**

## How to apply

1. **The floor is 20 individual observations.** Below it, do not chart. `form_metrics.py --emit-imr` refuses under that floor rather than emitting a series that will be charted anyway — the refusal is the enforcement, not the documentation.
2. **Check for a weekday signature before charting**, not after the first alarm. If the series has one, chart a weekly aggregate instead, or route the question to [`../../applied-statistics/CLAUDE.md`](../../applied-statistics/CLAUDE.md).
3. **Never widen the limits to make the alarms stop.** Alarms that are not real are evidence the series is wrong for the chart, not evidence the limits are too tight.
4. **Do not chart abandonment as a defect rate** without first fixing the defect definition — abandonment includes correct self-qualification, and counting it as a defect makes the metric worse the better the form gets. See [`../knowledge/form-telemetry-and-spc.md`](../knowledge/form-telemetry-and-spc.md) §4.
5. **The chart, the limits and the control plan belong to** [`../../process-improvement/agents/lean-six-sigma-blackbelt.md`](../../process-improvement/agents/lean-six-sigma-blackbelt.md). This plugin supplies the series and the hazard; it does not do the statistics.

## The anti-pattern

A weekly dashboard tile with a red band on a form that receives a handful of submissions a week, watched by someone who is expected to explain every excursion. That is a manufactured alarm loop, and the honest fix is to remove the chart, not to explain the alarms.

## Source

Assumption violations are standard SPC; the application to form telemetry is this plugin's synthesis and is marked as such above. The 20-observation floor is stated here, enforced in `form_metrics.py`, and asserted by the gate that runs it — one number, three surfaces, no drift. `lss_calc.py`'s two-observation acceptance was read from its source, 2026-08-17.
