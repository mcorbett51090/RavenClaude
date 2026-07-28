---
name: external-agent-onboarding
description: Onboards a non-Claude-Code coding agent (GitHub Copilot CLI / OpenAI Codex CLI / Cursor / Aider / Windsurf) to this repo at session start. Use when this repo will be operated on by an agent that does not natively read CLAUDE.md. Routes through AGENTS.md, then layers the per-host wiring, version floors, and failure-mode mitigations that host actually needs.
target_path: plugins/ravenclaude-core/skills/external-agent-onboarding/SKILL.md
last_reviewed: 2026-07-28
audience: [external-coding-agent, copilot-cli-user, codex-user, cursor-user, aider-user]
sources:
  - https://github.com/github/copilot-cli/blob/main/changelog.md (retrieved 2026-07-28)
  - ../../knowledge/copilot-cli-customization.md
  - ../../knowledge/codex-cli-customization.md
  - ../../knowledge/host-support.json
---

# external-agent-onboarding

> **Renamed 2026-07-28 (multi-host audit MH-23). Was `codex-onboarding`.** The old name owned the
> Codex discovery keyword while the content was almost entirely Copilot- and Cursor-specific — it had
> no Codex row in its version table, no `codex --version`, and no mention of `.agents/skills`,
> `sandbox_mode`, or `/hooks`. A name is read as a support claim. Same defect class as Gate 70's old
> label (MH-31), one directory away.
>
> **Its evidence base was also unfalsifiable:** every factual row cited
> `/tmp/research-codex-2026-updates.md`, a path that **does not exist on any machine**
> `[verified 2026-07-28: No such file or directory]`. This repo's own rule (`AGENTS.md`) requires a
> durable consequential claim to cite a check a later reader can actually run. Every surviving row
> below is re-sourced to a linkable URL with a retrieval date; **rows that could not be re-sourced
> were deleted, not re-dated.**

Cross-tool onboarding: gives a non-Claude-Code agent the context Claude Code gets from `CLAUDE.md`,
without assuming it has read it. **The one doc every supported host reads is `AGENTS.md`** — start
there, then read *your host's* section below. They are not interchangeable.

## First five minutes (every host)

1. **Read `AGENTS.md` end-to-end.** Canonical cross-tool guidance. The testing-instructions section
   and the layout-allow-list discipline are load-bearing — don't skim them.
2. **Read `.repo-layout.json`.** Every new file path MUST match an `allowed_globs` entry. CI fails
   otherwise, and the local hook fires only on Write/Edit/MultiEdit — not on `mkdir -p`.
3. **Read the relevant plugin's `CLAUDE.md`.** Despite the name it is that plugin's team constitution
   and is not Claude-specific.
4. **Skim `plugins/ravenclaude-core/skills/`** and match skill descriptions against your task.
5. **Read your host's section below** — wiring, version floor, and the failure mode specific to it.
6. **Read the document map first, if one exists.** A repo-root `DOCUMENT-MAP.md` resolves a
   known-document lookup in ~1 tool call instead of a find/grep sweep. Mechanism:
   [`../../knowledge/copilot-cli-customization.md`](../../knowledge/copilot-cli-customization.md) §7.

## Before every edit batch

- **Decision-tree intake** — which workflow am I in (new file / edit existing / refactor / spec-driven
  build)? Refuse the "do a little of each" path.
- **Spec-reread ritual** ([`../spec-reread-ritual/SKILL.md`](../spec-reread-ritual/SKILL.md)) if it has
  been > 30 min OR > 15 files since the last re-read.
- **Diff-budget check** ([`../diff-budget/SKILL.md`](../diff-budget/SKILL.md)) — compact past ~60% fill.

## Before every PR open

- **Spec-reread ritual** — non-negotiable; goal drift is a dominant agent failure mode and mechanical
  re-anchoring is the fix.
- **Validator handoff** — `scripts/audit-gates.sh` + `prettier --check .` + JSON-validity on touched
  manifests + `bash -n` on touched shell scripts.
- **Layout-allow-list discipline** — run the verification snippet in `AGENTS.md`.
- **Decision-review for yes/no calls** — route through the tribunal if the posture allows; otherwise
  escalate explicitly using the mandatory phrasing.

---

# Your host

**Which components actually run on your host is not a matter of opinion** — it is recorded in
[`../../knowledge/host-support.json`](../../knowledge/host-support.json), the single source of truth,
and every cell that says "no" says why. If this file and that map ever disagree, **the map wins.**

## GitHub Copilot CLI

**Wiring:** `ravenclaude install` (the default host). Skills symlink into `.claude/skills`; guardrails
are written **repo-level** to `.github/hooks/ravenclaude.json` and translated by the Copilot adapter.

**Three things that will bite you, all verified:**

1. **Plugin-level hooks do not fire.** [github/copilot-cli#2540](https://github.com/github/copilot-cli/issues/2540)
   — **still OPEN, re-checked 2026-07-28.** This is *why* the guardrails ship repo-level rather than
   bundled in the plugin. Do not "simplify" that; it is the workaround, not an oversight.
2. **There is no per-tool `matcher`.** Copilot's hooks config has no tool-scoping field, so every
   registered hook sees every tool call and must self-filter. See
   [`../../knowledge/copilot-cli-customization.md`](../../knowledge/copilot-cli-customization.md) §4.
3. **Tool-name VALUES are lowercase** (`bash`, `edit`, `view`) where Claude sends PascalCase. The
   adapter normalises them; before that fix the tribunal and web guard were silent no-ops.

**Version floor — `copilot --version`.** Each row quotes the changelog verbatim and links it. Rows
whose original justification could not be found in the changelog were **deleted.**

| Floor | Verbatim changelog entry | Why it matters here | Source · retrieved |
|---|---|---|---|
| **≥ 1.0.52** (2026-05-23) | *"Hooks (preToolUse, postToolUse, subagentStart, subagentStop) now fire correctly for sub-agent tool…"* | **The safety floor.** Below it a sub-agent's tool calls are **not** hooked — a subagent runs Bash past every guardrail this repo wires, silently. | [changelog.md](https://github.com/github/copilot-cli/blob/main/changelog.md) · 2026-07-28 |
| **≥ 1.0.57** recommended (2026-06-01) | *"Plugins auto-installed from repository settings no longer leak into user global config"* | Config hygiene — a repo's plugin settings otherwise bleed into your global config. | [changelog.md](https://github.com/github/copilot-cli/blob/main/changelog.md) · 2026-07-28 |
| 1.0.62 informational (2026-06-13) | *"PostToolUse hook matchers (e.g. Edit-pipe-Write) are now honored instead of silently dropped"* | **NOT a floor for this repo** — our generated Copilot hooks file carries no matchers (see #2). Listed so nobody re-derives it as one. | [changelog.md](https://github.com/github/copilot-cli/blob/main/changelog.md) · 2026-07-28 |

> **DELETED rows, and why — do not restore them without a source.** The previous table claimed a
> *"preToolUse silent-allow regression fixed (1.0.59)"* and a *"diff-not-reported-to-ACP bug fixed
> (1.0.48)"*. **Neither appears anywhere in the changelog** `[checked verbatim 2026-07-28]`. It also
> attributed the config-leak fix to **1.0.56**; the real entry is **1.0.57** (1.0.56 is a different
> fix — *"Repository plugin overrides no longer change globally enabled plugin settings"*). And it
> asserted **Cursor ≥ 3.3** with no citation of any kind.

`ravenclaude install` and `ravenclaude status` check this automatically and warn below 1.0.52 —
because a floor nobody checks is a floor that protects nobody.

## OpenAI Codex CLI

**Wiring:** `ravenclaude install --host codex`. **Supported since 2026-07-28** (audit MH-07).

- **Skills → `.agents/skills`**, NOT `.claude/skills`. Codex scans `.agents/skills` in every directory
  from cwd up to the repo root, then `$HOME/.agents/skills`, then `/etc/codex/skills`
  `[docs-verified — learn.chatgpt.com/docs/build-skills]`. Several third-party guides say
  `.codex/skills`; **they are wrong.**
- **Hooks are native — there is no adapter, and there must not be one.** Codex speaks the Claude hook
  contract: identical PascalCase events, identical stdin fields, identical `exit 2` blocking,
  identical PascalCase tool-name values. Only two env vars are missing (`CLAUDE_PROJECT_DIR`,
  `CLAUDE_SESSION_ID`), lifted from the stdin payload by a small shim.
- **⚠ Hook trust is HASH-BASED — this is the one that will silently disarm you.** Codex marks new or
  changed hooks for review and **skips them until trusted**. This repo updates by `git pull`, so
  **every update invalidates every changed hook.** Run **`/hooks`** inside Codex and re-trust, after
  every update. Nothing will tell you — the SessionStart banner is itself a hook. For teams,
  `requirements.toml` managed hooks are the only unattended-survival path. **Do not reach for
  `--dangerously-bypass-hook-trust`** — that is governance theatre (see anti-patterns).
- **The OS sandbox is your real boundary, and it is ON by default.** `sandbox_mode` ∈ `read-only` |
  `workspace-write` (default) | `danger-full-access`, × `approval_policy` ∈ `untrusted` |
  `on-request` | `never` — both **top-level** keys in `config.toml`. It applies to **spawned commands**,
  not just built-in file ops, so it closes the subprocess gap no tool-layer deny can.
- **Config precedence:** `~/.codex/config.toml`, then a project `.codex/config.toml` layered over it —
  **which loads only in TRUSTED projects**, and cannot override `profile`/`profiles`/auth/provider
  keys. The installer projects your comfort posture into it and **never weakens an existing value.**
- **Version check:** `codex --version`. **No version floor is asserted**, because none has been
  verified against a durable changelog — and this file no longer invents floors.

Full contract: [`../../knowledge/codex-cli-customization.md`](../../knowledge/codex-cli-customization.md).

## Cursor · Aider · Windsurf

**Not wired. Nothing installs guardrails, skills, or agents for these hosts today**, and this file will
not pretend otherwise — a false claim of support is worse than an admitted gap, because it stops
anyone from building the bridge that would make it true.

- **Aider** reads `CONVENTIONS.md`, and **only on explicit opt-in** (`--read` / `.aider.conf.yml`). It
  does **not** auto-read `AGENTS.md`; this repo asserted otherwise until 2026-07-28 and was wrong
  `[docs-verified — aider.chat/docs/usage/conventions.html]`.
- **Cursor**'s documented mechanism is `.cursor/rules/*.mdc`; `AGENTS.md` auto-load is unconfirmed.
- **Windsurf** is unverified, and the product was reportedly renamed to Devin Desktop.

If you are on one of these, read `AGENTS.md` by hand and treat every guardrail in this repo as
**advisory** — none of them will fire for you.

---

## Anti-patterns

| Anti-pattern | Where it bites |
|---|---|
| **Assuming hook denials fire on an old Copilot** | < 1.0.52 — sub-agent tool calls are unhooked. Check `copilot --version`. |
| **Assuming Codex hooks are trusted after an update** | Hash-based trust; a `git pull` disarms them until `/hooks`. |
| **Bypassing a trust gate to make trust convenient** | `--dangerously-bypass-hook-trust` is **governance theatre** — a control that looks thorough and constrains nothing. Audit the must-fail path instead. |
| **Wiring Codex skills into `.claude/skills`** | Codex never reads it. The install "succeeds" and wires nothing. |
| **Building a Codex envelope adapter** | Codex already speaks the contract. A second Copilot-shaped translation layer is the expensive wrong answer. |
| **Runaway-cost recursive loop** | Bound retries; cap recursive depth. |
| **Memory wall** | Context overflow + instruction dilution + state loss. See [`../wall-handling/SKILL.md`](../wall-handling/SKILL.md). |
| **Citing an unfalsifiable source** | The defect that produced this rewrite: every row here once cited a `/tmp` path no reader could check. Cite a URL with a retrieval date, or delete the claim. |

## What done looks like

1. `AGENTS.md` read end-to-end; the testing checklist internalized.
2. `.repo-layout.json` `allowed_globs` understood.
3. The relevant plugin's `CLAUDE.md` read.
4. **Your host's section above read**, and your version verified with the right command —
   `copilot --version` / `codex --version`. Not "etc."
5. **If you are on Codex:** `/hooks` run, and the RavenClaude hooks confirmed **trusted**.
6. The intake / spec-reread / diff-budget / validator-handoff loop is in working memory.
7. The document map (if any) read.

## See also

- [`../diff-budget/SKILL.md`](../diff-budget/SKILL.md) · [`../wall-handling/SKILL.md`](../wall-handling/SKILL.md) · [`../spec-reread-ritual/SKILL.md`](../spec-reread-ritual/SKILL.md)
- [`../../knowledge/host-support.json`](../../knowledge/host-support.json) — **which components run where; the map wins over this file**
- [`../../knowledge/copilot-cli-customization.md`](../../knowledge/copilot-cli-customization.md) · [`../../knowledge/codex-cli-customization.md`](../../knowledge/codex-cli-customization.md)
- [`../../CLAUDE.md`](../../CLAUDE.md) — the team constitution this skill mirrors
- [`../../../../docs/best-practices/agent-onboarding.md`](../../../../docs/best-practices/agent-onboarding.md)
