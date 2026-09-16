# Unified Model Matrix (UMM)

**SSOT** for every model / agent / effort routing decision in ravenclaude-core.
Machine form: [`unified-model-matrix.json`](unified-model-matrix.json) (+ [`unified-model-matrix.schema.json`](unified-model-matrix.schema.json)).

**Last reviewed:** 2026-09-16 · **Owner:** ravenclaude-core (domain-neutral).

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

- [`substrate-tier-map.json`](substrate-tier-map.json) — Grok (+ FORGE) host rows  
- [`model-tier-delegation.md`](model-tier-delegation.md) — stub pointer  
- [`concepts/cheap-lane-agent-matrix.md`](concepts/cheap-lane-agent-matrix.md) — Copilot effort honesty  
- Comfort seed: `templates/comfort-posture-balanced.yaml`
