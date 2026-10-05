# Five-host re-verification of the routing matrix's lever facts

Generated from `five-host-reverification.json`. Every lever fact that the routing matrix and the knowledge files it cites state for five hosts, checked against the verified atlas lever cells (vendor docs retrieved 2026-10-04).

**15 hold, 11 changed, 2 contradicted, 14 not covered** (42 facts).

**How far to trust this.** An opus reviewer produced the verdicts. I checked that every cited atlas cell exists and is not undocumented, and that every quote is in the cited evidence (39 of 42 verbatim once markup is ignored; 3 differ only by a link target or an ellipsis). I did not re-adjudicate each verdict. Three `holds` rows carry a caveat below. Atlas columns: `copilot-chat` is the atlas column `copilot-vscode`; `grok-build-cli` is `grok-build`.

`contradicted` means a verified atlas quote says otherwise as a current fact; `changed` means the atlas shows a newer or different value and the file's statement was plausible when written; `not-covered` means no atlas cell bears on it, or the cell is undocumented. Contradicted and changed rows are seeds for the register (`correct`) and inputs to the routing-matrix precursor PR.

## claude-code (5)

| Status | Fact | Source | Atlas cells | Evidence | Note |
|---|---|---|---|---|---|
| changed | Claude tier map: fast claude-haiku-4-5-20251001, balanced claude-sonnet-5, top claude-opus-4-8 | `rc/knowledge/substrate-tier-map.json:8` | `claude-code/F17.model-catalog` | E-claude-code-01997 | Newer Opus is the alias target (the quote covers Bedrock only). The full ids are pinned, so they may still work; the first-party default is not quoted. |
| changed | Current Claude opus id is claude-opus-4-8 and fable is claude-fable-5 | `rc/knowledge/model-catalog.json:6` | `claude-code/F17.model-catalog` | E-claude-code-01997 | Bedrock-scoped quote. The sibling capability map already calls Opus 4.8 and Fable 5 Legacy. |
| holds | Claude Code has a native effort dial for non-default effort | `rc/knowledge/agent-routing-matrix.md:154` | `claude-code/F18.where-set` | E-claude-code-07046, E-claude-code-00122 | Also the /effort selector slider (E-claude-code-00122). |
| holds | Dynamic Workflows in Claude Code orchestrate hundreds of parallel subagents | `claude-app-engineering/knowledge/model-selection-and-2026-capability-map.md:39` | `claude-code/F14.parallel-subagents`, `claude-code/F14.total-agent-caps` | E-claude-code-01274, E-claude-code-15872 | A run is capped at 1,000 agents (E-claude-code-15872). Caveat: holds for orchestration of many subagents; the atlas states a 1,000-agent cap per run, not a parallel count. |
| not-covered | Opus 5 effort defaults to high in Claude Code | `claude-app-engineering/knowledge/model-selection-and-2026-capability-map.md:16` | `claude-code/F18.effort-values` | none | Atlas quotes only a Projects default ('a new project runs every thread on Opus at high effort') without naming Opus 5. Per-model session defaults are not quoted. |

## codex-cli (9)

| Status | Fact | Source | Atlas cells | Evidence | Note |
|---|---|---|---|---|---|
| contradicted | Raising the Codex reasoning level costs latency, not dollars | `ai-coding-model-guidance/knowledge/ai-coding-right-size-cost-decision-tree.md:22` | `codex-cli/F18.thinking-budget-visibility` | E-codex-cli-00172 | More tokens cost more. Line 48 ('latency only') says the same thing. Line 37 ('no change in per-token cost') is not contradicted. |
| changed | Codex tier map: fast gpt-5.6-luna, balanced gpt-5.6-terra, top gpt-5.6-sol | `rc/knowledge/substrate-tier-map.json:28` | `codex-cli/F17.model-picker` | E-codex-cli-01182 | Codex docs now point to gpt-6-luna and gpt-6.1-sol. There is no Terra tier in the quote. |
| changed | Codex pro is a reasoning mode on Sol, not a separate slug | `rc/knowledge/substrate-tier-map.json:40` | `codex-cli/F18.effort-values`, `codex-cli/F18.model-dependence` | E-codex-cli-00649, E-codex-cli-01886 | Atlas gives Sol's effort as Light to Ultra and never names a pro mode. It is possibly renamed; treat it as unconfirmed. |
| changed | Codex balanced default is GPT-6 Sol | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:33` | `codex-cli/F17.model-picker`, `codex-cli/F18.model-dependence` | E-codex-cli-01182 | Docs name gpt-6.1-sol, not GPT-6 Sol, so the model was renamed or bumped. |
| holds | Codex cheapest fast tier is GPT-6 Luna | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:28` | `codex-cli/F17.model-picker` | E-codex-cli-01182 | The quote confirms the model is offered. That it is the cheapest is pricing and was not checked. Caveat: holds only that the model exists; the pricing claim was not checked. |
| holds | Codex /model switches both the model and its reasoning level | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:136` | `codex-cli/F17.model-picker` | E-codex-cli-01182 | It sets effort only when the model supports it. |
| holds | Reasoning level on Codex is a dial on the same model, separate from changing the model | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:154` | `codex-cli/F18.where-set` | E-codex-cli-02084, E-codex-cli-00649 | Also config model_reasoning_effort. The cost advice is not covered. |
| not-covered | Effort override on Codex CLI goes through an --effort flag (named with cheap-lane's flag) | `rc/knowledge/agent-routing-matrix.md:153` | `codex-cli/F18.where-set` | none | Atlas puts effort in config model_reasoning_effort, /reasoning, the app control and the GitHub action. Only Codex Security CLI has --effort. cheap-lane has no codex agent. |
| not-covered | Codex long-run agent and top tier is GPT-6 Astra | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:30` | `codex-cli/F17.model-catalog` | none | No cited quote names Astra. The catalog cell describes discovery (model/list, codex debug models), not a model list. |

## copilot-cli (10)

| Status | Fact | Source | Atlas cells | Evidence | Note |
|---|---|---|---|---|---|
| contradicted | Copilot CLI's only confirmed-working --model value is auto; six pinned slugs (incl. claude-haiku-4.5) were rejected at the API level | `rc/knowledge/agent-routing-matrix.md:55` | `copilot-cli/F17.model-flag-env` | E-copilot-cli-01391 | Docs document pinning by slug. The file's rejections were a v0.305.0 probe; enterprise model enablement (E-copilot-cli-00353) could explain them, so re-probe. |
| changed | Copilot --effort choices are none\|minimal\|low\|medium\|high\|xhigh\|max | `rc/skills/cheap-lane-delegation/SKILL.md:136` | `copilot-cli/F18.effort-values` | E-copilot-cli-00962 | The docs list five values, without none or minimal. The settings effortLevel accepts low..xhigh, default medium (E-copilot-cli-03753). |
| holds | Copilot CLI takes an --effort flag for non-default effort | `rc/knowledge/agent-routing-matrix.md:153` | `copilot-cli/F18.effort-values` | E-copilot-cli-00962 | The sentence refers to cheap-lane's wrapper flag. The host flag exists. |
| holds | Copilot Auto has named tiers efficiency / balance / intelligence, available in Copilot CLI | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:100` | `copilot-cli/F17.auto-routing` | E-copilot-cli-00900 | The file marks this [verify-at-use]. |
| holds | Copilot CLI has task-based auto model selection (Auto routes by task) | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:122` | `copilot-cli/F17.auto-routing` | E-copilot-cli-00369 |  |
| holds | Copilot model availability varies by plan and org policy; admins must enable models | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:106` | `copilot-cli/F17.model-catalog` | E-copilot-cli-00353 | The five-vendor picker claim in the same sentence is not covered. |
| not-covered | Copilot tier models as display names: Claude Haiku 4.5, Claude Sonnet 5, Claude Opus 5 | `rc/knowledge/substrate-tier-map.json:33` | `copilot-cli/F17.model-flag-env` | none | Atlas lists no Copilot model set. Its --model examples are slugs (claude-haiku-4.5), not the display names this map uses. |
| not-covered | Copilot CLI offers Claude Fable 5.1, Opus 5.5, GPT-6 Astra, Grok 4.6 and others as of 2026-09 | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:130` | `copilot-cli/F17.model-catalog` | none | Atlas has no model list for Copilot, only example slugs (gpt-5.4, claude-haiku-4.5). |
| not-covered | Copilot --model auto rejects --effort; effort applies only with a pinned effort-capable model | `rc/skills/cheap-lane-delegation/SKILL.md:122` | `copilot-cli/F18.model-dependence`, `copilot-cli/F17.auto-routing` | none | Atlas says only that some models support reasoning levels. It does not address Auto combined with --effort. |
| not-covered | No valid pinned Copilot --model slug is discoverable non-interactively | `rc/skills/cheap-lane-delegation/SKILL.md:121` | `copilot-cli/F17.model-catalog`, `copilot-cli/F17.model-flag-env` | none | Atlas cites a Supported AI models docs page and example slugs, and lists available models via /model. Non-interactive enumeration is not addressed. |

## copilot-chat (8)

| Status | Fact | Source | Atlas cells | Evidence | Note |
|---|---|---|---|---|---|
| changed | Models are selectable in VS Code across all modes: chat / ask / edit / agent | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:117` | `copilot-vscode/F19.named-modes` | E-copilot-vscode-00291 | The atlas lists the roles as Agent, Plan, Ask and custom. There is no Edit mode, and Plan is new. |
| changed | Copilot Chat's chat-mode surface is 'Copilot Chat / edit' | `ai-coding-model-guidance/knowledge/ai-coding-mode-selection-decision-tree.md:41` | `copilot-vscode/F19.named-modes` | E-copilot-vscode-00291 | No Edit mode is named. The supervised read/answer role is now Ask (no edits) or Plan. |
| holds | VS Code Copilot Chat exposes an interactive model picker directly | `rc/knowledge/agent-routing-matrix.md:57` | `copilot-vscode/F17.model-picker` | E-copilot-vscode-00165 | The file calls it the /model picker; the atlas describes a picker in the chat input field, not a /model command. |
| holds | Copilot Auto routing tiers roll out in VS Code | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:100` | `copilot-vscode/F17.auto-routing` | E-copilot-vscode-01056 | VS Code has an autoTier setting. The three tier names are quoted only from the CLI docs. |
| holds | Copilot offers Auto; let it pick the model unless you have a reason to override | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:119` | `copilot-vscode/F17.auto-routing` | E-copilot-vscode-00175 | The when-to-override advice is editorial and was not checked. |
| holds | Enterprise admins can set model=auto as the default for new conversations | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:113` | `copilot-vscode/F17.model-flag-env` | E-copilot-vscode-01178 | The policy is chat.defaultModel and needs VS Code 1.127 or later. |
| not-covered | GitHub tracks Copilot model availability per client (VS Code, Copilot CLI), not per Chat vs CLI, so both resolve through one copilot row | `rc/knowledge/agent-routing-matrix.md:53` | `copilot-vscode/F17.model-catalog`, `copilot-cli/F17.model-catalog` | none | Catalog cells say availability depends on harness, account and policy; neither mentions a per-client availability table. |
| not-covered | Copilot top tier is Claude Opus 5.5 and the balanced default is Claude Sonnet 5 | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:32` | `copilot-vscode/F17.model-catalog` | none | Atlas names no specific Copilot models in VS Code. |

## grok-build-cli (10)

| Status | Fact | Source | Atlas cells | Evidence | Note |
|---|---|---|---|---|---|
| changed | Grok tier map: fast and balanced use grok-4.5, top uses grok-4.6 | `rc/knowledge/substrate-tier-map.json:12` | `grok-build/F17.model-catalog` | E-grok-build-00144 | Atlas names grok-4.7 as the latest model. It does not mention 4.5 or 4.6 or say they are gone. |
| changed | Each Grok Build sub-agent runs in an isolated Git worktree/branch | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:171` | `grok-build/F14.parallel-subagents` | E-grok-build-00044, E-grok-build-00066 | Worktree isolation is opt-in per request, not automatic. GROK_SUBAGENTS also defaults to 0 (E-grok-build-00066). |
| changed | Grok CLI --effort accepts low\|medium\|high and rejects xhigh | `rc/skills/cheap-lane-delegation/SKILL.md:136` | `grok-build/F18.effort-values` | E-grok-build-00344 | xhigh is supported on Grok 4.7. The rejection was probed against the 4.5/4.6 tier models, which have no documented levels. |
| holds | Grok 4.7 is the current Grok flagship, superseding 4.6, and is used in Grok Build | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:161` | `grok-build/F17.model-catalog` | E-grok-build-00144 | Latest-model holds. The quote is from the Grok Build overview page but speaks of the API; Grok Build CLI availability is not stated directly. Caveat: holds for the latest-model claim; the quote is about the xAI API and does not state Grok Build CLI availability. |
| holds | Grok Build has a plan mode | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:171` | `grok-build/F19.plan-mode` | E-grok-build-00029 | The file's 'sub-task graph in a TUI' detail is not quoted. Plan mode gates edit tools, not the shell. |
| not-covered | Grok effort per tier: fast=low, balanced/top=high on grok-4.5/grok-4.6 | `rc/knowledge/substrate-tier-map.json:13` | `grok-build/F18.model-dependence` | none | Atlas lists effort levels for Grok 4.7 only (low, medium, high, xhigh). It gives none for 4.5 or 4.6. |
| not-covered | Grok 4.6 is the balanced/mid Grok option and still selectable | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:33` | `grok-build/F17.model-catalog` | none | Atlas names only grok-4.7. |
| not-covered | Grok 4.6 is the Grok Build CLI default model; 4.5 remains selectable (2026-08-14) | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:5` | `grok-build/F17.model-flag-env` | none | Atlas documents GROK_DEFAULT_MODEL and -m but gives no default value. |
| not-covered | grok-build-0.1, grok-build, grok-4.3 and grok-4.20 are unknown model ids in the Grok Build CLI | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:167` | `grok-build/F17.model-catalog` | none | Atlas does not list rejected ids. |
| not-covered | Grok Build runs up to 8 parallel sub-agents | `ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md:171` | `grok-build/F14.concurrency-caps`, `grok-build/F14.total-agent-caps` | none | The concurrency cell quotes only a 50 scheduled-task cap, and total-agent-caps is undocumented. |
