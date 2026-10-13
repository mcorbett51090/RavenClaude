# Unified Model Matrix (UMM)

**SSOT** for every model / agent / effort routing decision in ravenclaude-core.
Machine form: [`unified-model-matrix.json`](unified-model-matrix.json) (+ [`unified-model-matrix.schema.json`](unified-model-matrix.schema.json)).

**Last reviewed:** 2026-10-13 · **Owner:** ravenclaude-core (domain-neutral).

> **NOT `agent-routing-matrix`.** UMM answers *which tier × surface cell* (fast/balanced/top + archival pins + cheap-lane cells). Host/task-shape recommendations live in [`agent-routing-matrix.md`](agent-routing-matrix.md). Nav: [`routing-map.md`](routing-map.md).

## Claim

There is **one** matrix. Today's cheap-lane **agent × model × effort × budget** cells are the canonical tier×agent table; on-Claude role→tier mapping and archival surface pins (PreCompact / handoff fill / Explore) are **rows on that matrix**, not parallel doctrines.

## Tier rows (shared IDs)

| Tier | Claude alias | Use |
|---|---|---|
| `fast` | `haiku` | Volume: search, summarize, extract, format, inventory, archival fill |
| `balanced` | `sonnet` | Bounded edits against a plan |
| `top` | `opus` / frontier | Gates, adjudication, Team Lead judgment |

## Agent × tier cells (cheap-lane SSOT folded in)

| Tier | Claude | Grok (model / effort / perspective · budget) | Copilot (honesty) |
|---|---|---|---|
| `fast` | haiku | grok-4.5 / low / scanner · 15 turns / 300s | `--model auto`; **no `--effort`** with auto — timeout 300s only unless pinned |
| `balanced` | sonnet | grok-4.5 / high / architect · 30 turns / 600s | same auto limit; timeout 600s |
| `top` | opus | grok-4.6 / high / critic · 60 turns / 1200s (never auto-assigned) | same auto limit; timeout 1200s |

Grok cells come from [`substrate-tier-map.json`](substrate-tier-map.json) (same map FORGE uses). Copilot effort honesty is live-verified (2026-08-26) — see cheap-lane skill nuance.

### Grok visibility when `cheap_lane.mode: off` (HARD · M4)

**`mode: off` means inactive routing, not “Grok unsupported.”** The matrix always lists Grok (and Copilot) rows `[docs-verified 2026-09-16 — unified-model-matrix.json agent rows + comfort-posture-balanced.yaml cheap_lane.mode: off]`. Dashboards and docs must keep those columns visible; operators turn routing on with `advise` \| `agent`.

## Surfaces (default rows)

| Surface | Default agent | Default tier | mode gate | never-inherit-session | fit-override |
|---|---|---|---|---|---|
| session (Team Lead) | claude | top | n/a | false | n/a |
| subagent (scout / volume) | claude | fast | n/a | true if unpinned Explore → pin | volume → fast |
| subagent (coder) | claude | balanced | n/a | false | — |
| subagent (gate / review) | claude | top | n/a | false | **never demote gates** |
| cheap-lane | grok (default) \| copilot | fast | `cheap_lane.mode` | n/a (left session) | asymmetric → claude on ambiguity |
| tribunal seats | claude | per seat | Thing stakes | n/a | **cited-only** — no auto demotion (M6) |
| precompact | claude (fallback) | **fast** / haiku | cheap_lane for cheap path | **true** | summarize/extract → fast |
| handoff fill | claude detached | **fast** / haiku | — | **true** | extract → fast |
| explore (unpinned) | claude | **fast** / haiku pin | handoff_tax | **true** (pin) | — |
| explore (override agent, v0.352.0) | claude | **fast** / haiku via [`agents/explore.md`](../agents/explore.md) (tools: Read, Grep, Glob) | none (holds without a posture file) | **true** | — |
| advisor (session, v0.352.0) | claude | main `sonnet` (Sonnet 5.5, `claude-sonnet-5-5`) → advisor `opus` (Opus 5.5, `claude-opus-5-5`) | launcher-owned (`advisorModel` / `--advisor`); Anthropic API only | n/a | consult at plan lock / 2nd identical error / after dod-gate; skip < ~10 turns; **never overrides a gate or tool evidence** |

## Advisor (added 2026-10-13, v0.352.0)

`[docs-verified 2026-10-13 — code.claude.com/docs/en/advisor, platform.claude.com/docs/en/about-claude/models/overview]`

- **Pairing:** Sonnet 5.5 main (`claude-sonnet-5-5`) accepts Fable, Opus 5 or later, or Sonnet 5.5 as advisor, so `sonnet` + `opus` (Opus 5.5, `claude-opus-5-5`) is valid. Haiku 5.5 (`claude-haiku-5-5`) as main or advisor needs Claude Code 2.1.293+. Subagents inherit the advisor and run the same pairing check against their own model.
- **Enablement is outside this plugin.** Set by the fleet launcher (`--advisor opus` or `"advisorModel": "opus"`). Anthropic API only (not Bedrock, Vertex, Foundry). Off when `DISABLE_TELEMETRY` or another flag-fetch kill is set; `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` disables it. A background run with a bad pairing starts silently without the advisor.
- **Cost:** each call re-reads the full transcript **uncached** at Opus rates ($4 / $20 per MTok). About $0.60 input per call at 150k tokens. Cheaper than an Opus main model on long sessions; overhead on short ones. Toggling it does not break the main model's prompt cache.
- **Timing is model-driven.** No setting forces or caps calls. Steering is the CLAUDE.md "Advisor checkpoints" section plus the runaway-brake advisory on the 2nd identical mutating call. Monitor with `/usage` and the `Advising` transcript lines.
- **Deterministic gates stay first.** dod-gate, the tribunal, and guard denies are not replaced by an advisory model.

### Rejected: JEV per-turn router

JEV (TypeSafe AI's classifier, run through community proxies such as jevcc / jev-router) was evaluated and **rejected**:

1. **Third-party proxy that sends prompt context to TypeSafe** and needs a `JEV_API_KEY`. That is new egress of task text, which this matrix's non-claims rule out.
2. **Routes once per human turn, not per micro-fork.** Tool-loop steps and subagents keep the session tier. The "routes tool choice / retry forks in milliseconds" claim is unverified; no source gives a latency or quality benchmark.
3. **Conflicts with the central model pin and this matrix.** The fleet launcher pins Sonnet / xhigh, and the matrix plus `agent-dispatch-evaluator.sh` own tier decisions. A second router would fight both.
4. **Savings are unmeasured.** One catalog entry calls the routing defaults "the author's choices, not measured quality or savings".
5. **Breaks the prompt cache.** Switching the main model mid-session invalidates the cached prefix; the advisor does not.

## Posture knobs (`model_matrix.surfaces`)

```yaml
model_matrix:
  surfaces:
    explore_pin: haiku
    precompact_fallback: haiku
    handoff_fill: haiku
    never_inherit_session: [precompact, handoff, explore]
cheap_lane:                 # unchanged
  mode: off                 # default stays off
  tier: fast
  agent: grok
handoff_tax:                # meter caps stay; pin_explore = one-release alias
  report_cap_words: 400
  brief_cap_words: 600
  pin_explore: haiku        # ALIAS → surfaces.explore_pin
model_tier_surfaces:        # ALIAS one release → surfaces.*
  precompact_fallback_model: haiku
  handoff_fill_model: haiku
```

**Precedence:** `model_matrix.surfaces.*` wins when both new and old keys are set; absent new ⇒ old alias ⇒ haiku default. Seed-only for consumers (House Rule 3): existing custom posture is never clobbered by marketplace update; absent ⇒ old defaults.

**Phase D (0.323.14) soak:** SessionStart advisory when old keys are sole source or diverge; dashboard Save writes **only** `model_matrix.surfaces.*` for these pins (aliases still hydrate/read). Aliases remain in seed until a later soak-window drop.

## Locked levers

1. **surface** — session \| subagent \| cheap-lane \| tribunal \| precompact \| handoff \| explore  
2. **mode** — off \| advise \| agent (containment; orthogonal to “may leave session”)  
3. **agent** — claude \| grok \| copilot — Grok only when matrix routes `agent=grok`  
4. **model / effort / budget** — per tier × agent cell above  
5. **fit-override** — force cheaper tier for summarize/extract/format/inventory; **never escalate late/frontier by default**  
6. **never-inherit-session** — hard true for precompact, handoff fill, Explore pin  

## Pointers (folded docs)

| Was | Now |
|---|---|
| `skills/cheap-lane-delegation` matrix table | **Canonical cells** in this JSON; skill keeps live-verified nuance + points here |
| `knowledge/model-tier-delegation.md` | **Stub** → this file (short role table retained) |
| `model_tier_surfaces` (0.323.10) | `model_matrix.surfaces.precompact_fallback` / `handoff_fill` (+ aliases) |
| `handoff_tax.pin_explore` | `model_matrix.surfaces.explore_pin` (+ alias) |
| Thing `panel.*.model` | Cited tribunal surface only — composition change, not silent re-tier |
| Native CC auto-compact summarizer | **Out of matrix** — host-limited; honesty non-claim |

## Non-claims

- Does **not** enable `cheap_lane` by default  
- Does **not** fix native Claude Code auto-compact (still session model)  
- Does **not** auto-rewrite tribunal seat models  
- No new egress of task text beyond today's cheap_lane gate  

## Related

- [`routing-map.md`](routing-map.md) — four-row nav (spawn-team / agent-routing / agent-routing-matrix / UMM)  
- [`agent-routing-matrix.md`](agent-routing-matrix.md) — host×task-shape matrix (**different Q**)  
- [`substrate-tier-map.json`](substrate-tier-map.json) — Grok (+ FORGE) host rows  
- [`model-tier-delegation.md`](model-tier-delegation.md) — stub pointer  
- [`concepts/cheap-lane-agent-matrix.md`](concepts/cheap-lane-agent-matrix.md) — Copilot effort honesty  
- Comfort seed: `templates/comfort-posture-balanced.yaml`
