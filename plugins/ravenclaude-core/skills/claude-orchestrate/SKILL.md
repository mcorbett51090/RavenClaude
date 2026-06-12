---
name: claude-orchestrate
description: One-off Claude orchestration — route this task through Claude's brain even when the host CLI is Copilot/GPT/Grok. The `orchestrator:` knob in comfort-posture.yaml sets the always-on default; this skill is for on-demand invocation.
allowed-tools: Bash, Read
---

# Skill: claude-orchestrate

Route the current task through a Claude brain via `claude -p`, even when the host CLI is GitHub Copilot (GPT/Grok). The `orchestrator:` knob in `.ravenclaude/comfort-posture.yaml` gates team-dispatch automatically; invoke this skill for a **one-off** use without touching the posture.

---

## When to use

- You are in a Copilot/Codex/Grok session and the team-dispatch quality is poor.
- You want a one-shot Claude reasoning pass on a specific task brief.
- The always-on knob is `off` but you want Claude for this one dispatch.

**Under Claude Code (`THING_HOST == claude-code` or unset):** the host IS Claude — this skill is a no-op. It will tell you so clearly.

---

## Step 1 — Host check

Read `THING_HOST` from the environment.

- `THING_HOST == claude-code` or empty → print:
  > "Host is Claude Code (or unset). This skill is a no-op here — the host already IS Claude. Nothing to do."
  And stop.
- `THING_HOST == copilot` (or any non-`claude-code` value) → continue to Step 2.

---

## Step 2 — Read the knob and choose mode

Read `.ravenclaude/comfort-posture.yaml` → `orchestrator:` field.

| Value | Mode | Meaning |
|---|---|---|
| `off` | — | Knob is off; for one-off use, default to `full` unless the user specified a mode. |
| `decide` | `decide` | Claude returns a JSON dispatch plan; you execute it. |
| `full` or absent | `full` | One Claude call reasons through the task and returns artifact content. |

The user may override with an explicit `--mode decide` or `--mode full` argument in their invocation.

---

## Step 3 — Validate the brief

The brief is the skill's first positional argument (everything after `/claude-orchestrate`). If no brief was provided, print:

> "Usage: /claude-orchestrate <task brief>  
> Example: /claude-orchestrate plan the auth refactor across three services  
> Use --mode decide or --mode full to override the knob."

And stop.

---

## Step 4 — Print the cost note (required)

Before invoking, always print one line:

```
[claude-orchestrate] Routing to Claude via claude -p (mode: <decide|full>). One Claude call; +tokens.
```

This is the explicit cost disclosure. Cost is opt-in per invocation — the user sees it before any token is consumed.

---

## Step 5 — Invoke `claude-orchestrate.sh`

Run:

```bash
RAVENCLAUDE_ORCH_BRIEF="<the brief>" \
  bash plugins/ravenclaude-core/scripts/claude-orchestrate.sh <mode>
```

For `decide` mode, also pass the agent roster JSON if you have one:

```bash
RAVENCLAUDE_ORCH_BRIEF="<brief>" \
RAVENCLAUDE_ORCH_ROSTER='<roster json>' \
  bash plugins/ravenclaude-core/scripts/claude-orchestrate.sh decide
```

**FAIL-SAFE:** any non-zero exit means fall back to host orchestration. The script's own guards handle:

| Exit | Cause | Your action |
|---|---|---|
| 1 | Empty brief | Tell the user (Step 3 should have caught this) |
| 2 | `claude` CLI not in PATH | "claude CLI not found. Run under a session where `claude` is on PATH (e.g. after `npm install -g @anthropic-ai/claude-code`). Host handles orchestration." |
| 3 | `claude -p` call failed / `is_error` | "Claude call failed (auth, quota, or transient). Host handles orchestration as usual." |
| 7 | Recursion guard fired | "Re-entrant orchestration refused. This skill was invoked inside a tribunal seat — host handles orchestration." |
| 8 | Secret-shaped material in brief | "Secret-shaped material in brief — not sent to Claude. Remove any credentials from the task description and try again." |
| 9 | Relay-all egress floor blocked | "Relay-all egress floor: repo may hold PII and destination is not proven in-tenant/ZDR. Enable via Bedrock/Vertex, `orchestrator_zdr_confirmed: true`, or `orchestrator_repo_pii: false` in comfort-posture.yaml." |

---

## Step 6 — Surface the result

**`decide` mode:** the script returns a JSON dispatch plan:
```json
{"agents": [...], "parallelism": "sequential|parallel", "reasoning": "..."}
```
Parse the plan and execute it using the `spawn-team` dispatch sequence (Step 5 of `spawn-team`).

**`full` mode:** the script returns the artifact content directly (code, markdown, JSON, or whatever the task produces). Write it to the appropriate target path or return it inline.

---

## Security note

The `claude -p` call in `claude-orchestrate.sh` is the same proven pattern as the tribunal seats:
- Runs from a scratch `mktemp` dir — no project `CLAUDE.md` is loaded.
- `--tools ""` — the nested session has zero tools; no recursive dispatch or file writes.
- Secret scrub via `_scrub.sh` — the brief never egresses if it contains secret-shaped material.
- Three-layer recursion guard — re-entrant calls are refused.

**The `claude -p` execution path requires a security-reviewer sign-off before this feature reaches production consumers.** This is called out in the PR.
