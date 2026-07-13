# generative-web-media

**AI multimedia for brand & winery sites — a creative brief in, on-brand / web-optimized / license-clean assets out, behind a mandatory human curation gate.**

This plugin is the shared **foundation** for generating and shipping production web media: it routes a brief to the right generator, turns raw output into web-ready markup, pins a commercial-use license, and gates every asset on brand + accessibility before it can ship. It is provider-neutral (Grok-lean for images where competitive) and deliberately deep on images + web integration + legal safeguards + brand/accessibility, while *routing* video / 3D / audio competently.

> **Scope honesty.** This ships generative-media engineering judgment — **not legal advice and not a guarantee that any provider price or model capability is current.** Every price in the knowledge bank is marked `[unverified — confirm on provider pricing page]`. Legal/regulatory facts carry a retrieval date. Verify before you spend or commit on a client's behalf.

## The four agents

| Agent | Use it for |
|---|---|
| `generation-strategist` | Which generator/model for this asset; draft-vs-final cost tiering; editing round-trips (inpaint/outpaint/bg-removal/upscale); brand-style-reference setup. |
| `web-asset-pipeline-engineer` | Raw asset → AVIF/WebP responsive `<picture>` with explicit dims; LCP/CLS-safe markup; accessible muted-autoplay video embeds; `<model-viewer>` glTF; framework fit. |
| `asset-provenance-guardian` | Commercial-use license pinning (flags the FLUX-dev non-commercial trap); the provenance ledger; per-project generation budgets; EU AI Act Art.50 disclosure copy. |
| `brand-and-accessibility-reviewer` | Brand-hex/style conformance; anti-slop QA; AI-drafted + human-reviewed WCAG alt text; the mandatory human curation sign-off. |

## Quickstart

1. **Set your provider key.** The plugin declares the **fal** MCP server (`https://mcp.fal.ai/mcp`) so the substrate auto-wires on install. fal's hosted MCP is free + pay-per-run; the API key is the only manual input:

   ```shell
   export FAL_KEY="…"          # required for the fal substrate
   export XAI_API_KEY="…"      # optional — direct Grok path off fal
   ```

   If the declarative binding can't carry the `Authorization: Bearer $FAL_KEY` header in your Claude Code version, run [`/wire-media-substrate`](commands/wire-media-substrate.md) (a one-line `claude mcp add` with the header) or use the direct-provider script — see [Substrate](#substrate) below. **The tool is never a silent dead end:** the first `/generate-web-asset` run checks the substrate and tells you how to wire it if it's absent.

2. **Generate + ship an asset:** `/generate-web-asset` runs the end-to-end flow (route → generate → license-pin → web-optimize → brand/accessibility gate → **human curation sign-off**). It cannot report "done" without a curation artifact.

3. **Audit before launch:** `/audit-asset-licenses` scans a project's provenance ledgers for the FLUX-dev non-commercial trap and missing records; `/check-generation-budget` reports spend against the per-project cap.

## Commands

| Command | Does |
|---|---|
| [`/generate-web-asset`](commands/generate-web-asset.md) | End-to-end brief → shipped asset, with the hard curation gate. |
| [`/audit-asset-licenses`](commands/audit-asset-licenses.md) | Executable FLUX-trap + missing-provenance-record detector over a project. |
| [`/wire-media-substrate`](commands/wire-media-substrate.md) | Fallback substrate wiring when the declarative fal binding is insufficient. |
| [`/check-generation-budget`](commands/check-generation-budget.md) | Per-project generation spend vs the budget cap. |

## Scripts (probe-and-degrade, never a silent pass)

| Script | Runtime | Degrades to |
|---|---|---|
| [`scripts/web-optimize/optimize-image.mjs`](scripts/web-optimize/optimize-image.mjs) | Node + Sharp (via `npx`) | **LOUD-SKIP** with the exact `npx`/Sharp prerequisite if Node/Sharp is absent — "THIS IS NOT A PASS". |
| [`scripts/provenance.py`](scripts/provenance.py) | Python 3 stdlib | Prints the missing-input reason and exits non-zero — never a silent success. |
| [`scripts/gen-budget.py`](scripts/gen-budget.py) | Python 3 stdlib | Same LOUD-fail discipline; you supply every price. |
| [`scripts/generate-via-provider.sh`](scripts/generate-via-provider.sh) | `curl` + env key | LOUD-SKIP if `curl` or the key env-var is absent, printing exactly what to set. |

**Optimizer prerequisite:** the `<picture>` optimizer needs Node ≥ 18 with `sharp` (fetched on demand via `npx --yes`). On an offline/no-node host the optimizer **loudly skips** and the pipeline degrades to guidance-only — the web-ready output is gold *when the optimizer runs*, partial otherwise. This is stated plainly, not rounded up.

## Substrate

The generation substrate is the **fal** hosted MCP (declared in `plugin.json`). Three paths, in order:

1. **Declarative binding (default)** — auto-wired on install; set `FAL_KEY`.
2. **`/wire-media-substrate` (fallback)** — `claude mcp add` with the `Authorization: Bearer $FAL_KEY` header, for Claude Code versions where the declarative block can't carry auth.
3. **Direct provider (`generate-via-provider.sh`)** — a thin `curl` path to e.g. `api.x.ai/v1` for Grok, off fal entirely, so the preferred provider isn't gated behind fal adoption.

See [`NOTICE.md`](NOTICE.md) for third-party MCP attribution and the key-as-reference posture (keys are referenced by env-var name, never committed).

## Foundation role

This plugin is the shared foundation the **`brand-identity-studio`** plugin consumes: it owns the single provider matrix, the license/indemnity/provenance layer, raw generation, and web-optimization. `brand-identity-studio` sends a generation brief (the frozen schema in [`templates/asset-brief.md`](templates/asset-brief.md)) and consumes assets — it does not re-implement these layers. The DTCG design-token **producer** is `web-design:design-tokens-scaffolding`; this plugin only **consumes** tokens. See [`CLAUDE.md`](CLAUDE.md) §0.2.

## Requires

`ravenclaude-core@>=0.7.0`.
