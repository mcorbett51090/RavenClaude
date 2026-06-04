---
target_path: plugins/ravenclaude-core/skills/spec-reread-ritual/SKILL.md
description: Before writing any code for a task in a multi-task build, the agent MUST re-read the relevant spec section verbatim, paste it into the work log, and quote the prior. NO work from memory. Counters the "100% spec drift" failure mode from the Claude Code bug study (issue #19739) — where 11/11 sessions drifted from the spec and exact-match format compliance was 0%.
allowed-tools: Bash, Read, Grep
audience: [coder, architect, any sub-agent executing a brief]
counters_failure_modes: [T-3 silently dropped requirements, T-10 gaslighting/semantic inversion, T-12 self-awareness != behavioral change, T-7 lost-in-context]
sources:
  - /tmp/research-codex-failure-modes.md §3c (Claude Code issue #19739), §5 M-11, §8 #5/#6, §9a
---

# spec-reread-ritual

Before each task in a multi-task build, the agent re-reads the named section of the brief **verbatim** and pastes it into the work log. **No work from memory.** Quote, don't summarize — summary is where drift starts.

## The failure mode it counters

GitHub issue [anthropics/claude-code#19739](https://github.com/anthropics/claude-code/issues/19739) is the gold-standard primary source. Quantified findings over 11 systematic sessions:

- **Spec drift in 11/11 sessions (100%).** Convergence to spec never achieved.
- **Format-string exact-match rate: 0%.** The agent reproduced the *idea* of the format but never the exact string.
- **3+ unauthorized actions per session.**
- **Pattern 1.3 — Selective Hearing:** "'6 columns, same width' → heard '6 columns', ignored 'same width'."
- **Pattern 2.1 — Interpretive Compliance:** "Agent treats exact specifications as 'goals' rather than 'requirements'. Produces 'reasonable approximations' instead of literal matches."
- **Pattern 2.3 — Memory-based reconstruction.** The agent thinks it knows the spec, paraphrases from a fading working memory, and silently substitutes adjacent-but-wrong values.
- **Pattern 3.1 — Self-Awareness Does NOT Prevent Failure:** "Agent correctly identifies its own failure patterns, immediately reproduces them while documenting them."

The two interventions that **broke** the loop in [13]:

1. **Re-read spec before each step (not from memory)** — this skill.
2. **Step-by-step verification with grep/diff required** — see ``outcome-evidence/SKILL.md`` (deferred).

Source: research §3c + §5 M-11.

## When to invoke

- **Before the first line of any task** in a multi-task brief.
- **Before each `git commit`** — paste the just-completed task's acceptance criteria and grade each one with evidence.
- **After any session restart, context compaction, or model swap** — drift accumulates fastest across these boundaries.
- **Before responding to a correction** — the user said "you got X wrong"; re-read X verbatim before defending or conceding.

## The ritual

1. **Identify the relevant section of the spec by file path and §header.** Not by recollection — by path.
2. **Read it via the Read tool** (or `cat`-equivalent if Read is unavailable). Do not type it from memory.
3. **Paste it verbatim into the work log** under a `## Spec re-read — {timestamp} — {section}` heading. No edits, no normalizations, no "essentially this says."
4. **Quote the acceptance criteria as a checklist** — one line per criterion. This is the contract.
5. **Identify any criterion the just-prior work might have dropped** and flag it explicitly before writing more code.

## The "quote, don't summarize" rule

Summary is where drift starts. The agent's working memory of "the spec said 6 columns same width" decays in 200 tokens to "6 columns" — Pattern 1.3 in [13]. Verbatim quoting resets the working memory each task.

Example — wrong shape:

> The spec says we need a 6-column grid with consistent widths.

Example — right shape:

> Quoting psm-brief.md §3.2 verbatim:
>
> > GIVEN viewport 1440px THEN `.kpi-grid` has `computedStyle.gridTemplateColumns === "repeat(6, 1fr)"`
>
> Acceptance criteria:
> - [ ] 6 columns
> - [ ] each column 1fr (equal width)
> - [ ] grid template literally `repeat(6, 1fr)` (not the equivalent `1fr 1fr 1fr 1fr 1fr 1fr`)

The third criterion is the one Pattern 1.3 systematically drops.

## Hash-and-compare (the deterministic enforcement)

The skill's engine computes a SHA-256 hash of the just-quoted section and compares it to the hash from the previous invocation in this session. If the hashes differ:

- **The spec changed mid-build** — flag it; re-run the prior tasks against the new spec if any criterion changed.
- **OR** the agent paraphrased rather than re-reading — refuse to proceed; force a Read tool call.

## Composition with other skills

- **`prior-art-quote`** — before the *first* Write of a task, also quote the closest existing helper/component (counters T-7 lost-in-context).
- **`outcome-evidence`** — every "done" claim carries the command output that proves it (Pattern 5.1 counter).
- **`validator-handoff`** — after the task, a fresh validator independently re-reads the same spec and grades the work.

The three together implement the §8 #5/#6/#16/#17 stack from the research report.

## Anti-patterns

| Symptom | Why it's drift |
|---|---|
| "Per the spec, we need to..." (no quote) | Working from memory — Pattern 2.3 |
| "Essentially the spec says..." | Paraphrase — Pattern 2.1 (interpretive compliance) |
| Re-using a prior task's quoted spec for a new task | Stale context — drift across task boundary |
| Quoting the spec but then writing code that doesn't pass the just-quoted criteria | Self-awareness ≠ change — Pattern 3.1 |
| Skipping the re-read because "I already read it earlier this session" | The exact failure mode that 100% of sessions in [13] exhibited |

## What "done" looks like

The skill succeeds when, for the just-completed task:

1. The spec section was quoted verbatim into the work log (with file path + §header).
2. The acceptance criteria are listed as a checklist.
3. Each criterion is matched against the just-written code (via grep/diff/test output) before commit.
4. The hash of the quoted section matches what the next task will re-read (drift detector).

## Sources

- GitHub issue [anthropics/claude-code#19739](https://github.com/anthropics/claude-code/issues/19739) — patterns 1.3, 2.1, 2.3, 3.1, 4.3 (research ledger [13])
- Chris Ebert — *Notes from Code with Claude 2026* (ledger [14])
- Addy Osmani — *How to write a good spec for AI agents* (ledger [17])
- Vadim's blog — *The Agent That Says No* (ledger [30])

Full ledger: `/tmp/research-codex-failure-modes.md` §Sources.
