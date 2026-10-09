# Enhancement register — disposition (2026-10-09)

Follow-on triage of the coding-agent harness atlas **enhancement register**
([`data/register.json`](data/register.json) / [`md/register.md`](md/register.md) / [`register.html`](register.html)).
Machine-readable twin: [`data/register-dispositions.json`](data/register-dispositions.json).

The atlas build ships every entry as `status: proposed` (validator `R_REGISTER`).
This file is the backlog triage the atlas deferred: **update** or **deprecate** each feature
against HEAD on 2026-10-09, using the atlas cells and five-host re-verification as the harness evidence.

## Harness findings that drive triage

Snapshot **2026-10-04** (F23 rows **2026-10-05**): 8 hosts × 133 rows ≈ 1,064 cells; lifecycle layer;
ranked register of **55** RavenClaude follow-ons. Five-host re-verification of routing-matrix lever facts:
**15 hold · 11 changed · 2 contradicted · 14 not covered**. The two contradicted facts seed ENH-051 and ENH-048.

| Atlas product | What it means for RavenClaude |
|---|---|
| Codex CLI | Retired `approval_policy=untrusted`; `apply_patch` / hosted WebSearch hook paths; 32 KiB AGENTS.md cap; effort dial raises tokens; GPT-6 Luna / gpt-6.1-sol naming |
| Copilot CLI / VS Code Chat | `chat.useHooks` / `chat.useClaudeHooks`; Local vs Agent Host; slash commands + `@path`; `--model` slug pinning documented |
| Cursor | Invalid-JSON vs crash fail-open split; `failClosed`; skills / agents / Bugbot / `.cursorignore` lanes thin or absent |
| Gemini CLI | Four settings files; untrusted project hooks; AfterAgent retry; no `emit-gemini-config` / extension package |
| Grok Build / Bot | grok-4.7 + xhigh; opt-in worktree isolation; not in `host-support.json`; Bot approval expiry / skill enablement / Cloud Agents route |
| Claude Code | `auto` default version stamp; concurrent-subagent ceiling; `effort: normal` invalid; PermissionDenied hook gap; FORGE receipt / premise / sanitize / triage defects |

## Verdict summary

| disposition | count |
|---|---:|
| **update** | 55 |

**No entry is deprecated this pass.** Every `correct` / `reconcile` / `en-route-defect` still has its
`repo_claim` text in HEAD (or is an extend/new-lane/probe whose target files are still missing).
Deprecate only when a claim is gone *and* the proposal would now be wrong, or when a later atlas watch
withdraws the vendor fact. Three entries need a **proposal refresh** when implemented (atlas naming
drift since the register was frozen): ENH-025, ENH-052, ENH-053.

## Related lists (not this file)

| List | Role | Disposition under harness atlas |
|---|---|---|
| This register (55 ENH-*) | Harness-gap backlog from the 2026-10-04 atlas | **Authoritative feature list for this work** — dispositions below |
| `plugins/ravenclaude-core/concepts.json` (99 concepts) | Shipped product inventory for the dashboard | Unchanged; atlas does not deprecate concepts |
| `docs/norse-mythology-feature-map.md` (2026-05-23) | Naming / metaphor ideation | Keep as ideation; not a build backlog |
| `docs/research/2026-06-04-claude-features-gap-analysis/` | Consumer Claude surface gap vs Kopadze 17 | Orthogonal to coding-agent harness columns; leave alone |
| Product-inventory plan (2026-08-19 archive) | Efficacy harness for inventory authoring | Separate FORGE track; not the ENH register |

## Priority bands

Implement in register rank order unless a later watch flips a disposition. Bands for planning only:

| Band | Ranks | Focus |
|---|---|---|
| P0 — wrong docs / retired knobs | 1–11 | ENH-007…016 (Codex untrusted, Chat hook setting names, cost claim, effort mapping, Cursor fail modes, auto default, AGENTS.md cap, Grok xhigh, Copilot slash) |
| P1 — agent + FORGE truth | 12–17 | ENH-004 effort allow-list, forge-receipt keys, Chat harness scope, parallelism ceiling, Copilot `--model` probe reframing, Opus pin probe |
| P2 — host lanes + reconcile | 18–40 | Grok Build in host-support, Cursor/Gemini/Copilot extensions, tier-map GPT-6 / Grok 4.7, forge-worktree secret scan |
| P3 — deeper extend / defects / probes | 41–55 | Gemini settings/AfterAgent/extension, Cursor agents/Bugbot, PermissionDenied, openai.yaml, premise/sanitize/triage defects |

## Full list

| Rank | ID | Type | Disposition | Refresh proposal? | Surfaces | Note |
|---:|---|---|---|---|---|---|
| 1 | ENH-007 | correct | **update** |  | codex-cli | emit-codex-config.py still emits approval_policy=untrusted on the restrictive branch (line 197). Atlas: vendor retired untrusted. |
| 2 | ENH-008 | reconcile | **update** |  | codex-cli | codex-cli-customization.md and host-support.json still claim identical PascalCase tool-name values; atlas: apply_patch + hosted WebSearch have no Claude-shaped path. |
| 3 | ENH-020 | correct | **update** |  | copilot-vscode | host-support.json:62 still says chat.hooks.enabled; atlas/VS Code: chat.useHooks. |
| 4 | ENH-021 | reconcile | **update** |  | copilot-vscode | copilot-chat-customization.md:18 still says .claude/settings.json hooks load without chat.useClaudeHooks gate. |
| 5 | ENH-051 | correct | **update** |  | codex-cli | ai-coding-right-size-cost-decision-tree.md:22 and :48 still say latency-only; five-host re-verification marks this contradicted. Line 37 (per-token) can stay with a total-tokens rider. |
| 6 | ENH-011 | correct | **update** |  | codex-cli | host-support.json:232 still says model_reasoning_effort takes a Codex model id; generator does not emit effort from tier. |
| 7 | ENH-025 | reconcile | **update** | yes | cursor | Repo still states silent allow on malformed JSON (cursor-customization.md:34; host-support.json:94). Atlas: docs split invalid-JSON block vs crash/timeout fail-open. Update knowledge to that split; keep live probe. |
| 8 | ENH-001 | reconcile | **update** |  | claude-code | claude-code-permissions.md:81 still cites v2.1.228+/v2.1.233+; atlas: v2.1.283 for terminal and VS Code. |
| 9 | ENH-009 | reconcile | **update** |  | codex-cli | AGENTS.md still 49,679 bytes; host-support.json:306 has no 32 KiB caveat; emit-codex-config.py does not warn. |
| 10 | ENH-049 | reconcile | **update** |  | grok-build | cheap-lane-delegation/SKILL.md:136 still says CLI rejects xhigh for Grok; atlas: Grok 4.7 documents xhigh. Scope the rejection note to 4.5/4.6 probe models. |
| 11 | ENH-016 | correct | **update** |  | copilot-cli | host-support.json:184 still denies Copilot CLI user slash commands; installer does not link commands/. |
| 12 | ENH-004 | correct | **update** |  | claude-code | Ten core agents still carry effort: normal; check-frontmatter.py has no effort allow-list. |
| 13 | ENH-031 | en-route-defect | **update** |  |  | RECEIPT_KEY_ALLOWLIST still omits model, subagent_type, effort — forge-pipeline SKILL claims they are stored. |
| 14 | ENH-019 | reconcile | **update** |  | copilot-vscode | copilot-chat-customization.md still lacks Local vs Agent Host harness scoping. |
| 15 | ENH-005 | reconcile | **update** |  | claude-code | CLAUDE.md parallelism table still reads unlimited as uncapped; no Claude Code 20-concurrent caveat beside it. |
| 16 | ENH-048 | reconcile | **update** |  | copilot-cli | agent-routing-matrix.md:55 still states only confirmed-working --model is auto; five-host marks contradicted by docs that allow slug pinning — reframe as dated probe + re-probe. |
| 17 | ENH-050 | probe | **update** |  | claude-code | substrate-tier-map / model-catalog still pin claude-opus-4-8; lineup and atlas note Opus 5.5 on Copilot/Bedrock — probe still open. |
| 18 | ENH-042 | new-lane | **update** |  | grok-build | host-support.json hosts list has no grok-build (only claude-code, copilot, codex, cursor, gemini, aider, windsurf). New lane still absent. |
| 19 | ENH-022 | reconcile | **update** |  | copilot-vscode | Chat sibling-path Write ceiling still marked unverified in knowledge; atlas cites workspace-folder-only for built-in tools. |
| 20 | ENH-013 | reconcile | **update** |  | copilot-cli | SessionStart tier-A claim predates prompt-mode repo-hook gate; reconcile still needed. |
| 21 | ENH-014 | reconcile | **update** |  | copilot-cli | Customization doc still says path references never auto-load; atlas: Copilot CLI @path imports do. |
| 22 | ENH-010 | probe | **update** |  | codex-cli | Probe still open: Codex local hook fail-open vs host-support fail-closed claim for every other host. |
| 23 | ENH-043 | reconcile | **update** |  | grok-bot | Grok Bot quieter check-ins advice still needs 10-minute approval expiry caveat. |
| 24 | ENH-044 | extend | **update** |  | grok-bot | delegate-via-expert-bots has no Cursor Cloud Agents routing lane yet. |
| 25 | ENH-023 | extend | **update** |  | copilot-vscode | Chat doc still says compaction cannot be steered; atlas: setting can turn it off. |
| 26 | ENH-002 | extend | **update** |  | claude-code | guard-memory-compaction.sh still only blocks shrink; no near-cap (200-line / 25 KB) warn path. |
| 27 | ENH-026 | extend | **update** |  | cursor | wire_cursor does not write a .cursorignore secret-path block. |
| 28 | ENH-003 | improve | **update** |  | claude-code | No disable-model-invocation: true on /reset-plugin-cache or setup skills (only unrelated power-platform skill mentions the key). |
| 29 | ENH-015 | new-lane | **update** |  | copilot-cli | No repo mention of Copilot CLI experimental local OS sandbox as a containment lane. |
| 30 | ENH-037 | extend | **update** |  | gemini-cli | scripts/emit-gemini-config.py missing; Gemini posture projection not shipped. |
| 31 | ENH-024 | extend | **update** |  | copilot-vscode | Chat sandbox still documented only as a limit; chat.agent.sandbox.enabled not reflected. |
| 32 | ENH-027 | extend | **update** |  | cursor | wire_cursor wires hooks + rules only; no .cursor/skills/ linking. |
| 33 | ENH-045 | improve | **update** |  | grok-bot | Grok Bot money/deletion/social safeguards still persona-text only; Auto-review Ask-first rules not wired. |
| 34 | ENH-028 | improve | **update** |  | cursor | Cursor enforcing hooks still lack failClosed / exit-2-on-adapter-failure hardening in installer projection. |
| 35 | ENH-052 | reconcile | **update** | yes | codex-cli | substrate-tier-map.json still gpt-5.6-luna/terra/sol; lineup already documents GPT-6 Luna/Sol (and gpt-6.1-sol naming). Prefer aligning the map to current Codex docs, not deprecating the ENH. |
| 36 | ENH-053 | reconcile | **update** | yes | grok-build | substrate-tier-map still grok-4.5/4.6; lineup + atlas name grok-4.7 as flagship. Update the map; do not drop the ENH. |
| 37 | ENH-032 | en-route-defect | **update** |  |  | forge-worktree.sh:400 still scans ls-files -co (whole tree); tracked .env.example still blocks checkpoint. |
| 38 | ENH-054 | reconcile | **update** |  | grok-build | cross-tool-model-lineup-2026.md:171 still says each sub-agent runs in an isolated worktree; atlas: opt-in per request. |
| 39 | ENH-046 | reconcile | **update** |  | grok-bot | create-grok-bot/SKILL.md:28 still says skills are GLOBAL. |
| 40 | ENH-055 | reconcile | **update** |  | copilot-vscode | lineup still lists chat/ask/edit/agent; atlas: Agent, Plan, Ask + custom. |
| 41 | ENH-038 | reconcile | **update** |  | gemini-cli | gemini-customization.md still lists three settings locations; atlas: four merged files. |
| 42 | ENH-029 | extend | **update** |  | cursor | scripts/generate-cursor-agents.py does not exist; no .cursor/agents/ projection. |
| 43 | ENH-006 | extend | **update** |  | claude-code | hooks.json has no PermissionDenied entry; auto-mode denials still invisible to hook-events. |
| 44 | ENH-039 | extend | **update** |  | gemini-cli | Gemini AfterAgent (exit 2 = retry) not wired as Stop-lane counterpart. |
| 45 | ENH-017 | extend | **update** |  | copilot-cli | copilot-cli-customization.md:198 still marks allowed-tools as not yet adopted. |
| 46 | ENH-012 | extend | **update** |  | codex-cli | forge-pipeline and spawn-team agents/openai.yaml files are absent; allow_implicit_invocation not shipped. |
| 47 | ENH-018 | improve | **update** |  | copilot-cli | generate-copilot-plugin.py still states model/effort in headers only; no per-agent settings.json snippet. |
| 48 | ENH-047 | improve | **update** |  | grok-bot | grok-bot-token-spend still says set account on-demand limits without the Settings path / mid-run overshoot. |
| 49 | ENH-030 | new-lane | **update** |  | cursor | No .cursor/BUGBOT.md lane from install --host cursor. |
| 50 | ENH-033 | en-route-defect | **update** |  |  | premise-gate.py:163 still uses substring settle match (unsettled contains settled). |
| 51 | ENH-034 | en-route-defect | **update** |  |  | sanitize-webfetch-body.py still has ```\s*system\b.*\Z pattern that can eat post-fence content. |
| 52 | ENH-035 | en-route-defect | **update** |  |  | triage-outcome.sh still truncates compound subjects to 40 chars; cause-gate prefix match hazard remains. |
| 53 | ENH-036 | en-route-defect | **update** |  |  | _PHASE_RE still optionalizes the word Phase, so numbered headings open phases. |
| 54 | ENH-040 | probe | **update** |  | gemini-cli | gemini-extension.json absent; probe to package skills/agents as a Gemini extension still open. |
| 55 | ENH-041 | probe | **update** |  | gemini-cli | host-support.json gemini activation_gate still none; atlas: project hooks untrusted-by-default. |

## By type

### correct (6)

- **ENH-007** (r1) — **update** — Stop emitting retired approval_policy = "untrusted" in the Codex sandbox projection
- **ENH-020** (r3) — **update** — host-support.json calls the Chat hooks switch `chat.hooks.enabled`; VS Code documents `chat.useHooks`
- **ENH-051** (r5) — **update** — Correct 'Codex reasoning level costs latency, not dollars': Codex docs say higher effort also raises token usage
- **ENH-011** (r6) — **update** — Correct 'model_reasoning_effort takes a Codex model id' and map agent tier to effort on Codex
- **ENH-016** (r11) — **update** — host-support.json denies Copilot CLI user slash commands; docs list .claude/commands/ and /SKILL-NAME
- **ENH-004** (r12) — **update** — Ten agents declare `effort: normal`, a value outside the documented low/medium/high/xhigh/max set

### reconcile (19)

- **ENH-008** (r2) — **update** — Narrow 'identical tool-name values' for Codex: edits are apply_patch, and hosted WebSearch has no hook path
- **ENH-021** (r4) — **update** — Chat doc says `.claude/settings.json` hooks load; VS Code needs `chat.useClaudeHooks`, default off
- **ENH-025** (r7) — **update** · *refresh proposal* — Reconcile 'malformed hook response silently allows' with Cursor's documented block on invalid JSON
- **ENH-001** (r8) — **update** — Permissions note says auto is default from v2.1.228 on paid plans; docs now say v2.1.283 in terminal and VS Code
- **ENH-009** (r9) — **update** — Disclose Codex's 32 KiB AGENTS.md limit: this repo's root AGENTS.md is 49,679 bytes
- **ENH-049** (r10) — **update** — Scope 'CLI rejects xhigh' in the cheap-lane table to the Grok models tested: Grok 4.7 documents xhigh
- **ENH-019** (r14) — **update** — Chat doc's instruction and hook claims are not scoped to the Local harness; Agent Host harnesses differ
- **ENH-005** (r15) — **update** — Parallelism 'unlimited' reads as uncapped, but Claude Code refuses a 21st concurrent subagent by default
- **ENH-048** (r16) — **update** — Reconcile 'only confirmed-working Copilot CLI --model value is auto' with documented --model pinning by slug
- **ENH-022** (r19) — **update** — Ceiling table marks Chat sibling-path Write `[unverified]`; VS Code documents built-in tools as workspace-folder-only
- **ENH-013** (r20) — **update** — Copilot CLI SessionStart tier A predates the documented prompt-mode repo-hook gate (-p needs an env var)
- **ENH-014** (r21) — **update** — Customization doc says path references never auto-load; Copilot CLI documents @path imports that do
- **ENH-043** (r23) — **update** — Reconcile 'batch into quieter check-ins' with the 10-minute expiry of approvals on Bot-to-Bot work
- **ENH-052** (r35) — **update** · *refresh proposal* — Reconcile Codex tier ids (gpt-5.6-luna/terra/sol) with the gpt-6-luna and gpt-6.1-sol names Codex docs now give
- **ENH-053** (r36) — **update** · *refresh proposal* — Reconcile the Grok tier map (grok-4.5/4.6) with the atlas's grok-4.7 latest model and the lineup file
- **ENH-054** (r38) — **update** — Reconcile 'each Grok Build sub-agent runs in an isolated worktree' with opt-in per-request isolation
- **ENH-046** (r39) — **update** — Reconcile 'skills are GLOBAL' with per-Bot enablement of private skills in the Grok Bot plugins
- **ENH-055** (r40) — **update** — Reconcile Copilot Chat modes (chat/ask/edit/agent) with the Agent, Plan, Ask and custom roles VS Code documents
- **ENH-038** (r41) — **update** — Reconcile the three settings locations in gemini-customization.md with Gemini's four merged settings files

### en-route-defect (6)

- **ENH-031** (r13) — **update** — forge-receipt.py drops model, subagent_type and effort from every receipt, so the run log cannot say how a gate ran
- **ENH-032** (r37) — **update** — forge-worktree.sh checkpoint refuses whenever any .env-shaped file is tracked, even if unchanged
- **ENH-033** (r50) — **update** — premise-gate.py reads 'unsettled' and 'falsified' as settled, and its blast floor misses .md work
- **ENH-034** (r51) — **update** — sanitize-webfetch-body.py deletes the rest of a page after a closing code fence followed by the word 'system'
- **ENH-035** (r52) — **update** — cause-triage opens negatives on successful read-only commands and cause-gate matches unrelated ones on a 40-char prefix
- **ENH-036** (r53) — **update** — premise-gate.py parses numbered headings as phases, so a numbered sub-heading can make an over-floor phase pass

### extend (12)

- **ENH-044** (r24) — **update** — Route coding tasks to Cursor Cloud Agents through Grok Bot delegation in the delegate-via-expert-bots loop
- **ENH-023** (r25) — **update** — Chat doc says automatic compaction cannot be steered; VS Code documents a setting that turns it off
- **ENH-002** (r26) — **update** — Warn when MEMORY.md nears the documented 200-line / 25 KB load cap, not only when it shrinks
- **ENH-026** (r27) — **update** — Write a marker-delimited .cursorignore block for secret paths so Cursor's Agent and search cannot read them
- **ENH-037** (r30) — **update** · missing: `scripts/emit-gemini-config.py` — Project the comfort posture onto Gemini's approval mode and sandbox network setting, tighten-only
- **ENH-024** (r31) — **update** — Chat doc lists sandbox only as a limit; VS Code documents `chat.agent.sandbox.enabled` OS-level containment
- **ENH-027** (r32) — **update** — Wire RavenClaude skills into Cursor: install --host cursor should link skills into .cursor/skills/
- **ENH-029** (r42) — **update** · missing: `scripts/generate-cursor-agents.py` — Project RavenClaude agents to .cursor/agents/ with readonly: true on review-only agents, as the Codex lane does
- **ENH-006** (r43) — **update** — Register a PermissionDenied hook so auto-mode denials reach hook-events and the blocked-exhaustion gate
- **ENH-039** (r44) — **update** — Wire Gemini AfterAgent (exit 2 = automatic retry turn) as the Stop-lane counterpart
- **ENH-017** (r45) — **update** — Adopt Copilot's skill allowed-tools frontmatter, currently marked 'not yet adopted'
- **ENH-012** (r46) — **update** · missing: `plugins/ravenclaude-core/skills/forge-pipeline/agents/openai.yaml, plugins/ravenclaude-core/skills/spawn-team/agents/openai.yaml` — Ship agents/openai.yaml with allow_implicit_invocation: false for explicit-only skills on Codex

### improve (5)

- **ENH-003** (r28) — **update** — Use disable-model-invocation: true as a documented user-only gate on /reset-plugin-cache and setup skills
- **ENH-045** (r33) — **update** — Back the money, deletion and social-post safeguards with Auto-review 'Ask first' rules, not persona text alone
- **ENH-028** (r34) — **update** — Set failClosed on Cursor enforcing hooks and exit 2 on adapter failure so crashes stop failing open
- **ENH-018** (r47) — **update** — Pin projected agents' model and effort through Copilot's per-agent settings.json entry, not just a header note
- **ENH-047** (r48) — **update** — Name the on-demand cap path and its mid-run overshoot in grok-bot-token-spend

### new-lane (3)

- **ENH-042** (r18) — **update** — Record Grok Build in host-support.json: reads CLAUDE.md and Claude hook matchers, but hook failures fail open
- **ENH-015** (r29) — **update** — Record Copilot CLI's experimental local OS sandbox as a containment lane; no repo file mentions it
- **ENH-030** (r49) — **update** — Add a .cursor/BUGBOT.md lane: the layout .mdc rule never reaches Cursor Bugbot PR reviews

### probe (4)

- **ENH-050** (r17) — **update** — Probe whether the Claude tier map's claude-opus-4-8 pin lags the Opus 5.5 that the Bedrock opus alias resolves to
- **ENH-010** (r22) — **update** — Probe whether Codex local hooks fail open on error or timeout; host-support.json:94 says every other host fails closed
- **ENH-040** (r54) — **update** — Package ravenclaude-core as a Gemini extension to carry the skills and agents the installer cannot wire
- **ENH-041** (r55) — **update** — Reconcile host-support.json gemini activation_gate 'none' with Gemini's untrusted-by-default project hooks

## What would flip a disposition to deprecate

1. `repo_claim` quote absent from HEAD **and** the proposed edit would re-introduce a stale vendor fact.
2. Atlas watch MATERIAL finding that withdraws the cited cell (quote gone / page removed).
3. An owner Keep/Update/Deny that rejects the lane (especially `new-lane` / large `extend` items).

## Method (this session)

For each ENH-* entry: re-read repo_claim / repo_files against HEAD on cursor/harness-feature-disposition-b608; cross-check five-host-reverification.md where it seeds the same fact. Atlas register status stays proposed (validator R_REGISTER). Disposition is the follow-on keep/update/deprecate decision.

Checked: claim substring still in cited file (39 claim-bearing entries all present);
target-file existence for extend/new-lane (missing: `scripts/emit-gemini-config.py`,
`scripts/generate-cursor-agents.py`, two `agents/openai.yaml`); spot checks of
`RECEIPT_KEY_ALLOWLIST`, `effort: normal` count (10), `wire_cursor` (no skills),
`host-support.json` hosts (no grok-build), `substrate-tier-map.json` (gpt-5.6 + grok-4.5/4.6),
AGENTS.md size (49679).

