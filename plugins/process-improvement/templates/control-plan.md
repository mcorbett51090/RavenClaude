# Control plan — {{Process / Project Name}}

> The control plan is the handoff document from the improvement team to the Process Owner. It is complete when every improved CTQ has a named owner, a control chart, and a reaction plan. An unsigned control plan is not a control plan — it is a suggestion.
>
> **Process:** {{name}}
> **Project:** {{DMAIC project name}}
> **Baseline sigma / capability (pre-improvement):** {{value, with convention}}
> **Post-improvement sigma / capability:** {{value, with convention — fill after pilot confirms gain}}
> **Date:** {{YYYY-MM-DD}}
> **Control plan author:** {{...}}

---

## Control plan table

> One row per CTQ that was improved. All columns are required — leave no cell blank.

| # | Process step | CTQ | Specification / target | Operational definition | Measurement method | Sample size | Sample frequency | Control chart type | UCL | LCL | Reaction plan (brief) | Owner |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | {{Step name}} | {{Metric name}} | {{Target ± tolerance or LSL/USL}} | {{Exactly how this metric is measured}} | {{System / field / formula}} | {{n = ...}} | {{Daily / weekly / per batch}} | {{I-MR / p / c / Xbar-R / u}} | {{Calculated value}} | {{Calculated value}} | {{See reaction plan §2}} | {{Named person}} |
| 2 | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{See reaction plan §2}} | {{...}} |
| 3 | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{See reaction plan §2}} | {{...}} |

> **Control chart type reminder:**
> - Continuous, individual measurements → **I-MR**
> - Continuous, subgroups n 2–8 → **Xbar-R** | n ≥ 9 → **Xbar-S**
> - Attribute defective (pass/fail) → **p chart** (variable n) or **np chart** (fixed n)
> - Attribute defects, fixed opportunity → **c chart** | variable opportunity → **u chart**

---

## Reaction plans

> For each CTQ row in the table above, provide the full reaction plan. A reaction plan is a decision tree, not a narrative. If it takes more than 1 minute to find the right action, it won't be used.

### Reaction plan — CTQ 1: {{CTQ name}}

**Signal that triggers this plan:** {{Rule 1 (1 point outside ±3σ) / Rule 4 (8 consecutive points one side) / etc. — state the specific rule}}

**Immediate response (within {{X hours}}):**
1. {{First action — e.g., "Flag the affected units / outputs from this period for review"}}
2. {{Second action — e.g., "Notify {{owner}} by {{channel}}"}}
3. {{Continue production? Yes / No / Conditional — state the condition}}

**Investigation checklist (first 3–5 causes to check, in order of frequency):**
1. {{Most common cause — e.g., "Check if input data arrived late from {{supplier}}"}}
2. {{Second most common cause}}
3. {{Third most common cause}}
4. {{Fourth — optional}}
5. {{Fifth — optional}}

**Escalation path:** If first responder cannot resolve within {{X hours}} → escalate to {{name / role}}.

**Containment / rollback:** {{If the process has degraded, what protects the customer while root cause is addressed — e.g., "Manual review of all outputs until control chart returns to stable"}}

**Resolution criteria:** {{Process is stable when — e.g., "5 consecutive points within ±1σ of the center line with no rule violations"}}

---

### Reaction plan — CTQ 2: {{CTQ name}}

**Signal:** {{...}}

**Immediate response:**
1. {{...}}
2. {{...}}

**Investigation checklist:**
1. {{...}}
2. {{...}}
3. {{...}}

**Escalation:** {{...}}

**Containment:** {{...}}

**Resolution criteria:** {{...}}

---

## Standard work

> Standard work is the current best-known method for the improved process steps. It must be at the point of use — not in a SharePoint folder no one opens.

### Standard work — {{Improved step name}}

**Step sequence:**

| # | Action | Expected time | Quality check |
|---|---|---|---|
| 1 | {{Verb + object — e.g., "Verify all required fields in incoming requisition against the checklist"}} | {{X min}} | {{What done correctly looks like}} |
| 2 | {{...}} | {{...}} | {{...}} |
| 3 | {{...}} | {{...}} | {{...}} |
| 4 | {{...}} | {{...}} | {{...}} |

**Common errors and how to recognize them:**
- {{Error 1 — e.g., "Missing salary band — visible as blank field in HRIS; do not route until filled"}}
- {{Error 2}}

**Where this standard work lives:** {{Pinned in {{workflow tool}}; linked in {{template}}; printed at {{location}}}}

**Standard work owner:** {{Named person responsible for keeping this current}}

---

## Poka-yoke (mistake-proofing)

> For each high-severity failure mode (from FMEA) or recurring NVA/rework loop, state the mistake-proofing countermeasure.

| Failure mode | Poka-yoke type | Description | Status |
|---|---|---|---|
| {{e.g., "Invoice issued with missing GL code"}} | Prevention | {{Required GL code field in billing system — cannot submit without it}} | {{Implemented / Planned by {{date}}}} |
| {{e.g., "Deployment to production without smoke test"}} | Detection — immediate | {{Automated smoke-test gate; pipeline blocks promotion if test fails}} | {{...}} |
| {{...}} | {{Prevention / Detection-immediate / Detection-downstream}} | {{...}} | {{...}} |

---

## SPC monitoring setup

| CTQ | Control chart type | Ruleset applied | Data source | Collection owner | Plot / review frequency | Alert destination |
|---|---|---|---|---|---|---|
| {{...}} | {{I-MR / p / c / u / Xbar-R}} | {{Western Electric Rules 1–4 / Nelson Rules 1–8}} | {{System + field}} | {{Name}} | {{Daily / Weekly / Per batch}} | {{Slack channel / email / dashboard}} |
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

**Control limit recalculation trigger:** Recalculate UCL/LCL after any process change, or when ≥ 20 new post-change data points are available. Do not carry pre-improvement control limits into the Control phase monitoring.

---

## Process Owner handoff

**Process Owner:** {{Named person who accepts ongoing ownership of this process}}

**Handoff checklist:**

- [ ] Process Owner has reviewed the control plan table and reaction plans
- [ ] Process Owner understands how to read the control charts and apply the ruleset
- [ ] Standard work is accessible at the point of use and Process Owner knows where it is
- [ ] SPC alerts are routed to the Process Owner (or their designee)
- [ ] Process Owner has been briefed on the FMEA high-RPN items and the poka-yokes in place
- [ ] Escalation path in each reaction plan has named alternates the Process Owner has confirmed
- [ ] Control-phase tollgate completed with sponsor; financial benefit validated

**Process Owner sign-off:**

_By signing below, the Process Owner confirms they accept ongoing responsibility for this process and commit to executing the control plan._

**Process Owner:** _____________________________________________ **Date:** _____________

**Project Lead:** ________________________________________________ **Date:** _____________

**Sponsor:** _____________________________________________________ **Date:** _____________

---

## Control-phase tollgate summary

| Question | Evidence |
|---|---|
| Is the gain real and sustained? | {{Post-improvement control chart — stable at new level, ≥ 20 points}} |
| Is the gain meaningful vs. baseline? | {{Before: {{metric}} = {{value}}. After: {{metric}} = {{value}}. Improvement: {{Δ and %}}}} |
| Post-improvement capability? | {{Cpk / Ppk = {{value}}; verdict: {{incapable / marginal / capable / highly capable}}}} |
| Control plan complete? | {{All CTQs covered; all rows have named owners}} |
| Standard work in place? | {{Location: {{...}}; Owner: {{...}}}} |
| Financial benefit validated? | {{Amount: {{$X}}; validated by: {{name}} on {{date}}}} |

---

*Produced by the `process-improvement/skills/control-plan-and-sustain` skill. The control plan table, reaction plans, and standard work must all be complete before the Process Owner sign-off. An unsigned control plan is not a handoff.*
