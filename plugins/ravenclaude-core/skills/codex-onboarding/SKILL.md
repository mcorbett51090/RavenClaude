---
name: codex-onboarding
description: Onboards a non-Claude-Code agent (GitHub Copilot CLI / Cursor / Aider / Codex / Devin) to this repo on session start. Use when this repo will be operated on by a coding agent that does NOT natively read CLAUDE.md. Mirrors what CLAUDE.md provides to Claude Code, but routes through AGENTS.md (which all major 2026 agents read) and surfaces tool-version floors + 2026 H1 failure-mode mitigations.
target_path: plugins/ravenclaude-core/skills/codex-onboarding/SKILL.md
last_reviewed: 2026-07-08
audience: [external-coding-agent, codex-user, copilot-cli-user, cursor-user, aider-user]
sources:
  - /tmp/research-codex-2026-updates.md §1-§3, §7-§8 (Q1-Q2 2026 changes + 2026 best-practices consensus)
---

# codex-onboarding

Cross-tool onboarding skill: gives a non-Claude-Code agent the equivalent context Claude Code gets from `CLAUDE.md`, without assuming the agent has read it. **The single-source-of-truth doc all 2026 agents read is `AGENTS.md`** — this skill points there first, then layers in the 2026 H1 mechanical mitigations the marketplace expects.

## When to invoke

- First five minutes of every Codex / Copilot CLI / Cursor / Aider / Devin session against this repo.
- After a tool-version update where the agent's behavior contract may have changed.
- When `git fetch` shows main has moved during a long-running session (re-anchor).

## First five minutes (every session)

1. **Read `AGENTS.md` end-to-end.** It is the canonical cross-tool guidance. Don't skim; the testing-instructions section + the layout-allow-list discipline are load-bearing.
2. **Read `.repo-layout.json`.** Every new file path MUST match an `allowed_globs` entry. CI fails the build otherwise — the local hook fires only on Write/Edit/MultiEdit, not on `mkdir -p`.
3. **Read the relevant plugin's `CLAUDE.md`.** Despite the name, it is the team constitution for that plugin and is not Claude-specific. It carries the cross-tool house opinions every agent must enforce.
4. **Skim `plugins/ravenclaude-core/skills/`** for skills relevant to your task. The descriptions are written third-person and include trigger language — match against your task.
5. **Identify your tool's plugin/hook surface and version floor** (§Tool-version floors below).
6. **Read the document map first, if there is one.** If the repo root has a `DOCUMENT-MAP.md` (or an inline topic→path index in `AGENTS.md`), read it before any find/grep — it resolves a known-document lookup in ~1 tool call. Absent + the repo has a substantial docs tree → offer to seed one via `scripts/generate-document-map.py` (then hand-curate the topic labels); a repo with < ~20 docs doesn't need one. Mechanism: [`../../knowledge/copilot-cli-customization.md`](../../knowledge/copilot-cli-customization.md) §7; pattern: [`../../../../docs/best-practices/agent-onboarding.md`](../../../../docs/best-practices/agent-onboarding.md).

## Before every edit batch

- **Decision-tree intake**: which workflow am I in (new file / edit existing / refactor / spec-driven build)? Refuse the "do a little of each" path — the 2026 consensus is that conditional-workflow framing is what keeps agents on track.
- **Spec-reread ritual** ([`../spec-reread-ritual/SKILL.md`](../spec-reread-ritual/SKILL.md)) if it's been > 30 min OR > 15 files since the last re-read.
- **Diff-budget check** ([`../diff-budget/SKILL.md`](../diff-budget/SKILL.md)) — context fill % AND per-PR file count. Compact past ~60% fill.

## Before every PR open

- **Spec-reread ritual** — non-negotiable. The 2026 H1 retrospectives identified "goal drift" as one of six dominant agent-specific failure modes; mechanical re-anchoring at structured intervals is the consensus fix.
- **Validator handoff** — run `scripts/audit-gates.sh` + `prettier --check .` + JSON-validity on touched manifests + `bash -n` on touched shell scripts. The "validate-immediately" pattern is in Anthropic's Skills best-practices doc and was the highest-leverage mitigation for "tool-call chaos" (one of three dominant 2026 failure clusters per the H1 100-deployment retro).
- **Layout-allow-list discipline** — run the verification snippet in `AGENTS.md` § "Layout-allow-list discipline (added 2026-05-21 after PR #32 failed)".
- **Decision-review for yes/no calls** — if the active comfort-posture allows tribunal routing, use it; if not, escalate to the user explicitly with the mandatory phrasing.

## Tool-version floors (June 2026)

| Tool | Minimum version | Why this floor |
|---|---|---|
| **GitHub Copilot CLI** | **≥ 1.0.59** | preToolUse silent-allow regression fixed (1.0.59); diff-not-reported-to-ACP bug fixed (1.0.48); plugin auto-install global-config leak fixed (1.0.56). Earlier versions silently swallow hook denials. |
| **Cursor** | **≥ 3.3** | `/multitask` parallel agents + Composer 2.5 file-tree refactor. Cursor 2.x single-file inline edits don't match the marketplace's batch-edit semantics. |
| **Claude Code** | **latest** | Plugin marketplace first-class; `reloadSkills` hook output; expanded hook event set. |
| **Aider** | **latest with architect/editor pair** | The architect-plans + editor-emits-diff pattern measurably reduces multi-file refactor errors. |
| **Devin** | **latest** | Devin's "last 30% problem" is documented; expect human-review checkpoints for breaking API changes. |

`[verify-at-use — 2026-06-04 — Copilot CLI changelog versions per /tmp/research-codex-2026-updates.md §1]`

## The 2026 H1 mechanical mitigations (run before declaring "done")

These four mitigations are the cross-source 2026 consensus for keeping a coding agent in the loop:

1. **Validator handoff after every multi-file edit batch larger than 3 files.** Anthropic's validate-immediately pattern; mechanical, fast, mandatory.
2. **Per-call timeout + idempotency key + bounded retries on every mutating tool call.** "Tool-call chaos" is one of three dominant 2026 failure clusters; this is the mechanical fix.
3. **Compact proactively past ~60% context fill.** The 2026 rule of thumb is budget by fill %, not token count (Chroma 2025 context-rot study + Anthropic context-editing study showing 29-39% perf gain).
4. **Decision-tree workflow framing.** "Creating new content? → Follow Creation workflow. Editing existing content? → Follow Editing workflow." Anthropic's named "Conditional workflow pattern" — the 2026 canonical shape.

## Anti-patterns (2026 H1 named distinctly)

| Anti-pattern | Origin |
|---|---|
| **Silent-allow on preToolUse error** | Copilot CLI < 1.0.59 — DO NOT ASSUME hook denial works on older versions |
| **Plugin auto-install leaking into global config** | Copilot CLI < 1.0.56 |
| **Diff-not-reported-to-ACP-client** | Copilot CLI < 1.0.48 — wrappers were blind to multi-file edits |
| **Runaway-cost recursive loop** | Indie Hackers 2026: $4K/mo projected hit $11.2K in three weeks. Bound retries; cap recursive depth. |
| **"Last 30% problem"** | Devin's named failure: features need multiple human-feedback rounds. Surface the 30% explicitly. |
| **Governance theatre** | Security/approval workflows that look thorough but don't actually constrain. Audit the must-fail path. |
| **Memory wall** | Context overflow + instruction dilution + error accumulation + state loss + evaluation blindness. See [`../wall-handling/SKILL.md`](../wall-handling/SKILL.md). |

## What done looks like

A codex-onboarding invocation succeeds when:
1. `AGENTS.md` has been read end-to-end and the testing-instructions checklist is internalized.
2. `.repo-layout.json` `allowed_globs` is understood and the verification snippet has been bookmarked.
3. The relevant plugin's `CLAUDE.md` has been read.
4. The tool's version floor has been verified (`gh copilot --version` / `cursor --version` / etc.).
5. The decision-tree intake / spec-reread / diff-budget / validator-handoff loop is in the agent's working memory for the session.
6. The repo's document map (if any) has been read, so known-document lookups cost ~1 tool call, not a find/grep sweep.

## See also

- [`../diff-budget/SKILL.md`](../diff-budget/SKILL.md) — fill-% gating + per-PR file budget.
- [`../wall-handling/SKILL.md`](../wall-handling/SKILL.md) — memory-wall recovery.
- [`../spec-reread-ritual/SKILL.md`](../spec-reread-ritual/SKILL.md) — anti-drift mechanic.
- [`../../CLAUDE.md`](../../CLAUDE.md) — the team constitution this skill mirrors.
- `AGENTS.md` (at the repo root) — canonical cross-tool guidance (read this first).
- [`../../../../docs/best-practices/agent-onboarding.md`](../../../../docs/best-practices/agent-onboarding.md) — give a cold agent a document map (session-start discovery); mechanism in [`../../knowledge/copilot-cli-customization.md`](../../knowledge/copilot-cli-customization.md) §7.
- [`docs/best-practices/2026-q1-q2-failure-modes.md`](../../../../docs/best-practices/2026-q1-q2-failure-modes.md) — the H1 2026 failure-mode catalog.
