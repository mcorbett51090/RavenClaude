# Guardrails for bounded autonomy in Claude Code — research (2026-05-29)

> Commissioned by Matt: "put guardrails on Claude so it can truly be autonomous based on my input — auto can hallucinate and go down a rabbit hole destroying things along the way, and edit-approved and plan modes are too high-touch." This is the primary-source research backing the command-review assessment (`docs/command-review-autonomy-assessment-2026-05-29.md`) and the guardrail recommendations for RavenClaude.

## The reframing that dissolves the false choice

The pain reads as a single dial — per-edit approval ↔ `bypassPermissions` — but Claude Code exposes **seven independent layers**, and **four of them run deterministically with zero human interruption**. "Bounded autonomy" = fixing the *envelope* up front (deterministically) so only genuine novelty ever reaches the human.

The three failure modes map to three different layers; conflating them is why "auto vs. plan" felt binary:

| Failure mode | What it actually is | Solved by (no human in loop) |
|---|---|---|
| **Destroying things** | a *containment* problem | sandbox + deny rules + git/worktree |
| **Going down rabbit holes** | a *termination/scope* problem | Stop hooks, iteration caps, scoped subagents, a spec |
| **Hallucinating** | a *verification* problem | test-gating, evidence-before-done, adversarial review |

None of these requires per-edit approval.

## Layer 1 — Permission rules: the static deterministic envelope

`allow` / `ask` / `deny` in `settings.json`, evaluated **deny → ask → allow; first match wins, deny always precedes**. Enforced **by Claude Code, not the model** — CLAUDE.md text is advisory and cannot change what's allowed.

- **Tool-scoped deny rules are the hard floor**: `deny: ["Bash(git push --force *)", "Edit(/migrations/**)", "Read(//**/.env)"]`. A bare name (`Bash`) strips the tool from context; a scoped rule leaves the tool but blocks matches.
- **File-path scoping** uses gitignore semantics with four anchors (`//abs`, `~/home`, `/project-root`, `cwd-relative`).
- **Precedence guarantee**: a deny in *any* scope beats an allow in *any* other, and **managed settings cannot be overridden by `--allowedTools` or even `bypassPermissions`**. A deny is the only truly unbreakable boundary.
- **Documented fragility**: argument-constraining Bash *allow* patterns are "fragile" — beaten by flag reordering, protocol swaps, redirects, variables, and env-runner passthroughs (`devbox run`, `npx`, `docker exec`) that aren't wrapper-stripped. Anthropic's own guidance: don't constrain Bash args with allow patterns — deny the binary outright or use a PreToolUse hook.

**Touch: deterministic / no interrupt** (except `ask`, which should be empty in unattended mode).

## Layer 2 — Permission mode: how the un-ruled remainder is handled

| Mode | Un-ruled calls | Interrupt? | Fit |
|---|---|---|---|
| `default` | reads auto; else prompts | interrupts | per-edit babysitting (rejected) |
| `acceptEdits` | edits + cwd file ops auto | partial | iterate-while-watching |
| `plan` | read-only | interrupts at plan | the other rejected option |
| **`auto`** | **classifier reviews each call** | classifier / no interrupt | **the middle ground** |
| `dontAsk` | **denies** anything not pre-approved | deterministic / no interrupt | locked-down CI |
| `bypassPermissions` | everything | none | containers only |

**`auto` mode is the headline answer** (v2.1.83+, Opus/Sonnet 4.6+, Anthropic API, research preview). A **separate classifier model reviews each action before it runs**, blocking anything that "escalates beyond your request, targets unrecognized infrastructure, or appears driven by hostile content Claude read":

- **Blocked by default**: `curl|bash`, external exfil of sensitive data, prod deploys/migrations, mass cloud-storage deletion, IAM grants, modifying shared infra, irreversibly destroying pre-session files, **force-push or pushing to `main`**.
- **Allowed by default**: local cwd file ops, installing declared deps, reading `.env` and sending creds to *their matching* API, read-only HTTP, pushing to the branch you started on / Claude created.
- **Anti-rabbit-hole brake (built in, not configurable)**: block **3× consecutively or 20× total** → auto mode pauses to prompting (interactive) or **aborts the session** (in `-p`).
- **Spoken boundaries become block signals** ("don't push until I review") — **but not durable**: re-read from transcript each check, **lost on context compaction**. For a hard guarantee the docs say use a **deny rule**, not a spoken boundary.
- **Injection-hardened**: classifier sees user messages + tool *calls* + CLAUDE.md, but **tool results are stripped**; a server-side probe pre-scans results.
- On entering auto mode, broad code-exec allow rules (`Bash(*)`, package-run, `Agent`) are **dropped** and restored on exit — no accidental blank check.

**`dontAsk`** is the deterministic sibling for headless/CI: every would-be prompt becomes a **denial**; only `allow`-matches and read-only Bash run. No classifier latency, no model in loop.

**Protected paths** (every mode but `bypassPermissions`): `.git`, `.claude` (most), `.mcp.json`, shell rc, `.gitconfig` are never auto-approved — protects repo + agent config from self-modification.

## Layer 3 — Hooks: the deterministic enforcement plane

Docs are explicit: *"Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens."* **Hooks run even in `bypassPermissions`.**

- **PreToolUse** is the only event that can *prevent* a call: returns `permissionDecision: deny|ask|allow|defer` + reason, **and can rewrite the call via `modifiedInput`** (swap a destructive command for a safe one). A hook *block* short-circuits before rules; a hook *allow* does **not** bypass deny/ask rules — so **hooks can only tighten, never loosen**. Exactly the safety property wanted.
- **PostToolUse** `decision: "block"` feeds an error back to force a fix (lint/test failed → keep working).
- **Stop / SubagentStop** `decision: "block"` (or exit 2) **refuses to let the turn end** — the deterministic definition-of-done gate. Force-overridden after **8 consecutive Stop blocks** (can't deadlock).
- **PostToolBatch** can stop the loop before the next model call — a batch-level kill switch.
- Hook handler types include `"prompt"` (model yes/no) and `"agent"` (spawn a verification subagent) — a hook can run a cheap LLM check deterministically at a gate. **(This is exactly what RavenClaude's tribunal does.)**

**Touch: deterministic / no interrupt** — the purest "bounded by up-front input" layer.

## Layer 4 — Sandboxing & blast-radius containment (OS-level)

OS-enforced filesystem/network isolation for the Bash tool + children (Seatbelt on macOS, bubblewrap+socat on Linux/WSL2). Key property: *"the OS enforces the boundary on the running process… regardless of what the model chose to run and even if an allowed command does more than its name suggests"* — survives injection and mislabeled commands.

- **Filesystem**: default = write only cwd+subdirs, read everything except `denyRead`. **Default gap**: `~/.aws/credentials` and `~/.ssh` are *readable* by default — add them to `denyRead`.
- **Network**: no domains pre-allowed; out-of-sandbox proxy. **Limitation**: proxy does no TLS inspection, so a broad `github.com` allow enables domain-fronting exfil — use a MITM proxy if the threat model needs it.
- **`autoAllowBashIfSandboxed: true` (default)** is the autonomy unlock: sandboxed Bash runs **without prompting even with `ask: Bash(*)`** — the sandbox boundary substitutes for the prompt. Composes with `auto` mode.
- **Self-protection**: sandbox auto-denies writes to its own `settings.json` at every scope.
- **Org lockdown**: `failIfUnavailable: true` + `allowUnsandboxedCommands: false` (kills the `dangerouslyDisableSandbox` escape hatch).
- **Heavier**: Anthropic dev container (non-root; blocks `--dangerously-skip-permissions` as root). **Git worktrees** are an explicit blast-radius control — isolated checkout/branch, discardable; `WorktreeCreate/Remove` hook events gate them.

**Touch: deterministic / no interrupt** once configured.

## Layer 5 — Anti-hallucination & anti-rabbit-hole: verification + termination

Anthropic: *"Claude stops when the work looks done. Without a check it can run, 'looks done' is the only signal… you become the verification loop. Give Claude something that produces a pass or fail, and the loop closes on its own"* — claimed **2–3× quality** from a self-verification path.

Four gate strengths (increasing determinism):
1. **In-prompt**: "run tests, iterate until they pass, show output." No setup.
2. **`/goal` condition**: a separate evaluator re-checks a stated condition every turn until it holds.
3. **Stop-hook gate**: turn can't end until a script's check passes (force-override after 8). Strongest *unattended* definition-of-done.
4. **Adversarial subagent review**: a fresh-context reviewer sees only diff + criteria, not the reasoning that produced it — *"the agent doing the work isn't the one grading it."* (`/code-review`).

**Evidence-before-done** is explicit: show test output / the command + what it returned / a screenshot — never assert success.

Anti-rabbit-hole specifics: the 3/20-block and 8-Stop-block caps are non-negotiable runaway brakes; "the infinite exploration" is a named failure — scope narrowly or delegate to subagents so exploration burns the *subagent's* context; context degradation itself drives rabbit holes ("performance degrades as context fills"); **self-grading is unreliable** — use fresh context. Over-review caution: a reviewer asked for gaps "will usually report some, even when the work is sound" → ask only for correctness/requirement gaps.

## Layer 6 — Scope confinement (bound to the spec)

- **Subagent `tools:` frontmatter is an allowlist** — omit it and the subagent inherits *everything* incl. Bash. Documented horror story: a refactor agent that inherited Bash "decided it could test its refactor by running `git reset`… wiping 40 minutes of uncommitted work." **Ship every agent with an explicit `tools:` line.** A read-only researcher gets `Read, Grep, Glob` and literally cannot write.
- **`Agent(Name)` deny rules / `--disallowedTools`** disable specific subagents.
- **Self-contained `SPEC.md` then fresh session**: interview the human, write the spec (files/interfaces in scope, explicit out-of-scope, an end-to-end verification step), execute clean. *"Time spent making the spec precise pays off more than time spent watching the implementation."* — the literal embodiment of "autonomy bounded by up-front input."
- **`--allowedTools` on `claude -p`** scopes each headless invocation.
- **Current limitation**: open request [#30161](https://github.com/anthropics/claude-code/issues/30161) for `denyMainOnly` (restrict a tool to subagents only) — today you compose mode + per-agent allowlists.

## Layer 7 — Observability, checkpoints, rollback

- **Native OpenTelemetry**: logs/metrics/traces with no plugins — every prompt, tool/MCP call (params, success/fail, duration), which policy decided each action, which hooks ran. Point `OTEL_EXPORTER_OTLP_*` at a collector/SIEM. Framing: permissions/hooks/sandbox decide what's *allowed*; OTel shows what *happened*.
- **Checkpoints / `/rewind`**: auto-snapshot before each change; restore conversation/code/both. **Caveat: tracks only Claude's changes, not external processes — not a git replacement.**
- **Git as the real rollback substrate**: commit per step; auto mode refuses force-push and direct-to-`main`.

## Industry framing

- **Human-on-the-loop vs in-the-loop**: per-edit/plan = *in*-the-loop; bounded autonomy = *on*-the-loop (set the envelope, supervise exceptions/exit). Safe transition = *progressive validation* (staged like autonomous driving) — earn autonomy on a task class after it repeatedly passes verification.
- **NIST AI RMF Agentic Profile (2025)** maps ~1:1 onto Claude Code's stack: tool-use risk = rules + classifier; runtime governance = hooks + sandbox; delegation chains = subagent scoping + auto-mode subagent checks; accountability = OTel.
- **AURA** formalizes autonomy risk assessment with agent-to-human escalation — the principle behind auto mode's "block-then-fall-back-to-human" and the tribunal's `defer`.

## Synthesized recommendation — the layered "bounded autonomy" stack

**A. Containment (set-and-forget) — stops "destroying things"**
1. Run in a disposable container or **git worktree** (isolated, discardable).
2. **Enable the sandbox**: `autoAllowBashIfSandboxed: true`, `denyWrite` outside cwd, `denyRead: ["~/.aws","~/.ssh"]`, tight `allowedDomains`. Org/CI: `failIfUnavailable: true` + `allowUnsandboxedCommands: false`.
3. **Hard deny rules in *managed* settings**: force-push, push-to-`main`, prod/migration, `Edit(/migrations/**)`, secret reads, deletes outside cwd. Deny is the only unbreakable boundary — put irreversible/high-blast actions here, never in a spoken "don't."

**B. Disposition (no per-edit prompts) — the middle ground itself**
4. **`auto` mode** for interactive-but-unattended (classifier + 3/20 brake). **OR `dontAsk` + explicit `allow`-list** for fully-headless `claude -p`.
5. **`allow: ["Bash"]` + a PreToolUse hook** denying the dangerous subset — unprompted Bash with a deterministic floor that survives `bypassPermissions`.

**C. Scope — stops "rabbit holes" (part 1)**
6. **Write a self-contained `SPEC.md` up front**, execute in a fresh session.
7. **Every subagent gets an explicit `tools:` allowlist**; PreToolUse layout hook rejects off-spec writes.

**D. Verification — stops "hallucinating" + "rabbit holes" (part 2)**
8. **Stop-hook definition-of-done gate**: turn can't end until tests/build/lint pass (override after 8).
9. **Adversarial fresh-context review** before done (`/code-review` or a scoped reviewer subagent).
10. **Demand evidence** in the prompt — test output / command results / screenshots.

**E. Observability & recovery — supervise the exception, not the step**
11. **Pipe OTel to a collector/SIEM**; PostToolUse audit-log hook as backup.
12. **Commit per step**; rely on `/rewind` for in-session try/revert (≠ git for external changes).

**Why this is bounded autonomy, not babysitting:** Layers A, C, D, E are 100% deterministic — configured once from the up-front input, they fire without interrupting. Layer B (`auto`'s classifier) is the only model-in-the-loop piece and interrupts **only** on the 3rd-consecutive/20th-total genuine boundary hit. The human moves from *in* the loop (approving each action) to *on* the loop. The agent's freedom is real, but **deny rules + sandbox + Stop-hook gate + scoped subagents form a fixed box it cannot reason, hallucinate, or be injected out of** — because those four are enforced by Claude Code and the OS, not by the model.

**The single most important principle:** *spoken/CLAUDE.md boundaries are advisory and lost to compaction; only deny rules, hooks, and the sandbox are enforced.* For anything you truly cannot tolerate, **constrain the agent — don't tell the agent.**

## Sources

Primary (Anthropic, fetched May 2026): [Configure permissions](https://code.claude.com/docs/en/permissions) · [Permission modes](https://code.claude.com/docs/en/permission-modes) · [Sandboxing](https://code.claude.com/docs/en/sandboxing) · [Hooks reference](https://code.claude.com/docs/en/hooks) · [Best practices](https://code.claude.com/docs/en/best-practices) · [Agent SDK permissions](https://code.claude.com/docs/en/agent-sdk/permissions) · [Sub-agents](https://code.claude.com/docs/en/sub-agents) · [Worktrees](https://code.claude.com/docs/en/worktrees) · [Monitoring](https://code.claude.com/docs/en/monitoring-usage) · [Dev container](https://code.claude.com/docs/en/devcontainer).

Practitioner/framework: Jakub Kontra (hooks); Dotzlaw (deterministic control); PubNub (subagent best practices); TrueFoundry / trailofbits / Shaharia Azam (sandboxing & Docker isolation); SigNoz & General Analysis (OTel); NIST AI RMF Agentic Profile (CSA); AURA & Three-Pillar (arXiv); Falconer (levels of autonomy). Two anthropic.com engineering posts 403'd and are cited via their corroborated docs equivalents.

**Caveats:** `auto`-mode version/model/provider requirements and the 3/20-block & 8-Stop-block thresholds are explicit in the docs and **not configurable**. `denyMainOnly` is an open feature request (roadmap signal, not shipped).
</content>
</invoke>
