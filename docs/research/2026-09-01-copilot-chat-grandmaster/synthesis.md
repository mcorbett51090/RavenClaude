# How GitHub Copilot Chat Actually Works — a grandmaster-level reference for RavenClaude

**Drafted:** 2026-09-01
**Method:** 5-angle fan-out (WebSearch/WebFetch agents), cross-source corroboration in lieu of a
dedicated adversarial-verification pass (skipped under a conserve-tokens directive; the hooks findings
below were independently corroborated by 5 official GitHub Docs pages + 3 `github/copilot-cli` GitHub
issues, which is stronger evidence than a single verifier agent would add).
**Purpose:** give RavenClaude and its Copilot-facing plugins (`copilot-hook-adapter.sh`,
`substrate-tier-map.json`, the MCP allowlist engine, `handoff-spawn.sh`, the multi-host worldview docs)
an authoritative, cited, dated picture of Copilot Chat/CLI/coding-agent internals — replacing several
`VERIFY-IN-COPILOT` guesses in the existing adapter with sourced facts.
**Freshness warning:** this space moves fast (GitHub shipped a billing-model change and a model-lineup
deprecation on the same day this was written). Re-verify anything load-bearing before trusting it past
~90 days, per this repo's own platform-fact staleness convention.

---

## 0. The product surface — four distinct things share the "Copilot" name

Do not treat "Copilot" as one product. Four surfaces, different autonomy models, different config:

| Surface | What it is | Where it runs | Governs |
|---|---|---|---|
| **Copilot Chat** (VS Code / Visual Studio / JetBrains) | IDE sidebar/inline chat, Ask/Edit/Agent modes | Your machine | This doc's §1–2, §5 |
| **Copilot CLI** | Terminal-native agent, GA 2026-02-25 | Your machine | §3 (hooks — the most load-bearing section for RavenClaude), §4 (MCP), §6 (tool shapes) |
| **Copilot coding agent** | Cloud-hosted, async, works Issues→PRs | GitHub Actions (ephemeral) | §3 (a genuinely different hook profile), §4 |
| **Copilot code review** | PR review surface | GitHub-hosted | Billing note only (§7) |

**Copilot Workspace no longer exists** — sunset 2025-05-30; its architecture folded into coding agent
(GA to paid subscribers since 2025-09). If any RavenClaude doc still treats Workspace as a live, separate
product, that's stale.

**Terminology shift (Nov 2025, still rippling):** VS Code renamed **"chat modes" → "custom agents."**
`.chatmode.md` is **deprecated**; the current format is `.agent.md`, living in `.github/agents/`
(workspace) or `~/.copilot/agents` (user profile), with frontmatter `tools` / `description` / `model`
(string or priority array) / `handoffs`. A new built-in **"Plan"** agent + a **"Handoff"** feature (a
Plan agent's output passed to an implementation agent) shipped alongside the rename. If any RavenClaude
doc or generator still says `.chatmode.md`, it's describing the pre-2025-11 world.
[code.visualstudio.com/blogs/2025/11/03/unified-agent-experience] · [code.visualstudio.com/docs/agent-customization/custom-agents, dated 2026-08-26]

---

## 1. Chat Participant / Language Model Tool / Language Model APIs (VS Code extension surface)

This is the API a *third-party extension* uses to add a Copilot Chat participant — relevant if
RavenClaude ever wants to ship a VS Code extension that plugs into Copilot Chat rather than adapting
its hooks (RavenClaude already has one: `vscode-extension/ravenclaude-precompact-guard`, shipped
2026-09-01, which uses exactly the mechanism named below).

- **Chat participants:** `vscode.chat.createChatParticipant(id, handler)`, declared in
  `package.json` → `contributes.chatParticipants` (`id`, `name` for `@mentions`, `fullName`,
  `description`, `isSticky`). Handler signature:
  `(request, context: ChatContext, stream: ChatResponseStream, token) => Promise<ChatResult>`.
  `ChatResponseStream` offers `markdown()`, `button()`, `filetree()`, `anchor()`, `progress()`,
  `reference()`. `ChatContext.history` is scoped to turns that mentioned the participant and is
  **not** auto-injected — the participant chooses to use it.
- **Slash commands:** built-in (`/explain`, `/fix`, `/tests`, `/new`, `/clear`, `/fixTestFailure`) vary
  **by host IDE** — the official cheat sheet organizes them per-surface (VS Code / Visual Studio /
  Xcode / JetBrains), and JetBrains' list is CLI-flavored (`/compact`, `/remote`), which may be page
  conflation rather than a real JetBrains chat-command set — flagged unresolved.
- **Language Model Tools API** (Copilot's function/tool-calling): `vscode.lm.registerTool(name, tool)`,
  declared under `contributes.languageModelTools` (`name`, `modelDescription`, `userDescription`,
  `canBeReferencedInPrompt`, `inputSchema`, `when`). Two lifecycle methods: `prepareInvocation()`
  (confirmation UI before running — the safety gate) and `invoke()`. Invoked either automatically by
  agent mode or explicitly via `#toolname` in a prompt.
- **Language Model API:** `vscode.lm.selectChatModels({vendor, id, family, version})` →
  `LanguageModelChat[]`; `model.sendRequest(messages, options, token)` streams a response. The
  `family` example strings in the docs (`gpt-4o`, `claude-3.5-sonnet`) are stale relative to the
  current 2026 lineup — don't cite the specific family strings, just the API shape.
- **Chat modes / custom agents:** three built-in — **Ask** (read-only Q&A), **Edit** (scoped, per-turn
  accept/reject file edits), **Agent** (autonomous multi-file edits + terminal commands, configurable
  auto-approve allow/deny lists). Custom agents are `.agent.md` files (see §0).
- **Context variables:** `#file`, `#selection`, `#codebase` (semantic workspace search, distinct from
  the `@workspace` participant), `#git`, `#changes` (PR diff), `#problems`, `#testFailure`,
  `#terminalLastCommand`. A *separate*, narrower symbol-level set (`#block`/`#class`/`#function`/`#sym`)
  also appears in the official cheat sheet — the two lists weren't reconciled in this pass; treat the
  full context-variable surface as **not fully confirmed**, source-conflicted between two GitHub docs
  pages.
- **Instructions/prompt files (source of truth is `docs.github.com`, not the VS Code page — see §5):**
  `.github/copilot-instructions.md` (repo-wide) + `.github/instructions/*.instructions.md`
  (`applyTo`-glob-scoped, combined additively with the repo-wide file) + `.github/prompts/*.prompt.md`
  (on-demand `/name` slash commands — explicitly marked **preview/unstable by GitHub itself**). A
  singular `.github/copilot-prompt.md` file (no `s`, no directory) is **not corroborated** by any
  fetched source — if RavenClaude docs ever named that path, it's wrong; the real mechanism is the
  `.github/prompts/` directory.

[code.visualstudio.com/api/extension-guides/ai/{chat,tools,language-model}] · [docs.github.com/en/copilot/reference/chat-cheat-sheet] · [docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions]

---

## 2. What the researcher couldn't resolve — stated honestly

- Whether VS Code Copilot Chat's context-variable surface is the broad set (§1) or the narrow
  symbol-only set from the cheat sheet, or both scoped differently — genuinely conflicting sources.
- Drag-and-drop context attachment (dragging a file/terminal output into the chat box) — not
  corroborated by any officially fetched page; may not be a real, current feature.
- A secondary claim that custom agents can live in `.claude/agents` "for Claude format compatibility"
  — came from a single auto-summarized fetch, not independently verified. Interesting if true (would
  mean VS Code Copilot Chat can read RavenClaude's own agent files), but **do not build on it** without
  a direct re-check.

---

## 3. The hooks/lifecycle system — the section RavenClaude's adapter most needed

**This is now backed by an authoritative, dated official page:**
`docs.github.com/en/copilot/reference/hooks-reference`, cross-corroborated by 4 more official docs
pages and 3 `github/copilot-cli` GitHub issues. Confidence here is high.

### 3.1 Canonical event names — camelCase, not PascalCase

The **real, canonical** names are camelCase: `sessionStart`, `sessionEnd`, `userPromptSubmitted`,
`userPromptTransformed`, `preToolUse`, `postToolUse`, `postToolUseFailure`, **`agentStop`** (not
`Stop`), `subagentStart`, `subagentStop`, `errorOccurred`, `preCompact`, `notification`,
`permissionRequest`. **PascalCase aliases are accepted for backward compatibility** (`SessionStart`,
`PreToolUse`, `Stop`, `PreCompact`, …), but every current doc example and worked tutorial uses
camelCase. **Action for RavenClaude:** if `generate-copilot-plugin.py` or the generated
`.github/hooks/*.json` emits PascalCase event keys, verify they still resolve via the alias path — they
likely do (this repo's adapter has apparently worked), but the canonical form is camelCase and a future
Copilot release could tighten alias support.

### 3.2 PreToolUse payload — confirmed correct as implemented

`{toolName, toolArgs: "<JSON string>", cwd, sessionId, timestamp}` — `toolArgs` **is a stringified
JSON string** (escaped quotes), confirmed by 4 independent sources plus a GitHub issue specifically
about parsing it. `copilot-hook-adapter.sh:88-102`'s
`(.toolArgs // "{}") | (try fromjson catch {command: .})` already handles this correctly.

### 3.3 Response envelope — confirmed correct as implemented

Top-level `{permissionDecision, permissionDecisionReason}`, **no `hookSpecificOutput` wrapper**.
Confirmed by a verbatim-quote search of the reference page (zero occurrences of `hookSpecificOutput`)
**and** by GitHub issue #2013 ("`preToolUse hookSpecificOutput.updatedInput` is ignored in Copilot
CLI") — sending the Claude-Code-shaped wrapped payload is silently ignored. The adapter's
top-level-JSON emit is correct; no change needed.

### 3.4 Tool name vocabulary — corrected

**Authoritative list:** `ask_user`, `bash`, `create`, `edit`, `glob`, `grep`, `powershell`, `task`,
`view`, `web_fetch`, `web_search`.

`copilot-hook-adapter.sh:88-100`'s jq map currently covers: `bash`, `shell`(alias), `view`, `read`(alias),
`create`, `write`(alias), `edit`, `str_replace`(alias), `multiedit`(alias), `web_fetch`, `webfetch`(alias),
`web_search`, `websearch`(alias).

**Gap found — five real Copilot tool names are unmapped:** `ask_user`, `glob`, `grep`, `powershell`,
`task`. These are not in the jq map, so they fall through to the adapter's own unmapped-name detection
(`copilot-hook-adapter.sh:107-116`), which only *warns to stderr* — it does not stop the tool from
reaching `thing-orchestrator.sh`'s dispatch `case` (`hooks/thing-orchestrator.sh:113-116`, per the
adapter's own header comment), which matches only `Bash | Read | Write | Edit | MultiEdit | WebFetch |
WebSearch` and falls to `*) exit 0` — **no review, silent no-op**. This is the *exact* same P0 class the
2026-07-28 fix closed for `bash`/`edit`/`view` (see `ravenclaude-two-host-worldview` in memory), now
recurring for five more real tool names that didn't exist (or weren't confirmed) at the time of that
fix. **Concretely: a Copilot CLI session's `grep`, `glob`, `powershell`, `task`, and `ask_user` tool
calls are not reviewed by the command-review tribunal or `guard-web-access.sh` today.** `str_replace`
in the current map is a dead/unconfirmed entry — harmless to keep, doesn't hurt anything, but isn't a
real Copilot tool name per the current docs.

**Also confirmed:** `str_replace_editor`-family tool shapes independently corroborate what these tools
likely do — `edit` uses `{path, old_str, new_str}` (batchable across one turn), `view` uses `{path,
view_range}` with a 50KB truncation, `bash` uses `{command, mode: sync|async, initial_wait, detach}`
with `shellId` for backgrounded processes and companion `read_bash`/`write_bash`/`stop_bash` tools —
**but this is sourced from a leaked/reverse-engineered system prompt, not official docs**, so treat the
exact field names as directionally reliable, not contractually stable.

### 3.5 SessionStart context injection — confirmed, refined

`sessionStart` injects via a JSON `additionalContext` key — confirmed. Plain unstructured stdout is
*preserved in the hook's output stream* but is **not itself parsed into model context** — only the
`additionalContext` JSON key actually injects. The adapter's dual-emit
(`copilot-hook-adapter.sh:192-197`, both the structured field and a plain `printf`) is therefore
**not wrong, but the plain-stdout half is likely inert for context injection** — harmless hedging, not
a bug, and not worth removing without further verification (removing it costs nothing to keep).

### 3.6 Stop hook — confirmed, real event name corrected

Exists, supports `{decision: "block"|"allow", reason}` — confirmed. The **real event name is
`agentStop`**; `Stop` is the accepted PascalCase alias (the adapter's internal `stop` mode name is just
its own dispatch label, unaffected). When blocking, `reason` becomes **the prompt for the forced next
turn**, not just a rejection message shown to the user — worth knowing if RavenClaude ever tunes
`dod-gate.sh`'s block-reason wording for Copilot specifically (it's currently host-agnostic prose,
which happens to work either way).

### 3.7 PreCompact — confirmed, matches existing "claims-table" reasoning

Exists as `preCompact` (alias `PreCompact`): "context compaction is about to begin (manual or
automatic)," filterable on `trigger: "manual"|"auto"`, **notification-only — cannot block or modify
compaction.** Under the cloud/coding agent it only ever fires with `trigger:"auto"` (no interactive user
to invoke `/compact`). This independently confirms the reasoning already recorded in
`copilot-hook-adapter.sh:254-263`'s precompact-mode comment (which cites an internal "claims-table" —
this external doc now backs the same conclusion from a second, official source).

### 3.8 hooks.json — richer than the adapter's own header comment implies

CLI config locations: repo `.github/hooks/*.json`, personal `~/.copilot/hooks/*.json` (or
`$COPILOT_HOME/hooks/`), org/enterprise policy `/etc/github-copilot/policy.d/*.json`, plus inline
definitions in `.github/copilot/settings.json` / `~/.copilot/settings.json`. **Coding/cloud agent
reads ONLY `.github/hooks/*.json`, and it must exist on the repository's default branch.** Schema:
`{"version":1,"hooks":{"<eventName>":[{"type":"command"|"http"|"prompt", "bash"/"powershell"/"command"/
"exec"+"args", "cwd", "env", "timeoutSec", "matcher"(regex)}]}}`. RavenClaude's own header comment
(`GitHub Copilot CLI bridge` in `CLAUDE.md`) says enforcement hooks ship as repo-level `.github/hooks/*.json`
due to bug #2540 (plugin-level `preToolUse` hooks not firing) [unverified — not isolated this session,
carried from this repo's own prior reasoning]. That's independently **consistent** with the docs
finding that coding agent *only* reads that path, but confirm #2540's current status before any future
move to plugin-level hooks — coding agent structurally can't use them regardless of that bug.

### 3.9 Cloud/coding-agent hook-behavior divergence — new, useful detail

Several events behave differently or not at all under the coding agent vs. interactive CLI — relevant
if RavenClaude ever extends the adapter to distinguish the two Copilot surfaces (it currently treats
"Copilot" as one thing):

- `notification` never fires (no user to notify).
- `permissionRequest` doesn't fire / has no effect — docs say use `preToolUse` instead.
- A `preToolUse` decision of `"ask"` is **silently treated as `"deny"`** (no one to ask).
- `sessionStart`/`sessionEnd` fire exactly once per job; `userPromptSubmitted` fires at most once.
- A `decision:"block"` from `agentStop` still counts against the job's overall timeout.
- `powershell` command hooks never run (Linux sandbox only — `bash` only).

---

## 4. MCP support — genuinely unresolved upstream, not a RavenClaude gap

This closes the "Future Work" item 4 from the 2026-06-03 diagnostic (`mcp.allowed_servers` allowlist
UI gap, never verified against the Copilot MCP surface). **Verdict: there is no single stable answer to
verify against — GitHub itself has not standardized this.**

### 4.1 Config fragmentation across the three surfaces (all real, all different)

| Surface | Config location | Root key | Server-type field |
|---|---|---|---|
| VS Code | `.vscode/mcp.json` (workspace) or user-profile via "MCP: Open User Configuration" | `servers` | `type: "stdio"\|"http"\|"sse"` |
| Copilot CLI | `~/.copilot/mcp-config.json` (user) + `.mcp.json` or `.github/mcp.json` (project, closer-to-cwd wins) | (top-level array/object per file) | `type: "local"` (not `"stdio"`!) or `"http"` |
| Coding agent | Pasted JSON in repo Settings → Copilot → coding agent | `mcpServers` | (implicit) |

**`.vscode/mcp.json`'s format is explicitly NOT supported by Copilot CLI** — confirmed in CLI docs. A
single MCP server config cannot be copy-pasted across all three surfaces without editing, even though
all three are GitHub/Microsoft products.

### 4.2 Tool naming — three inconsistent schemes, none canonical

- **VS Code chat internals:** an undocumented `f1e_<toolname>` prefix stripped of server-name reference
  (e.g. `f1e_create_or_update_file`) — confirmed via a GitHub issue where a reporter noted the
  dispatched name didn't match the MCP server's declared name; maintainers closed it "as designed" with
  no public explanation. **17 months stale relative to this research date** — re-verify before relying
  on it.
- **Coding-agent policy YAML (the closest to an official convention):** `<server>/<tool>` (forward
  slash), e.g. `github/read-only-tool`, with `<server>/*` wildcards — documented in
  `docs.github.com/en/copilot/reference/custom-agents-configuration`. This governs the **allowlist**,
  not necessarily the literal dispatch-time token.
- **Copilot SDK (.NET):** a caller expected `<server>-<tool>` (hyphen) and reported the expected names
  simply never appeared at runtime — a filed bug, not a working convention.

**Net:** unlike Claude Code's single `mcp__<server>__<tool>` convention, Copilot has no equivalent
cross-surface guarantee. **Recommendation for RavenClaude's MCP allowlist engine:** do not assume a
`mcp__server__tool`-shaped name will ever appear in a Copilot-originated tool call. If the allowlist
engine (`v0.41.0`, `_decision_detail` in the tribunal) is ever extended to Copilot, it should special-case
by known surface — the coding-agent `server/tool` convention is at least documented — and otherwise
treat the tool name as opaque/pass-through rather than parsing a prefix.

### 4.3 Other confirmed facts worth knowing

- VS Code enforces a **128-tool-per-request cap**; `chat.tools.autoApprove` / `.terminal.autoApprove` /
  `.urls.autoApprove` (regex-based) exist, with an org-level `chat.tools.eligibleForAutoApproval`
  override that can force manual approval even when a user wants auto-approve.
- Coding agent/code review: **no MCP resources, no prompts — tools only**; **no OAuth-authenticated
  remote servers**; **no write-tools by default** (repo admin must explicitly enable); secrets must be
  named `COPILOT_MCP_`-prefixed "Agents secrets."
- VS Code *does* support MCP sampling (`chat.mcp.serverSampling`) — more complete than the coding
  agent's MCP support, contrary to a common assumption that Copilot clients lack sampling entirely.
- Relevant VS Code settings live under `chat.mcp.*`, **not** `github.copilot.chat.mcp.*` — MCP support
  moved into VS Code core, not a Copilot-extension-scoped namespace. If any RavenClaude doc references
  the old namespace, it's stale.

---

## 5. Models, plans, and billing — verify before quoting a specific number

**This section changes fastest of all six** — GitHub shipped a billing-regime change and a model
deprecation wave on dates that bracket this research. Treat every number here as dated, not evergreen.

- **Claude models are natively available in Copilot Chat** (not BYOK) — confirmed across three
  independent official docs pages (models list, pricing table, plan comparison).
- **Billing changed 2026-06-01:** GitHub replaced the flat "premium request" multiplier system with
  **usage-based "AI Credits"** (1 credit = $0.01, priced per-million-tokens per model). The old
  multiplier table (Opus 4.6/4.7 = 27×, Sonnet 4.6 = 9×, etc.) now applies **only to legacy annual-plan
  holders** who are grandfathered — it is not the mainline metering unit anymore. Monthly credit
  allowances: Free (limited), Pro 1,500/mo, Pro+ 7,000/mo, Max (new $100/mo tier) 20,000/mo, Business
  1,900/user/mo, Enterprise 3,900/user/mo.
- **Model deprecations effective 2026-09-01 — today, this document's own date:** Gemini 3.1 Pro →
  3.6 Flash; **Claude Opus 4.5/4.6 → 4.7/4.8/5; Claude Sonnet 4.5/4.6 → Sonnet 5** (with an exception
  keeping Sonnet 4.6 for individual annual subscribers); Raptor Mini → MAI-Code-1-Flash.
  **Cross-check against RavenClaude's own config:** `plugins/ravenclaude-core/knowledge/substrate-tier-map.json`'s
  `copilot` host entries are `fast: "Claude Haiku 4.5"`, `balanced: "Claude Sonnet 5"`,
  `top: "Claude Opus 5"` — **these are already the post-deprecation model names, not the deprecated
  ones.** No fix needed; this is a positive confirmation the config is current, not a defect.
- **BYOK is real and reached GA in VS Code 2026-04-22**, gated to Business/Enterprise plans (org-policy
  controlled, on by default). Supported providers: Anthropic, OpenAI, Google Gemini, OpenRouter,
  Azure/Foundry, plus local runtimes (Ollama, Foundry Local). BYOK usage bills directly through the
  chosen provider and does **not** count against Copilot's AI-credit quota; not available for code
  completions, only Chat/agent-mode/custom agents.
- **Four distinct autonomy surfaces**, confirmed: Copilot Chat (Ask/Edit/Agent modes in the IDE),
  Copilot CLI (GA 2026-02-25, terminal-native, per-action approval prompts), Copilot coding agent
  (cloud/async, GitHub-Actions-hosted, issue→PR), Copilot code review (13× legacy multiplier per
  review — unusually heavy).
- **No stable, documented signal exists (as of this research) for a spawned subprocess to detect "I am
  running under Copilot Chat agent mode."** [web-sourced 2026-09-01] `COPILOT_AGENT` is an *open feature request*
  (`microsoft/vscode#311734`), not shipped. Similarly, Copilot CLI has no public `COPILOT_CLI=true`-style
  contract (`github/copilot-cli#2107`, open ask) — `COPILOT_CLI_BINARY_VERSION` only exists in
  single-executable build mode. **The one surface where "am I under Copilot" is answerable today is the
  coding agent**, indirectly, via standard GitHub-Actions env vars (`GITHUB_ACTIONS=true`, `CI=true`,
  `GITHUB_ACTOR`) — not an explicit Copilot signal, an inference from the Actions-hosted architecture.

---

## 6. Context engine + CLI tool-call shapes

- **`@workspace` uses a hybrid multi-strategy search** — semantic search, grep, "usages" analysis, file
  search — pulling from three index sources: GitHub-hosted repos (remote, indexed server-side,
  available "instantly after first build"), Azure DevOps repos, and local VS Code semantic indexes.
  **Local semantic indexing defaults ON for personal accounts, OFF for org/enterprise accounts.**
  Numeric fallback thresholds (file-count ceilings before dropping to "basic" search) are sourced from
  third-party reverse-engineering, not official docs — don't cite a specific number.
- **Instructions-file precedence, confirmed:** repo-wide `.github/copilot-instructions.md` and
  path-scoped `.github/instructions/*.instructions.md` are used **additively** (both apply when both
  match), not override-one-another. A separate axis — personal > repository > organization — governs
  *conflicts* between scope levels, but "all sets of relevant instructions are provided to Copilot"
  regardless. **Copilot CLI's own docs decline to define a general precedence order** for duplicate
  personal/repo instructions — a materially weaker guarantee than the other surfaces state.
- **CLI tool-call shapes (leaked/reverse-engineered system prompt — directionally reliable, not
  contractually stable):** `edit` = `{path, old_str, new_str}` (Anthropic `str_replace_editor` family,
  note the field names are `old_str`/`new_str`, not Claude Code's own `old_string`/`new_string`); `view`
  = `{path, view_range}`, 50KB truncation, line-numbered output, no stated image support; `bash` =
  `{command, mode: sync|async, initial_wait(default 30s), detach}` with `shellId` + `read_bash`/
  `write_bash`/`stop_bash` for backgrounded processes.
- **The approval model is a generic tool-gate, not a granular classifier**, and GitHub's own docs state
  it explicitly: path/command scoping is "**heuristic, not a cryptographic security boundary**." Flags:
  `--allow-tool='shell(CMD)'`, `--deny-tool='shell(rm)'`, `--allow-tool='write'`,
  `--allow-tool='MCP_SERVER(tool)'`, `--allow-all-paths`, `--allow-url=DOMAIN`, blanket `--allow-all`/
  `--yolo`. A local sandbox (`/sandbox enable`) denies filesystem escape; `copilot --cloud` runs fully
  isolated remotely. **No documented equivalent of an arbitrary user-defined hook that can inspect-and-
  veto an individual tool call based on custom logic** was found beyond the allow/deny-tool pattern list
  — Copilot CLI does have a generic "Hooks" customization surface, but whether it can *veto* a specific
  call (vs. run alongside lifecycle events) wasn't confirmed in this pass.

---

## 7. Gap-closure checklist for RavenClaude's own code

Concrete, file:line-anchored items surfaced by this research. None of these were independently
re-verified by a dedicated adversarial pass (skipped per conserve-tokens) — treat as high-confidence
(multi-source corroborated) rather than certainty, and confirm against a live Copilot CLI session
before merging any code change.

1. **`copilot-hook-adapter.sh:88-102` tool-name map is missing 5 real tool names.** Add `ask_user`,
   `glob`, `grep`, `powershell`, `task` to the jq map (mapping each to itself or to a sensible Claude
   equivalent — `grep`→ maybe nothing needed if the tribunal should just review it as-is; `task` may
   warrant special handling since it likely represents a Copilot subagent dispatch). Without this,
   these five tool types are silently unreviewed by the command-review tribunal and
   `guard-web-access.sh` under Copilot CLI today — the same P0 class already fixed once for
   `bash`/`edit`/`view` on 2026-07-28. This is the single most actionable finding in this research.
2. **`str_replace` in the same map is a dead/unconfirmed entry.** Harmless to leave; not a real
   Copilot tool name per current docs. Low priority.
3. **Verify `generate-copilot-plugin.py`'s generated hook event names against the canonical camelCase
   set** (`sessionStart`, `preToolUse`, `agentStop`, `preCompact`, etc.) — a targeted grep during this
   research came back empty rather than confirming either way (worth a follow-up, not chased further
   under the conserve-tokens directive). If the generator emits PascalCase, it's *probably* fine via
   the alias path, but worth a positive confirmation.
4. **No code change needed — confirmed correct:** the response envelope (top-level JSON, no
   `hookSpecificOutput`), the `toolArgs`-as-string handling, the SessionStart `additionalContext` key,
   the `agentStop`/`Stop` block shape, and the PreCompact notification-only behavior all match what the
   adapter already does. This validates several `VERIFY-IN-COPILOT` markers in the adapter's own header
   comment — they can be downgraded from "unverified" to "confirmed 2026-09-01" in the file.
5. **`substrate-tier-map.json`'s `copilot` host entries are already correct** post-today's-deprecation
   (Sonnet 5 / Opus 5 / Haiku 4.5) — no action needed, but worth a comment noting the 2026-09-01
   deprecation wave was checked against and passed.
6. **MCP allowlist engine:** if ever extended to review Copilot-originated MCP calls, do not assume a
   `mcp__server__tool` name shape. Treat tool names as opaque under VS Code Chat / Copilot SDK; only the
   coding-agent's `server/tool` policy-YAML convention is documented, and even that governs the
   allowlist, not necessarily the dispatch-time token.
7. **Cloud/coding-agent hook divergence (§3.9) is currently invisible to the adapter** — it treats all
   Copilot as one surface. If RavenClaude ever wires hooks for the coding agent specifically (via
   `.github/hooks/*.json` on the default branch, per §3.8), account for: no `notification`, `ask`→`deny`,
   `powershell` hooks never firing, and `agentStop` blocks counting against the job timeout.

---

## Sources consulted (representative — full list in each research thread)

- `docs.github.com/en/copilot/reference/hooks-reference` — the single most load-bearing source, dated
  and cross-corroborated by 4 more docs.github.com pages + `github/copilot-cli` issues #1157, #2013, #3349.
- `docs.github.com/en/copilot/{reference/chat-cheat-sheet, how-tos/configure-custom-instructions/*,
  how-tos/copilot-cli/*, concepts/agents/*, reference/copilot-billing/*, about-github-copilot/plans-for-github-copilot}`
- `code.visualstudio.com/{api/extension-guides/ai/*, docs/copilot/*, docs/agents/*, blogs/2025/11/03/unified-agent-experience}`
- `github.blog/changelog/{2026-02-25-github-copilot-cli-is-now-generally-available,
  2026-04-22-bring-your-own-language-model-key-in-vs-code-now-available,
  2026-07-31-upcoming-august-2026-model-deprecations-in-github-copilot}`
- `github.com/microsoft/vscode` issues #246093, #246552, #308463, #311734; `github.com/microsoft/vscode-copilot-release#14104`
- `github.com/github/copilot-cli` issues #1004, #1157, #2013, #2107, #3349, #3705; `github.com/github/copilot-sdk#861`
- `asgeirtj/system_prompts_leaks` (Copilot CLI system-prompt capture — explicitly marked unofficial/directional)
