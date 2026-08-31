# Form telemetry, and the seam to statistical process control

**Retrieved / verified:** 2026-08-17. This file is the plugin's fact bank for form measurement. The skills reference it; they do not restate it.

> [NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not established practice. We found no published work joining web-form telemetry to SPC/DMAIC (open-web search, 2026-08-17); the negative finding is bounded by that method and is not proof of universal absence.]

Read that marker before anything below. Every metric definition here is ordinary web analytics. The **join** — treating a form as an instrumented process whose completion series is charted and whose failures are classified as common- or special-cause — is ours. Nothing on this page is a citation to a published method for that join, because we did not find one.

---

## 1. Name the denominator before you quote a rate

A form "completion rate" is meaningless without its denominator, and the three plausible denominators differ by more than most of the improvements anyone argues about.

| Denominator | What it counts | When it is the right one |
| --- | --- | --- |
| **Page views** | Everyone who loaded the page carrying the form | Almost never. It measures the page's traffic mix, not the form. |
| **Form starts** | Sessions that produced a **first interaction** with a form field | The default. It isolates people who tried. |
| **Eligible sessions** | Sessions that reached the form with the intent it serves | Only when you can define eligibility without circularity. |

**GA4's `form_start` fires on the first interaction with a form, not on the form becoming visible** (enhanced measurement, retrieved 2026-08-17 — https://support.google.com/analytics/answer/9216061). That is a _good_ default and a _bad_ surprise: a team reading "starts" as "saw the form" will over-report completion and then not understand why the fix did nothing.

Two more properties of the platform default worth knowing before you design around it:

- `form_submit` fires on submission, not on server-side acceptance. A form that submits and then 500s counts as a submit.
- `form_id`, `form_name` and `form_destination` arrive as event parameters and are **not** dimensions until you register custom dimensions for them. Until you do, every form on the property is one undifferentiated series (retrieved 2026-08-17 — https://support.google.com/analytics/answer/9216061).

**Completion and abandonment are exact complements** on a single denominator: `abandonment = 1 − completion`. Quoting both from different denominators is the most common way a form dashboard becomes internally inconsistent. See [`../best-practices/name-the-denominator-before-you-quote-a-completion-rate.md`](../best-practices/name-the-denominator-before-you-quote-a-completion-rate.md).

---

## 2. Time-to-complete is the disambiguator

Completion rate alone cannot tell you whether a form is easy or whether the hard part happens off-form. Time-to-complete for **completers only** separates:

- **Short and high-completion** — the form is doing its job.
- **Long and high-completion** — people are pushing through friction. This is where a field that requires a lookup ("your account number", "your policy reference") hides.
- **Short and low-completion** — people bounce at first contact. Usually a mismatch between the promise and the ask.
- **Long and low-completion** — the worst case, and the one where per-field data is worth collecting.

Report it as a **median plus a spread**, never a mean alone. Session-duration distributions are right-skewed by abandoned tabs, and a mean is a claim about the tail.

---

## 3. Per-field drop-off, and why it is a proxy

The standard per-field metric is "the last field the user interacted with before leaving". Every vendor computes it; **nobody has validated it as a measure of the field that caused the abandonment** `[unverified — no validation study located; open-web search 2026-08-17]`.

The reason to distrust it is structural, not statistical:

- A user who reads the **next** field's label, decides they cannot answer it, and leaves is recorded against the **previous** field.
- A user who leaves because of something off-form — a price, a phone call, a second thought — is recorded against wherever they happened to stop.
- A field that is simply last on the form absorbs every reason for leaving at the end.

So per-field drop-off is a **hypothesis generator**, not a diagnosis. It tells you where to look and what to ask about in a usability session. `form_metrics.py` prints the proxy caveat in its own output header for exactly this reason — the number should never travel without it.

---

## 4. What "defect" means for a form

Statistical process control needs an operational definition of a defect before it needs a chart. For a form, the defect is **not** an abandonment. Abandonment is often a correct outcome: a person who discovers on the form that they are in the wrong place and leaves is a success for everyone.

Three defect classes are worth counting separately, because each has a different owner:

| Defect class | Operational definition | Owner |
| --- | --- | --- |
| **Validation defect** | A submission attempt rejected by validation that a correctly-formed answer should have passed | The form's design |
| **Delivery defect** | A submission the server accepted that never reached the process behind it | The submission path |
| **Triage defect** | A submission delivered to the wrong queue, or with a field the queue needed left blank | The intake taxonomy |

A rate quoted without naming which of the three it counts is the same error as a rate quoted without a denominator.

---

## 5. The hand-off to SPC — and the hazard that goes first

The seam: `form_metrics.py --emit-imr` emits an **individuals series** (one observation per completed submission) on stdout as bare numbers, and [`../../process-improvement/scripts/lss_calc.py`](../../process-improvement/scripts/lss_calc.py) computes the I-MR limits from it. Two scripts, one seam, no duplicated statistics — the control-chart arithmetic is not reimplemented here.

⛔ **The hazard ships before the method, not in a footnote.** Small-business form series are low-volume and autocorrelated by weekday and by campaign. Naive three-sigma limits on such a series manufacture false special-cause signals, and a team that reacts to them is tampering — adding variation by responding to noise. The minimum this plugin will chart is **20 individual observations**, and `--emit-imr` refuses below that floor rather than emitting a series that will be charted anyway. See [`../best-practices/do-not-put-three-sigma-limits-on-a-low-volume-form-series.md`](../best-practices/do-not-put-three-sigma-limits-on-a-low-volume-form-series.md).

⛔ **Autocorrelation is not fixed by more data.** A weekday effect is a real, repeating structure; charting it as if the observations were independent produces limits that are too tight and a chart that alarms every Monday. If the series has a weekday signature, chart a **weekly aggregate**, or route the question to [`../../applied-statistics/CLAUDE.md`](../../applied-statistics/CLAUDE.md). Do not widen the limits to make the alarms stop.

**Where the seam ends.** Control limits, chart selection, common- vs special-cause response and the control plan all belong to [`../../process-improvement/agents/lean-six-sigma-blackbelt.md`](../../process-improvement/agents/lean-six-sigma-blackbelt.md). Any inferential question — "is this difference real?", a capability confidence interval, a designed experiment — routes to [`../../applied-statistics/CLAUDE.md`](../../applied-statistics/CLAUDE.md). This plugin measures and hands over; it does not infer.

---

## 6. What this file does not own

- **Conversion diagnosis** — the funnel, the field-count evidence and the counter-evidence to "fewer fields always converts better" live in [`../../web-design/skills/conversion-design/SKILL.md`](../../web-design/skills/conversion-design/SKILL.md) §3. One source, one home.
- **Survey instrument design** — a survey is a different object from a transactional form; route to [`../../ux-research/CLAUDE.md`](../../ux-research/CLAUDE.md).
- **Chart construction and control-plan design** — `process-improvement`, as above.
