---
proposal_id: 2026-05-21-001
proposed_at: 2026-05-21
proposed_by: matt
status: accepted-with-modifications
topic: cross-plugin / knowledge-format / agent-decision-making
last_updated: 2026-05-21
implemented_in: docs/best-practices/decision-trees-in-knowledge-files.md + plugins/power-platform/knowledge/programmatic-flow-creation.md (canonical example) + flow-engineer/solution-alm-engineer inline priors + Capability Grounding Protocol pre-action clause + Researcher staleness check
modifications_from_proposal:
  - Format changed from ASCII tree primary to Mermaid flowchart primary (per deep-researcher's LLMermaid Dual-Path Reinforcement evidence + Matt's existing memory preference for Mermaid in docs)
  - Consumer fork-with-attribution deferred (no real consumer ask yet — premature)
  - Permission-awareness ask SPLIT into separate proposal 2026-05-22-001 (different problem shape requires different solution shape)
  - v0.1.0 scope reduced to single-plugin pilot (power-platform) per architect Option A — observe before generalizing
related_asks:
  - Consumer fork-with-attribution (DEFERRED to v0.2.0+ — wait for ≥3 trees + real consumer ask)
  - Permission-awareness preamble per environment (SPLIT to proposal 2026-05-22-001)
---

# Decision Trees in AI Agent Memory Files — Problem Definition & Proposal

*Prepared for RavenClaude review — 2026-05-21*

---

## Problem Statement

AI agents accumulate **domain-specific procedural knowledge** in memory files. Today that knowledge is stored as **prose paragraphs** — readable, but not *traversable*. When the agent encounters a situation covered by that knowledge, it must:

1. Recall the relevant prose from memory
2. Interpret which case applies
3. Infer the correct action

This works until it doesn't. The failure modes are:

| Failure | What happens |
|---|---|
| **Over-reaction** | Agent picks the sledgehammer (full solution reimport, 20 min) when a scalpel (surgical temp solution, 2 min) was available |
| **Under-reaction** | Agent keeps retrying a portal toggle that will never work because the root cause is a missing connection binding |
| **Wrong branch** | Agent diagnoses a `For_a_selected_row_V2 / 404` error as "flow is off" and tries to activate it, rather than recognising it as stale clientdata requiring reimport |
| **Skipped step** | Agent forgets to delete the temp solution after surgical import, leaving orphaned solution records in Dataverse |

**Root cause:** prose knowledge doesn't force the agent to check conditions in order before acting. A decision tree does.

---

## The Pattern: Procedural Decision Trees in Memory Files

A decision tree stored in a memory file has three properties prose doesn't:

**1. Exhaustive branching.** Every case is named. The agent can't skip a branch by selective recall.

**2. Deterministic output.** Each leaf is a concrete action (command, API call, UI step), not a recommendation. The agent doesn't have to interpret — it just executes the leaf.

**3. Self-documenting tradeoffs.** The tree makes the *why* visible at each branch node, so the agent can surface it to the user as a confirmation prompt without synthesising it from prose.

---

## Proposed Format for RavenClaude Plugins

```
DECISION_TREE: <Domain> — <Situation>
│
├─ CONDITION: <what to check first>
│   ├─ TRUE  → <next condition or leaf action>
│   └─ FALSE → <next condition or leaf action>
│
├─ CONDITION: <second check>
│   ├─ <value A> → LEAF: <concrete action + command>
│   ├─ <value B> → LEAF: <concrete action + command>
│   └─ <value C> → LEAF: <concrete action + command>
│
└─ ESCALATE: <condition that requires human approval before proceeding>
      Prompt format: "What I'm about to do / Why it matters / Blast radius"
```

---

## Where Decision Trees Belong vs. Prose

| Knowledge type | Format |
|---|---|
| Concepts, definitions, platform gotchas | Prose |
| "When to use X vs. Y" comparisons | Prose table |
| Multi-step procedures where the first step determines the rest | **Decision tree** |
| Approval gates with blast-radius definitions | Decision tree leaf + confirmation prompt |

---

## What Triggers a Decision Tree (Heuristics for Plugin Authors)

A knowledge block should become a decision tree when it contains **any of these signals**:

- The phrase "it depends on..."
- Two or more methods that solve the same problem with different risk/cost profiles
- A step that must check a condition before knowing which next step to take
- An escalation that should always fire in one branch and never in another

---

## Concrete Reference Implementation (BTCSI repo)

The PA flow fix tree was added to `docs/agent-memory.md` on 2026-05-21. It already demonstrates value: in prior sessions the agent used full solution reimport (5–20 min) for single broken flows. The tree makes the surgical path (~2 min) the default by forcing the "how many flows?" condition check first.

```
DECISION_TREE: Power Automate Flows — Stuck / Broken / Off
│
START: One or more PA flows are broken, off, misnamed, or have a trigger error
│
├─ Can you toggle the flow ON from the portal (no errors)?
│   └─ YES → Just toggle it on. Done. No import needed.
│
├─ Bulk toggle fails (0x80060467 / "not in a valid state")
│   or trigger shows "For_a_selected_row_V2 / 404" error?
│   │
│   ├─ How many flows are affected?
│   │   ├─ 1–5 flows
│   │   │     → SURGICAL TEMP SOLUTION (preferred, ~2 min)
│   │   │       1. Create temp BTCSIFlowFix solution via Web API
│   │   │       2. AddSolutionComponent (type 29) for each affected flow only
│   │   │       3. Export → pac unpack → edit JSON/XML → pac pack → import
│   │   │       4. Delete temp solution
│   │   │       Touches nothing else.
│   │   │
│   │   └─ 6+ flows OR flows span multiple entities
│   │         → FULL SOLUTION REIMPORT (5–20 min)
│   │           1. pac solution export <OwnerSolution>
│   │           2. pac solution unpack → fix all flows → pac pack
│   │           3. pac solution import -ap
│   │           ⚠ Risk: overwrites portal changes since last export.
│   │           Always check git diff after portal pull.
│
├─ Trigger shows "For_a_selected_row_V2 / 404" error?
│   └─ Root cause: clientdata has stale environment/table metadata.
│      Fix: surgical temp solution → verify trigger block references
│      current environment URL + correct table name → reimport.
│
└─ Flow activated but immediately turned itself off?
      Likely: missing connection reference binding in this environment.
      Fix: portal → Connections → bind the CR → retry activation.
      Do NOT reimport — reimport won't fix a missing connection binding.
```

**Summary of tradeoffs:**

| Method | Time | Risk | Use when |
|---|---|---|---|
| Portal toggle | Seconds | None | Flow just needs activation |
| Surgical temp solution | ~2 min | Minimal — only touches named flows | 1–5 broken/misnamed flows |
| Full solution reimport | 5–20 min | Overwrites all components since last export | Many flows or confirmed auth corruption |
| Connection re-bind | Seconds | None | Flow turns itself off immediately after activation |

---

## Suggested Addition to RavenClaude Plugin

1. **Memory file authoring convention** — when a plugin author writes a memory file, the prompt engineer agent should flag any prose block that matches the "triggers" list above and suggest converting it to a decision tree.

2. **Agent reading convention** — when an agent loads a memory file containing a `DECISION_TREE:` block, it should traverse it top-to-bottom before selecting a method, rather than pattern-matching on keywords in the situation description.

3. **Leaf format standard** — every leaf node should include: action name, estimated duration, blast radius (what gets touched), and whether it requires an approval gate.

---

# Review & Disposition (added 2026-05-21)

## Reviewer findings

**Architect** (RavenClaude `ravenclaude-core/architect`, completed 2026-05-21):

- Marketplace already has a decision tree under that exact name (`plugins/data-platform/skills/stack-selection.md` is called a "Case A/B/C/D decision tree" in 3 places) — but the existing implementation is more primitive (numbered-list of 4 questions, no Mermaid, no leaf rationale). Matt's proposal is an upgrade, not a novelty.
- The genuinely-new mechanism is the **pre-action traversal prior** — agents must traverse the tree BEFORE selecting a method, not pattern-match on keywords. The format alone doesn't change behavior; the inline prior does.
- The Capability Grounding Protocol handles the *blocked* case (try alternates after failure); the decision tree handles the *happy-path action-selection* case. Complementary, not duplicative.
- Recommended Option A: single-plugin pilot (retrofit power-platform `programmatic-flow-creation.md` first, observe, then generalize).
- Strong recommendation to **split the permission-awareness ask** into a separate proposal — different problem shape (environmental priors vs procedural priors), different solution shape.
- Forbidden: parser, validator, tree-aware skill, separate file extension, new top-level directory. House-rule alignment.

**Deep-researcher** (completed 2026-05-21):

- Confirmed the pattern has a name in the SRE-adjacent literature: **"agent runbooks"** (Sema4.ai, Google Cloud Security community ship this as a product category in 2026).
- Anthropic's own Skills documentation explicitly endorses decision-tree structure for complex conditional logic in `SKILL.md` files.
- Recommended **Mermaid primary** over ASCII based on LLMermaid "Dual-Path Reinforcement" research — text + parseable graph syntax double-encodes structure, improving LLM follow-rates.
- Tree-of-Thoughts is the wrong analogue (runtime exploration ≠ memory representation). LangGraph's `StateGraph` with conditional edges is the closest production analogue — but RavenClaude is markdown-native, so adopt its *vocabulary*, not its Python runtime.
- Decision trees go stale faster than prose when underlying platforms change → mandatory `last-verified:` date + Researcher staleness check (90 days).

## Matt's decisions (2026-05-21, via AskUserQuestion)

1. **Format:** Mermaid primary + prose summary + per-leaf rationale (researcher's recommendation chosen over architect's markdown-table-primary)
2. **Scope split:** decision-trees ship v0.1.0 alone; permission-awareness as separate proposal `2026-05-22-001`
3. **Pilot:** Option A — single-plugin pilot (power-platform `programmatic-flow-creation.md` first); observe before generalizing
4. **Anti-stale:** ship `last-verified:` field + Researcher 90-day staleness check now

## What shipped in v0.1.0

| Artifact | Path |
|---|---|
| Best-practice rule | [`../best-practices/decision-trees-in-knowledge-files.md`](../best-practices/decision-trees-in-knowledge-files.md) |
| Canonical example (retrofit) | [`../../plugins/power-platform/knowledge/programmatic-flow-creation.md`](../../plugins/power-platform/knowledge/programmatic-flow-creation.md) §"Decision Tree: PA flow recovery — stuck / broken / off" |
| Pre-action traversal prior on `flow-engineer` | [`../../plugins/power-platform/agents/flow-engineer.md`](../../plugins/power-platform/agents/flow-engineer.md) §"Decision-tree traversal (priors)" |
| Pre-action traversal prior on `solution-alm-engineer` | [`../../plugins/power-platform/agents/solution-alm-engineer.md`](../../plugins/power-platform/agents/solution-alm-engineer.md) §"Decision-tree traversal (priors)" |
| Capability Grounding Protocol pre-action clause | [`../../plugins/ravenclaude-core/CLAUDE.md`](../../plugins/ravenclaude-core/CLAUDE.md) §"Pre-action traversal of decision trees (added 2026-05-21)" |
| Researcher staleness check | [`../../plugins/ravenclaude-core/skills/researcher/SKILL.md`](../../plugins/ravenclaude-core/skills/researcher/SKILL.md) §"Decision-tree staleness check (added 2026-05-21)" |
| Sibling proposal (split out) | [`2026-05-22-001-environment-context-permission-posture.md`](2026-05-22-001-environment-context-permission-posture.md) |

## What did NOT ship (and why)

- **Consumer fork-with-attribution** — deferred to v0.2.0+. No real consumer ask yet; the IaC overlay pattern (Kustomize/Helm) is the structural precedent if/when needed.
- **Cross-plugin tree adoption (edtech / data-platform / etc.)** — deferred. Single-plugin pilot first; observe behavior change on the PA flow case before generalizing.
- **Decision-tree parser / validator** — forbidden by house rule. The format is prose-with-discipline, not executable.
- **Permission-awareness mechanism** — split to proposal `2026-05-22-001` for separate evaluation.

## Test plan (the observation step from Option A)

The proof-point is: **next time Matt has a PA flow that needs recovery, observe whether the `flow-engineer` agent traverses the decision tree before picking a method.**

- Pass: agent picks portal-toggle / surgical / connection-rebind for the small-blast-radius cases without defaulting to full reimport.
- Fail: agent still defaults to full reimport on first try → the inline prior wording isn't carrying; revise the prior or escalate to Team Lead dispatch-template framing.

If the proof-point passes, generalize to other plugins. If it fails, the format change wasn't sufficient and we need to revisit upstream (priming at dispatch time, not just in the agent file).
