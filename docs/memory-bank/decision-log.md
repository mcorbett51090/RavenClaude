# Decision Log

> Major architectural / structural decisions for this hub, with the reasoning that drove them. One section per decision, reverse-chronological. Intended as the answer to future "why is it like this?" questions.

## Format

```markdown
## YYYY-MM-DD — Decision title

**Context:** What forced the decision. 1–2 sentences.

**Options considered:**
- Option A — pros / cons
- Option B — pros / cons
- Option C — pros / cons

**Chosen:** Option X.

**Reasoning:** Why X over the others. 2–4 sentences.

**Consequences:** What this commits us to going forward. What's now hard to change.

**Trace:** Related lesson(s) in `lessons-learned.md`, related PRs / issues. Optional.
```

---

## 2026-05-16 — Adopt agentic-harness patterns (structured output, focused tasks, run artifacts) into ravenclaude-core

**Context:** A Grok analysis of `agentic-harness` (Rust agent SDK) surfaced four patterns worth absorbing into ravenclaude-core: schema-guided + delimited structured outputs, focused-task delegation discipline, standardized per-run artifacts, and explicit context hygiene. Two "proposal" documents (`ENHANCEMENT_README.md` at repo root, `docs/ENHANCEMENT_PROPOSAL.md`) captured the rationale for adopting them.

**Options considered:**
- Adopt all four patterns immediately as mandatory — pros: maximum lift, sharp posture. Cons: would mandate output formats that no current agent emits, creating a half-state where docs say one thing and agents do another.
- Adopt partially (write the docs, retrofit agents later) — pros: incremental, lower risk. Cons: creates the half-state described above.
- Reject — pros: simpler. Cons: leaves real reliability gains on the table.

**Chosen:** Adopt the patterns into core `CLAUDE.md` as **roadmap / aspirational** rather than mandatory, until the agent retrofit ships. The Structured Output Protocol is documented as the target format; current agents continue using Markdown Output Contracts as the fallback.

**Reasoning:** Mandating an output format no agent actually uses misleads consumers (they'd expect parseable JSON from sub-agent handoffs and get prose). The doc-only adoption keeps the design committed and visible without lying about the runtime state. The retrofit can land per-agent as each is touched.

**Consequences:** Future agent edits should add the `---RESULT_START--- … ---RESULT_END---` block to that agent's Output Contract. When all 23 agents emit it, the Structured Output Protocol section in `plugins/ravenclaude-core/CLAUDE.md` can be promoted from "Roadmap" to "Active." Other patterns (focused tasks, run artifacts, context hygiene) remain in core CLAUDE.md as guidance.

**Trace:** The two proposal documents were deleted in this same change — their content is now in `plugins/ravenclaude-core/CLAUDE.md` (Structured Output Protocol section, Focused Task Execution section, Run Artifacts standard) and this decision-log entry. The `structured-output` skill referenced by the original proposal does not yet exist in `plugins/ravenclaude-core/skills/`; that's a follow-up item.

---

_Older entries below as they accumulate._
