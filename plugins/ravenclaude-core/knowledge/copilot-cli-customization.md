# GitHub Copilot CLI — the customization surface

**Last reviewed:** 2026-06-09 · **Confidence:** high (verified against the GitHub Copilot CLI customization docs — custom instructions, custom agents, agent skills, hooks, and the using-the-CLI reference; URLs in § Sources, retrieved 2026-06-09). GA Feb 2026 ([changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)).
**Owner:** the Copilot CLI bridge in [`../CLAUDE.md`](../CLAUDE.md) § "GitHub Copilot CLI bridge". This file is the **canonical, complete** reference; the bridge prose is the RavenClaude-specific wiring on top of it.

This is what GitHub Copilot CLI reads for customization, and how RavenClaude maps onto each surface. Every path/field below is from the live docs; the few RavenClaude-specific mechanics the docs don't cover are marked `[verify-at-use]`.

## 1. Custom instructions (auto-included every request)

Copilot CLI **automatically adds** these to every request at session start — *"Instructions are automatically added to requests that you submit to Copilot."* You don't invoke them; they're always-on context.

| File | Scope |
|---|---|
| `.github/copilot-instructions.md` | repository-wide |
| `.github/instructions/*.instructions.md` | path-scoped (each has an `applyTo:` glob); at repo root or under the cwd |
| `AGENTS.md` | repo root, the cwd, or any dir in `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` |
| `$HOME/.copilot/copilot-instructions.md` | personal (all repos) |
| `CLAUDE.md` / `GEMINI.md` | repo root — read as alternatives |

**Nuance `[verify-at-use]`:** the docs say the *instruction files* are auto-included; they do **not** state that a *path reference inside* one (e.g. "read `.ravenclaude/environment-context.md`") auto-loads that referenced file's content. Treat a reference as a pointer the agent reads on demand — put must-have content directly in an auto-loaded file. Convention: keep `copilot-instructions.md` short and point it at `AGENTS.md`.

## 2. Custom agents

| Location | Scope |
|---|---|
| `.github/agents/*.agent.md` | project (repository) |
| `~/.copilot/agents/*.agent.md` | personal |

- **Precedence:** a same-named agent in `~/.copilot/agents/` (home) **overrides** the repo one.
- **Format:** `<name>.agent.md` (Markdown + frontmatter). `name`; optional `tools` (by default an agent has **all** tools — a `tools` spec only *restricts*).
- **Invocation:** `/agent` (interactive picker) · explicit ("use the security-expert agent") · inference from the agent's `description` · programmatic `copilot --agent <name> --prompt "…"`.
- Agents run as temporary subagents with their **own isolated context window**.

## 3. Agent skills

| Location | Scope |
|---|---|
| `.github/skills/`, `.claude/skills/`, `.agents/skills/` | project |
| `~/.copilot/skills/`, `~/.agents/skills/` | personal |

- Each skill is its own subdirectory (lowercase, hyphenated) with a `SKILL.md`.
- **`SKILL.md` frontmatter:** `name` (required, lowercase-hyphenated) · `description` (required — what it does + *when* Copilot should use it) · optional `license` · optional **`allowed-tools`** (pre-approves tools, e.g. `shell`, without per-use confirmation).
- **Discovery/invocation:** auto-discovered; Copilot decides from the prompt + `description`, or the user forces it with `/skill-name`. When invoked, **all** files in the skill dir become available to the agent.
- **Instructions vs. skills (the docs' own guidance):** custom instructions for simple guidance relevant to *almost every* task; skills for detailed guidance Copilot should load *only when relevant*.

## 4. Hooks

External commands fired at lifecycle points (custom automation, security/policy gates).

| Location | Scope |
|---|---|
| `.github/hooks/NAME.json` | repository |
| `~/.copilot/hooks/` (or `$COPILOT_HOME/hooks/`) | personal |

- **Events:** `sessionStart`, `sessionEnd`, `userPromptSubmitted`, `preToolUse`, `postToolUse`, `errorOccurred` (`agentStop` also appears in examples).
- **`preToolUse` is the powerful one** — it can **approve or deny** a tool call, and it **fails closed** (an error/crash/timeout *denies* the tool rather than silently allowing it). `sessionStart` output is informational (ignored by the agent).
- **Config (JSON, version 1):**
  ```json
  {
    "version": 1,
    "hooks": {
      "preToolUse": [
        { "type": "command", "bash": "…", "powershell": "…", "cwd": ".", "timeoutSec": 10, "env": {} }
      ]
    }
  }
  ```
- **⚠️ Plugin-level hooks do NOT fire** — `preToolUse` hooks defined in a *plugin's* `hooks.json` never execute (main session or subagents): [github/copilot-cli#2540](https://github.com/github/copilot-cli/issues/2540). **Ship enforcement hooks repo-level (`.github/hooks/`)**, not plugin-level, until #2540 closes.

### ⚠️ THE NO-MATCHER ASYMMETRY — read this before writing any hook that branches on a tool

This is the structural difference that caused the single worst defect found in the
2026-07-28 multi-host audit, and it will cause the next one if it is not understood.

**Claude Code filters hooks by a per-tool `matcher` in `hooks.json`.** A hook registered
for `Bash` is only ever invoked for `Bash`, so a hook may reasonably assume its own tool
shape and treat an unexpected `tool_name` as "not mine — exit 0, no decision".

**Copilot CLI has a per-tool matcher — but only in one of its two hook formats.**

> ⚠️ **CORRECTED 2026-07-28.** This section previously said, flatly, *"Copilot CLI has no
> per-tool matcher."* **That is false**, and it was itself the MH-24 fix — the entry the
> audit's build order called *"the highest leverage in the ledger: the guardrail against
> the next MH-01."* A guardrail against false claims that was itself a false claim.

Copilot supports **two payload formats, selected by the casing of the event name**
`[docs-verified 2026-07-28 — docs.github.com/en/copilot/reference/hooks-configuration]`:

| Format | Event names | Per-tool matcher? |
|---|---|---|
| **native** | `preToolUse`, `sessionStart`, `agentStop`, `userPromptSubmitted` … | **No** — scoping is a native regex rule, not a tool matcher |
| **Claude-compatible** | `PreToolUse`, `SessionStart`, `Stop` … (PascalCase) | **Yes** — *"apply Claude's matcher semantics"*; field names switch to snake_case |

Corroborated independently by the changelog: **1.0.62** — *"PostToolUse hook matchers (e.g.
`Edit|Write`) are now honored instead of silently dropped."* So matchers are honored from
**1.0.62**; below it they are ignored and the hook fires for every tool.

**RavenClaude's generated file has always used PascalCase keys** — so Claude matcher
semantics were available the whole time and simply were not used. They are now projected
from the canonical manifest (MH-12), which is what makes the two consequences below
*historical* rather than ongoing.

Two consequences, and RavenClaude was bitten by both **while running matcher-free**:

1. **The Claude-shaped "unknown tool → exit 0" default becomes a silent security hole.**
   Under Claude Code that default is safe, because the matcher guaranteed the tool was
   already the right one. Under Copilot it means *anything the hook does not recognise
   sails through unreviewed*. `thing-orchestrator.sh` dispatched on a case-sensitive
   `Bash | Read | Write | Edit | MultiEdit | WebFetch | WebSearch | mcp__*` list and fell
   to `*) exit 0`.

2. **The tool NAMES differ, so nothing matched.** GitHub documents its tools lowercase —
   *"before the agent uses any tool (such as `bash`, `edit`, `view`)"*
   ([hooks](https://docs.github.com/en/copilot/concepts/agents/hooks), retrieved 2026-07-28).
   `bash` is not `Bash`. Combined with (1), **the command-review tribunal and the
   web-access guardrail were complete, silent no-ops under Copilot** — fully wired,
   reviewing nothing. Fixed by normalising tool-name values in
   `hooks/copilot-hook-adapter.sh` (commit `f55039ec`).

**Rules that follow — apply these to every new hook and every new host:**

- **Normalise the tool name at the adapter, once.** Never let a host's raw vocabulary
  reach a hook that dispatches on Claude's names.
- **An unrecognised tool name is a finding, not a default.** Log it. The blind spot that
  hid this bug was that an unmapped name produced *silence*.
- **Never let a test fixture invent a tool name.** Gate 20's fixture drove the adapter
  with `toolName:"shell"` — a name in neither vocabulary — and passed. A fixture must be
  derived from the platform's documented values, never from what the code expects.
- **There are TWO tool vocabularies, and conflating them is its own bug** (corrected
  2026-07-29, audit MH-10). The line below used to say the tool list was simply
  "not published"; that was true of one vocabulary and false of the other, and the
  audit ledger's own remedy for MH-10 inherited the confusion by proposing that the
  agent allowlist reuse the hook map.

  | Vocabulary | Used by | Names | Status |
  |---|---|---|---|
  | **Hook `toolName` event values** | `hooks-configuration`, consumed by `copilot-hook-adapter.sh` | `bash`, `view`, `edit`, `grep`, `glob`, `web_fetch`, `ask_user`, `task`, `create`, `powershell` | `bash`/`edit`/`view` **docs-verified**; the rest are defensive guesses marked in the code. **The complete list is still NOT published at a fetchable URL** (two candidate pages 404'd, 2026-07-28). Settle by running `copilot` and enumerating. |
  | **Agent-profile `tools:` allowlist** | `.agent.md` frontmatter, emitted by `generate-copilot-plugin.py` | `read`, `edit`, `search`, `execute`, `shell`, `bash`, `powershell`, `agent`, `web`, `todo`, `view`, `grep`, `glob`, `custom-agent` | **`[docs-verified 2026-07-29]`** — [custom-agents-configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration), the page the CLI's own custom-agents how-to designates as authoritative. |

  They **overlap but are not the same list**: `web_fetch` / `ask_user` / `create` are not
  agent-profile names, and `read` / `search` / `web` / `todo` / `agent` are not hook names.

- **The agent-profile reference settles the three things a security boundary needs**
  `[docs-verified 2026-07-29]`: it applies to *"agent profiles in GitHub.com, the Copilot
  CLI, and supported IDEs"*; `tools` is *"List of tool names the custom agent can use...
  If unset, defaults to all tools"*; and — the load-bearing one — ***"All unrecognized tool
  names are ignored, which allows product-specific tools to be specified in an agent
  profile without causing problems."***

  **That last sentence sets the failure direction and is why the allowlist is now
  projected.** A wrong name is *dropped*, never widened: the worst case is an agent
  lacking a capability (visible), never one silently gaining write or shell (invisible).
  It also means extra equal-privilege spellings are free, so each Claude tool maps to
  every equal-privilege Copilot name rather than one guessed favourite. **The invariant
  that keeps that safe — never put a class on a row the canonical agent didn't declare —
  is enforced by Gate 166, not by care.**

- **The allowlist is ENFORCED — observed, not merely documented** `[verified 2026-07-29,
  Copilot CLI 1.0.70]`. Three probes against a scratch repo with `--allow-all-tools` (so
  permission prompts could not be mistaken for restriction):

  | Probe | Result |
  |---|---|
  | control agent, no `tools:` | created the file, via a shell command |
  | agent restricted to `read, view, grep, search, glob` | replied `CANNOT_WRITE`; no file created |
  | same restricted agent, explicitly told to leak via `curl`/`git` | `LEAK_FAILED` (*"Skill 'curl' not found"*); no file created |

  **`read` and `search` were silently dropped** — the restricted agent ended up with
  exactly `view` / `grep` / `glob`. That is the *unrecognized-names-are-ignored* rule
  observed in the wild, and it is the empirical case for mapping each Claude tool to
  **every** equal-privilege spelling: a map that had guessed `read` alone would have left
  every projected agent with **no file-reading tool at all** — a silent capability
  amputation that nothing in CI could have caught.

- **Never trust an agent's self-report of its own tools; test the behaviour.** Asked to
  name its tools, the restricted probe listed `git` and `curl` alongside the real ones.
  Neither exists — the follow-up leak attempt died with *"Skill 'curl' not found"*, and the
  names it did print (`functions.sql`, `multi_tool_use.parallel`) are internal namespacing.
  Taken at face value that self-report reads as a leaky allowlist and would have been filed
  as a live security hole. **The question is "can it write?", never "what does it say it
  has?"** — the same rule this file already states for test fixtures.

## 5. Runtime & config

- **`settings.json`** and **`mcp-config.json`** live in **`~/.copilot/`** by default; **`COPILOT_HOME`** overrides that directory (so all of settings / MCP / hooks move with it).
- **`COPILOT_CUSTOM_INSTRUCTIONS_DIRS`** — comma-separated dirs Copilot also scans for `AGENTS.md`.
- **Permissions:** Copilot asks before a tool that modifies/executes (e.g. `touch`, `chmod`, `node`, `sed`); approve per-op / per-session / deny. `--allow-all` and `--yolo` enable everything (use with care).

## 6. How RavenClaude maps onto each surface

| Copilot CLI surface | RavenClaude wiring |
|---|---|
| **Custom instructions** | Root `AGENTS.md` carries the cross-tool discipline; `scripts/generate-copilot-plugin.py` projects it into `copilot/AGENTS.md` so it travels with the agents (wired via `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`). Consumers keep a short `.github/copilot-instructions.md` pointing at `AGENTS.md`. |
| **Custom agents** | `copilot/agents/*.agent.md` (frontmatter = `name` + `description`, body verbatim), loaded **live** via `copilot --plugin-dir copilot/` `[verify-at-use — --plugin-dir is owner-verified; not in the customization docs reviewed 2026-06-09]`. The native `.github/agents/` + `~/.copilot/agents/` dirs are an alternative path RavenClaude does not currently use. |
| **Agent skills** | `scripts/ravenclaude install` wires skills → the consumer's `.claude/skills/` (a docs-confirmed project-skills dir), read live. RavenClaude `SKILL.md` files use `name` + `description`; Copilot's `allowed-tools` is available as a future friction-reducer (not yet adopted). |
| **Hooks** | Wired **repo-level** to `.github/hooks/ravenclaude.json` via [`hooks/copilot-hook-adapter.sh`](../hooks/copilot-hook-adapter.sh), which translates Copilot's I/O envelopes (`toolName`/`toolArgs` ⇄ `tool_name`/`tool_input`; top-level `permissionDecision`; `sessionStart` `additionalContext`) so the **existing, unmodified** Claude hook scripts run. Repo-level because of #2540. |
| **MCP** | Bundled MCP → `${COPILOT_HOME:-~/.copilot}/mcp-config.json` by `scripts/ravenclaude`. |
| **Update model** | Everything is read **live from disk**, so an update is `git pull` (`ravenclaude update` / the `rc` alias) — no Copilot re-install/cache. |

## 7. Document discovery (DOCUMENT-MAP.md)

**The gap this closes** (a corollary of §1, not a new claim): Copilot CLI *auto-includes* the instruction files above on **every** request — but they carry *behaviour*, not a **location index**, and per §1's `[verify-at-use]` note a *path referenced inside* an auto-loaded file is **not** itself auto-loaded. So a cold agent re-runs `find`/`grep` each turn to relocate a document it already "knows" exists. A flat, keyword-indexed **topic → path** table fixes that: one lookup resolves any mapped document.

**Placement — prefer inline, fall back to a file:**

| Option | Cost | Use when |
|---|---|---|
| **Inline** the topic→path table directly into an already-auto-loaded file (`AGENTS.md` / `.github/copilot-instructions.md`) | Standing prompt tokens every request; **0** extra tool calls | The index is small enough to sit in the instruction file — the **preferred** shape |
| **Standalone `DOCUMENT-MAP.md`** + one line in an auto-loaded file telling the agent to read it first | **1** `read` call per session; no standing token cost | The index is too large to inline |

The standalone file is the *fallback*, not the default — a bare `DOCUMENT-MAP.md` that nothing auto-loads and nothing points at is invisible (the §1 not-auto-loaded rule again).

**Sizing:** overkill below ~50 docs (one `grep` is fine); the sweet spot is ~50–300; beyond ~1000 a semantic index (a Copilot Space) beats a flat table `[verify-at-use — Copilot Space scaling not re-checked here]`.

**Format** — flat, one table, keyword-first so the agent can `grep` the *map* instead of the filesystem:

```markdown
## Reports & designs
| Topic | File |
|---|---|
| CSP thematic review Power BI report | docs/project-allocation-2026-07.html |
| Onsite report SOP templates          | docs/sops/onsite/A. FINALISED TEMPLATES/ |
```

**Maintenance — seed, then hand-curate.** [`../../../scripts/generate-document-map.py`](../../../scripts/generate-document-map.py) *seeds* a map (enumerates files, best-effort titles from a first `# H1` / frontmatter). It **cannot** synthesise good topic keys — that judgement ("this is the file an agent looks up when asked about X") is the load-bearing part and stays human. Treat generator output as a starting draft to edit, **never** a regenerated source of truth. A **stale** map is *worse* than none (it routes the agent to a dead path); review it when a mapped document moves.

**Honesty note:** a consumer reported ~6 tool calls / ~45s → ~5s per lookup after adopting a map `[unverified — single foreign-repo anecdote, illustrative only]`. The real win is narrow — repos where a known-document lookup was genuinely multi-round; where one `grep` already finds it, a map is ceremony.

**See also:** [`../../../docs/best-practices/agent-onboarding.md`](../../../docs/best-practices/agent-onboarding.md) — the cross-tool pattern · the [`external-agent-onboarding`](../skills/external-agent-onboarding/SKILL.md) skill wires the session-start read.

## Sources

All retrieved 2026-06-09:
- [Adding custom instructions for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)
- [Creating and using custom agents for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli)
- [Adding agent skills for Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
- [Using hooks with Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-hooks) · [Hooks configuration reference](https://docs.github.com/en/copilot/reference/hooks-configuration)
- [Using GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli) · [#2540 — plugin hooks don't fire](https://github.com/github/copilot-cli/issues/2540)
