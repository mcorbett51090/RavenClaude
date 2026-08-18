---
name: form-telemetry-and-control
description: "Define a form's measurement contract before instrumenting it: which events, which denominator, what counts as a defect, how per-field drop-off lies, and how to hand an individuals series to statistical process control without manufacturing false signals on a low-volume form."
---

# Skill: form-telemetry-and-control

> **Invoked by:** `process-improvement/process-analyst` (when the process being baselined starts at a web form), `web-design/ux-designer`, and `marketing-operations` work that needs a form number to mean something.
>
> **When to invoke:** before instrumenting a form; when two dashboards disagree about the same form's completion rate; when someone proposes charting a form metric; when a form "improved" and nobody can say against what.
>
> **Output:** a populated [`../../templates/form-telemetry-plan.md`](../../templates/form-telemetry-plan.md), and — where the volume supports it — an individuals series handed to `process-improvement` for charting.

> [NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not established practice. We found no published work joining web-form telemetry to SPC/DMAIC (open-web search, 2026-08-17); the negative finding is bounded by that method and is not proof of universal absence.]

⛔ That marker is load-bearing, not decorative. The metric definitions in this skill are ordinary web analytics. **The join to statistical process control is ours**, and a reader is entitled to know that before they present a control chart of a form metric to a stakeholder as standard practice.

## The discipline in one sentence

A form number without a **named denominator** and a **named defect definition** is a decoration.

## Not this skill

| You are actually doing | Go here |
| --- | --- |
| Building the chart, choosing the chart type, setting control limits, writing the control plan | [`../../../process-improvement/agents/lean-six-sigma-blackbelt.md`](../../../process-improvement/agents/lean-six-sigma-blackbelt.md) and [`../../../process-improvement/scripts/lss_calc.py`](../../../process-improvement/scripts/lss_calc.py) |
| Any inferential question — "is this difference real?", a confidence interval, a designed experiment | [`../../../applied-statistics/CLAUDE.md`](../../../applied-statistics/CLAUDE.md) |
| Funnel and conversion diagnosis, field-count evidence, trust signals | [`../../../web-design/skills/conversion-design/SKILL.md`](../../../web-design/skills/conversion-design/SKILL.md) |
| Attribution, channel ROI, campaign measurement | [`../../../marketing-operations/CLAUDE.md`](../../../marketing-operations/CLAUDE.md) |
| Survey instrument design | [`../../../ux-research/CLAUDE.md`](../../../ux-research/CLAUDE.md) |
| Warehouse modelling of the event stream | [`../../../data-platform/skills/stack-selection/SKILL.md`](../../../data-platform/skills/stack-selection/SKILL.md) |

## Step 1 — Fix the denominator, in writing, first

Three plausible denominators; they do not agree; the choice is not recoverable after the fact. The definitions and the platform defaults are in [`../../knowledge/form-telemetry-and-spc.md`](../../knowledge/form-telemetry-and-spc.md) §1.

The default is **form starts**, defined as *first interaction with a field*. Write the definition into the plan in words a second analyst would implement identically. Then state completion and abandonment as **exact complements on that one denominator**, and never quote them from different ones. See [`../../best-practices/name-the-denominator-before-you-quote-a-completion-rate.md`](../../best-practices/name-the-denominator-before-you-quote-a-completion-rate.md).

## Step 2 — Enumerate the events, and what each one does not mean

At minimum: view, start, per-field first-interaction, validation-error, submit attempt, server acceptance.

The two gaps that cause most confusion:

- **A submit event is not an acceptance.** Instrument the server's acceptance separately or you cannot distinguish "the form worked" from "the form posted".
- **A validation error is not a defect** until you say which errors count. A user mistyping their own email is not a form defect; a valid address rejected by an over-tight pattern is.

Identify each form distinctly. On a platform where the form identifier arrives as an event parameter rather than a dimension, that registration is a setup step — until it is done, every form on the property is one undifferentiated series.

## Step 3 — Define the defect

Three classes, three owners — validation, delivery, triage. The operational definitions are in [`../../knowledge/form-telemetry-and-spc.md`](../../knowledge/form-telemetry-and-spc.md) §4. Pick the ones you will count and write the definition down before the first observation, not after the first argument.

⛔ **Abandonment is not automatically a defect.** Someone who discovers on the form that they are in the wrong place and leaves is a success. Counting them as defects makes the metric worse the better the form gets at qualifying people.

## Step 4 — Collect per-field data, and label it as a proxy wherever it goes

Per-field error rate is a real measurement. Per-field **drop-off** is a proxy for "the field that caused the exit" and has not, as far as we can establish, been validated as such — see [`../../knowledge/form-telemetry-and-spc.md`](../../knowledge/form-telemetry-and-spc.md) §3.

`../../scripts/form_metrics.py` prints that caveat in its own output header. Keep it attached when the number moves into a slide.

## Step 5 — Compute the numbers with the script, not by hand

```sh
python3 plugins/forms-engineering/scripts/form_metrics.py path/to/sessions.csv
```

Emits starts, submits, completion and abandonment **with the denominator printed**, time-to-complete for completers, per-field error rate, and per-field last-touch drop-off carrying its proxy label. The synthesis marker goes to **stderr in every mode**, so it reaches a human without polluting a pipe.

## Step 6 — Hand the individuals series over. Do not chart it here.

```sh
python3 plugins/process-improvement/scripts/lss_calc.py imr \
  --values "$(python3 plugins/forms-engineering/scripts/form_metrics.py --emit-imr path/to/sessions.csv)"
```

`--emit-imr` writes **numbers only** to stdout — no header, no banner — precisely so that substitution works. The arithmetic belongs to `lss_calc.py`, which is verified and gated; nothing statistical is reimplemented here.

⛔ **Command substitution, not a pipe.** `lss_calc.py imr` requires `--values` and reads no stdin; a piped form discards the left side and exits non-zero.

⛔ **Below 20 individual observations, do not chart it at all.** `--emit-imr` refuses under that floor. Form series are low-volume and autocorrelated by weekday and campaign; naive three-sigma limits on such a series manufacture false special-cause signals, and reacting to them is tampering. The rule and its reasoning: [`../../best-practices/do-not-put-three-sigma-limits-on-a-low-volume-form-series.md`](../../best-practices/do-not-put-three-sigma-limits-on-a-low-volume-form-series.md).

## Step 7 — Say what would change your mind

Write, in the plan, the observation that would falsify the improvement you expect. A measurement plan whose every possible outcome is consistent with success is not a measurement plan.
