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
