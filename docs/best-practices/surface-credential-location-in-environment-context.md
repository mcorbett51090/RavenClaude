# Surface credential location and deploy route in agent-readable context, so the agent doesn't guess

**Status:** Pattern — strong default; deviate only with a written reason.

**Domain:** Agent operability / environment orientation (cross-domain).

**Applies to:** Any consumer project where a Claude Code / GitHub Copilot CLI agent must deploy or call authenticated APIs (Fabric, Dataverse, Azure, cloud databases, …).

---

## Why this exists

An agent that needs to deploy or call an authenticated API should never have to guess, or ask, where credentials live or which deploy route is correct — that's a wasted round-trip, and a wrong guess can burn a failed attempt (a 401, a partial deploy). Give the agent the **non-secret** orientation it needs, in a file the agent host loads at session start, and "ask the user / fail / retry" becomes "read it, act correctly the first time."

## How to apply

Record the non-secret orientation in `.ravenclaude/environment-context.md` at the repo root — this is additive to that file's existing job of recording per-environment role and pre-authorization (see `plugins/ravenclaude-core/templates/environment-context.md`); this rule specifically covers the credential-variable-names and deploy-route orientation that template doesn't already prescribe a place for.

**Do:**
- Record the workspace / resource / tenant IDs needed for orientation, once you've checked whether they're safe to commit in this specific repo (see the repo-visibility check below) — the canonical template already treats tenant IDs as potentially sensitive per engagement (`plugins/ravenclaude-core/templates/environment-context.md`, "What NOT to put in this file": *"Specific tenant IDs if your engagement context requires them confidential — use a slug instead"*). Don't treat "not a secret" as the same question as "safe to publish."
- Record the **names** of the env vars that hold secrets (e.g. `AZURE_CLIENT_SECRET`) — never the values.
- Record the correct deploy/execution route explicitly (e.g. "push to the default branch → the Actions workflow deploys" vs. "run the script directly").
- Include a copy-paste deploy checklist.
- **Check the repo's visibility before deciding how identifying an ID is allowed to be.** A tenant ID, workspace GUID, or resource name that's harmless in a private client repo is a different risk in a public marketplace or open-source repo — it becomes a durable, searchable, permanent association between an org and its infrastructure, even though it's not a credential. Before committing any ID to a public repo's `environment-context.md`, ask: would I be comfortable with this ID being indexed by a search engine forever? If not, use a slug (as the template already recommends) instead of the real value, and say so explicitly rather than silently omitting the field.
- Rely on the template's existing staleness mechanisms rather than inventing a new one: the **verify-me probe** (a cheap read-only call like Dataverse `WhoAmI` — a `401`/`403` means re-confirm before trusting the file) and the **Refresh triggers** list (new/retired environment, role/grant change, rotated auth mechanism) already cover "don't let it drift." Point any new engagement-specific staleness concern at those two mechanisms instead of adding a parallel one.
- Re-verify the auto-load behavior described below whenever the agent host (Copilot CLI, Claude Code) has a version bump — the auto-inclusion mechanism is a host feature, not a protocol guarantee, and host releases can change what's auto-loaded without notice.

**Don't:**
- Don't put secret values in the file — secrets stay as Codespace/CI secrets (environment variables) or a vault. Only variable names and appropriately-vetted non-secret IDs go in the file. (This matches RavenClaude's existing design: `environment-context.md` is explicitly not a credential store, and the capability-orientation hook emits env-var *names* only.)
- Don't treat "the template doesn't call this a secret" as clearance to commit it to a public repo without the visibility check above.

### Getting it into the agent's context — what's verified vs. what to assume

`[verified 2026-06-09]` GitHub Copilot CLI automatically includes these instruction files in every request at session start: `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md` (repo root / cwd / `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`), `$HOME/.copilot/copilot-instructions.md`, and `CLAUDE.md` / `GEMINI.md` at the repo root (per the [GitHub Copilot CLI custom-instructions docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions): *"Instructions are automatically added to requests that you submit to Copilot"*). Claude Code reads `CLAUDE.md` / `AGENTS.md` the same way. Re-check this against current docs after any Copilot CLI or Claude Code version bump — see the re-verify-on-host-version-change note above.

`[unverified — not in the GitHub docs as of 2026-06-09]` Whether a path reference *inside* an instruction file (e.g. "the deploy route is in `.ravenclaude/environment-context.md`") auto-loads that referenced file's full content is not documented. Design for two cases:

1. **Put the orientation directly in an auto-loaded file** (a short `.github/copilot-instructions.md` / `AGENTS.md` section, or a path-scoped `.github/instructions/deploy.instructions.md`) when you want it guaranteed in context.
2. **Reference `environment-context.md`** from those files and rely on the agent reading it on demand — under RavenClaude, the SessionStart capability-orientation hook surfaces the file's presence and summary (not its full content), so the agent knows to open it.

Keep `copilot-instructions.md` short and point it at `AGENTS.md` (the repo's existing cross-tool convention).

## Edge cases / when the rule does NOT apply

- A repo with no authenticated deploy surface (pure documentation or static content) doesn't need it.
- Per-environment role / pre-authorization detail is already `environment-context.md`'s job — this rule specifically adds the credential-variable-name and deploy-route orientation so the agent stops guessing; don't duplicate role/authorization content that already has a home there.
- If every environment the agent touches is genuinely public-safe to name (e.g. a public sandbox tenant with no real data), the visibility-check step above still costs nothing to run but won't change the outcome — it's a judgment gate, not a mandatory redaction.

## See also

- `plugins/ravenclaude-core/templates/environment-context.md` — the canonical template, including the existing tenant-ID sensitivity note, the verify-me probe, and the Refresh triggers list this doc points to rather than duplicating.
- `plugins/ravenclaude-core/skills/environment-discovery/SKILL.md` — auto-discovers and drafts the file (read-only; refuses to write credential values).
- `plugins/ravenclaude-core/CLAUDE.md` § "Session-start environment-context load" — the capability-orientation hook that surfaces the file at session start (and, under Copilot, via the hook adapter's `additionalContext` mapping).
- `plugins/power-platform/knowledge/fabric-deploy-from-codespace-route-via-ci.md` — a concrete deploy-route/auth-triage case this rule would have shortened, once promoted from staging.
- [GitHub Copilot CLI custom-instructions docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions).

## Provenance

Consumer Copilot-CLI deploy engagement, 2026-06-09: an agent hit a deploy auth wall partly because the credential location and correct deploy route weren't surfaced up front. The user reported Copilot "prefers" credential orientation in its instruction files; verified 2026-06-09 against the GitHub Copilot CLI docs (instruction files are auto-included; the referenced-file auto-load nuance is flagged above). Generalized; client/org identifiers removed. Revised during promotion to reconcile with the canonical template's existing tenant-ID and staleness guidance, and to add the repo-visibility check for public marketplace/open-source repos.

---

_Last reviewed: 2026-09-11 by consumer-project session_
