# Orchestration decision trees

Agent routing, delegation, and error-handling decisions — traverse top-to-bottom before picking a method. Last reviewed: 2026-06-05.

## Decision Tree: Agent Output — Which Status to Report

**When this applies:** A specialist agent has finished its work (or reached a limit) and must populate the `status` field in the Structured Output Protocol block. The wrong status misroutes the Team Lead — a `complete` on partial work hides a gap; a `blocked` on recoverable work abandons automatable progress.

**Last verified:** 2026-06-05 against the Structured Output Protocol specification and Capability Grounding Protocol requirements.

```mermaid
flowchart TD
    START[Agent finished its task or hit a limit] --> Q1{Were all stated success criteria met?}
    Q1 -->|yes - all criteria met| LEAF_A[status complete - confidence reflects verification basis - handoff to next specialist if applicable]
    Q1 -->|no - not all criteria met| Q2{Did the agent exhaust the CGP alternate-methods enumeration?}
    Q2 -->|no - not yet exhausted| LEAF_B[Not done yet - apply CGP - enumerate 2 or more alternatives and try the next-easiest before reporting]
    Q2 -->|yes - exhausted| Q3{Was partial progress made - some criteria met?}
    Q3 -->|yes - some criteria met| LEAF_C[status partial - deliverables lists what was completed - risks-or-open-questions explains the gap - next-actions gives the recovery path]
    Q3 -->|no - no progress - genuinely stuck| LEAF_D[status blocked - mandatory CGP phrasing in report - next-actions names the escalation path - confidence reflects the degree of uncertainty]
```

**Rationale per leaf:**
- *complete* — all success criteria met; the confidence float should reflect whether the criteria were verified against this-session evidence (0.9+) or domain knowledge (0.7–0.9).
- *not done yet* — a premature "blocked" that skips CGP is the protocol's most-flagged anti-pattern; apply the alternate-methods rule before reporting any non-complete status.
- *partial* — partial progress is the correct honest status when some work is done; it keeps the Team Lead informed without declaring a false completion.
- *blocked* — only valid after CGP is exhausted; the mandatory-phrasing block in the Markdown report is required (what was tried, what failed, what remains).

**Tradeoffs summary:**

| Status | When valid | Risk if mis-used |
|---|---|---|
| complete | All criteria met, verified | Hides gaps if criteria were not actually checked |
| partial | Some criteria met, some not | Team Lead may under-prioritize re-engagement |
| blocked | CGP exhausted, no progress | Wastes a round-trip if CGP was not actually applied |

## Decision Tree: Plugin Capability Gap — Skill vs New Agent vs Core Agent

**When this applies:** A domain plugin team has identified a new capability need. The question is whether to add a skill file, add a domain-specific agent, or point at an existing core agent. Getting this wrong creates dispatch ambiguity or unused agents.

**Last verified:** 2026-06-05 against the "domain plugins extend core via skills and knowledge" house rule and the project-management carve-out precedent.

```mermaid
flowchart TD
    START[New domain capability identified] --> Q1{Does a ravenclaude-core agent already produce this deliverable type?}
    Q1 -->|yes - core agent covers the deliverable type| Q2{Could the core agent produce indistinguishable output if handed a domain skill and knowledge file?}
    Q2 -->|yes - a skill would do it| LEAF_A[Ship a skill plus inline prior on the core agent - no new agent]
    Q2 -->|no - the domain craft is genuinely incompatible| LEAF_B[Ship a domain agent with a distinct deliverable format - document why the core agent cannot produce it]
    Q1 -->|no - no core agent covers this deliverable type| Q3{Is this a generalist concern that splits cleanly into hygiene-stays-core and deep-craft-lives-in-plugin?}
    Q3 -->|yes - clean split exists| LEAF_C[Keep the hygiene part in or routing to core - build the deep-craft plugin agent for the specialist half only - document the litmus test]
    Q3 -->|no - genuinely new role with no core analog| LEAF_D[New agent is justified - document the deliverable format and the absence of a core analog before shipping]
```

**Rationale per leaf:**
- *Skill + inline prior* — the default; covers the vast majority of domain-specific needs without creating dispatch ambiguity.
- *Domain agent (incompatible craft)* — justified only when the core agent genuinely cannot produce the output; cite the specific incompatibility in the agent's CLAUDE.md.
- *Hygiene/deep-craft split* — the project-management carve-out pattern; applies only when the split is clean and the deep craft carries a recognized body (PMBOK, AGILE canon, etc.).
- *New agent (no core analog)* — justified; document what distinguishes it from any core role.

**Tradeoffs summary:**

| Method | Dispatch risk | Maintenance cost | Use when |
|---|---|---|---|
| Skill + inline prior | None | Low - lives in the domain plugin | Core agent type matches, domain adds craft |
| Domain agent (incompatible) | Medium - Team Lead must distinguish | High - rubric must stay current | Genuinely incompatible deliverable format |
| Hygiene/deep-craft split | Low if litmus is enforced | Medium - two surfaces to maintain | Clean split, recognized specialist canon |
| New agent (no analog) | Low - no core to confuse | High | No core analog at all |

## Decision Tree: Session Start — What to Check Before the First Action

**When this applies:** A new session begins — the agent is about to take its first action. The question is which checks to run before acting to avoid the most common session-start failure modes: acting blind to existing state, re-proposing something already done, or picking the wrong method because the routing tree was not traversed.

**Last verified:** 2026-06-05 against the session-start capability hook, environment-context check, and decision-tree pre-action traversal requirements.

```mermaid
flowchart TD
    START[Session begins - first action about to be taken] --> Q1{Is there an environment-context file at .ravenclaude/environment-context.md?}
    Q1 -->|yes| Q2{Does the proposed action fall into a pre-authorized action category for the current environment?}
    Q2 -->|yes - pre-authorized| LEAF_A[Execute without prompting for authorization - skip the auth round-trip]
    Q2 -->|no - not pre-authorized or file is silent| Q3{Is there a matching decision tree in the active plugin for this request?}
    Q3 -->|yes - matching tree| LEAF_B[Traverse the decision tree top-to-bottom against the user context - then select the leaf - only then act]
    Q3 -->|no - no matching tree| Q4{Is there a hook-events.jsonl from the current session with relevant denials?}
    Q4 -->|yes - relevant denials exist| LEAF_C[Read the denial rule before choosing an approach - avoid re-selecting the denied path]
    Q4 -->|no - clean state| LEAF_D[Apply the routing tree to select the right specialist or method - proceed with the standard CGP discipline]
    Q1 -->|no - no environment-context file| Q3
```

**Rationale per leaf:**
- *Execute pre-authorized* — the environment-context check closes the "did you try X?" round-trip for actions the agent is already authorized to take.
- *Traverse decision tree first* — the pre-action traversal closes the "wrong branch from the start" failure mode; the tree is the proactive half of dispatch discipline.
- *Read denials before choosing* — a session where a guardrail already fired on an approach is telling the agent something; re-selecting the denied path wastes a call.
- *Routing tree + CGP* — the default path when no special conditions apply; route first, act with CGP discipline, apply alternate-methods if needed.

**Tradeoffs summary:**

| Check | Cost | Failure prevented | Skip when |
|---|---|---|---|
| Environment-context check | One file read | Unnecessary auth round-trip | File does not exist |
| Decision-tree traversal | 30 seconds of reasoning | Wrong method on first try | No matching tree in the plugin |
| Hook-events read | One glob + read | Re-selecting a denied approach | Clean session or no relevant denials |
| Routing tree | Reasoning only | Wrong specialist selected | Team Lead handles directly (trivial task) |
