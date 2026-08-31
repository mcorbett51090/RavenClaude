# Parked — analog-repos leftovers (pickup sheet)

**Date:** 2026-08-14 · **Owner:** Matt  
**Increment:** `analog-repos-gap-fill` — **closed**. Do not reopen it.  
**This file is the pickup sheet** for the next session. The increment itself is done.

Written for an agent that does **not** have this session’s transcript. Read this file, then the cited sources. Do not re-derive the analog survey.

## Say this to pick one up

Copy one line into a fresh window. Do not `/fork`. Do not `/compact`.

| Pick | Exact prompt |
|---|---|
| **Q1 / L4** MCP quarantine | `Forge leftover Q1 — MCP result quarantine as its own plan. Read docs/follow-ups/2026-08-14-analog-repos-leftovers.md first. Do not extend the WebFetch sanitizer matcher with mcp__.` |
| **Q2** closeness scorecard | `Forge leftover Q2 — analog closeness scorecard skill as its own plan. Read docs/follow-ups/2026-08-14-analog-repos-leftovers.md first.` |
| **Hygiene** stale analog worktrees | `Clean the analog-repos stale worktrees listed in docs/follow-ups/2026-08-14-analog-repos-leftovers.md. Use the cleanup-worktrees skill. Do not force-delete.` |
| **This checkout is stale** | `Work from a tree that has origin/main. Do not edit plugins on a behind-main checkout.` |

Host-agnostic spawn (same as any other parked task):

```text
cd <project-root-that-is-on-origin/main>
grok "Continue task analog-repos-leftovers in this repo. Read .ravenclaude/runs/analog-repos-leftovers/handoff.md first (then meta.json, decisions.md, summary.md if present). Fresh window. Do not /fork. Do not /compact. Do not re-derive the brief from history you do not have. Execute the next steps in the brief."
```

If that run dir is missing, **this file is the brief**. The increment run dir lives only on the machine that wrote it (gitignored).

## Status — do not redo

| Item | Status | Cite |
|---|---|---|
| Survey N=13 (cap 30, shortfall 17) | **closed** — honest. Do not pad to 30. | [catalog](../plans/2026-08-14-analog-repos-gap-fill/catalog.md) |
| F1 WebFetch sanitizer | **shipped** #928, `0.267.0`, hooks 34 | [decision](../decisions/2026-08-14-analog-repos-gap-fill.md) |
| F2 injection + minting evals | **shipped** #929 | same |
| F3 docs promote | **shipped** on `main` | same |
| Same-host handoff spawn | **shipped** #934, `0.269.0`, hooks 35 | #934 |
| Draft plan #926 | closed as superseded | — |

Next plugin-touching PR verifies HEAD and bumps to **0.270.0**. Do not reuse 0.267.0 / 0.268.0 / 0.269.0.

## Parked items

### 1. Q1 / L4 — MCP result quarantine

**Trigger to unpark:** owner asks for MCP quarantine, or a judged hole shows unsanitized `mcp__.*` tool output reaching the model.

**What it is:** PostToolUse `updatedToolOutput` matcher for `mcp__.*`, same fail-open contract as F1. **Product-shaped default change** — needs its own `/forge` and a House Rule 3 walkthrough. Depends on F1 already shipped.

**What it is not:** adding `mcp__.*` to `sanitize-webfetch-output`’s existing matcher. That is explicitly banned until this forge lands.

**Acceptance:** same fail-open fixtures on an MCP-shaped payload; House Rule 3 walkthrough; version **0.270.0+**.

**Queue row:** [pr-queue.md](../plans/2026-08-14-analog-repos-gap-fill/pr-queue.md) Q1.

### 2. Q2 — analog closeness scorecard skill

**Trigger to unpark:** owner asks for the scorecard. Surface budget for the analog increment already spent the one counted class (the WebFetch hook).

**What it is:** a skill that recomputes M/H/G/O/E/I/T/V + closeness from analog evidence. Must-fail fixture required.

**What it is not:** a fourth analog fill. Not a reason to add a hook.

**Queue row:** pr-queue.md Q2.

### 3. Hygiene — merged analog worktrees

**Trigger to unpark:** any session in the Grok `update` worktree (or after it is gone, any session that still sees these paths).

Attached under `/Users/matthewcorbett/.grok/worktrees/matthewcorbett-ravenclaude/update/.claude/worktrees/`:

| worktree | branch | note |
|---|---|---|
| `feat-webfetch-sanitize` | `feat/ravenclaude-core-webfetch-sanitize-hook` | F1 — merged #928 |
| `feat-injection-evals` | `feat/evals-injection-minting-cases` | F2 — merged #929 |
| `feat-handoff-same-host` | `feat/ravenclaude-core-handoff-same-host` | #934 — merged |
| `forge-analog-repos-gap-fill` | `forge/analog-repos-gap-fill` | survey branch — merged / superseded |

Use `cleanup-worktrees`. Close the VS Code tab for each lane first. `git branch -d` only, never `-D`, unless the user approves.

`forge-copilot-forge-helpers` is **not** analog leftovers. Leave it.

### 4. Stale `~/RavenClaude` checkout

**Trigger to unpark:** a session whose `git status -sb` shows `behind origin/main` on `~/RavenClaude`.

That tree is the shared anchor and is often many commits behind. The analog increment was finished in the Grok `update` worktree at `b2e7114c`. Do not land plugin edits on a stale `main`. Pull into a new worktree, or work in a tree that already has `origin/main`.

## Do-not-redo (copy into any new forge)

- Do not rebase or re-merge #928 / #929 / #934.
- Do not claim 30 gold analogs. N=13.
- Do not add `mcp__.*` to the WebFetch sanitizer matcher without a new forge (L4).
- Do not bump `ravenclaude-core` to 0.267.0 / 0.268.0 / 0.269.0.
- Do not use `grok -p`, `--single`, `/fork`, or a Grok SessionStart injection to continue.

## Where the files live

| Tier | Path | Who sees it |
|---|---|---|
| **Committed (this file)** | `docs/follow-ups/2026-08-14-analog-repos-leftovers.md` | every clone after pull |
| Catalog / matrix / queue | `docs/plans/2026-08-14-analog-repos-gap-fill/` | every clone |
| Close-out decision | `docs/decisions/2026-08-14-analog-repos-gap-fill.md` | every clone |
| Local leftover run | `.ravenclaude/runs/analog-repos-leftovers/` | this machine |
| Closed increment run | `.ravenclaude/runs/analog-repos-gap-fill/` | machine that wrote the handoff (update worktree) |
| Survey harvest | `.ravenclaude/runs/forge/analog-repos-gap-fill/` | same, gitignored |
| Stream | `rc streams set-active analog-repos-leftovers` | this machine; SessionStart can suggest it |

## Next plugin bump

**0.270.0** after verifying HEAD. Serial `plugin.json` ban from the analog increment is lifted.
