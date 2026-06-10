<!-- RAVENCLAUDE-STAGING-METADATA
type: best-practice
topic: architecture
proposed-by: consumer engagement — Copilot CLI deploy session needing credential/route discovery at session start
proposed-on: 2026-06-09
target-file: docs/best-practices/surface-credential-location-in-environment-context.md
status: pending
-->

# Surface credential location + deploy route in agent-readable context so the agent doesn't guess

**Status:**
- **Pattern** — strong default; deviate only with a written reason.

**Domain:** Agent operability / environment orientation (cross-domain).

**Applies to:** Any consumer project where a Claude Code / GitHub Copilot CLI agent must deploy or call authenticated APIs (Fabric, Dataverse, Azure, cloud DBs, …).

---

## Why this exists

An agent that needs to deploy or call an authenticated API should never have to GUESS or ASK where credentials live or which deploy route is correct — that's a wasted round-trip, and guessing wrong burns a failed attempt (e.g. a 401). Give the agent the **non-secret** orientation it needs, in a file the agent host loads at session start, and "ask the user / fail / retry" becomes "read it, act correctly the first time."

## How to apply

Record the NON-SECRET orientation in `.ravenclaude/environment-context.md` at the repo root:

**Do:**
- Record all workspace / resource / tenant IDs that are **non-secret** and safe to commit.
- Record the **names** of the env vars that hold secrets (e.g. `AZURE_CLIENT_SECRET`) — never the values.
- Record the **correct deploy/execution route** explicitly (e.g. "push to the default branch → the Actions workflow deploys" vs "run the script directly").
- Include a copy-paste deploy checklist.

**Don't:**
- Don't put secret VALUES in the file — secrets stay as Codespace/CI secrets (env vars) or a vault. Only var NAMES and non-secret IDs go in the file. (This matches RavenClaude's existing design: `environment-context.md` is explicitly **not** a credential store, and the capability-orientation hook emits env-var *names* only.)
- Don't let it drift — update it when the deploy route, workspace, or credential var names change.

### Getting it into the agent's context — what's verified vs. what to assume

`[verified 2026-06-09]` GitHub **Copilot CLI automatically includes** these instruction files in every request at session start: `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, **`AGENTS.md`** (repo root / cwd / `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`), `$HOME/.copilot/copilot-instructions.md`, and **`CLAUDE.md` / `GEMINI.md`** at the repo root (per [GitHub Copilot CLI custom-instructions docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions): *"Instructions are automatically added to requests that you submit to Copilot"*). Claude Code reads `CLAUDE.md` / `AGENTS.md` the same way.

`[unverified — not in the GitHub docs]` Whether a **path reference inside** an instruction file (e.g. "the deploy route is in `.ravenclaude/environment-context.md`") auto-loads that *referenced* file's full content is **not documented**. So design for two cases:

1. **Put the orientation directly in an auto-loaded file** (a short `.github/copilot-instructions.md` / `AGENTS.md` section, or a path-scoped `.github/instructions/deploy.instructions.md`) when you want it guaranteed in context.
2. **Reference `environment-context.md`** from those files and rely on the agent reading it **on demand** — and, under RavenClaude, the SessionStart capability-orientation hook surfaces the file's *presence + summary* (not its full content) so the agent knows to open it.

Keep `copilot-instructions.md` short and point it at `AGENTS.md` (the repo's existing cross-tool convention).

## Edge cases / when the rule does NOT apply

- A repo with no authenticated deploy surface (pure-docs or static-content) doesn't need it.
- Per-environment role / pre-authorization detail is already the `environment-context.md` template's job — this rule specifically adds the **credential-var-names + deploy-route** orientation so the agent stops guessing.

## See also

- `plugins/ravenclaude-core/templates/environment-context.md` — the canonical template.
- `plugins/ravenclaude-core/skills/environment-discovery/SKILL.md` — auto-discovers + drafts the file (read-only; refuses to write credential values).
- `plugins/ravenclaude-core/CLAUDE.md` § "Session-start environment-context load" — the capability-orientation hook that surfaces the file at session start (and, under Copilot, via the hook adapter's `additionalContext` mapping).
- [GitHub Copilot CLI custom-instructions docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions).

## Provenance

Consumer Copilot-CLI deploy engagement, 2026-06-09: an agent hit a deploy auth wall partly because the credential location + correct deploy route weren't surfaced up front. The user reported Copilot "prefers" credential orientation in its instruction files; verified 2026-06-09 against the GitHub Copilot CLI docs (instruction files ARE auto-included; the referenced-file auto-load nuance is flagged above). Generalized; client/org identifiers removed.

---

_Last reviewed: 2026-06-09 by consumer-engagement contribution (Copilot-CLI mechanism verified against docs.github.com)_
