# Multi-host audit — Round 1 — Lens: **OpenAI Codex CLI**

**Auditor:** Claude model reasoning *about* Codex CLI (not Codex itself). Every finding is tagged
`[verified]` (this-session file/command check), `[docs-verified]` (URL given), or `[inferred]`.
**Date:** 2026-07-28 · **Repo root:** `/Users/matthewcorbett/RavenClaude`

---

## 0. Verdict in one paragraph

**RavenClaude is not fit to serve a Codex CLI operator today, and the reason is the opposite of what
the repo assumes.** The marketplace treats "non-Claude host" as a synonym for "GitHub Copilot CLI" —
one installer, one adapter, one generated projection, one dashboard install tab, all Copilot. Codex
gets a name on a skill, a name on a CI gate, and a sentence in `AGENTS.md`. Meanwhile Codex CLI has
converged on the **Claude Code hook contract almost exactly** — same event names, same stdin field
names, same `hookSpecificOutput.permissionDecision` / `updatedInput` / `additionalContext` envelope,
same `exit 2 + stderr = block` semantics, and a plugin loader that reads a plugin's `hooks/hooks.json`
directly `[docs-verified]`. Copilot needed a 456-line generator **plus** a ~300-line envelope adapter
because its envelope differs; **Codex needs neither.** The Codex lane is therefore not merely a stub —
it is the *cheapest* host to support properly and the one the repo has invested the least in. What is
genuinely missing and genuinely hard is the **trust/approval mapping**: Codex owns an OS-level sandbox
and a 6-layer `config.toml` precedence chain that RavenClaude's comfort-posture engine cannot currently
address at all, and Codex's per-hook **hash-based trust** silently disarms modified hooks — which
directly breaks RavenClaude's headline "an update is just `git pull`" pillar.

### Ground truth used (docs-verified)

| Fact | Source |
|---|---|
| Hook events: `SessionStart` `SessionEnd` `PreToolUse` `PermissionRequest` `PostToolUse` `PreCompact` `PostCompact` `UserPromptSubmit` `SubagentStart` `SubagentStop` `Stop`; schema `{"hooks":{Event:[{matcher, hooks:[{type:"command", command, timeout}]}]}}`; stdin `{session_id, transcript_path, cwd, hook_event_name, model, permission_mode, tool_name, tool_input, tool_use_id, tool_response}`; stdout `{continue, stopReason, systemMessage, hookSpecificOutput:{permissionDecision, updatedInput, additionalContext, decision}}`; **exit 2 = block (reason from stderr); other non-zero = "hook failure reported, processing continues"**; plugin-bundled hooks load from the plugin's `hooks/hooks.json` and receive `PLUGIN_ROOT` / `PLUGIN_DATA`; non-managed hooks are **hashed and trusted by hash** — a new *or modified* hook is skipped until reviewed via `/hooks` | https://learn.chatgpt.com/docs/hooks |
| Config at `~/.codex/config.toml` + project `.codex/config.toml`; precedence CLI flags > project (trusted only) > `--profile` > user > `/etc/codex/config.toml` > defaults; `approval_policy` ∈ {untrusted, on-request, never}; `sandbox_mode` ∈ {read-only, workspace-write, danger-full-access} | https://learn.chatgpt.com/docs/config-file/config-basic |
| Skills live in `$CODEX_HOME/skills` (default `~/.codex/skills`) and repo-local **`.agents/skills`**, scanned from cwd up to repo root; SKILL.md name+description, progressive disclosure, `/skills` or `$` to invoke | https://developers.openai.com/codex/skills |
| `CODEX_HOME`, `CODEX_SQLITE_HOME`, `CODEX_API_KEY`, `CODEX_ACCESS_TOKEN`, `CODEX_CA_CERTIFICATE`, `CODEX_NON_INTERACTIVE`, `CODEX_INSTALL_DIR`, `RUST_LOG`. **No documented env var is set inside a session to identify the host**; `shell_environment_policy` controls what the sandboxed shell inherits (`inherit = none|core`) | https://learn.chatgpt.com/docs/config-file/environment-variables |

---

## P0 — broken or blocking for this host

### P0-1 · There is no install/wiring path for Codex at all — the entire plugin is unreachable

**Evidence** `[verified]`
- `scripts/ravenclaude:2` — *"install / update the RavenClaude plugins for **GitHub Copilot CLI**"*. It is the only installer in the repo.
- `scripts/ravenclaude:10` — skills are symlinked into `<project>/.claude/skills`. `scripts/ravenclaude:137-142` does the `mkdir -p "$project/.claude/skills"`.
- `scripts/ravenclaude:13`, `:221` — MCP is merged into `${COPILOT_HOME:-$HOME/.copilot}/mcp-config.json`.
- `scripts/ravenclaude:183-217` — hooks are written to `.github/hooks/ravenclaude.json` **through `copilot-hook-adapter.sh`**.
- `scripts/generate-dashboards.py:6634` — the dashboard's only install surface is headed `Install RavenClaude &mdash; GitHub Copilot CLI`; `:6638` offers exactly one alternative: *"Using Claude Code instead? See the Claude Code guide."* `_INSTALL_COMMANDS` (`:1555-1580`) is five Copilot commands including `copilot --plugin-dir …`.

Codex reads skills from `$CODEX_HOME/skills` and `.agents/skills` `[docs-verified]` — **never `.claude/skills`** (that is Copilot's read path). It reads MCP from `~/.codex/config.toml` `[mcp]`, not `~/.copilot/mcp-config.json`. So `ravenclaude setup` run by a Codex operator completes "successfully" and wires **zero** skills, **zero** hooks, **zero** MCP into their host. Nothing in the repo tells them so.

**Remedy** — add a host dimension to the installer rather than a second installer:
`ravenclaude install --host codex` that (a) symlinks the 50 skills into `<project>/.agents/skills/` (repo-local, team-shareable — the better default) with a `--user` variant for `$CODEX_HOME/skills`, (b) writes `.codex/config.toml` `[mcp]` entries instead of `~/.copilot/mcp-config.json`, (c) emits `.codex/hooks.json` (see P0-2). Default `--host` by probing `command -v codex` / `command -v copilot`. In the dashboard, promote the install tab from a Copilot page with a Claude Code footnote to a **3-tab host switcher** (Claude Code · Copilot CLI · Codex CLI) — note this costs a Gate 132 DOM-ratchet raise, which per `plugins/ravenclaude-core/CLAUDE.md` is at zero slack and needs owner approval.
**Effort: M**

---

### P0-2 · The 18 hooks are structurally Codex-loadable but fail open on variable names alone

**Evidence** `[verified]`
- `plugins/ravenclaude-core/hooks/hooks.json:2` — `"$schema": "https://json.schemastore.org/claude-code-hooks.json"`; `:3` — *"Paths use `${CLAUDE_PLUGIN_ROOT}`"*.
- Every command is `${CLAUDE_PLUGIN_ROOT}/hooks/<script>.sh` (e.g. `hooks.json:11`, `:15`, `:19`).
- Five PostToolUse entries pass `"$CLAUDE_TOOL_FILE_PATH"` as argv (`hooks.json:11,15,19,25,31`).
- Across `plugins/ravenclaude-core/hooks/*.sh`: `CLAUDE_PROJECT_DIR` ×28, `CLAUDE_SESSION_ID` ×24, `CLAUDE_PLUGIN_ROOT` ×12, `CLAUDE_TOOL_FILE_PATH` ×6.
- `plugins/ravenclaude-core/hooks/_emit-event.sh:142` — `local project_dir="${CLAUDE_PROJECT_DIR:-}"`; the helper silently no-ops when it is empty.
- Event overlap is **6/6**: RavenClaude registers `PreToolUse`(5) `PostToolUse`(2) `Stop`(1) `UserPromptSubmit`(1) `SubagentStart`(1) `SessionStart`(1) — every one is a documented Codex event `[docs-verified]`.

Codex supplies `PLUGIN_ROOT` / `PLUGIN_DATA` to plugin hooks, and `cwd` / `session_id` **on stdin**, not as `CLAUDE_*` env vars `[docs-verified]`. Consequence `[inferred, from the two verified halves]`: `${CLAUDE_PLUGIN_ROOT}` resolves empty → the command string becomes `/hooks/format-on-write.sh` → non-zero, non-2 exit → Codex *"reports hook failure and processing continues"* `[docs-verified]`. **Every guardrail — the tribunal, the layout gate, the destructive-command guard, the runaway brake, the DoD gate — fails open**, and because `_emit-event.sh` no-ops without `CLAUDE_PROJECT_DIR`, `hook-events.jsonl` is never written, so the dashboard's entire **Guardrails** destination (Heimdall, Víðarr) and the SessionStart capability banner's "RECENT GUARDRAIL ACTIVITY" line render permanently empty. This is exactly the silent-green shape catalogued in the repo's own failure-mode index.

**Remedy** — a **20-line env shim**, not a Copilot-style envelope adapter. `hooks/codex-hook-shim.sh` that: exports `CLAUDE_PLUGIN_ROOT="${PLUGIN_ROOT:?}"`, tees stdin and exports `CLAUDE_PROJECT_DIR` from `.cwd` and `CLAUDE_SESSION_ID` from `.session_id`, derives `CLAUDE_TOOL_FILE_PATH` from `.tool_input.file_path`, then `exec`s the real hook with stdin replayed. **No JSON translation is needed in either direction** — verify field-by-field against the Codex hooks doc before writing a line. Ship a generated `codex/hooks.json` that wraps each existing entry through the shim. Belt-and-braces: change the failure mode from fail-open to loud by having the shim `exit 2` with a stderr reason if `PLUGIN_ROOT` is unset.
**Effort: S** (the shim) **/ M** (with the generated `codex/hooks.json` + a gate).

---

## P1 — significant gap; the host is materially underserved

### P1-1 · No generated Codex projection — and the record shows no decision to skip it

**Evidence** `[verified]`
- `plugins/ravenclaude-core/copilot/` exists (`AGENTS.md`, `README.md`, `plugin.json`, `agents/` ×15), generated by `scripts/generate-copilot-plugin.py` (456 lines) with a `--check` freshness gate.
- `find . -iname "*codex*"` returns 11 paths — 4 docs, 3 `ai-coding-model-guidance` files, 2 SVGs, the onboarding skill, the Gate 70 test. **No `codex/` directory, no `generate-codex-plugin.py`.**
- `.repo-layout.json` `allowed_globs` contains `plugins/*/copilot/**` but **not** `plugins/*/codex/**` — so a projection would be denied by `enforce-layout.sh` and `validate-layout.yml` until the glob is added.
- No `docs/decisions/` entry, no CLAUDE.md milestone, and no `Value-add completeness` table row dispositions Codex. It is an omission, not a documented N-A.

The asymmetry is the finding. `generate-copilot-plugin.py:11-16` records that the Copilot package declares **only `agents`** — *"NO `skills` / `hooks` keys … plugin-level preToolUse hooks don't fire in Copilot today (github/copilot-cli#2540)"*. Codex has no such defect: plugin-bundled hooks load from `hooks/hooks.json` and skills are a first-class plugin component `[docs-verified]`. **A Codex projection would be strictly more capable than the Copilot one already shipped, for less work.**

**Remedy** — `scripts/generate-codex-plugin.py`, sibling to the Copilot generator, byte-deterministic + `--check` gated, emitting `plugins/ravenclaude-core/codex/` with: `plugin.json` declaring `skills` **and** `hooks` (both of which Copilot's cannot), the 15 agents, `hooks.json` wrapped through the P0-2 shim, and a `codex/AGENTS.md` carrying the same accuracy-discipline + dashboard-launch blocks the Copilot projection carries (`copilot/AGENTS.md:20-64`). Add `plugins/*/codex/**` to `.repo-layout.json` **in the same commit** (the repo's own layout-discipline rule, `AGENTS.md:148-151`). Add the freshness `--check` to `validate-marketplace.yml`.
**Effort: M**

---

### P1-2 · `codex-onboarding` is a Copilot/Cursor skill wearing a Codex name

**Evidence** `[verified]` — `plugins/ravenclaude-core/skills/codex-onboarding/SKILL.md`
- `:45-52` "Tool-version floors" table rows: **GitHub Copilot CLI, Cursor, Claude Code, Aider, Devin**. There is **no Codex row.**
- `:82` "what done looks like": *"The tool's version floor has been verified (`gh copilot --version` / `cursor --version` / etc.)"* — no `codex --version`.
- `:66-74` anti-patterns: 3 of 7 are Copilot-CLI-version-specific, 1 is Devin-specific. None is Codex-specific.
- Nothing in the file mentions `approval_policy`, `sandbox_mode`, `~/.codex/config.toml`, `.agents/skills`, `$CODEX_HOME`, `/hooks`, `codex exec`, or Codex's own hook system.
- `:3` positions Codex 4th in a list of 5 hosts, yet Codex owns the skill's name.

A Codex operator who invokes the skill named for their host is taught about Copilot CLI's 1.0.59 `preToolUse` regression and Cursor's Composer refactor. The most Codex-relevant thing in the file is `:24` ("read `.repo-layout.json`") — good, generic advice.

**Remedy** — split. Keep a generic `external-agent-onboarding` (the first-five-minutes ritual, spec-reread, diff-budget, validator handoff — all genuinely portable), and add a real per-host section. The Codex section must carry: the `~/.codex/config.toml` ↔ `.codex/config.toml` precedence chain, `approval_policy` × `sandbox_mode` and how they interact with this repo's testing instructions, `.agents/skills` as the repo-local skills path, `/hooks` trust review, and `codex --version`. Cite the docs URLs inline per `AGENTS.md:206`.
**Effort: M**

---

### P1-3 · The onboarding skill's entire evidence base is a dead `/tmp` path

**Evidence** `[verified]`
- `SKILL.md:8` — `sources: - /tmp/research-codex-2026-updates.md §1-§3, §7-§8`.
- `SKILL.md:53` — `[verify-at-use — 2026-06-04 — Copilot CLI changelog versions per /tmp/research-codex-2026-updates.md §1]` — the sole provenance for the whole version-floor table.
- `ls /tmp/research-codex-2026-updates.md` → `No such file or directory`.
- `SKILL.md:5` — `last_reviewed: 2026-07-08`; the `verify-at-use` marker is dated 2026-06-04, now 7+ weeks stale.

This is the repo's own Claim-Grounding rule failing on the repo's own file: `AGENTS.md:206` requires a durable consequential claim to *"cite the this-session check that backs it inline"*. A `/tmp` path is **unfalsifiable by construction** — it cannot be checked by any later reader on any machine. Every version floor in the table is therefore an unmarked, trusted-looking prior with no recoverable source. This is the same shape the plugin constitution calls out as *"mirroring an unproven golden reference."*

**Remedy** — re-derive each row from a durable, linkable source and cite it inline as a markdown link (backticked paths are invisible to Gate 29's `check-md-links.py` — see `plugins/ravenclaude-core/CLAUDE.md` v0.194.0). Any row that cannot be re-sourced gets deleted, not re-dated. Add a `last_verified` per row.
**Effort: S**

---

### P1-4 · The trust/approval model does not map, and RavenClaude's containment guidance is wrong for Codex

**Evidence**
- `[docs-verified]` Codex's actual controls are `approval_policy` ∈ {untrusted, on-request, never} × `sandbox_mode` ∈ {read-only, workspace-write, danger-full-access}, resolved through six layers ending at `/etc/codex/config.toml`, plus `requirements.toml` managed policy (`allow_managed_hooks_only`) and MDM.
- `[verified]` RavenClaude's posture engine emits **only** `.claude/settings.json` `allow`/`ask`/`deny` rules — `plugins/ravenclaude-core/scripts/apply-comfort-posture.py` is the single translator; nothing in the repo writes `~/.codex/config.toml` or `.codex/config.toml`.
- `[verified]` `plugins/ravenclaude-core/CLAUDE.md` § "Containment posture" states: *"Claude Code can add an OS sandbox … but there is no evidence Copilot CLI honors it — so under Copilot the container/worktree is the containment, not the sandbox."* The section generalizes from Copilot to every non-Claude host.

That generalization is **false for Codex**, which ships its own OS-level sandbox as a first-class, default-on control `[docs-verified]`. A Codex operator reading RavenClaude's containment guidance is told to reach for a devcontainer when their host already holds the stronger, OS-enforced boundary — and is told nothing about the knob that actually governs their blast radius. The 12-category comfort-posture matrix has no projection onto `approval_policy` × `sandbox_mode` at all, so the dashboard's headline product (posture editing) does nothing for this host.

**Remedy** — two pieces, in order. (1) Correct the containment section: add a Codex row stating the OS sandbox **is** available and is the boundary, with the `sandbox_mode` values and what each permits. (2) Add a Codex emission target to `apply-comfort-posture.py` — a coarse but honest mapping (`security_deny` floor present + no `allow` on remote-mutate ⇒ `approval_policy = untrusted` + `sandbox_mode = read-only`; balanced ⇒ `on-request` + `workspace-write`; never auto-emit `danger-full-access` / `never`) written to `.codex/config.toml`, with a `posture-events.jsonl` entry like the existing path. State plainly in the dashboard that the Codex mapping is coarser than the Claude one — a 12-category matrix does not have 12 degrees of freedom on this host.
**Effort: L**

---

### P1-5 · Codex's hash-based hook trust breaks the "an update is just `git pull`" design pillar

**Evidence**
- `[docs-verified]` *"Codex hashes each hook and tracks trust by hash. New **or modified** hooks are marked for review and **skipped until trusted**. Users review via `/hooks`."* Plugin-bundled hooks use the same non-managed trust flow; installing a plugin does **not** auto-trust its hooks.
- `[verified]` `plugins/ravenclaude-core/CLAUDE.md` § GitHub Copilot CLI bridge: *"we deliberately do NOT use Copilot's install-and-cache mechanism … the plugin loads **live** … so an **update is just `git pull`**. No re-install, ever."* `scripts/ravenclaude:46` bakes this into the `rc` alias: `ravenclaude update && copilot --plugin-dir …`.

Under Codex the live-load pillar **inverts into a silent disarm**: every `git pull` that changes a byte of any hook script invalidates its hash, and that hook is then skipped until the user notices and runs `/hooks`. Given RavenClaude's release cadence (18 hooks, near-weekly plugin bumps), the steady state for a Codex consumer is *guardrails silently off after every update* — with no banner, because the SessionStart banner is itself a hook.

**Remedy** — (a) document it loudly in the Codex onboarding section and the generated `codex/AGENTS.md`: *after every `ravenclaude update`, run `/hooks` and re-trust.* (b) Make it mechanical: have `ravenclaude update --host codex` print the list of hooks whose hash changed and end with an explicit `Run /hooks in Codex to re-trust N hooks` line. (c) For teams, document the `requirements.toml` **managed-hooks** path — managed hooks are auto-trusted by policy and cannot be disabled `[docs-verified]`, which is the only configuration where RavenClaude's guardrails survive an update unattended on this host. Do **not** reach for `--dangerously-bypass-hook-trust`; naming it as the fix would be exactly the "governance theatre" anti-pattern the onboarding skill itself lists (`SKILL.md:73`).
**Effort: S** (docs + update-command line) **/ M** (managed-hooks guidance + template).

---

### P1-6 · The dashboard is Claude-Code-shaped throughout, and the in-flight host page excludes Codex by design

**Evidence** `[verified]`
- `scripts/generate-dashboards.py:2074-2078` — `_render_install_tab` docstring: *"Guides a **GitHub Copilot CLI** user to wire RavenClaude's agents/skills/hooks/MCP into Copilot."*
- `:6634`, `:6638` — the tab offers a binary: Copilot, or "Using Claude Code instead?". No third door.
- `:1646` — *"All 4 shipped commands are Claude Code slash commands"*; `:1704-1719` renders *"This is a Claude Code command. A web page can't run it for you… paste into Claude Code."* A Codex operator sees four commands they cannot run and no equivalent.
- `:328`, `:395` — the Help drawer is *"the About, **Claude Code**, **Copilot CLI**, and Commands"* sections; the Learn & Help blurb promises *"install & update guides for Claude Code and GitHub Copilot CLI"*.
- The one live host-awareness surface, `#/mimir`, is defined at `:457` as answering *"what does **Claude Code** know about this session?"* by reading `~/.claude/`.
- **The forthcoming fix excludes Codex too.** `docs/plans/2026-07-28-prompt-engineering-learn/plan.md` D3 ships a Control → "Host & context" page (`#/host-context`) whose entire job is *"which CLI · which files it reads, in order · what belongs in them · what is actually wired."* §6.1 binds it to **exactly three states** and states it *"NEVER renders 'GitHub Copilot CLI' in v1."* `grep -i "codex\|cursor\|aider\|windsurf" plan.md` → **zero matches** across 762 lines. So the page built to answer "which host am I in" will tell a Codex operator *"cannot determine."*

Also note `plan.md` §6.4 correctly forbids `os.environ` iteration and mandates a closed allow-list of probed names — the right call, and it means adding Codex is a one-constant edit, not a redesign.

**Remedy** — three cheap moves, none requiring the detection problem to be solved. (1) In `plan.md` §6.4's `_HOST_SIGNAL_NAMES` constant, add a **Codex** branch. Per the Codex env-var doc there is *no* documented in-session host marker `[docs-verified]`, so do **not** invent one — instead honor an explicit `host: codex` key in `.ravenclaude/comfort-posture.yaml` as a first-class positive signal, which is honest, user-controlled, and works for every future host. (2) Have the "what is actually wired" card check `.agents/skills/`, `.codex/config.toml`, and `.codex/hooks.json` alongside the Claude paths — booleans keyed off a fixed relative-path list, exactly as §6.4 already requires. (3) Retitle the Install tab and add the Codex column (see P0-1). The `#/mimir` reader stays Claude-only and should say so rather than being generalized.
**Effort: M**

---

## P2 — clear-value improvement

### P2-1 · `AGENTS.md` claims cross-tool canonicity, but its two operational sections are Claude-Code-only

**Evidence** `[verified]`
- `AGENTS.md:3` — *"Cursor, **OpenAI Codex CLI**, Aider, GitHub Copilot, and Windsurf read this file natively."*
- `AGENTS.md:16-21` — the **Setup commands** block is `/plugin marketplace add ./` + `/plugin install ravenclaude-core@ravenclaude` — Claude Code slash commands that do not exist in Codex.
- `AGENTS.md:25` — routes the reader to *"the dashboard's **Install a plugin (Bifröst)** tab (`/dashboard` → `#/bifrost`)"*. `/dashboard` is a Claude Code slash command (`plugins/ravenclaude-core/CLAUDE.md` § slash commands), and the Bifröst wizard's own four steps are the same four Claude slash commands.

`codex-onboarding/SKILL.md:23` makes step 1 of every Codex session *"Read `AGENTS.md` end-to-end … don't skim."* The first substantive thing that agent reads is a setup procedure it structurally cannot execute, followed by a pointer to a command that does not exist on its host. This is the canonical cross-tool file failing its named audience in its second section.

**Remedy** — restructure Setup as a three-row host table (Claude Code / Copilot CLI / Codex CLI), each with the command that actually works on that host, and replace the bare `/dashboard` pointer with the host-agnostic `bin/rc dashboard` launcher the repo already ships (`plugins/ravenclaude-core/bin/rc`, v0.158.0) — which is precisely the discoverability problem `rc` was built to solve for Copilot and was never extended to Codex.
**Effort: S**

---

### P2-2 · The pre-PR testing checklist requires network installs a Codex sandbox blocks

**Evidence**
- `[verified]` `AGENTS.md:119-120` — `npx --yes prettier@3.9.4 --write .` then `--check .`, marked **REQUIRED before pushing**. `AGENTS.md:126` — `pip install --quiet ruff && ruff check .`, gated by CI.
- `[docs-verified]` `sandbox_mode` restricts filesystem **and network** access; `workspace-write` is the standard interactive mode.
- `[inferred]` Under the default interactive sandbox a Codex agent running steps 3 and 4 of this checklist gets a network denial, not a lint result.

The repo's own CGP then obliges that agent to *"read the actual error first and name its specific mechanical cause"* (`AGENTS.md:208`) — but nothing anywhere tells it the cause is `sandbox_mode`, so it will most likely mis-diagnose it as a missing tool and either abandon the check or ask the user for something they cannot grant mid-turn.

**Remedy** — one note under the testing block: *"On Codex CLI these two steps need network egress; if they fail, the cause is `sandbox_mode`, not a missing tool. Either pre-install `prettier` + `ruff` into the image, or run these steps outside the sandbox. Do not treat a sandbox denial as 'lint unavailable'."* Better still, add a `scripts/lint-local.sh` that prefers already-installed binaries and only falls back to `npx`/`pip`, so the happy path needs no network at all.
**Effort: S**

---

### P2-3 · Gate 70 is named for Codex but tests nothing about Codex-as-host — and the name misleads

**Evidence** `[verified]`
- `plugins/ravenclaude-core/hooks/tests/test-gate70-codex-trust-hooks.sh:2-3` — *"fixture tests for Gate 70 (**Codex desktop trust review** remediation: Findings 1, 2, 5)."*
- Its six subtests exercise `DATA_PLATFORM_STRICT`, `APPLIED_STATS_STRICT`, `EDTECH_PS_STRICT`, `dod-gate.sh` first-run trust, and `guard-web-access.sh` first-use ask (`:42-249`). **Nothing invokes a Codex envelope, config file, path, or CLI.**
- `scripts/audit-gates.sh:4175` labels it *"Gate 70: Codex desktop trust review hooks"*.

This is remediation of findings **Codex produced while reviewing RavenClaude** — good work, unrelated to hosting on Codex. The name is the single largest source of "Codex support exists" confusion in the repo; it was cited as evidence of an existing Codex lane in the brief for this very audit.

**Remedy** — rename the fixture to `test-gate70-trust-review-remediation.sh` and relabel the gate to *"Gate 70: external trust-review remediation (STRICT hooks + dod-gate + web-access)"*. Update `audit-gates.sh:94-95` and `:4175-4190`. Keep a one-line provenance comment naming where the findings came from. Zero behavior change; it stops the name laundering into a capability claim.
**Effort: S**

---

### P2-4 · No `knowledge/codex-cli-customization.md` — every Codex-facing doc grounds itself in Copilot's mechanics

**Evidence** `[verified]`
- `ls plugins/ravenclaude-core/knowledge/` — 23 entries; `copilot-cli-customization.md` exists, **no Codex analog**.
- `docs/best-practices/agent-onboarding.md:17` — *"Canonical mechanism: `copilot-cli-customization.md` §7"* — and `:7` scopes that best-practice to *"repos operated by non-Claude-Code agents (GitHub Copilot CLI, Cursor, Aider)"*, which does not even list Codex.
- `codex-onboarding/SKILL.md:28` and `:93` both route the reader to `copilot-cli-customization.md` §7 for the document-discovery mechanism.

So the skill named `codex-onboarding` sends a Codex agent to Copilot's mechanism doc for its load-bearing mechanic. The Copilot doc is explicitly docs-verified and well-maintained (per the plugin CLAUDE.md, re-verified 2026-06-09) — the problem is that Codex's instruction-file, skills, hooks, config, and sandbox surfaces are all *different*, and none of them is written down anywhere in the repo.

**Remedy** — author `knowledge/codex-cli-customization.md` as the sibling: instruction files + precedence (`AGENTS.md` locations and merge order), skills paths (`$CODEX_HOME/skills`, `.agents/skills` scanned cwd→repo-root), the hooks event set + envelope + trust model, `config.toml` layering, `approval_policy` × `sandbox_mode`, MCP config location, and a RavenClaude-maps-onto-each table — the exact shape of the Copilot file. Every claim carries its `learn.chatgpt.com` / `developers.openai.com` URL + retrieval date. This is the prerequisite artifact for P1-2, P1-4, and P1-6; sequence it first.
**Effort: M**

---

## P3 — nit / polish

### P3-1 · The skill's `name` and its `audience` disagree about who it serves
`plugins/ravenclaude-core/skills/codex-onboarding/SKILL.md:3` describes it as onboarding *"GitHub Copilot CLI / Cursor / Aider / Codex / Devin"* and `:6` lists `audience: [external-coding-agent, codex-user, copilot-cli-user, cursor-user, aider-user]` — Codex is one of five, yet owns the directory name and therefore the discovery keyword. `[verified]` **Remedy:** rename the directory to `external-agent-onboarding` and keep `codex` in the description's trigger language, or split per P1-2. **Effort: S**

### P3-2 · `AGENTS.md:3`'s five-host native-reader claim carries no marker
*"Cursor, OpenAI Codex CLI, Aider, GitHub Copilot, and Windsurf read this file natively"* is stated as fact with no citation and no `[unverified — training knowledge]` marker, in the file whose own §"Accuracy discipline" (`:204-208`) mandates one for durable claims. `[verified]` Codex's half is true `[docs-verified]`; the other four are unchecked here. **Remedy:** add inline dated links for each host that is verified and drop or mark the rest. **Effort: S**

### P3-3 · `bin/rc` was built to solve exactly this problem for Copilot and stops there
`plugins/ravenclaude-core/bin/rc` exists because *"there is no `/dashboard` slash command in Copilot"* (plugin CLAUDE.md v0.158.0) — the identical gap Codex has. The generated `copilot/AGENTS.md:28-64` carries a whole "Launch the comfort-posture dashboard" block teaching the host to run it. `[verified]` **Remedy:** carry that block verbatim into the `codex/AGENTS.md` produced by P1-1's generator; it is copy-paste, and it makes `rc dashboard` the one launch verb across all three hosts. **Effort: S**

---

## Appendix A — the one-line summary of the architectural mistake

The repo's mental model is **`{Claude Code} ∪ {everything else = Copilot}`**. The correct model, given
what Codex now is, is **`{Claude-Code-contract hosts: Claude Code, Codex} ∪ {Copilot, which needs an
envelope adapter}`**. Codex is on the *near* side of the boundary the repo drew, and has been treated
as though it were on the far side. Every P0 and most P1s follow from that one misclassification.

## Appendix B — what was checked and found genuinely fine

- **`AGENTS.md` §Testing instructions (`:91-142`), §Layout discipline (`:82-89`, `:148-168`), §PR conventions (`:172-192`), §Accuracy discipline (`:204-208`)** — portable shell + portable policy. This is real, usable grounding for a Codex agent and is the reason the answer to "is AGENTS.md alone sufficient?" is *"sufficient to work honestly, insufficient to be wired."*
- **`.repo-layout.json` + the CI backstop** — `AGENTS.md:87` frames `validate-layout.yml` as the *"cross-tool backstop"*, and the root `CLAUDE.md` § "Layout enforcement (Claude Code path)" spells out that it *"catches direct human commits, **Cursor/Codex/Aider edits**"*. That design decision is correct and is the one place the repo genuinely anticipated a Codex operator. `[verified]`
- **The 6/6 hook-event overlap** — an unplanned but real asset. Nothing needs redesigning to use it.
- **`plan.md` §6.4's leak-safety design** (closed allow-list of env NAMES, booleans not paths, no `os.environ` iteration) — the right constraint, and it makes the P1-6 remedy a small diff rather than a redesign.
