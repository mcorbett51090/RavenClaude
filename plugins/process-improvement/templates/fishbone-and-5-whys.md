# Fishbone (Ishikawa) diagram + 5 Whys — {{Problem Statement}}

> Use this template in the DMAIC Analyze phase after the baseline is established. The fishbone organizes candidate causes; the 5 Whys drills each candidate to its root; the validation step confirms the root with data before the Improve phase begins.
>
> **Process:** {{process name}}
> **Effect (problem):** {{one-sentence quantified problem statement from the charter}}
> **Date:** {{YYYY-MM-DD}}
> **Author:** {{...}}

---

## Fishbone — 6M cause categories

> Fill in every category. The real cause is often in the category the team least expects. Get input from frontline workers — they see causes management does not.

### Machines / Technology

*What tools, systems, or automated processes could cause this effect?*

- {{Cause 1 — e.g., "Alert system doesn't flag SLA breach until 10 min after breach"}}
- {{Cause 2}}
- {{Cause 3}}

### Methods / Process

*What process steps, procedures, work instructions, or standard practices contribute?*

- {{Cause 1 — e.g., "Approval requires two sequential sign-offs with no parallel path"}}
- {{Cause 2}}
- {{Cause 3}}

### Materials / Information

*What inputs, data, reference information, or specifications are defective, late, or missing?*

- {{Cause 1 — e.g., "Claims arrive without supporting documentation in ~40% of cases"}}
- {{Cause 2}}
- {{Cause 3}}

### Measurement

*Could the problem be a measurement artifact — wrong definition, wrong collection point, non-reproducible measure?*

- {{Cause 1 — e.g., "Cycle-time clock starts at form submission, not at request receipt — understates true wait"}}
- {{Cause 2}}
- {{Cause 3}}

### Man / People

*What training gaps, staffing issues, incentive misalignments, or awareness failures contribute?*

- {{Cause 1 — e.g., "Team rotates monthly — no one owns an invoice end-to-end"}}
- {{Cause 2}}
- {{Cause 3}}

### Mother Nature / Environment

*What external, seasonal, regulatory, or environmental factors contribute?*

- {{Cause 1 — e.g., "Deployment failures spike on Fridays before the quarterly release freeze"}}
- {{Cause 2}}
- {{Cause 3}}

---

## Cause prioritization

After brainstorming, identify the **vital few** candidate causes — the ones most likely to explain the observed magnitude of the problem.

| Candidate cause | Category (6M) | Likelihood (H/M/L) | Impact if true (H/M/L) | Priority |
|---|---|---|---|---|
| {{...}} | {{...}} | {{H/M/L}} | {{H/M/L}} | {{1/2/3...}} |
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

_High-likelihood × high-impact causes get 5 Whys first. Don't spend a 5 Whys on a low-probability cause before exhausting the plausible ones._

---

## 5 Whys — Cause 1

**Candidate cause being drilled:** {{state the cause from the fishbone, from the priority table above}}

| Step | Why? | Answer |
|---|---|---|
| **Why 1** | Why does {{the effect stated above}} occur? | {{First-level cause}} |
| **Why 2** | Why does {{Why 1 answer}} occur? | {{Second-level cause}} |
| **Why 3** | Why does {{Why 2 answer}} occur? | {{Third-level cause}} |
| **Why 4** | Why does {{Why 3 answer}} occur? | {{Fourth-level cause}} |
| **Why 5** | Why does {{Why 4 answer}} occur? | {{Root cause — should be actionable and system/process-level}} |

**Root cause from this chain:** {{state the root — the Why 5 answer, or earlier if actionable root was found}}

**Actionable?** {{Yes — {{who can change it}} / No — add Why 6}}

**Prevents recurrence?** {{Yes / No — if no, go deeper}}

---

## 5 Whys — Cause 2

**Candidate cause being drilled:** {{...}}

| Step | Why? | Answer |
|---|---|---|
| **Why 1** | Why does {{effect}} occur? | {{...}} |
| **Why 2** | Why does {{Why 1}} occur? | {{...}} |
| **Why 3** | Why does {{Why 2}} occur? | {{...}} |
| **Why 4** | Why does {{Why 3}} occur? | {{...}} |
| **Why 5** | Why does {{Why 4}} occur? | {{...}} |

**Root cause:** {{...}}

---

## 5 Whys — Cause 3 (add as needed)

_Copy the table above for each additional high-priority candidate cause._

---

## Root cause summary

| Root cause | Source (fishbone → 5 Whys chain) | Validated with data? | Validation method |
|---|---|---|---|
| {{Root cause 1}} | {{Category → Why chain}} | {{Yes / No / Pending}} | {{Stratified comparison / hypothesis test / scatter plot / pilot}} |
| {{Root cause 2}} | {{...}} | {{...}} | {{...}} |
| {{Root cause 3}} | {{...}} | {{...}} | {{...}} |

---

## Validate with data — the mandatory step

> A root cause identified from a fishbone and 5 Whys is a **hypothesis**, not a finding. Proceed to Improve only after data confirms the cause.

For each root cause in the summary table above, state the validation plan:

### Root cause 1 validation

- **Hypothesis:** "When {{root cause}} is present / at high level, {{the effect metric}} is significantly {{higher/lower/more variable}} than when it is absent / at low level."
- **Data needed:** {{what data, from where, for what time period / sample}}
- **Validation method:** {{stratified comparison / scatter plot + correlation / pilot / hypothesis test}}
- **Inferential test (if needed):** {{name the test — t-test / chi-square / ANOVA / regression}} → **Route to `applied-statistics`** for execution and defense
- **Result:** {{fill in after data is collected — confirmed / not confirmed / inconclusive}}
- **Conclusion:** {{proceed to Improve / go back to fishbone / need more data}}

### Root cause 2 validation

- **Hypothesis:** {{...}}
- **Data needed:** {{...}}
- **Validation method:** {{...}}
- **Inferential test:** {{...}} → route to `applied-statistics` if needed
- **Result:** {{...}}
- **Conclusion:** {{...}}

---

## Analyze-phase gate

> Do not begin the Improve phase until this gate is answered **Yes**.

**Gate question:** "Do we have data showing the process output changes predictably when the root cause is present vs. absent, and is the change large enough to explain the observed problem?"

- [ ] At least one root cause confirmed with data
- [ ] Hypothesis tests (if used) completed and defended by `applied-statistics`
- [ ] The confirmed root cause explains the magnitude of the problem (not just a weak correlation)
- [ ] Sponsor / champion briefed on the confirmed root cause
- [ ] Improve-phase solution concept approved by sponsor

---

*Produced by the `process-improvement/skills/root-cause-analysis` skill. Connect to `fishbone-and-5-whys.md` in the `templates/` directory. Confirmed root causes feed the `fmea.md` and the Improve-phase solution design.*
