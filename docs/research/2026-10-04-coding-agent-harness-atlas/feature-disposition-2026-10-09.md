# Enhancement register — disposition (2026-10-09)

**Implementation pass (same day):** 55 **done**, 0 still **update**. Machine twin: [`data/register-dispositions.json`](data/register-dispositions.json).

> Register `status` remains `proposed` for the atlas validator. Disposition is backlog truth.

## Status after implementation

| disposition | count |
|---|---:|
| **done** | 55 |
| **update** | 0 |

## Follow-through closed this pass (were update)

- **ENH-050** (r17) — Kept `claude-opus-4-8` pin; `notes.claude_aliases` records Bedrock/Copilot alias skew.
- **ENH-013** (r20) — SessionStart Tier A mechanism text names held-constant prompt-mode env vars; re-probe before tier D.
- **ENH-010** (r22) — Top-level `hook_error_posture`; Codex explicit-deny + exit-0 success; local crash/timeout still `[unverified]`.
- **ENH-023** (r25) — Precompact-guard README offers opt-in auto-compaction-off setting (never default).
- **ENH-024** (r31) — `rcwt new` pins `chat.agent.sandbox.enabled` by default (`RCWT_NO_CHAT_SANDBOX=1` opt-out).
- **ENH-039** (r44) — AfterAgent contract documented; Stop-lane wiring held until stdin payload verified.
- **ENH-017** (r45) — `allowed-tools` adopted on `scenario-retrieval`; docs match.
- **ENH-040** (r54) — Gemini extension packaging shipped; skills/agents stay unsupported until live install.

## Done

- **ENH-007** (r1) · correct — Stop emitting retired approval_policy = "untrusted" in the Codex sandbox projection
- **ENH-008** (r2) · reconcile — Narrow 'identical tool-name values' for Codex: edits are apply_patch, and hosted WebSearch has no hook path
- **ENH-020** (r3) · correct — host-support.json calls the Chat hooks switch `chat.hooks.enabled`; VS Code documents `chat.useHooks`
- **ENH-021** (r4) · reconcile — Chat doc says `.claude/settings.json` hooks load; VS Code needs `chat.useClaudeHooks`, default off
- **ENH-051** (r5) · correct — Correct 'Codex reasoning level costs latency, not dollars': Codex docs say higher effort also raises token usage
- **ENH-011** (r6) · correct — Correct 'model_reasoning_effort takes a Codex model id' and map agent tier to effort on Codex
- **ENH-025** (r7) · reconcile — Reconcile 'malformed hook response silently allows' with Cursor's documented block on invalid JSON
- **ENH-001** (r8) · reconcile — Permissions note says auto is default from v2.1.228 on paid plans; docs now say v2.1.283 in terminal and VS Code
- **ENH-009** (r9) · reconcile — Disclose Codex's 32 KiB AGENTS.md limit: this repo's root AGENTS.md is 49,679 bytes
- **ENH-049** (r10) · reconcile — Scope 'CLI rejects xhigh' in the cheap-lane table to the Grok models tested: Grok 4.7 documents xhigh
- **ENH-016** (r11) · correct — host-support.json denies Copilot CLI user slash commands; docs list .claude/commands/ and /SKILL-NAME
- **ENH-004** (r12) · correct — Ten agents declare `effort: normal`, a value outside the documented low/medium/high/xhigh/max set
- **ENH-031** (r13) · en-route-defect — forge-receipt.py drops model, subagent_type and effort from every receipt, so the run log cannot say how a gate ran
- **ENH-019** (r14) · reconcile — Chat doc's instruction and hook claims are not scoped to the Local harness; Agent Host harnesses differ
- **ENH-005** (r15) · reconcile — Parallelism 'unlimited' reads as uncapped, but Claude Code refuses a 21st concurrent subagent by default
- **ENH-048** (r16) · reconcile — Reconcile 'only confirmed-working Copilot CLI --model value is auto' with documented --model pinning by slug
- **ENH-042** (r18) · new-lane — Record Grok Build in host-support.json: reads CLAUDE.md and Claude hook matchers, but hook failures fail open
- **ENH-022** (r19) · reconcile — Ceiling table marks Chat sibling-path Write `[unverified]`; VS Code documents built-in tools as workspace-folder-only
- **ENH-014** (r21) · reconcile — Customization doc says path references never auto-load; Copilot CLI documents @path imports that do
- **ENH-043** (r23) · reconcile — Reconcile 'batch into quieter check-ins' with the 10-minute expiry of approvals on Bot-to-Bot work
- **ENH-044** (r24) · extend — Route coding tasks to Cursor Cloud Agents through Grok Bot delegation in the delegate-via-expert-bots loop
- **ENH-002** (r26) · extend — Warn when MEMORY.md nears the documented 200-line / 25 KB load cap, not only when it shrinks
- **ENH-026** (r27) · extend — Write a marker-delimited .cursorignore block for secret paths so Cursor's Agent and search cannot read them
- **ENH-003** (r28) · improve — Use disable-model-invocation: true as a documented user-only gate on /reset-plugin-cache and setup skills
- **ENH-015** (r29) · new-lane — Record Copilot CLI's experimental local OS sandbox as a containment lane; no repo file mentions it
- **ENH-037** (r30) · extend — Project the comfort posture onto Gemini's approval mode and sandbox network setting, tighten-only
- **ENH-027** (r32) · extend — Wire RavenClaude skills into Cursor: install --host cursor should link skills into .cursor/skills/
- **ENH-045** (r33) · improve — Back the money, deletion and social-post safeguards with Auto-review 'Ask first' rules, not persona text alone
- **ENH-028** (r34) · improve — Set failClosed on Cursor enforcing hooks and exit 2 on adapter failure so crashes stop failing open
- **ENH-052** (r35) · reconcile — Reconcile Codex tier ids (gpt-5.6-luna/terra/sol) with the gpt-6-luna and gpt-6.1-sol names Codex docs now give
- **ENH-053** (r36) · reconcile — Reconcile the Grok tier map (grok-4.5/4.6) with the atlas's grok-4.7 latest model and the lineup file
- **ENH-032** (r37) · en-route-defect — forge-worktree.sh checkpoint refuses whenever any .env-shaped file is tracked, even if unchanged
- **ENH-054** (r38) · reconcile — Reconcile 'each Grok Build sub-agent runs in an isolated worktree' with opt-in per-request isolation
- **ENH-046** (r39) · reconcile — Reconcile 'skills are GLOBAL' with per-Bot enablement of private skills in the Grok Bot plugins
- **ENH-055** (r40) · reconcile — Reconcile Copilot Chat modes (chat/ask/edit/agent) with the Agent, Plan, Ask and custom roles VS Code documents
- **ENH-038** (r41) · reconcile — Reconcile the three settings locations in gemini-customization.md with Gemini's four merged settings files
- **ENH-029** (r42) · extend — Project RavenClaude agents to .cursor/agents/ with readonly: true on review-only agents, as the Codex lane does
- **ENH-006** (r43) · extend — Register a PermissionDenied hook so auto-mode denials reach hook-events and the blocked-exhaustion gate
- **ENH-012** (r46) · extend — Ship agents/openai.yaml with allow_implicit_invocation: false for explicit-only skills on Codex
- **ENH-018** (r47) · improve — Pin projected agents' model and effort through Copilot's per-agent settings.json entry, not just a header note
- **ENH-047** (r48) · improve — Name the on-demand cap path and its mid-run overshoot in grok-bot-token-spend
- **ENH-030** (r49) · new-lane — Add a .cursor/BUGBOT.md lane: the layout .mdc rule never reaches Cursor Bugbot PR reviews
- **ENH-033** (r50) · en-route-defect — premise-gate.py reads 'unsettled' and 'falsified' as settled, and its blast floor misses .md work
- **ENH-034** (r51) · en-route-defect — sanitize-webfetch-body.py deletes the rest of a page after a closing code fence followed by the word 'system'
- **ENH-035** (r52) · en-route-defect — cause-triage opens negatives on successful read-only commands and cause-gate matches unrelated ones on a 40-char prefix
- **ENH-036** (r53) · en-route-defect — premise-gate.py parses numbered headings as phases, so a numbered sub-heading can make an over-floor phase pass
- **ENH-041** (r55) · probe — Reconcile host-support.json gemini activation_gate 'none' with Gemini's untrusted-by-default project hooks
- **ENH-050** (r17) · probe — Probe whether the Claude tier map's claude-opus-4-8 pin lags the Opus 5.5 that the Bedrock opus alias resolves to
- **ENH-013** (r20) · reconcile — Copilot CLI SessionStart tier A predates the documented prompt-mode repo-hook gate (-p needs an env var)
- **ENH-010** (r22) · probe — Probe whether Codex local hooks fail open on error or timeout; host-support.json:94 says every other host fails closed
- **ENH-023** (r25) · extend — Chat doc says automatic compaction cannot be steered; VS Code documents a setting that turns it off
- **ENH-024** (r31) · extend — Chat doc lists sandbox only as a limit; VS Code documents `chat.agent.sandbox.enabled` OS-level containment
- **ENH-039** (r44) · extend — Wire Gemini AfterAgent (exit 2 = automatic retry turn) as the Stop-lane counterpart
- **ENH-017** (r45) · extend — Adopt Copilot's skill allowed-tools frontmatter, currently marked 'not yet adopted'
- **ENH-040** (r54) · probe — Package ravenclaude-core as a Gemini extension to carry the skills and agents the installer cannot wire
