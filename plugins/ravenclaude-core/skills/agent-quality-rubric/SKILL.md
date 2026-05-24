---
name: agent-quality-rubric
description: Score and improve an agent file against a 6-dimension rubric — Mission clarity, Scope sharpness, Capability Grounding alignment, Output-Contract completeness, Escalation paths, Example scenarios. Each dimension scored 1-5 with anchors; includes a remediation template that turns a low score into an actionable PR. Reach for this skill when authoring a new agent, reviewing a PR that adds or modifies an agent, or running a periodic agent-bank audit. Used by `prompt-engineer` (primary) plus `architect`.
---

# Skill: agent-quality-rubric

You are reviewing an agent file (typically `plugins/<plugin>/agents/<role>.md`). The rubric below is a 6-dimension scorecard that surfaces concrete gaps and feeds an actionable remediation PR — not a vibe-check.

The rubric exists because agent quality is the single largest predictor of marketplace output quality, and "looks fine to me" is not a maintainable review standard. Each dimension is anchored 1-5 with text descriptions so two reviewers grade the same agent within roughly one point.

## When to invoke this skill

- Authoring a new agent (before opening the PR).
- Reviewing a PR that adds or modifies an agent (cite dimension + score in your review comments).
- Periodic agent-bank audit (e.g. quarterly): score every agent in `plugins/*/agents/` and queue any dimension ≤2 for remediation.
- The Researcher's Weekly Deep Research can run this against agents in its sweep.

## The 6 dimensions

### Dimension 1 — Mission clarity

**The one-sentence-mission test:** can you state, in one sentence with no hedges, what this agent does and does not do? If you find yourself writing "...and also..." you've already failed clarity.

| Score | Anchor |
|---|---|
| **5** | Mission stated in the first paragraph in one sentence; reading the rest of the agent only confirms it. |
| **4** | Mission stated, requires one supporting clause but still parseable in a single read. |
| **3** | Mission inferable from the agent body but never stated explicitly; readers will reconstruct different missions. |
| **2** | Two or more competing missions in the file ("this agent does X *and* Y"). |
| **1** | No discernible mission; the file reads like a grab-bag of responsibilities. |

### Dimension 2 — Scope sharpness

**The "NOT for X" test:** does the agent explicitly say what it does NOT handle? Sharpness comes from negation; positive scope alone always overlaps with neighboring agents.

| Score | Anchor |
|---|---|
| **5** | Explicit "Not for X / not for Y" list, with the named alternative agent for each excluded case. |
| **4** | Negation present but no named alternative ("not for security review" with no pointer to security-reviewer). |
| **3** | Implicit scope only; reader has to compare against other agent files to infer the boundary. |
| **2** | Overlap with at least one other agent in the same plugin; no disambiguation. |
| **1** | Drift-prone: the agent claims responsibilities that already live elsewhere in the marketplace. |

### Dimension 3 — Capability Grounding alignment

**The Grounding Protocol inheritance test:** does the agent reference the plugin's CLAUDE.md §5 Capability Grounding Protocol? Does its Output Contract include the line *"Grounding checks performed: ..."*? Does it acknowledge the alternate-methods rule, the pre-action decision-tree traversal, and the environment-context check?

| Score | Anchor |
|---|---|
| **5** | Explicit "inherits the Capability Grounding Protocol" line; output template includes "Grounding checks performed"; alternate-methods rule referenced when relevant. |
| **4** | Protocol referenced but the output template doesn't propagate the checks-performed line. |
| **3** | Protocol named, but no operational tie-in (reader is expected to know what it means). |
| **2** | Protocol not mentioned; agent may silently violate the alternate-methods rule. |
| **1** | Agent contradicts the protocol (e.g. tells the user "this isn't possible" without enumerating alternatives). |

### Dimension 4 — Output-Contract completeness

**The five-line check:** does the Output Contract specify (a) Status, (b) Files-changed list, (c) any mandatory plugin-specific lines (e.g. "Grounding checks performed", "Decision-tree branch chosen"), (d) the `---RESULT_START---` JSON block per [`structured-output.md`](../structured-output/SKILL.md), and (e) a reporting cap (word/line limit)?

| Score | Anchor |
|---|---|
| **5** | All five present; the JSON shape is explicit with all required keys (`status`, `summary`, `deliverables`, `handoff_recommendation`, `confidence`, `risks_or_open_questions`, `next_actions`). |
| **4** | All five present but the JSON shape lists fewer than the canonical 7 keys. |
| **3** | Four of five (typically missing the structured JSON block or the reporting cap). |
| **2** | Two or three of five — agent will produce inconsistent, hard-to-parse handoffs. |
| **1** | Free-form output instructions; downstream automation will break on this agent's reports. |

### Dimension 5 — Escalation paths

**The named-handoff test:** when this agent hits a problem outside its scope, does it know exactly which OTHER agent to escalate to, and does it know why? "Escalate to the Team Lead" alone is necessary but not sufficient — name the specialist + reason.

| Score | Anchor |
|---|---|
| **5** | Table or list of escalation rows: surfacing → likely cause → named target agent. At least 3 rows; covers the most common cross-boundary cases. |
| **4** | List present but missing one obvious case (e.g. agent touches auth but doesn't name `security-reviewer`). |
| **3** | "Escalate to Team Lead" only; no named specialists. |
| **2** | Escalation mentioned but no rules; reader has to guess. |
| **1** | No escalation guidance — agent will either over-claim or silently drop work it can't do. |

### Dimension 6 — Example scenarios

**The agent-scenario-authoring frontmatter test:** does the YAML frontmatter include `audience`, `works_with`, `scenarios`, and `quickstart` per [`docs/best-practices/agent-scenario-authoring.md`](../../../../docs/best-practices/agent-scenario-authoring.md)? The repo-guide generator picks them up automatically for per-agent cards and the Overview use-case lookup table — missing fields = invisible agent.

| Score | Anchor |
|---|---|
| **5** | All four fields populated with at least 3 scenarios; each scenario has trigger phrasing a user would actually type. |
| **4** | All four fields present but scenarios are thin (1-2) or generic. |
| **3** | Three of four fields; one is empty placeholder. |
| **2** | Two or fewer fields; agent is essentially invisible in the repo-guide. |
| **1** | No scenario-authoring frontmatter — repo-guide can't render the agent's card. |

## Scoring guidance

| Total score | Disposition |
|---|---|
| **27-30** (avg 4.5+) | Ships as-is. |
| **22-26** (avg 3.7+) | Ship with minor edits — note the weakest dimensions in the PR description. |
| **16-21** (avg 2.7+) | Revise before merge. Address every dimension scoring ≤3. |
| **10-15** | Rewrite the weakest dimensions individually. The skeleton is salvageable. |
| **6-9** | Block — re-author from a fresh brief via [`draft-agent-brief`](../draft-agent-brief/SKILL.md). |

A single dimension scored 1 is a block regardless of total. Mission-clarity ≤2 is a block regardless of total — the rest of the agent inherits the ambiguity.

## Using the rubric in a PR review

Comment on the PR diff using this shape:

> **Dimension 3 (Capability Grounding) — score 2.** Agent doesn't mention the alternate-methods rule. When the chosen tool fails, this agent will report blocked without enumerating Approach B / C. Add the standard CGP-inheritance paragraph from `agents/architect.md` lines 18-26 as a template.

One comment per dimension scored ≤3 is the right cadence. Don't comment on dimensions scored ≥4 unless you have a concrete suggestion — noise dilutes the load-bearing comments.

## Remediation template (drop into a PR description)

When a PR's purpose is to lift an agent's rubric score, the PR description should follow this shape so the reviewer can verify each gap was closed:

```markdown
## Agent quality rubric — remediation PR

**Agent:** `plugins/<plugin>/agents/<role>.md`
**Pre-remediation score:** <total>/30
**Target score:** <total>/30

### Dimensions addressed

| Dimension | Pre | Post | Change made |
|---|---|---|---|
| Mission clarity | <n> | <n> | <one-line description, or "no change"> |
| Scope sharpness | <n> | <n> | <e.g. added "Not for X — escalate to Y" list> |
| Capability Grounding | <n> | <n> | <e.g. added §5 inheritance paragraph + "Grounding checks performed" line> |
| Output-Contract | <n> | <n> | <e.g. added ---RESULT_START--- JSON block with 7 canonical keys> |
| Escalation paths | <n> | <n> | <e.g. added 4-row escalation table> |
| Example scenarios | <n> | <n> | <e.g. populated audience / works_with / scenarios / quickstart> |

### Verification

- [ ] `python3 -m json.tool` passes on any JSON examples in the agent file
- [ ] Repo-guide preview renders the agent's per-agent card without warnings
- [ ] At least one downstream agent's escalation table now points to this agent (if applicable)
- [ ] Plugin's CLAUDE.md skill/agent index updated if scope changed
```

## Anti-patterns

- **Scoring without quoting.** Every score ≤3 must be paired with a quoted excerpt from the agent file (or a noted absence) so the author knows what to fix.
- **Vibe-grading.** "Feels like a 4" is not a score. Anchor to the dimension's text descriptions.
- **Average-only verdict.** A 30/30 with one dimension at 1 still blocks. Read every row.
- **Re-scoring without reading the remediation.** When a PR lifts a score, re-grade the affected dimensions against the new text, not from memory of the old text.
- **Treating Mission and Scope as one dimension.** They aren't — a clear mission can still overlap with neighbors. Scope sharpness is the negation test, not the mission test.

## See also

- [`structured-output.md`](../structured-output/SKILL.md) — the Output-Contract dimension's reference.
- [`scenario-retrieval.md`](../scenario-retrieval/SKILL.md) — informs the Escalation-paths dimension when agents should consult scenarios before answering.
- [`draft-agent-brief.md`](../draft-agent-brief/SKILL.md) — feeds in when total score ≤9 and the agent needs a re-author.
- [`prompt-pattern-library.md`](../prompt-pattern-library/SKILL.md) — the canonical patterns the rubric checks for compliance with.
- [`../../../docs/best-practices/agent-scenario-authoring.md`](../../../../docs/best-practices/agent-scenario-authoring.md) — the Dimension 6 reference.
