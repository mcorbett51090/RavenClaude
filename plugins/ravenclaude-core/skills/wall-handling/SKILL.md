---
target_path: plugins/ravenclaude-core/skills/wall-handling/SKILL.md
description: When an agent hits a wall (same tool + same error 3+ times, an impossible TypeScript fix, a missing API surface, a failing test it can't resolve in one attempt), STOP — do not invent the API, do not delete the prop, do not '@ts-ignore'. Take the documented default with an inline comment, or ask the user. Counters the "agents push forward through impossible tasks" failure mode (Cognition/Devin retrospective + Claude Code spec-drift study).
allowed-tools: Bash, Read, Grep
audience: [architect, coder, security-reviewer, any sub-agent in a multi-task build]
counters_failure_modes: [T-4 going off-script when stuck, T-11 wall-hit loop without adaptation, T-10 gaslighting/semantic inversion]
sources:
  - /tmp/research-codex-failure-modes.md §3a (Devin), §3c (Claude Code issue #19739), §5 M-10, §8 #11, §9a
---

# wall-handling

Routes an agent's "I hit a wall" moment through a documented ladder of responses — **re-read the prior → take the documented default with an inline comment → ask the user** — instead of the failure mode where the agent invents an API, deletes the failing prop, swaps `@ts-ignore` in, or loops on the same tool call.

## When to invoke

The skill fires on these observable signals:

- Same `(tool, error)` fingerprint repeated **3+ times** in a single session (the loop signature)
- A TypeScript / lint / compile error the agent cannot resolve in **one** attempt
- A test that has failed **3 attempts** after seemingly-correct fixes
- A required package or API surface that "should" exist but doesn't (no `node_modules` entry; `command not found`; `404` from the API)
- Any moment the agent is about to write `// @ts-ignore`, `// eslint-disable`, `if False:`, delete a failing assertion, or rename a JSON field to avoid a parse error

## The failure mode it counters

Cognition's 2025 Devin annual review and the SitePoint Devin Aftermath piece both name **"pushes forward with impossible tasks rather than escalating"** as the central Devin failure mode — iterating a doomed plan instead of saying "this needs a human decision." Claude Code issue [anthropics/claude-code#19739](https://github.com/anthropics/claude-code/issues/19739) ([13] in the research ledger) corroborates this with patterns 4.1 (Going off-script when stuck), 4.3 (Tool Avoidance), and 5.1 (Verification Theater) — the agent simulates progress by deleting the constraint instead of solving it.

Source: research §3a + §3c + §4 T-4/T-11.

## The ladder

Walk these in order. Stop at the first one that resolves.

### Rung 1 — Re-read the prior

1. Locate the relevant brief / spec / `psm-brief.md` / `AGENTS.md` section / decision tree.
2. **Quote it verbatim into the work log.** Do not summarize.
3. Ask yourself: did the spec already prescribe the default for this situation? Did it forbid the workaround you were about to apply?

This rung catches the case where the wall isn't real — the spec already names the answer and the agent was mid-drift.

### Rung 2 — Take the documented default with an inline comment

If the spec names a default for the silent case, **apply it inline with a citation comment**:

```ts
// PSM-DEFAULT (psm-brief.md §3.2): chart background is theme.surface.subtle
// because the spec leaves color silent — do not invent a custom shade
background: 'var(--theme-surface-subtle)',
```

```python
# PSM-DEFAULT (psm-brief.md §Acceptance Criteria): when fixture lacks
# an explicit min_cell, default to n>=10 per ferpa-aggregate-threshold-defaults.md
min_cell = config.get("min_cell", 10)
```

The inline comment is **load-bearing**: it tells the next reader (human or agent) *why* the default was taken and which document authorized it. No silent decisions.

### Rung 3 — Ask the user

If the spec is silent AND no documented default exists, **stop and ask** — do not guess.

The mandatory phrasing:

> "I hit a wall on [specific mechanical cause — the status code, the test failure, the missing API]. I tried [Approach A → outcome], [Approach B → outcome]. The spec is silent on [the underlying question]. I did NOT take an alternative action because [why the alternatives I could think of would be a silent decision]. I recommend either [option 1] or [option 2]. Which?"

This is the same shape as the Capability Grounding Protocol's mandatory-phrasing block, applied to the wall moment.

## Anti-patterns (the things this skill exists to prevent)

| The agent is about to... | Why it's a wall-hit failure | What this skill says |
|---|---|---|
| Write `// @ts-ignore` to silence a type error | Going off-script when stuck (T-4) | STOP — re-read the type definition, then ask |
| Delete the assertion in a failing test | Test theater (T-5) | STOP — the test is telling you the contract is broken |
| Rename a JSON field to match what the code expects | Schema drift (T-6) | STOP — confirm which is canonical, the fixture or the code |
| Invent a Recharts prop / OpenAI parameter that "should" exist | Hallucinated API surface (T-2) | STOP — read the actual library/API docs; ask if missing |
| Retry the same failing call a 4th time | Wall-hit loop (T-11) | STOP — same `(tool, error)` 3+ times is the loop signature |
| Add a `// TODO: figure out why` and ship | Verification theater (T-9) | STOP — a TODO is not a fix; tee up the real question |
| "Stub" the missing dependency and commit | Going off-script (T-4) | STOP — the dependency is missing; ask before stubbing |

## Loop-fingerprint detection (the M-10 mechanic)

The skill's harness keeps a per-session table of `(tool_name, error_class)` fingerprints. After 3 identical fingerprints, the harness halts execution and emits the Rung 3 message. RavenClaude's Sága-log substrate (`.ravenclaude/runs/`) is where the fingerprint table lives.

## Composition with CGP

The Capability Grounding Protocol's alternate-methods rule fires *before* the wall — when Approach A fails, enumerate B/C/D and try the next-easiest. **This skill fires after** — when even the alternate-methods enumeration has hit a dead end, or when the agent is about to take a silent harmful action. CGP catches "I gave up too early"; wall-handling catches "I refused to give up at all."

## What "done" looks like for this skill

A wall-handling invocation succeeds when the agent has:

1. **Re-read the prior** (and pasted it into the work log)
2. **Either applied a documented default with inline citation OR escalated to the user with the mandatory phrasing**
3. **Logged the wall + resolution** to `.ravenclaude/runs/walls/` so the next session can learn from it

## Sources

- Cognition AI — *Devin's 2025 Performance Review* (research ledger [2])
- SitePoint — *Devin Aftermath: AI Engineers in Production* (research ledger [6])
- GitHub issue [anthropics/claude-code#19739](https://github.com/anthropics/claude-code/issues/19739) — patterns 4.1, 4.3, 5.1 (ledger [13])
- Anthropic Engineering — *Effective harnesses for long-running agents* (ledger [15])
- Beginners in AI — *Why AI Coding Agents Fail: The 9 Failure Modes and the Fix* (ledger [29])
- MatrixTrak — *Agent keeps calling same tool: why autonomous agents loop forever* (ledger [29])

Full ledger: `/tmp/research-codex-failure-modes.md` §Sources.
