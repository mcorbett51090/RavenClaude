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

## Claude Code platform notes (2026-09-28 coding-factory adapt — angle-sourced)

These are **Claude Code platform** behaviors (not RavenClaude delegation doctrine); they change how a session's model + effort resolve, so they belong beside the tier map. All angle-sourced; no prices restated beyond the angle. **These do NOT change RavenClaude's canonical `model-catalog.json` `current.opus` (still `claude-opus-4-8`)** — migrating the internal catalog to Opus 5.5 is a separate ratchet/drift-gate change, not this doc adapt.

- **The session default is no longer necessarily the "cheap lane" (CC 2.1.280).** **Pro and Team Standard now default to Opus** (matching Max / Team Premium (plan name UNVERIFIED) / Enterprise), and the default Opus is **Claude Opus 5.5** (`claude-opus-5-5`; 1M context, $4/$20 per Mtok, $0.20/Mtok cache reads). Push-down to `sonnet` / `haiku` for read-a-lot / bounded work stays **explicit** — do not assume the session model is the fast tier. [angle `release-claude-code-2.1.280`]
- **Effort no longer inherits onto a newly released model (CC 2.1.280).** `/effort` levels saved before it became per-model **do not apply to newly released models** (e.g. Opus 5.5 starts at the model default until picked). **Set `/effort` explicitly per model after switching.** Separately, Opus 4.7/4.8 + Fable 5 launch-default effort **no longer overrides** an explicit `effortLevel` set via `-p` / Agent SDK / project / managed / `--settings` / per-model level — so a headless `-p` pack that sets `effortLevel` **is honored** on 4.7/4.8/Fable 5. [angle `release-claude-code-2.1.280`]
- **Managed model allowlist — `availableModelsMatch: "exact"` + `deniedModels` (CC 2.1.283).** With `availableModelsMatch: "exact"`, an `availableModels` entry allows **only that named version** — a new release stays **blocked until it is added to `availableModels`**. `deniedModels` blocks a model **even when `availableModels` allows it** (the cost/risk deny lever). **Ops consequence:** each release-compare model adapt (a new Opus/Sonnet/etc. id) must **also** be added to `availableModels` in the managed settings, or an exact-match org silently cannot select it. [angle `release-claude-code-2.1.283`] See the org-model-policy worksheet's Claude Code section and the proposed `cost-rail-claude-code-managed-model-allowlist` inventory row (proposed, not yet shipped).
