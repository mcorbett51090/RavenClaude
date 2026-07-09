---
name: mimir
description: "Claude-Code-session-state surfacing contract for the Mímir dashboard tab. Documents the five reachable on-disk sources under `~/.claude/` and `<project>/.claude/`, the encoded-path algorithm + reverse-decode fallback, the hard scrubbing/torn-write/staleness/worktree/server-parity invariants, the per-card source map, and the honest empty-state contract for in-process-only fields. Read this before authoring or modifying `_read_mimir` (in both `serve-dashboards.py` copies), the `/__mimir` endpoint, the `#/mimir` generator tab, or the Gate 49 render fixture."
last_reviewed: 2026-06-03
confidence: high
---

# Skill: mimir

## What this is

The **surfacing contract** between Claude Code's on-disk session state (under `~/.claude/` + `<project>/.claude/`) and the dashboard's Mímir tab (`#/mimir`, "Session" / "Mímir's well"). It names what is reachable, what isn't, how to read it without leaking user-prompt content, and which honest empty state to render for the in-process-only fields. **Invoke it before editing `_read_mimir` in either `serve-dashboards.py` copy, the `/__mimir` endpoint, the generator tab, or Gate 49.** One reader contract. No mocks. No inlined dynamic bytes.

Plan reference: [`docs/plans/2026-06-03-mimir-session-tab/plan.md`](../../../../docs/plans/2026-06-03-mimir-session-tab/plan.md) §"Phase 0 — Reachability research" + §"Phases" + §"Risk matrix". Per-conflict resolution: `.ravenclaude/runs/forge/mimir-session-tab/gap-delta.md` (gitignored local run-dir artifact) C1-C8. Norse precedents (same glob-and-inline read shape): Heimdall (`/__heimdall`), Víðarr (`/__vidarr`), Norns (`/__norns`), Níðhöggr (`/__nidhoggr`).

## Reachability map

Empirically probed against `~/.claude` on this host (2026-06-03). Per-source: what is reachable, what is not, and the JSON shape excerpt the reader keys off.

| Source                                          | Reachable                                                                                                                                                                                                                                                                       | Not reachable                                                              | Drives                                  |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | --------------------------------------- |
| `~/.claude/settings.json`                       | `theme`, `permissions`, `enabledPlugins`, `extraKnownMarketplaces`, `skipWorkflowUsageWarning`, `skipAutoPermissionPrompt`                                                                                                                                                      | **No `model` key. No `effort` key.** Plan tier (Pro/Max/Team).             | Settings card (theme).                  |
| `<project>/.claude/settings.json`               | `"model": "claude-opus-4-8"` (the configured-model surface), `permissions`, `hooks`                                                                                                                                                                                             | Reasoning effort (in-process).                                             | Settings card (configured model).       |
| `~/.claude/projects/<encoded>/*.jsonl`          | Event stream. Per event: `sessionId`, `cwd`, `gitBranch`, `version`, `timestamp`. Types: `permission-mode`, `user`, `assistant`, `file-history-snapshot`, `ai-title`, `attachment`, `last-prompt`, `queue-operation`, `system`, `pr-link`                                       | **`type=user` event content (HARD DENY — see scrubbing).** `ai-title` content (rejected — titles can echo prompts). | Recent project sessions card; last-used model (newest `type=assistant`'s `model`). |
| `~/.claude/stats-cache.json`                    | `version`, `lastComputedDate`, `dailyActivity[]` (`{date, messageCount, sessionCount, toolCallCount}`), `dailyModelTokens`, `modelUsage` per model (`{inputTokens, outputTokens, cacheReadInputTokens, cacheCreationInputTokens, webSearchRequests, costUSD, contextWindow}`), `totalSessions`, `totalMessages`, `longestSession`, `firstSessionDate`, `hourCounts`, `totalSpeculationTimeSavedMs` | Live current-turn counts. `costUSD: 0` on subscription (tier not stored).  | Activity-summary card.                  |
| `~/.claude/sessions/<pid>.json`                 | `{pid, sessionId, cwd, startedAt, version, kind, entrypoint, status, updatedAt}`                                                                                                                                                                                                | In-process `/status` cache. `/effort` dial.                                | Current-session card (match by `cwd == project_root` AND `status == "busy"`). |

**JSONL event shape excerpts (verified):**

```json
{"type":"permission-mode","permissionMode":"default","sessionId":"...","cwd":"...","gitBranch":"...","timestamp":"..."}
{"type":"assistant","model":"claude-opus-4-8","usage":{"input_tokens":1234,"cache_read_input_tokens":5678,"output_tokens":42,"service_tier":"standard","speed":"standard"},"sessionId":"...","timestamp":"..."}
```

**stats-cache.json shape excerpt:**

```json
{
  "version": "...",
  "lastComputedDate": "2026-06-02",
  "totalSessions": 1234,
  "totalMessages": 56789,
  "dailyActivity": [{"date":"2026-06-02","messageCount":123,"sessionCount":4,"toolCallCount":456}],
  "modelUsage": {"claude-opus-4-8": {"inputTokens":..., "outputTokens":..., "cacheReadInputTokens":..., "costUSD":0}}
}
```

## The encoded-path algorithm + fallback

The Mímir reader must locate the per-project JSONL directory under `~/.claude/projects/<encoded>/`. The algorithm is **two-stage**: compute the documented key, fall back on miss.

### Stage 1 — compute (the documented path)

```python
def encode_project_key(project_root: str) -> str:
    # Strip leading "/", replace every "/" with "-".
    return project_root.lstrip("/").replace("/", "-")
```

Worked examples:

| `$CLAUDE_PROJECT_DIR`                                     | Encoded key                                       |
| --------------------------------------------------------- | ------------------------------------------------- |
| `/workspaces/RavenClaude`                                 | `-workspaces-RavenClaude`                         |
| `/workspaces/RavenClaude/.claude/worktrees/foo`           | `-workspaces-RavenClaude--claude-worktrees-foo`   |
| `/home/codespace/contoso`                                   | `-home-codespace-contoso`                           |

Note the worktree case: the embedded `/.` becomes `--` (one dash for the slash, one for the dot's slash). **Use `$CLAUDE_PROJECT_DIR` verbatim — never normalized.** See §"The worktree-aware rule".

### Stage 2 — fallback (defense against Anthropic ABI drift — gap-delta C3 / Panel-A R1)

If `~/.claude/projects/<computed>/` does not exist, glob `~/.claude/projects/*/` and reverse-decode each candidate (replace `-` with `/`, prepend `/`) to compare against `project_root`. On match, use the candidate. If no candidate matches, return the honest empty state (`{exists: false}`). Anthropic could rotate to URL-encoding / base64 / hash without notice; the fallback keeps Mímir from silently returning empty.

```python
def resolve_project_dir(claude_home: Path, project_root: str) -> Path | None:
    computed = claude_home / "projects" / encode_project_key(project_root)
    if computed.exists():
        return computed
    # Fallback: reverse-decode candidates.
    for candidate in (claude_home / "projects").glob("*"):
        if not candidate.is_dir():
            continue
        decoded = "/" + candidate.name.replace("-", "/")
        if decoded == project_root:
            return candidate
    return None
```

## The hard scrubbing contract (gap-delta C7 + C8)

Two non-negotiable invariants. Both are tested by Gate 49.

1. **NEVER surface `type=user` event content.** The reader extracts **metadata only** from `type=user` events: `timestamp`, `gitBranch`, `entrypoint`. The event's `message.content` field is **never read into the response payload** under any circumstance. Sentinel-string fixture (Gate 49): a JSONL `type=user` event containing `MIMIR_SENTINEL_PROMPT_TEXT` → assert the sentinel does NOT appear anywhere in `/__mimir`'s output.

2. **`_scrub_reason()` applied UNIVERSALLY to all string values at the JSON-encoding boundary.** Source: [`hooks/_scrub.sh`](../../hooks/_scrub.sh) (the substrate-wide invariant from v0.110.0). Apply once, at the encoding boundary — not per call-site (negligible compute; closes the false-negative class where a model alias, branch name, file path, or version string happens to contain a secret-shaped substring). Gate 49 fixture: a branch `feature/Bearer-eyJ...` surfaces as `[REDACTED]`.

3. **Reject `ai-title` surfacing.** Claude-generated session titles can echo prompt text (proper nouns, codenames, project specifics). Treat the field as if it were `type=user` content: read nothing.

## The torn-write discipline (gap-delta C4)

JSONLs are append-only files written by a live Claude Code process. A concurrent writer can leave a partial final line; an unwrapped `json.loads(line)` crashes the endpoint. The reader inherits the Norse-tab pattern:

```python
for line in fh:
    line = line.strip()
    if not line:
        continue
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        continue  # Torn / garbage line — silently drop. NEVER raise.
    # ... process ev
```

Wrap **every** `json.loads(line)` in try-except. Corrupt lines drop silently. The endpoint must never 500 on a partial write.

## The stats-cache staleness disclosure (RM4)

`stats-cache.json` carries `lastComputedDate: "YYYY-MM-DD"` — pre-computed by Claude Code, up to **24h behind**. Without explicit disclosure, the user reads the count as live and trusts a stale number.

**Contract:** every activity card sourcing from `stats-cache.json` MUST display `lastComputedDate` as a **first-class** `as of YYYY-MM-DD` pill — visible, not a tooltip. The Mímir reader emits `as_of: stats["lastComputedDate"]` at the card root; the client render attaches the pill. Gate 49 fixture: a populated card without the pill in the rendered output → assertion fails.

## The worktree-aware rule (RM5)

`$CLAUDE_PROJECT_DIR` is the **only** authoritative project-root signal. Use it **verbatim** — never normalize (no `realpath`, no symlink-resolve, no trailing-slash strip). Worktrees produce their **own** encoded dirs (`/workspaces/RavenClaude/.claude/worktrees/hook-trust-codex` → `-workspaces-RavenClaude--claude-worktrees-hook-trust-codex`), and a normalized lookup collapses them onto main's encoded key — finds zero files silently, renders an empty Mímir tab when the worktree session is in fact active.

Gate 49 fixture: `$CLAUDE_PROJECT_DIR = /workspaces/RavenClaude/.claude/worktrees/foo` → assert the JSONL glob finds the worktree's own sessions, not main's.

## The server-parity discipline (RM6 / Panel-B R3)

`_read_mimir` lives **byte-identically in BOTH `serve-dashboards.py` copies** — the root copy and the bundled-plugin copy (`plugins/ravenclaude-core/scripts/serve-dashboards.py`). Gate 32 verifies the `/__mimir` endpoint **name** appears in both files; it does **NOT** diff the function body bytes. An asymmetric bug-fix to one copy silently passes Gate 32 while the two copies diverge.

**Human discipline (DoD):** every commit that touches `_read_mimir` runs a **two-file diff** on the function bodies before pushing. The git-commit hook does not catch this — the maintainer must.

**Follow-up (out of MVP):** a Gate-32-extended that diffs the `_read_mimir` body bytes between the two copies. Tracked in plan §"Open questions parked" / RM6.

## Per-card source map

The Mímir tab renders four cards. Each card names the source file(s) and field(s) it reads.

| Card                             | Source                                                                                          | Fields read                                                                                                                                                          |
| -------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Current session**              | `~/.claude/sessions/<pid>.json` (match `cwd == project_root` AND `status == "busy"`) + leading `permission-mode` event of the matching `~/.claude/projects/<encoded>/*.jsonl` | `sessionId` (truncated), `version`, `startedAt`, `pid`, `entrypoint`, `kind`; `permissionMode` from JSONL                                                            |
| **Activity summary**             | `~/.claude/stats-cache.json`                                                                    | `lastComputedDate` (as the `as of` pill), `totalSessions`, `totalMessages`, last 7 days of `dailyActivity`, per-model `modelUsage` (`inputTokens`, `outputTokens`, `cacheReadInputTokens`) |
| **Recent project sessions**      | `~/.claude/projects/<encoded>/*.jsonl` (mtime-desc, last 5, bounded 50KB read per file)         | filename (UUID truncated), mtime, count of `type=assistant` events, sum of `output_tokens`, first `gitBranch` (scrubbed) from any event metadata. **NEVER reads `type=user` content.** |
| **Static-host empty state**      | (none — rendered when the dashboard serves from a static host without `/__mimir`)               | Pointer text: "open the served dashboard for live session data" (Heimdall precedent)                                                                                 |

Additional surfaced field: **configured model** from `<project>/.claude/settings.json` + **last-used model** from the newest JSONL's most-recent `type=assistant.model`. Surface both as "Configured: X / Last used: Y" on the Current-session card — catches mid-session `/model` switches without scanning entire JSONLs.

## Unreachable items — honest empty-state contract

Three pieces of Claude Code session state are **in-process only** — not persisted to disk. The Mímir tab must render an honest pointer, NOT a dash, NOT a "—", NOT a "0", NOT a "loading…".

| Field                    | Why unreachable                                                                       | Pointer text                                       |
| ------------------------ | ------------------------------------------------------------------------------------- | -------------------------------------------------- |
| `/effort` reasoning dial | In-process only; never written to `settings.json` or sessions/                        | `"in-process only — run /status in Claude Code"`   |
| Plan tier (Pro/Max/Team) | `costUSD: 0` confirms subscription but no tier label stored anywhere on disk          | `"in-process only — run /status in Claude Code"`   |
| Live `/status` cache     | Held in the Claude Code process; never serialized                                     | `"in-process only — run /status in Claude Code"`   |

**The contract:** the pointer text is literally `"in-process only — run /status in Claude Code"` (a Python string in `_read_mimir`'s response). The client renders it as a muted pill in the card slot. Gate 49 asserts the pointer text is present for each unreachable field; a card showing `—` for an unreachable field is a test failure.

## Output Contract

This skill emits no runtime artifact of its own — it is a *contract*, consumed by the dashboard reader (`_read_mimir`), the `/__mimir` endpoint, the generator tab, and Gate 49. When `prompt-engineer` or `architect` critiques an instance of this contract (e.g. a Phase-2 PR adding `_read_mimir`), the response ends with the cross-plugin Structured Output JSON block per [`structured-output/SKILL.md`](../structured-output/SKILL.md):

```
---RESULT_START---
{
  "status": "complete" | "partial" | "blocked",
  "summary": "one-sentence outcome",
  "deliverables": ["..."],
  "handoff_recommendation": {"to_specialist": "<role or null>", "reason": "..."},
  "confidence": 0.0-1.0,
  "risks_or_open_questions": ["..."],
  "next_actions": ["..."]
}
---RESULT_END---
```

## References

- Plan + risk matrix: [`docs/plans/2026-06-03-mimir-session-tab/plan.md`](../../../../docs/plans/2026-06-03-mimir-session-tab/plan.md).
- Per-conflict resolution: `.ravenclaude/runs/forge/mimir-session-tab/gap-delta.md` (gitignored local run-dir artifact) C1-C8.
- Panel-B reachability findings (the empirical probe): `.ravenclaude/runs/forge/mimir-session-tab/plan-B.md` (gitignored local run-dir artifact) §"Phase 0".
- Substrate-wide scrub helper: [`plugins/ravenclaude-core/hooks/_scrub.sh`](../../hooks/_scrub.sh) (v0.110.0 — the single source of truth for `_scrub_reason()`).
- Norse precedents (same glob-and-inline read shape):
  - **Heimdall** (perimeter-alarm tab — `_read_hook_events`, `/__heimdall`): plugin CLAUDE.md "Heimdall — perimeter-alarm dashboard tab".
  - **Víðarr** (security log tab — `_read_vidarr_events`, `/__vidarr`): plugin CLAUDE.md "Víðarr — posture/security event-log tab".
  - **Norns** (Urðr/Verðandi/Skuld lineage tab — `_read_norns`, `/__norns`): plugin CLAUDE.md "Norns — Urðr / Verðandi / Skuld lineage tab".
  - **Níðhöggr** ("Debt watch" card — `_read_nidhoggr`, `/__nidhoggr`): plugin CLAUDE.md "Níðhöggr 'Debt watch' card".
- Agent-quality rubric (the bar this skill is scored against): [`plugins/ravenclaude-core/skills/agent-quality-rubric/SKILL.md`](../agent-quality-rubric/SKILL.md).
- Structured Output Protocol: [`plugins/ravenclaude-core/skills/structured-output/SKILL.md`](../structured-output/SKILL.md).
- Companion contract (parallel shape — substrate-neutral contract consumed by adapters): [`plugins/ravenclaude-core/skills/adaptive-run-classifier/SKILL.md`](../adaptive-run-classifier/SKILL.md).

---

## Self-score (agent-quality-rubric — target ≥4 every dimension)

Scored against the 6-dimension rubric in [`agent-quality-rubric/SKILL.md`](../agent-quality-rubric/SKILL.md).

| Dimension                          | Score | Anchor / rationale                                                                                                                                                                       |
| ---------------------------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Mission clarity                 | **5** | One-sentence mission stated in §"What this is" first paragraph: surfacing contract between Claude Code session state and the `#/mimir` tab; rest of the file confirms it.               |
| 2. Scope sharpness                 | **5** | Explicit "Unreachable items" table names what the skill does NOT surface (in-process-only fields), with the pointer text to render instead. Scope is bounded by the reachability map.    |
| 3. Capability Grounding alignment  | **4** | Reachability map is grounded in this-session probe (per plan §Phase 0); the encoded-path fallback is the alternate-methods inheritance against ABI drift. Inherits CGP via plugin CLAUDE.md (no per-skill restatement is the marketplace convention). |
| 4. Output-Contract completeness    | **4** | Skill emits a *contract*, not runtime artifacts — the Output-Contract section names the consumers and points reviewers to the canonical SOP JSON block (same pattern as `adaptive-run-classifier`). Reporting cap inherited from the SOP skill.  |
| 5. Escalation paths                | **4** | Server-parity discipline names the follow-up gate owner (RM6 → `code-reviewer`); torn-write / scrubbing / staleness each name the risk-matrix row (RM2/RM7/RM4) that tracks them; security-reviewer is the named owner for RM7/RM8 (scrub + path-traversal). |
| 6. Example scenarios               | **4** | Skill files don't carry the agent-scenario-authoring frontmatter (that's an agent-only schema in `scripts/check-frontmatter.py`); the worked examples for the encoded-path algorithm + the per-card source map + the unreachable-field pointer text are the concrete scenarios a reader needs. |

**Total:** 26/30. **Average:** 4.33. **Disposition:** ships as-is (per rubric: 22-26 ships with minor edits noted in PR description; 27-30 ships as-is). No dimension scored 1; no dimension scored ≤2; mission clarity is 5.
