# 2026 Q1-Q2 coding-agent failure modes (H1 retrospective)

> Cross-source synthesis of agent-specific failure modes observed in production across H1 2026. Updates the existing `codex-failure-modes.md` taxonomy with what's new since the 2025 catalog. Source: `/tmp/research-codex-2026-updates.md` §5 + §8.

---

## The three dominant clusters (H1 2026 100-deployment retro — digitalapplied.com)

1. **Eval gaps** — passes dev (human-curated golden set), degrades in prod when input distribution shifts. Root cause: golden set used only to gate initial release; no behavioral assertions for silent regressions; no prod-trace replay against golden set in CI.

2. **Tool-call chaos** — malformed arguments, retried mutating tools without idempotency keys, hanging tools without timeouts, infinite loops on ambiguous error states. The mechanical fix is per-tool timeouts + idempotency keys on every mutating call + bounded retries + structured tool error responses.

3. **Governance theatre** — security/approval workflows that look thorough but don't actually constrain agent behavior. Audit the must-fail path (the marketplace's audit-gates.sh discipline).

---

## Six agent-specific failure modes (cross-source consensus 2026)

| # | Mode | Detection signal | Mitigation |
|---|---|---|---|
| 1 | **Tool misuse** | Tool fails with similar args twice | spec-reread + decision-tree intake |
| 2 | **Context loss** | Sessions >10 turns show measurable 15-30% retention drop | compact at ~60% fill; structured snapshots |
| 3 | **Goal drift** | Plan diverges from spec by >30% over time | spec-reread ritual at structured intervals |
| 4 | **Retry loops** (cost-runaway) | Same operation retried >3× | bounded retries; idempotency keys; cap recursive depth |
| 5 | **Cascading errors** in multi-agent | Subagent failure not surfaced to orchestrator | structured-output protocol + adjudicator escalation |
| 6 | **Silent quality degradation** | Tests pass; production output observably worse | prod-trace replay against golden set in CI |

`[verify-at-use — 2026-06-04 — Latitude / MindStudio / Trantor / digitalapplied retrospectives]`

---

## The memory wall (five sub-failures specific to long-running jobs)

Per MindStudio's 2026 memory-wall analysis:

1. **Context overflow** — relevant context truncated as session grows
2. **Instruction dilution** — original spec attention drops below new turns
3. **Error accumulation** — wrong-path edits compound silently
4. **State loss** — cross-turn state forgotten
5. **Evaluation blindness** — agent stops noticing its own quality drop

Anthropic-published mitigation data: **context editing alone delivered 29% perf improvement; context-editing + memory tool reached 39%; 84% token consumption reduction in a 100-turn web-search eval.** `[verify-at-use — 2026-06-04]`

---

## Context-rot consensus (Chroma 2025 study, widely cited 2026)

All 18 frontier models degrade via lost-in-the-middle + attention dilution + distractor interference. Independent benchmarks:
- A 200K-advertised model becomes unreliable around ~130K.
- A 1M-token model degrades around 600-700K.

**The 2026 rule of thumb: budget by fill %, not token count; compact proactively past ~60%.** `[verify-at-use]`

---

## New in 2026 (not in the 2025 catalog)

Items called out explicitly as **new** for 2026:

- **Silent-allow preToolUse hook regression** (Copilot CLI < 1.0.59).
- **Plugin auto-install global-config leak** (Copilot CLI < 1.0.56).
- **Silent diff-not-reported to ACP clients** (Copilot CLI < 1.0.48).
- **"Last 30%" problem named distinctly from "eval gap"** (Devin-specific origin, now generalized).
- **Governance theatre** named distinctly from technical failures.
- **Memory-wall five-failure taxonomy** is structurally new.
- **Runaway-cost recursive loop** is now top-tier production failure, not edge case (Indie Hackers 2026 case: $4K/mo projection hit $11.2K in three weeks).

---

## Mechanical mitigations (the H1 2026 consensus)

| Mitigation | Lands as |
|---|---|
| **Validator handoff after every multi-file edit batch >3 files** | RavenClaude's `audit-gates.sh` + `prettier --check .` + JSON validity + `bash -n` |
| **Per-call timeout + idempotency key + bounded retries on mutating tools** | Diff-budget skill discipline |
| **Compact proactively past ~60% context fill** | Diff-budget skill (fill-% gating) |
| **Decision-tree workflow framing** | Each skill's intake-decision block |
| **Spec-reread ritual at structured intervals (every 30 min, every PR open)** | `spec-reread-ritual` skill |
| **Prod-trace replay against golden set in CI** | (gap in RavenClaude today; track as future enhancement) |

---

## Tool-version floors that prevent regression-class failures

> **Corrected 2026-09-03 (`dependency-update-sweep` Phase 1 fix-forward).** The three original
> Copilot rows and the Cursor row were unsourced and, on cross-check against this repo's own
> already-completed re-derivation, **wrong or fabricated**:
> [`plugins/ravenclaude-core/skills/external-agent-onboarding/SKILL.md`](../../plugins/ravenclaude-core/skills/external-agent-onboarding/SKILL.md)
> re-derived the Copilot floor table verbatim from the
> [copilot-cli changelog](https://github.com/github/copilot-cli/blob/main/changelog.md)
> `[checked verbatim 2026-07-28]` and found *"preToolUse silent-allow regression fixed (1.0.59)"* and
> *"diff-not-reported-to-ACP fixed (1.0.48)"* **appear nowhere in it**, the config-leak fix is
> **1.0.57**, not 1.0.56 (1.0.56 is a different fix), and the Cursor **≥ 3.3** claim carried "no
> citation of any kind." The rows below are the same source's real, cited floors — this row set is
> now a mirror of that skill's table, not an independent claim; if they drift, fix both in one PR
> (this repo's own dated-supersession convention).

| Tool | Minimum version | Why | Source · retrieved |
|---|---|---|---|
| GitHub Copilot CLI | **≥ 1.0.52** (safety floor) | *"Hooks (preToolUse, postToolUse, subagentStart, subagentStop) now fire correctly for sub-agent tool…"* — below it a sub-agent's tool calls are not hooked at all | [changelog.md](https://github.com/github/copilot-cli/blob/main/changelog.md) `[docs-verified 2026-07-28, cross-checked 2026-09-03]` |
| GitHub Copilot CLI | **≥ 1.0.57** (recommended) | *"Plugins auto-installed from repository settings no longer leak into user global config"* | [changelog.md](https://github.com/github/copilot-cli/blob/main/changelog.md) `[docs-verified 2026-07-28, cross-checked 2026-09-03]` |
| GitHub Copilot CLI | **≥ 1.0.62** (recommended) | *"PostToolUse hook matchers (e.g. Edit-pipe-Write) are now honored instead of silently dropped"* | [changelog.md](https://github.com/github/copilot-cli/blob/main/changelog.md) `[docs-verified 2026-07-28, cross-checked 2026-09-03]` |
| Claude Code | latest | Plugin marketplace + `reloadSkills` + expanded hook events | `[unverified — training knowledge, no specific version cited]` |

**Deleted:** the original Cursor **≥ 3.3** row — unsourced, no citation of any kind, and already
deleted from the sibling table above for the same reason. Do not restore it without a source.

---

## See also

- `plugins/ravenclaude-core/skills/external-agent-onboarding/SKILL.md` — the cross-tool onboarding skill that consumes this doc.
- `plugins/ravenclaude-core/skills/wall-handling/SKILL.md` — memory-wall recovery.
- `plugins/ravenclaude-core/skills/spec-reread-ritual/SKILL.md` — anti-drift mechanic.
- `plugins/ravenclaude-core/skills/diff-budget/SKILL.md` — fill-% gating + per-PR file budget.
- `/tmp/research-codex-failure-modes.md` — the original 12-row taxonomy this doc extends.
- `/tmp/research-codex-2026-updates.md` §5 + §8 — H1 2026 source synthesis.
