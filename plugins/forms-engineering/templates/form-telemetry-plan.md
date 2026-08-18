# Form telemetry plan — `<form name>`

**Owner:** `<named person>` · **Date:** `<YYYY-MM-DD>`

Produced by [`../skills/form-telemetry-and-control/SKILL.md`](../skills/form-telemetry-and-control/SKILL.md). Fill it **before** instrumenting; a denominator chosen after the fact is not recoverable.

> [NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not established practice. We found no published work joining web-form telemetry to SPC/DMAIC (open-web search, 2026-08-17); the negative finding is bounded by that method and is not proof of universal absence.]

⛔ Section 5 of this template hands a series to statistical process control. That join is **ours**, not received practice. Keep the marker attached to anything derived from section 5.

---

## 1. The denominator

| | |
| --- | --- |
| **Chosen denominator** | `<page views / form starts / eligible sessions>` |
| **Written definition** | `<in words a second analyst would implement identically>` |
| **Why not the other two** | |
| **Where it is printed** | next to every figure, not in a footnote |

## 2. Events

| Event | Fires when | What it does NOT mean | Parameters | Registered as a dimension? |
| --- | --- | --- | --- | --- |
| view | | | | |
| start | first interaction with a field | that the form was seen | | |
| field first-interaction | | | | |
| validation error | | that a defect occurred | | |
| submit attempt | | server acceptance | | |
| server acceptance | | | | |

## 3. Defect definitions

| Class | Counts as a defect when | Does **not** count | Owner |
| --- | --- | --- | --- |
| Validation | | a user mistyping their own data | |
| Delivery | | | |
| Triage | | | |

⛔ **Abandonment is not automatically a defect.** Someone who discovers on the form that they are in the wrong place and leaves is a success.

## 4. Per-field data

| Field | Error rate | Last-touch drop-off (PROXY) |
| --- | --- | --- |
| | | |

⛔ Last-touch drop-off is a **hypothesis generator**, not a diagnosis: the last field touched is not the field that caused the exit, and the proxy has not been validated `[unverified — no validation study located, open-web search 2026-08-17]`. Keep this caveat attached wherever the column travels.

## 5. The control seam

| | |
| --- | --- |
| **Series charted** | `<one observation per what?>` |
| **n available** | `<count>` |
| **Floor** | **20 individual observations** — below it, do not chart |
| **Weekday signature checked?** | `<yes/no; if yes, aggregate weekly instead>` |
| **Who owns the chart** | [`../../process-improvement/agents/lean-six-sigma-blackbelt.md`](../../process-improvement/agents/lean-six-sigma-blackbelt.md) |

```sh
python3 plugins/process-improvement/scripts/lss_calc.py imr \
  --values "$(python3 plugins/forms-engineering/scripts/form_metrics.py --emit-imr <sessions.csv>)"
```

⛔ Command substitution, not a pipe: `lss_calc.py imr` requires `--values` and reads no stdin.

Any inferential question — "is this difference real?", a confidence interval, a designed experiment — routes to [`../../applied-statistics/CLAUDE.md`](../../applied-statistics/CLAUDE.md).

## 6. What would change our mind

| Expected improvement | The observation that would falsify it |
| --- | --- |
| | |

A plan whose every possible outcome is consistent with success is not a plan.
