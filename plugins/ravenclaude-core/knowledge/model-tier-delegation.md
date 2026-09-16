# Model-tier delegation — stub pointer (folded into UMM)

> **As of 0.323.11 this file is a stub.** The SSOT is
> [`unified-model-matrix.md`](unified-model-matrix.md) +
> [`unified-model-matrix.json`](unified-model-matrix.json).
> Cheap-lane agent×model×effort cells, Claude role→tier mapping, and archival
> surface pins (PreCompact / handoff / Explore) all live there.

**Last reviewed:** 2026-09-16. Companion still useful for deep hooks/meter prose:
[`handoff-tax-meter`](../hooks/handoff-tax-meter.sh), [`explore-tier-pin`](../hooks/explore-tier-pin.sh),
[`spawn-team`](../skills/spawn-team/SKILL.md). Nested-dispatch determination and
roster ratchets (Gates 287–289) are unchanged; see git history of this file pre-0.323.11
for the long-form doctrine if you need the dated verification trail.

## Short role → tier table (Claude / on-session)

| Role in the run | Tier | `model:` alias |
|---|---|---|
| Decompose / judge / adjudicate (Team Lead) | **top** / frontier | `opus` |
| Search, grep, classify, extract, format, inventory | **fast** | `haiku` |
| Bounded code edits against a plan | **balanced** | `sonnet` |
| Gates that hold merge (security / final review) | **top** / frontier | `opus` — **never demote** |
| Recovery when a worker botches it | escalate **up** one tier | — |

Claude alias map: `fast`↔`haiku`, `balanced`↔`sonnet`, `top`↔`opus`.

## Archival surfaces (never inherit session)

| Surface | Default | Posture SSOT | One-release alias |
|---|---|---|---|
| PreCompact Claude fallback | haiku / fast | `model_matrix.surfaces.precompact_fallback` | `model_tier_surfaces.precompact_fallback_model` |
| Handoff MODEL FILL | haiku / fast | `model_matrix.surfaces.handoff_fill` | `model_tier_surfaces.handoff_fill_model` |
| Un-pinned Explore | haiku / fast | `model_matrix.surfaces.explore_pin` | `handoff_tax.pin_explore` |

Absent ⇒ haiku. Raising to sonnet is a comfort override. Opus/fable/session/inherit → haiku.
**Honesty:** Claude Code native auto-compact summarizer still uses the **session model** — UMM does not claim that path is fixed.

## Tribunal (cited-only)

Thing `panel.*.model` seats are a **composition** surface. UMM cites them; it does **not** auto-demote seats for savings (M6). ≥2 distinct backbones invariant unchanged.

## Cheap lane

Off by default. When `cheap_lane.mode` ∈ {advise, agent}, cells are the Grok/Copilot rows of the UMM JSON. `mode: off` = inactive routing — **Grok remains listed** in the matrix (M4).

## Knobs (meter caps stay under handoff_tax)

| Knob | Where | Default |
|---|---|---|
| `model_matrix.surfaces.explore_pin` | comfort-posture | `haiku` |
| `model_matrix.surfaces.precompact_fallback` | same | `haiku` |
| `model_matrix.surfaces.handoff_fill` | same | `haiku` |
| `handoff_tax.report_cap_words` / `brief_cap_words` | same | 400 / 600 |
| `handoff_tax.pin_explore` | same | alias → explore_pin (one release) |
| `cheap_lane.mode` | same | `off` |

Self-test pins: `python3 plugins/ravenclaude-core/scripts/explore-tier-pin.py --self-test`,
`precompact-digest.py --self-test`, `context-handoff.py --self-test`.
