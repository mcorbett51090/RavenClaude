# Decision trees in knowledge files

> **Status:** rule. **Why it exists:** plugin authors were independently inventing the same shape (see `plugins/data-platform/skills/stack-selection.md` "Case A/B/C/D decision tree" + `plugins/power-platform/knowledge/programmatic-flow-creation.md` summary table) without a documented format. Authoring drift was producing inconsistent agent behavior: same multi-conditional procedural knowledge, different shapes, different traversal fidelity. **How to apply:** when a knowledge file contains procedural priors with branching conditions, format the branching as a Mermaid flowchart + per-leaf rationale + `last-verified:` date, and add a pre-action traversal inline prior on the relevant agents.

This rule was extracted from proposal `docs/proposals/2026-05-21-001-decision-trees-in-memory-files.md` (Matt 2026-05-21) after architect + deep-researcher review (both completed 2026-05-21).

---

## When a knowledge block should be a decision tree

Convert prose to a decision tree when ANY of these signals appear:

- The phrase "it depends on..."
- Two or more methods solve the same problem with different risk/cost profiles (e.g., surgical 2 min vs full reimport 20 min)
- A step must check a condition before knowing which next step to take
- An escalation should always fire in one branch and never in another
- Observed failure mode is **wrong-branch-from-the-start** (the agent diagnosed wrong on first try — Capability Grounding Protocol's alternate-methods rule doesn't help, because there was no failure to enumerate alternates from)

## When NOT to use a tree (load-bearing — half of `data-platform/knowledge/` should stay prose)

- Landscape / comparison content (e.g., "EdTech AI vendor pricing landscape") — prose + comparison table is better
- Definitions, concepts, platform gotchas — prose
- "When to use X vs. Y" with no branching — prose table
- Anything with branching depth 1-2 — markdown decision table is enough; Mermaid is overkill
- Content where the underlying platform changes faster than ~quarterly — tree will go stale faster than prose

## The format

A decision tree section in a knowledge file has five required parts:

```markdown
## Decision Tree: <Domain> — <Situation>

**When this applies:** <2-3 sentences naming the situation in OBSERVABLE terms — error code, symptom, partner state. Not "when the agent is uncertain.">

**Last verified:** <YYYY-MM-DD> against <platform / version / source>.

` ` `mermaid
flowchart TD
    START[Entry condition] --> Q1{First decision point in observable terms}
    Q1 -->|YES branch| LEAF_A[Method A — short label]
    Q1 -->|NO branch| Q2{Next decision point}
    Q2 -->|case 1| LEAF_B[Method B]
    Q2 -->|case 2| LEAF_C[Method C]
` ` `

**Rationale per leaf:**
- *Method A* — why this branch terminates here (1 sentence)
- *Method B* — why (1 sentence)
- *Method C* — why (1 sentence)

**Tradeoffs summary table** (REQUIRED for trees with ≥3 leaves):

| Method | Time | Blast radius | Approval gate? | Use when |
|---|---|---|---|---|
| ...
```

Replace `` ` ` ` `` with three actual backticks. The `last-verified:` date is non-negotiable (anti-staleness backstop).

## Why Mermaid (not ASCII, not YAML, not JSON Schema)

- **Mermaid is parseable** — CI can lint the graph (catches typos in node IDs, dangling edges)
- **Mermaid renders in [`repo-guide.html`](../../repo-guide.html)** ([▶ view rendered](https://mcorbett51090.github.io/RavenClaude/repo-guide.html)) and GitHub natively — the visual diagram and the source-text are the same artifact
- **Mermaid tokenizes more predictably for LLMs** than ASCII drawing characters — LLMermaid research ("Dual-Path Reinforcement") shows text + parseable graph syntax improves agent follow-rates
- **YAML / JSON Schema is overkill** when the *model* is the executor (not a deterministic runtime). The schema adds tokens without adding constraint
- **ASCII is readable but agent-unfriendly** — `├─ YES →` tokenizes unpredictably; `Q1 -->|YES| LEAF_A` is consistent

## The pre-action traversal prior (the genuinely-new mechanism)

The decision tree section in a knowledge file is NOT consumed automatically. Agents must be **primed** to traverse it before selecting a method. Add a sentence to each agent that should consult the tree:

> **Decision-tree traversal (priors).** When the user's situation matches the entry condition in [`../knowledge/<topic>.md`](../knowledge/<topic>.md) `## Decision Tree`, traverse the Mermaid graph top-to-bottom before selecting a method. Do NOT pattern-match on keywords in the user's situation description. The first branch where the condition resolves cleanly is the leaf to apply.

This is the load-bearing addition. The format alone (Mermaid section) doesn't change behavior; the prior (agent instructed to traverse before acting) does.

## Capability Grounding Protocol relationship

The Capability Grounding Protocol (`plugins/ravenclaude-core/CLAUDE.md` §"Capability Grounding Protocol") handles the **reactive** case: agent tried A, A failed, enumerate alternates before declaring blocked.

The decision-tree pre-action traversal handles the **proactive** case: agent has not yet acted; choose the right branch on first attempt instead of picking willy-nilly.

The two compose. CGP catches what the tree missed; the tree prevents needing CGP in the first place.

## Node prerequisites: the `requires:` annotation (added 2026-05-26)

A leaf often only works if the agent holds a specific **auth or permission** — e.g. the Dataverse-Web-API branch in [`../../plugins/power-platform/knowledge/programmatic-flow-creation.md`](../../plugins/power-platform/knowledge/programmatic-flow-creation.md) only works with a service principal that has `System Administrator` (or create/update on the `workflow` table) in the target environment. Make that prerequisite explicit so the agent checks it **before** committing to the branch instead of discovering the gap mid-execution.

Annotate the leaf with a `requires:` note in the rationale list (or a `Requires?` column in the tradeoffs table):

> - *Method B (Dataverse Web API)* — … **requires:** SPN with `System Administrator` (or create/update on the `workflow` table) in the target Dataverse environment.

**How the agent uses it (convention, not a parser):** at session start the [`capability-orientation`](../../plugins/ravenclaude-core/hooks/capability-orientation.sh) hook injects a capability banner naming the agent's detected auth + effective permissions, and `.ravenclaude/environment-context.md` stays authoritative for per-environment roles. Before traversing into a `requires:`-annotated branch, the agent cross-checks the prerequisite against that banner / file. If the prerequisite is held → proceed without asking. If it is NOT held (or unknown) → that is exactly the "do I have authority?" moment the Capability Grounding Protocol's pre-action environment-context check governs: confirm or escalate before picking the branch.

This keeps the **mechanism** in core (the banner + the CGP check) and the **permission taxonomy** with the domain tree (each tree names the roles/scopes its own branches need) — no central registry, no parser, consistent with "Forbidden infrastructure" below.

## Forbidden infrastructure (house-rule alignment — added 2026-05-21)

This best-practice is a **convention**, not a parser. Do NOT add:

- A `DECISION_TREE:` parser or validator beyond `prettier --write`
- A "tree-aware" skill that programmatically traverses the Mermaid
- A new top-level `trees/` directory
- A separate file extension (`.tree.yaml`, etc.)
- A new agent role (e.g., `decision-tree-evaluator`)

If the format needs tooling beyond Mermaid syntax linting, the format is wrong. The whole point of the convention is "prose with discipline" — the agent reads the same markdown a human reads.

## Staleness check

Decision trees go stale faster than prose when the underlying platform changes (an API returns 409 instead of 404; a method becomes deprecated). The mitigation:

- **`last-verified: YYYY-MM-DD`** in the tree section header — mandatory
- The Researcher meta-skill (`plugins/ravenclaude-core/skills/researcher.md`) flags any decision tree with `last-verified:` older than 90 days for re-verification on its weekly sweep
- Re-verification = author confirms each leaf still applies; updates the date or revises the tree

## Consumer override (DEFERRED to v0.2.0+)

Premature in v0.1.0. When ≥3 trees exist AND a real consumer asks to override a marketplace-shipped tree, the architect's recommendation is **in-file annotation** (consumer adds an "## Override" section below the canonical tree, preserving the marketplace default visible) rather than a sidecar `.local.md` file. The IaC Kustomize-overlay pattern is the structural precedent.

## Canonical example

[`plugins/power-platform/knowledge/programmatic-flow-creation.md`](../../plugins/power-platform/knowledge/programmatic-flow-creation.md) — the Power Automate flow-fix tree (surgical-vs-reimport decision). This is the reference implementation; new trees should mirror its shape.

## Why this rule exists (paper trail)

- Matt's proposal: `docs/proposals/2026-05-21-001-decision-trees-in-memory-files.md`
- Architect review: completed 2026-05-21, key finding "the marketplace already has decision trees unnamed — `stack-selection.md` calls itself one in 3 places — proposal is an upgrade not a novelty"
- Deep-researcher: completed 2026-05-21, key finding "this pattern is sold as a product category in 2026 — Anthropic Skills docs endorse it, Google Cloud Security ships 'agent runbooks,' Sema4.ai sells the category. The naming difference (runbook vs decision tree) is why a search for 'decision tree in LLM memory' didn't immediately surface the lineage."
- Matt's call: Mermaid primary + Option A single-plugin pilot + split permission-awareness into separate proposal + ship `last-verified:` + Researcher check now (2026-05-21).
