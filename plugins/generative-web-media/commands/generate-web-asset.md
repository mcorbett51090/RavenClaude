---
description: "End-to-end: a creative brief -> routed generation -> license-pinned -> web-optimized (AVIF/WebP responsive <picture>) -> brand + accessibility gate -> MANDATORY human curation sign-off. Cannot reach done without a curation artifact."
argument-hint: "[what asset + for which page + client or internal + brand source]"
---

You are running `/generative-web-media:generate-web-asset`. Orchestrate all four agents end to end.

> Generative-media judgment, not legal advice. Every provider price is `[unverified — confirm on provider pricing page]`. Keys (`FAL_KEY`/`XAI_API_KEY`) are read from env by name, never committed.

## Preconditions (check first — never a silent dead tool)

1. **Substrate check.** Confirm the fal MCP is wired (needs `FAL_KEY`) OR a direct-provider key is set. If neither: run `scripts/generate-via-provider.sh --check` and instruct the user to `export FAL_KEY=…` / run [`/wire-media-substrate`](wire-media-substrate.md). Do **not** proceed silently against a dead tool (red-team RT2).

## Steps

1. **Capture the brief** — the asset, the page, client-vs-internal, and the brand token source (a DTCG file or `brand-extraction`'s `brand.json`). Shape it into the frozen [`../templates/asset-brief.md`](../templates/asset-brief.md) contract.
2. **Pin the license first** (`asset-provenance-guardian`) — traverse the license-first tree; block FLUX-dev/non-commercial on client work; pick a Firefly-class indemnified provider if `indemnity_required`. Record intent to the ledger.
3. **Route + generate** (`generation-strategist`) — pick the modality lane, the provider/model (matrix-sourced, Grok-lean where competitive), draft-vs-final tiering; prefer an editing round-trip if a brand-locked asset exists. Log spend with `gen-budget.py`.
4. **Web-optimize** (`web-asset-pipeline-engineer`) — run `scripts/web-optimize/optimize-image.mjs` (LOUD-SKIP + manual pipeline if Node/Sharp is absent); emit AVIF/WebP responsive `<picture>` with explicit dims + LCP/CLS-safe markup, or the real video/3D embed.
5. **Record provenance** (`asset-provenance-guardian`) — `provenance.py record` with license class + indemnity + C2PA status; add EU Art.50 disclosure copy if the site serves EU visitors.
6. **Brand + accessibility gate** (`brand-and-accessibility-reviewer`) — brand-hex/style conformance, anti-slop QA (reject baked-in text), AI-drafted + human-reviewed alt text.
7. **HARD GATE — human curation sign-off.** The flow **cannot report done** without a recorded human selection artifact (who / what / when / alt approved). If it is absent, STOP and request it — the gate is a blocker, not a suggestion (red-team RT6).

## Output

The shipped `<picture>`/embed markup, the provenance record path, the license class + indemnity status, the budget status, and the curation sign-off record. Any price `[unverified]`.
