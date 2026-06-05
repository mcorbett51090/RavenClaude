# Cpk and Ppk Answer Different Questions — Never Conflate Them

**Status:** Absolute rule
**Domain:** Process Improvement — capability analysis
**Applies to:** `process-improvement`

---

## Why this exists

Cpk and Ppk are capability indices calculated from the same data but using different estimates of process spread. **Cpk uses the within-subgroup standard deviation** (short-term variation, excluding between-subgroup shifts); **Ppk uses the overall standard deviation** (long-term variation, including all sources of shift and drift). A process with a Cpk of 1.8 and a Ppk of 0.9 is meeting spec in the short term but drifting out of spec over time — the gap is a signal, not a coincidence. Conflating the two (reporting Cpk when Ppk is required, or vice versa) is an explicit anti-pattern in `CLAUDE.md` §4 and can lead to a process being declared capable when it is not.

## How to apply

**Decision rule:**

| Question | Index to use |
|---|---|
| "Is the process inherently capable — given no shifts or drifts?" | **Cpk** (short-term, within-subgroup σ̂ from the R-bar or S-bar chart) |
| "Is the process actually meeting spec over the real operating period, including all shifts and drifts?" | **Ppk** (long-term, overall σ from all data pooled) |
| "Is the process centered and symmetric?" | **Cp** (Cpk without the centering correction) vs **Pp** |

**Reporting template:**
```
Capability study period: [start] – [end]
Subgroup structure: [n=X per subgroup, every Y hours/units]
Cpk: [value] (σ̂ = within-subgroup, via [R-bar / S-bar method])
Ppk: [value] (σ = overall, all data pooled)
Gap (Cpk − Ppk): [value] — [interpretation: large gap = significant process shift/drift]
USL: [value], LSL: [value] (if one-sided, state direction)
```

**Interpreting the gap:**
- Cpk ≈ Ppk (gap < 0.1): the process is stable; short-term and long-term behavior are the same.
- Cpk >> Ppk (large positive gap): the process is capable in the short term but shifts or drifts; investigate sources of between-subgroup variation.
- Cpk < 1.33 OR Ppk < 1.33: the process is not capable at the general industry baseline `[unverified — training knowledge; confirm threshold against the client's specification and quality system before quoting]`.

**Do:**
- Report both Cpk and Ppk in every capability study — they tell a complete story together.
- State which estimate of σ was used (R-bar, S-bar, or overall) and the subgroup structure.
- Route the confidence-interval calculation on Cpk/Ppk to `applied-statistics`.

**Don't:**
- Report only Cpk to a customer when the process has known between-subgroup shifts (that's selecting the favorable number).
- Use Ppk for a study period shorter than one full production cycle (it won't capture the long-term shifts it's designed to surface).
- Use either index when the control chart shows the process is not in statistical control — capability is meaningless on an unstable process.

## Edge cases / when the rule does NOT apply

- **Attribute data** (defect counts, pass/fail): Cpk/Ppk don't apply. Use sigma level / DPMO or a p-chart / u-chart to assess capability.
- **Non-normal data with significant skew**: standard Cpk/Ppk formulas assume normality. Route to `applied-statistics` for a transformation or a non-normal capability analysis (Minitab Johnson/Box-Cox or percentile-based Ppk).

## See also

- [`../agents/lean-six-sigma-blackbelt.md`](../agents/lean-six-sigma-blackbelt.md) — interprets the capability study and routes the inference
- [`./separate-common-cause-from-special-cause.md`](./separate-common-cause-from-special-cause.md) — the prerequisite: establish control before computing capability

## Provenance

Codifies the explicit anti-pattern "Confusing Cpk with Ppk and reporting one as the other" from `CLAUDE.md` §4. Cpk/Ppk definitions: AIAG Statistical Process Control Manual (2nd edition); Montgomery, "Introduction to Statistical Quality Control." _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
