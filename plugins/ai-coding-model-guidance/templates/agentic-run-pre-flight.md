> **Use for:** a pre-run checklist before launching an autonomous AI coding agent task (Copilot coding agent, Codex CLI autonomous mode, or Grok API agent). Complete every section before starting the run. A partially-completed checklist is not a completed checklist.

---

# Agentic Run Pre-Flight Checklist

**Task name / reference:** [ticket / PR / short description]
**Date:** [YYYY-MM-DD]
**Run initiated by:** [developer name or agent]

---

## 1. Task scope (required before running)

- **Start state:** [branch name, file state, test status — what exists right now]
- **End state:** [testable criterion — how you will know the task is done]
- **Repos in scope:** [explicit list]
- **Files allowed to modify:** [glob pattern or explicit list]
- **Files NOT to touch:** [migrations, infra, secrets, any exclusions]
- **External calls permitted:** [none / read-only API calls / [specific APIs]]

---

## 2. Blast radius classification

- [ ] **Low** — reversible; local files only; no external state
- [ ] **Medium** — PR opened or test suite modified; reversible via PR close
- [ ] **High** — database writes / deploy trigger / secret rotation / force-push

> If High: a human approval gate is required before the run starts and before each irreversible step. Document the gate holder: [name / role]

---

## 3. Model selection

| Decision | Value |
|---|---|
| Platform | [GitHub Copilot / OpenAI Codex / xAI Grok] |
| Model tier | [Balanced default / Raised reasoning / Frontier] |
| Reasoning level (Codex only) | [low / medium / high / max / n/a] |
| Model id (verify-at-use) | [id or "see lineup — verify before running"] |
| Rationale | [1 sentence: why this tier for this blast class] |

---

## 4. Context demand check

- Estimated demand tier: [Low / Medium / High / Very High]
- Chunking required: [yes / no]
- If yes — sub-tasks defined: [yes / no / list]

---

## 5. Recovery plan

- What does the agent do on unexpected state mid-run? [halt and report / continue with flag / other]
- Checkpoint points: [list any explicit human-review points during the run]
- Rollback procedure: [git reset to branch HEAD / PR close / other]

---

## 6. Org policy check

- [ ] Verified the selected model is not blocked by org model rules
- [ ] API key in use is scoped appropriately for this run
- [ ] No compliance flag requires security-reviewer approval before running

---

## Sign-off

- [ ] All sections above are complete
- [ ] A second reviewer has signed off (required for High blast-radius runs): [name]
- **Run approved:** [yes / pending — reason]
