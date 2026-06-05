# Project-management decision trees

> **Last reviewed:** 2026-06-01. Canonical `## Decision Tree:` sections for the `project-management` plugin, in the marketplace format ([`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../docs/best-practices/decision-trees-in-knowledge-files.md)): an observable **When this applies**, a **Last verified** date, a Mermaid flowchart, per-leaf rationale, and a tradeoffs table.
>
> **Decision-tree traversal (priors).** When the situation matches a tree's entry condition, traverse the graph top-to-bottom **before** picking a delivery approach — do NOT pattern-match on "we're an agile shop" or "the client wants a Gantt." The first branch that resolves cleanly is the leaf to apply.

---

## Decision Tree: Delivery approach — predictive, agile, or hybrid?

**When this applies:** a project is starting (or being reset) and the question is _how to run it_ — a predictive plan-of-record (delivery-lead), an empirical sprint/flow cadence (scrum-master), or a hybrid that does both at different altitudes. Observable inputs: how stable the **requirements** are, how fixed the **scope/date/budget** are by contract or mandate, whether the work is **discovery-heavy** vs well-understood, and whether a **governance/stage-gate** obligation exists. The failure this prevents: forcing a Gantt onto genuinely exploratory work, or running pure open-ended sprints under a fixed-scope-fixed-date contract.

**Last verified:** 2026-06-01 against PMBOK 7 (development-approach + tailoring) and the Scrum Guide as domain-standard framings. Method definitions are standard framings, not engagement advice — confirm against the engagement's actual contract/governance before committing.

```mermaid
flowchart TD
    START[New or reset project — how to run it?] --> REQ{Are requirements stable and well-understood up front?}
    REQ -->|YES — stable, low discovery| GOV{Fixed scope+date+budget OR a stage-gate/governance mandate?}
    REQ -->|NO — evolving / discovery-heavy| FIX{Is scope OR date contractually fixed?}
    GOV -->|YES| PRED["PREDICTIVE (delivery-lead)<br/>charter + WBS + baseline + change control + earned value"]
    GOV -->|NO — could flex| HYB1["HYBRID — predictive frame, agile delivery<br/>baseline the milestones, run the build in sprints"]
    FIX -->|NO — scope and date can flex| AGILE["AGILE (scrum-master)<br/>backlog + sprints/flow + velocity + empirical replanning"]
    FIX -->|YES — fixed wrapper, uncertain interior| HYB2["HYBRID<br/>fixed outer baseline + change control,<br/>agile increments inside; reconcile each cycle"]
    AGILE --> FLOW{Cadenced deliverables, or continuous interrupt-driven work?}
    FLOW -->|Cadenced + planning rhythm| SCRUM["Scrum — sprint goal + ceremonies + velocity"]
    FLOW -->|Continuous / variable priority| KANBAN["Kanban — WIP limits + flow metrics, no sprint"]
```

**Rationale per leaf:**

- _PREDICTIVE_ — stable requirements **and** a fixed scope/date/budget or a stage-gate mandate is the predictive sweet spot: a baseline you can measure change and earned value against. Owned by `delivery-lead`.
- _HYBRID (predictive frame, agile delivery)_ — stable-enough requirements but flexibility on the how: baseline the milestones for governance, but build in sprints so the team keeps empirical feedback. The most common real-world shape.
- _AGILE_ — evolving/discovery-heavy requirements with scope/date that can flex: commit to a backlog and replan empirically each cycle. Owned by `scrum-master`. Forcing a frozen baseline here manufactures false precision.
- _HYBRID (fixed wrapper, uncertain interior)_ — the hard case: a contract fixes scope or date but the interior is genuinely uncertain. Hold a predictive outer baseline + change control, run agile increments inside, and **reconcile every cycle** (burn-up vs baseline) so the fixed commitment and the empirical reality stay honest. Both leads collaborate.
- _SCRUM vs KANBAN_ — within agile, the work shape decides: cadenced deliverables with a planning rhythm → Scrum (sprint goal + ceremonies); continuous, interrupt-driven, variable-priority work (support, ops) → Kanban with WIP limits and flow metrics. Don't impose sprints on a queue.

**Tradeoffs summary:**

| Approach | Best when | Plan artifact | Change handling | Primary owner |
|---|---|---|---|---|
| Predictive | stable reqs + fixed scope/date or stage-gate | charter + WBS + baseline | integrated change control vs baseline | `delivery-lead` |
| Hybrid (predictive frame) | stable reqs, flexible delivery | milestone baseline + sprint plan | change control at milestone level | `delivery-lead` + `scrum-master` |
| Hybrid (fixed wrapper) | fixed contract, uncertain interior | outer baseline + inner backlog | reconcile burn-up vs baseline each cycle | both leads |
| Agile — Scrum | evolving reqs, cadenced deliverables | product + sprint backlog | re-prioritize each sprint | `scrum-master` |
| Agile — Kanban | continuous, interrupt-driven flow | flow policy + WIP limits | continuous re-prioritization | `scrum-master` |

Whichever leaf wins, RAID discipline applies throughout (`risk-and-raid-analyst`) and the cadence/format of stakeholder reporting follows from it (`stakeholder-comms-lead`). The lightweight RAID/status hygiene for the repo itself stays with [`../../ravenclaude-core/agents/project-manager.md`](../../ravenclaude-core/agents/project-manager.md); this tree picks the *delivery approach* the specialists then run.

## See also

- [`../best-practices/`](../best-practices/) — the named rules the leaves implement (single-owner, baseline-before-change, scored-RAID, narrative-first reporting).
- [`../../ravenclaude-core/agents/project-manager.md`](../../ravenclaude-core/agents/project-manager.md) — the domain-neutral PM hygiene agent this plugin extends.
- [`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../docs/best-practices/decision-trees-in-knowledge-files.md) — the format this tree follows.

## Refresh triggers

- A change in PMBOK / Scrum Guide guidance these framings cite → re-verify + re-date.
- A new specialist agent or skill that adds a delivery sub-method (would add a leaf).
- `Last verified:` older than 90 days (the marketplace anti-staleness backstop).

---

## Decision Tree: Risk response — which response strategy to choose?

**When this applies:** A risk has been scored on the register and the team must choose a response strategy. Observable trigger: a risk entry in the register with a probability × impact score and no response assigned; or the team debating whether to "just accept" a high-scored risk.

**Last verified:** 2026-06-05 against PMBOK 6th edition §11.5 (risk response planning) and the `risk-and-raid-analyst` agent constitution.

```mermaid
flowchart TD
    START[Risk scored and entered in register] --> Q1{Is the risk probability AND impact both low?}
    Q1 -->|YES — low P and low I| ACCEPT[Accept — document, monitor; no active action needed now]
    Q1 -->|NO — either P or I is medium/high| Q2{Can the root cause be eliminated entirely?}
    Q2 -->|YES — change the approach to remove the cause| AVOID[Avoid — change plan, scope, or approach to remove the risk]
    Q2 -->|NO — cannot fully eliminate| Q3{Can the financial impact be transferred to a third party?}
    Q3 -->|YES — via contract, insurance, or warranty| TRANSFER[Transfer — contract clause, insurance, SLA with supplier]
    Q3 -->|NO — must carry the risk| Q4{Can we reduce probability OR impact to an acceptable level with specific actions?}
    Q4 -->|YES| MITIGATE[Mitigate — actions to reduce P or I, owner and date required]
    Q4 -->|NO — cannot reduce meaningfully| ACCEPT2[Accept actively — contingency reserve; define trigger for contingency plan]
```

**Rationale per leaf:**
- *Accept (passive)* — low P + low I risks cost more to manage than the expected loss; monitor only.
- *Avoid* — eliminates the risk by changing the approach; highest-value response when available but requires a plan change.
- *Transfer* — shifts the financial impact; does not reduce probability; the risk still requires monitoring.
- *Mitigate* — reduces P or I to an acceptable band; the most common response for medium-high risks; requires a specific named action, not a platitude.
- *Accept (active)* — carries the risk with a contingency plan and a defined trigger; used when avoidance and mitigation are not cost-effective.

**Tradeoffs summary:**

| Response | Eliminates risk | Cost | Use when |
|---|---|---|---|
| Avoid | YES | Plan-change cost | The cause can be designed out |
| Transfer | NO (shifts financial) | Contract/insurance premium | Financial impact is transferable |
| Mitigate | NO (reduces) | Action cost | P or I can be reduced to acceptable |
| Accept (passive) | NO | Monitoring only | Low P and low I |
| Accept (active) | NO | Contingency reserve | High P or I but no better option |

---

## Decision Tree: Status RAG — which color is correct?

**When this applies:** Preparing a status report or steering pack and choosing the RAG (Red/Amber/Green) status for the project or a workstream. Observable trigger: a project manager asking "what color should this be?" — especially when there is pressure to show Green on a project with schedule or cost indicators in the amber range.

**Last verified:** 2026-06-05 against the `status-leads-with-narrative-and-matches-the-numbers` best-practice and house opinions §3-4 from `CLAUDE.md`.

```mermaid
flowchart TD
    START[Assign a RAG status] --> Q1{Does the project have an open P1 issue or an SPI or CPI below 0.8?}
    Q1 -->|YES| RED[RED — project is in distress. Escalation memo required.]
    Q1 -->|NO| Q2{Any of: SPI or CPI 0.8 to 0.95, a high-scored risk with no mitigation in place, a milestone at risk within the next two cycles?}
    Q2 -->|YES — one or more of these| AMBER[AMBER — project is under pressure. Narrative must state the specific cause and recovery plan.]
    Q2 -->|NO| Q3{Is the project tracking to scope, schedule, and cost baselines with no open high risks?}
    Q3 -->|YES| GREEN[GREEN — on track. Narrative confirms and notes any watches.]
    Q3 -->|NO — ambiguous signals| AMBER
```

**Rationale per leaf:**
- *RED* — an open P1 issue or EV indices below 0.8 mean the project cannot self-recover without intervention; the RAG must reflect this even if the sponsor will dislike it. A Green RAG on a Red project is a governance failure.
- *AMBER* — pressure exists but recovery is possible without sponsor intervention; the narrative must be specific (not "some slippage") and must include a recovery action with owner and date.
- *GREEN* — all indicators are on-track; the narrative confirms this and notes any developing watches (risks trending up) for early awareness.

**Tradeoffs summary:**

| RAG | SPI/CPI range | Open high risk | Action required |
|---|---|---|---|
| GREEN | ≥ 0.95 | Mitigated | Narrative confirmation + watches |
| AMBER | 0.80–0.95 | Present, being managed | Recovery plan with owner + date |
| RED | < 0.80 | P1 issue open | Escalation memo; sponsor decision required |

> **The RAG never contradicts the numbers.** A Green RAG with a CPI of 0.78 is a misreport, not an optimistic assessment (house opinion #4, anti-pattern §4 from `CLAUDE.md`).

---

## Decision Tree: Sprint scope injection — accept, defer, or cancel the sprint?

**When this applies:** Mid-sprint, a stakeholder or Product Owner wants to inject new scope. Observable trigger: a new story, bug, or requirement surfaces after the sprint planning is closed and the team has started work.

**Last verified:** 2026-06-05 against the Scrum Guide 2020 (sprint cancellation), the `scrum-master` agent constitution, and `scope-absorption-is-a-defect` best-practice.

```mermaid
flowchart TD
    START[New scope item arrives mid-sprint] --> Q1{Is this a production-down or critical-security incident?}
    Q1 -->|YES| INJECT[Inject immediately — remove equivalent capacity from the sprint backlog; record the trade-off visibly]
    Q1 -->|NO| Q2{Does accepting it require dropping more than 20% of the current sprint commitment?}
    Q2 -->|YES — major disruption| Q3{Is the sprint goal still achievable with the new scope included?}
    Q2 -->|NO — minor, fits within slack| SWAP[Swap: add new item, remove lowest-priority item of equal size; record in sprint log]
    Q3 -->|YES — new scope aligns with the goal| REPLAN[Re-plan the sprint with PO: adjust the backlog, document the trade-off]
    Q3 -->|NO — goal is void| CANCEL[Cancel the sprint. Replanning session with PO. New sprint goal + new sprint plan.]
```

**Rationale per leaf:**
- *Inject* — production/security incidents override the sprint plan; equivalent capacity removal makes the trade-off visible instead of silent.
- *Swap* — minor injection that fits within the sprint's buffer; equal-size swap keeps capacity honest.
- *Re-plan* — major injection that changes the backlog significantly but doesn't void the sprint goal; the PO makes the trade-off explicit.
- *Cancel* — a sprint whose goal is rendered irrelevant by new scope should be cancelled (Scrum Guide); continuing a sprint toward an obsolete goal wastes the remaining cycles.

**Tradeoffs summary:**

| Situation | Action | Trade-off visible? | Sprint goal preserved? |
|---|---|---|---|
| Critical incident | Inject + remove equivalent | YES | Possibly not — document |
| Minor new scope | Swap equal size | YES | YES |
| Major new scope, goal intact | Re-plan with PO | YES | YES |
| Major new scope, goal voided | Cancel sprint | YES | NO — new goal needed |

---

## Decision Tree: Change request — approve, reject, or defer?

**When this applies:** A change request has been raised on a baselined predictive project (or at a milestone gate on a hybrid). The change control board or PM must disposition it. Observable trigger: a formal or informal request to alter scope, schedule, cost, or quality that has arrived after the baseline is approved.

**Last verified:** 2026-06-05 against PMBOK 6 §4.6 (Perform Integrated Change Control) and the `baseline-before-you-change-control` and `scope-absorption-is-a-defect` best-practices.

```mermaid
flowchart TD
    START[Change request received] --> Q1{Is the change within the PM authority level - cost and schedule impact below delegation threshold?}
    Q1 -->|YES - within PM authority| Q2{Is the change within approved scope and does not add net cost or delay?}
    Q2 -->|YES - clarification or defect fix| APPROVE_PM[PM approves - log in change register; no baseline update required]
    Q2 -->|NO - adds work or changes baseline| ASSESS[Impact assessment required - schedule and cost delta calculated]
    Q1 -->|NO - above PM authority| BOARD[Escalate to change control board or sponsor]
    ASSESS --> Q3{Does the project have contingency reserve that covers the cost and schedule impact?}
    Q3 -->|YES - within contingency| APPROVE_CONTINGENCY[Approve - draw from contingency; update baseline; log in register]
    Q3 -->|NO - exceeds contingency| Q4{Is the change a must-have requirement for project success or regulatory compliance?}
    Q4 -->|YES - non-negotiable| APPROVE_ADDL[Approve with additional budget or schedule request - escalate for funding]
    Q4 -->|NO - desirable but optional| Q5{Can the change be deferred to a later phase or release without impacting current scope?}
    Q5 -->|YES - can defer| DEFER[Defer to next phase - log in backlog for future consideration]
    Q5 -->|NO - cannot defer without blocking| REJECT[Reject - document rationale; re-scope or re-prioritize with sponsor]
```

**Rationale per leaf:**
- *PM approves* — minor clarifications and defect corrections within existing scope do not require a formal baseline change; log them for traceability.
- *Approve within contingency* — this is what contingency reserve exists for; draw on it deliberately with documentation, do not use it silently.
- *Approve with additional budget/schedule* — a must-have that exceeds contingency requires a conscious sponsor decision to expand the budget envelope; the PM cannot absorb it silently.
- *Defer* — a desirable but non-critical change is better captured for a future phase than absorbed into a running project with a fixed baseline.
- *Reject* — optional changes that cannot be deferred and would breach the budget or schedule without a proportionate benefit should be rejected formally and documented; an informal "no" is not a change decision.

**Tradeoffs summary:**

| Disposition | Baseline changes? | Contingency impact | Authority required | Use when |
|---|---|---|---|---|
| PM approves (minor) | NO | None | PM | Clarification or defect within scope |
| Approve within contingency | YES | Drawn | PM (if within threshold) | Valid change, reserve available |
| Approve with addl budget | YES | Exceeded | Sponsor / board | Non-negotiable change exceeding reserve |
| Defer | NO | None | PM + PO | Optional change, safe to move to next phase |
| Reject | NO | None | PM / board | Optional change with no deferral path |

---

## Decision Tree: Escalation threshold — resolve at team level or escalate?

**When this applies:** An issue has been raised in the project and the team must decide whether it can be resolved within the project team or whether it requires escalation to the PM, the sponsor, or the steering committee. Observable trigger: a blocker, a conflict, a resource constraint, or a risk event that the team cannot resolve with their existing authority and resources.

**Last verified:** 2026-06-05 against the `issue-triage-before-escalation` best-practice and the `stakeholder-comms-lead` agent constitution.

```mermaid
flowchart TD
    START[Issue identified] --> Q1{Can the issue be resolved within the project team with existing authority and resources?}
    Q1 -->|YES - within team authority| RESOLVE[Resolve at team level - log in RAID; owner and date assigned]
    Q1 -->|NO - beyond team authority| Q2{Does the issue affect the scope, schedule, cost, or quality baseline?}
    Q2 -->|NO - operational blocker only| PM_LEVEL[Escalate to PM - PM resolves via team leads or resource reallocation]
    Q2 -->|YES - threatens a baseline| Q3{Is the baseline impact material - above PM delegation threshold?}
    Q3 -->|NO - within PM authority| PM_CR[PM raises change request and resolves - update RAID and change log]
    Q3 -->|YES - above PM authority| Q4{Is the issue time-critical - must be resolved within 48 hours to avoid cascade impact?}
    Q4 -->|YES - urgent| SPONSOR_URGENT[Immediate escalation to sponsor - verbal first, written memo within 24 hours]
    Q4 -->|NO - can wait for next governance cycle| STEERING[Package for steering committee - full impact analysis and recommendation in next pack]
```

**Rationale per leaf:**
- *Resolve at team level* — the default; most blockers are operational and the team has the authority to resolve them. Log in RAID, assign owner and date.
- *Escalate to PM* — when the blocker crosses team boundaries (e.g. a dependency on another team that the project team cannot unblock).
- *PM raises CR* — a baseline-threatening issue that is within the PM's delegation: raise the change request, get the disposition, update the register.
- *Immediate sponsor escalation* — a time-critical baseline threat cannot wait for a scheduled steering meeting; verbal first, written escalation memo within 24 hours.
- *Steering committee* — a significant baseline impact that is not immediately time-critical belongs in the next steering pack with full impact analysis and a recommendation; the sponsor should be pre-wired before the pack goes out.

**Tradeoffs summary:**

| Level | When | Response time | Artefact |
|---|---|---|---|
| Team | Operational, within authority | Immediate | RAID log entry |
| PM | Cross-team dependency or operational authority gap | Hours to 1 day | RAID update + action |
| PM via CR | Baseline-threatening, within PM delegation | 1–2 days | Change request |
| Sponsor (urgent) | Baseline-threatening, time-critical | Within 24 hours | Verbal + written escalation memo |
| Steering | Baseline-threatening, not time-critical | Next scheduled meeting | Steering pack item with recommendation |

---

## Decision Tree: Closing a phase gate — proceed, hold, or reset?

**When this applies:** A predictive or hybrid project has reached a planned phase gate or stage gate (end of design, end of build, end of UAT, etc.). The sponsor and PM must decide whether to proceed to the next phase, hold pending resolution of open items, or reset the current phase. Observable trigger: a formal phase review is scheduled and the phase deliverables are being assessed against the gate criteria.

**Last verified:** 2026-06-05 against PMBOK 6 §4.7 (Close Project or Phase) and PRINCE2 stage-gate methodology.

```mermaid
flowchart TD
    START[Phase gate review] --> Q1{Are all phase deliverables complete and accepted by the sponsor or product owner?}
    Q1 -->|NO - one or more deliverables not accepted| Q2{Are the incomplete items minor defects with agreed completion plan and owner?}
    Q2 -->|YES - minor with plan| CONDITIONAL[Conditional proceed - approved exceptions log; completion before next milestone]
    Q2 -->|NO - significant gaps| HOLD[Hold - phase not closed; address gaps; re-schedule gate review]
    Q1 -->|YES - all deliverables accepted| Q3{Are open high-scored risks or unresolved P1 issues present?}
    Q3 -->|YES - open high risk or P1| Q4{Are risk responses in place and sponsor accepts residual risk?}
    Q4 -->|NO - no mitigation or acceptance| HOLD
    Q4 -->|YES - sponsor accepts residual risk with documented decision| PROCEED_RISK[Proceed with documented risk acceptance - update RAID; confirm contingency in next phase plan]
    Q3 -->|NO - no material open risks| Q5{Does the next phase plan exist - scope, resource, schedule, and budget approved?}
    Q5 -->|NO - next phase plan not approved| HOLD_PLAN[Hold on next phase start - gate is clear but phase cannot begin without an approved plan]
    Q5 -->|YES - approved| PROCEED[Proceed - phase formally closed; next phase initiated]
```

**Rationale per leaf:**
- *Conditional proceed* — minor exceptions are acceptable at a gate if they are logged, owned, and have a firm completion date before the next milestone where they would matter.
- *Hold* — significant deliverable gaps or unmitigated high risks mean the gate criteria are not met; the phase is not yet complete.
- *Proceed with documented risk acceptance* — a sponsor who knowingly accepts a residual risk can close the gate; the key is that the decision is documented, not that the risk is zero.
- *Hold on next phase start* — the current phase may be complete, but proceeding without an approved plan for the next phase is scope-creep into unplanned work; the plan comes first.
- *Proceed* — all criteria met; close the current phase formally and initiate the next with an approved plan.

**Tradeoffs summary:**

| Gate outcome | Phase closed? | Next phase starts? | Condition |
|---|---|---|---|
| Proceed | YES | YES | All criteria met |
| Proceed with risk acceptance | YES | YES | Sponsor accepts residual risk in writing |
| Conditional proceed | Conditionally | YES, with exceptions log | Minor gaps with owned completion plan |
| Hold | NO | NO | Significant gaps or unmitigated high risks |
| Hold on plan | YES | NO | Phase complete but next phase plan not approved |
