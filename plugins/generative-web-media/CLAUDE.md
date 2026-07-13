# Generative Web Media Plugin — Team Constitution

> Team constitution for the `generative-web-media` Claude Code plugin. Four specialist agents — **generation-strategist**, **web-asset-pipeline-engineer**, **asset-provenance-guardian**, **brand-and-accessibility-reviewer** — plus a knowledge bank, skills, best-practices, templates, commands, and runnable scripts, aimed at one job: take a creative brief and return **on-brand, web-optimized, license-clean multimedia assets with a mandatory human curation gate**. Built for a site builder producing brand or winery sites who wants real judgment on the generator, the license, the web pipeline, and the brand/accessibility bar — not a raw PNG from a text box.
>
> **Orientation:** this file is **domain-specific** to generative web media. For the domain-neutral team constitution every plugin inherits, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 0. Scope, foundation role & verify-at-use (read first)

### 0.1 Scope

This plugin ships **generative-media engineering judgment — not legal advice, not a copyright/ownership guarantee, and not a promise that any provider price or model capability is current.** The agents:

- route a brief to a generator, optimize the output for the web, pin a commercial-use license, and gate on brand + accessibility; they do **not** certify that an asset is legally clear for a given jurisdiction or that a provider's indemnity covers a specific claim — that goes to counsel via `ravenclaude-core/security-reviewer`;
- treat the **provider / model / price / license landscape as volatile**: every model name, capability, and especially every **price** is marked `[unverified — confirm on provider pricing page]` and must be re-confirmed against the provider before it drives a spend or a client commitment;
- store **no client secrets** — API keys (`FAL_KEY`, `XAI_API_KEY`, …) are referenced by env-var name, never written into the repo.

### 0.2 Foundation role — the seam that must not drift

This plugin is the **shared foundation** the sibling brand plugin depends on. It **exclusively owns** the single provider matrix, the single license/indemnity/provenance knowledge base, the cost ledger, raw generation, web-optimization, and the **consumer side of the brand-token contract**.

> **Downstream consumer: the `brand-identity-studio` plugin. This plugin (`generative-web-media`) exposes {provider-matrix, license-layer, brand-token-contract, raw-generation, web-optimization} as the foundation. `brand-identity-studio` MUST NOT re-implement them — it sends a generation brief and consumes assets.**

**Token-producer amendment (settled with the sibling plan).** The DTCG (Design Tokens Community Group) design-token **PRODUCER** is [`web-design:design-tokens-scaffolding`](../web-design/CLAUDE.md); `generative-web-media` only **CONSUMES** tokens through the brand-token contract (§6) — it never generates, owns, or is the source of the token file. `brand-identity-studio` likewise emits a generation brief (the frozen schema in [`templates/asset-brief.md`](templates/asset-brief.md)); it does not own the provider matrix or the license layer. **One home per layer** is the whole point — two matrices that disagree on a Recraft price by month 2 is the failure this seam prevents (red-team RT1).

### 0.3 Verify-at-use

Dated specifics — provider/model capabilities, prices, license terms, regulatory dates — live (flagged) in [`knowledge/`](knowledge/). Prices are **always** `[unverified — confirm on provider pricing page]`; regulatory and license facts carry a retrieval date. Re-confirm before quoting.

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`generation-strategist`](agents/generation-strategist.md) | Brief → provider/model routing across images/video/3D/audio; draft-vs-final cost tiering; brand-style-reference conditioning handoff; editing round-trips (inpaint/outpaint/bg-removal/upscale) | "which generator for this hero image?"; "draft cheap then final?"; "can we edit this instead of regenerating?"; "route this video/3D/audio ask" |
| [`web-asset-pipeline-engineer`](agents/web-asset-pipeline-engineer.md) | Raw asset → production web asset: AVIF/WebP responsive `<picture>` with explicit dims, LCP/CLS-safe markup, muted-autoplay `prefers-reduced-motion` video embeds, `<model-viewer>` glTF; framework fit | "make this a `<picture>` with responsive widths"; "our LCP is 4s"; "embed this hero video accessibly"; "put this 3D model on the page" |
| [`asset-provenance-guardian`](agents/asset-provenance-guardian.md) | Commercial-use license pinning (the FLUX-dev trap; Firefly-indemnified where required), the provenance ledger (prompt/model/license/date), per-project generation budgets, EU AI Act Art.50 disclosure copy | "is this generator cleared for a client site?"; "log the provenance"; "are we over budget?"; "do we need an AI-disclosure notice?" |
| [`brand-and-accessibility-reviewer`](agents/brand-and-accessibility-reviewer.md) | The ship gate: brand-hex/style conformance, anti-slop QA (garbled in-image text, off-brand drift, no baked-in text), AI-drafted + human-reviewed WCAG alt text, mandatory human curation sign-off | "does this match the brand?"; "the text in this image is garbled"; "write alt text"; "sign this off before it ships" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. Per the marketplace house rule, this plugin ships specialist *doing*-agents and does not fork core's *review* roles (security/legal verdicts escalate to `ravenclaude-core/security-reviewer`). Team growth ships as skills + knowledge + templates, not a fifth parallel agent.

---

## 2. Routing rules (Team Lead)

- **"Which generator / model / provider / draft-vs-final / editing round-trip / brand-style conditioning setup"** → `generation-strategist`.
- **"Web-optimize / AVIF / WebP / `<picture>` / responsive widths / LCP / CLS / video embed / `<model-viewer>` / framework fit"** → `web-asset-pipeline-engineer`.
- **"License / commercial use / FLUX-dev / indemnity / provenance ledger / generation budget / EU AI Act disclosure"** → `asset-provenance-guardian`.
- **"Brand conformance / anti-slop QA / alt text / curation sign-off / is this ready to ship"** → `brand-and-accessibility-reviewer`.
- **The DTCG token file / design-token scaffolding itself** → `web-design/design-tokens-scaffolding` (we consume, don't produce — §0.2).
- **The brand-identity system (logo system, wordmark, full identity)** → `brand-identity-studio` (it sends us briefs — §0.2).
- **Any legal verdict, secret handling, or prompt-injection-over-generated-content risk** → `ravenclaude-core/security-reviewer` (mandatory).
- **Current provider price / model-capability verification beyond the matrix** → `ravenclaude-core/deep-researcher`.

---

## 3. Cross-cutting house opinions (every agent enforces)

1. **Never ship a raw image.** A generator emits a large PNG/JPEG; the web needs AVIF+WebP+fallback, responsive widths, and explicit dims. The raw file never reaches production.
2. **Pin the license before the prompt.** Decide the commercial-use license *first* — a beautiful FLUX-dev asset is worthless on a client site because FLUX-dev open weights are non-commercial. License gate outranks the Grok/aesthetic default.
3. **Overlay text, don't bake it.** Models garble in-image text and it can't be edited, localized, or made accessible. Render real HTML/SVG type over the image; keep generated images text-free.
4. **Style-reference beats seed-pinning.** For brand consistency, assemble 3–10 reference images / a Recraft brand-style upload, then post-overlay the exact brand hex — don't trust a seed or the model's color memory.
5. **Human curation is not optional.** Every asset passes a mandatory human selection/approval gate before production. The `/generate-web-asset` command cannot reach "done" without a curation artifact.
6. **Route cheap draft before premium final.** Iterate on a cheap draft model to lock composition/brand, then spend on one premium final render. Per-project generation budgets are a design input, not a surprise.
7. **License ≠ copyright ownership.** A paid plan lets you use/sell the output; it does not confer enforceable US copyright over the AI-generated portions (human-authorship rule). Where enforceability matters, recommend a human-editing pass.
8. **Cite the source + mark every price `[unverified]`.** The provider landscape moves monthly; quote a price only as `[unverified — confirm on provider pricing page]`, never as settled fact.

---

## 4. Depth ordering (honest, not shallow-everywhere)

"Full multimedia" here does **not** mean 5% depth in each modality. The declared depth ordering:

- **Images — v1 DEEP.** Photoreal + illustration + vector/SVG + text-in-image, provider-neutral (Grok-lean where competitive), with **editing round-trips (inpaint / outpaint / bg-removal / upscale) as first-class steps**, not just text-to-image.
- **Video — routed, real embed pipeline.** Generation routed to a capable API; the **web embed is real** (muted autoplay, `prefers-reduced-motion`, poster-frame LCP, WebM/H.264 fallback) because premium winery sites lead with cinematic hero video.
- **3D — routed, light.** Text/image → textured glTF mesh routed to the Meshy/Rodin/TRELLIS class; `<model-viewer>` embed guidance.
- **Audio — routed, lightest.** Ambient/SFX/voiceover routed to a capable API; **explicit anti-autoplay-audio** web-delivery guidance (video soundtrack framing).

A plugin that nails images+web+legal+brand and *routes* video/3D/audio competently beats one shallow across all five — this is deliberate.

---

## 5. Knowledge bank

Agents **traverse the relevant decision tree before choosing** ([`knowledge/generation-decision-trees.md`](knowledge/generation-decision-trees.md)) rather than keyword-matching. Volatile provider/price/license specifics live (dated, prices `[unverified]`) in the reference docs; re-verify before quoting.

| File | Read when |
|---|---|
| [`knowledge/provider-model-matrix-2026.md`](knowledge/provider-model-matrix-2026.md) | Choosing a provider/model — the single provider matrix (Grok-lean image row; the FLUX-dev non-commercial flag; Firefly-indemnified default; Grok-no-indemnity risk note). All prices `[unverified]`. |
| [`knowledge/web-media-pipeline.md`](knowledge/web-media-pipeline.md) | Web-optimizing an asset — AVIF/WebP/fallback, responsive widths, CLS-safe dims, LCP/`fetchpriority`, build-time-vs-CDN, the real video/3D embed patterns. |
| [`knowledge/legal-and-provenance-2026.md`](knowledge/legal-and-provenance-2026.md) | A license/copyright/provenance/disclosure question — Thaler (no copyright in pure-AI output), license≠ownership, C2PA fragility, EU AI Act Art.50 (enforceable 2 Aug 2026). |
| [`knowledge/generation-decision-trees.md`](knowledge/generation-decision-trees.md) | Before choosing — the four Mermaid trees: modality-depth, license-first→Grok-lean→fallback, build-time-vs-CDN, format-choice. |

---

## 6. The brand-token contract (the frozen seam)

`brand-identity-studio` (and `web-design`'s token output) hand this plugin a **generation brief** — the frozen v1.0 schema in [`templates/asset-brief.md`](templates/asset-brief.md). This plugin **consumes** it (routes, generates, optimizes, licenses, gates) and **returns** `{asset_uri, provenance_record, provider, indemnity_status, license_class}`. The schema is frozen so the two plugins can evolve independently; a change to it is a coordinated cross-plugin decision, not a unilateral edit. Brand conditioning consumes tokens from *whatever source is present* — the DTCG output (greenfield) or `ravenclaude-core:brand-extraction`'s `brand.json` (existing site) — brand-extraction is one *adapter*, not a hard-wire.

---

## 7. Skills, best-practices, templates, commands, scripts

**Skills (6):** [`prompt-to-asset-routing`](skills/prompt-to-asset-routing/SKILL.md), [`web-optimization-pipeline`](skills/web-optimization-pipeline/SKILL.md), [`license-and-provenance-ledger`](skills/license-and-provenance-ledger/SKILL.md), [`brand-conditioned-generation`](skills/brand-conditioned-generation/SKILL.md), [`curation-and-accessibility-gate`](skills/curation-and-accessibility-gate/SKILL.md), [`generation-budget-guard`](skills/generation-budget-guard/SKILL.md).

**Best-practices (6):** see [`best-practices/README.md`](best-practices/README.md) — never-ship-a-raw-image, pin-the-license-before-the-prompt, overlay-text-dont-bake-it, style-reference-beats-seed-pinning, human-curation-is-not-optional, route-cheap-draft-before-premium-final.

**Templates (5):** [`asset-brief.md`](templates/asset-brief.md) (the frozen contract), [`generation-defaults.yaml`](templates/generation-defaults.yaml), [`asset-provenance-ledger-entry.json`](templates/asset-provenance-ledger-entry.json), [`picture-element-snippet.html`](templates/picture-element-snippet.html), [`model-viewer-3d-embed.html`](templates/model-viewer-3d-embed.html).

**Commands (4):** [`/generate-web-asset`](commands/generate-web-asset.md) (end-to-end + hard curation gate), [`/audit-asset-licenses`](commands/audit-asset-licenses.md) (executable FLUX-trap + missing-record detector), [`/wire-media-substrate`](commands/wire-media-substrate.md) (fallback if the declarative binding is insufficient), [`/check-generation-budget`](commands/check-generation-budget.md).

**Scripts (4):** [`scripts/web-optimize/optimize-image.mjs`](scripts/web-optimize/optimize-image.mjs) (+`package.json`, Node/Sharp via `npx`, LOUD-SKIP if absent), [`scripts/provenance.py`](scripts/provenance.py) (stdlib), [`scripts/gen-budget.py`](scripts/gen-budget.py) (stdlib), [`scripts/generate-via-provider.sh`](scripts/generate-via-provider.sh) (curl + env key, direct-provider fallback off fal). All probe-and-degrade with a LOUD-SKIP — never a silent pass.

---

## 8. Substrate — the declarative fal MCP binding + the fallback

`plugin.json` declares the **fal** MCP server (`https://mcp.fal.ai/mcp`) so the generation substrate auto-wires on install. fal's hosted MCP exposes many image/video/audio/3D models behind one endpoint; the server is free, pay-per-run, and the **API key is the only manual input** — set `FAL_KEY` in the environment. Because a remote+key MCP may need an `Authorization: Bearer <FAL_KEY>` header that a declarative `mcpServers` block may not carry, [`/wire-media-substrate`](commands/wire-media-substrate.md) is the documented **fallback** (`claude mcp add` with the auth header) and [`scripts/generate-via-provider.sh`](scripts/generate-via-provider.sh) is the **direct-provider path** (e.g. `api.x.ai/v1` for Grok, off fal entirely). First run of `/generate-web-asset` checks for a wired substrate and instructs if absent — **never a silent dead tool** (red-team RT2). See [`NOTICE.md`](NOTICE.md) for attribution and the key-as-reference posture.

---

## 9. Output contract

Each agent ends with its role-specific contract (see the agent file) **plus the cross-plugin Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)). Every generation recommendation carries a mandatory **`License + provenance:`** line (license class, indemnity status, provenance-record path) and every price is `[unverified — confirm on provider pricing page]`.

---

## 10. Escalating out of the team — the seams

- **`web-design/design-tokens-scaffolding`** — owns the DTCG design-token file; we consume it (§0.2, §6).
- **`brand-identity-studio`** — owns the identity system; it sends us generation briefs (§0.2).
- **`ravenclaude-core:brand-extraction`** — the adapter that turns an existing site into a `brand.json` we can condition on (one source among others).
- **`ravenclaude-core/security-reviewer` (mandatory)** — every legal verdict, secret-handling design, and prompt-injection-over-generated-content risk.
- **`ravenclaude-core/deep-researcher`** — current provider price / model-capability verification beyond the dated matrix.
- **`frontend-engineering`** — the broader site build the assets drop into (bundle budget, rendering strategy) beyond the asset markup we emit.

---

## 11. Milestones

- **v0.1.0** — initial build-out: 4 agents (generation-strategist, web-asset-pipeline-engineer, asset-provenance-guardian, brand-and-accessibility-reviewer), 6 skills, a 4-doc knowledge bank (provider matrix, web-media pipeline, legal-and-provenance, 4 Mermaid decision trees; all prices `[unverified]`), 6 best-practices, 5 templates, 4 commands, 4 scripts (optimize-image.mjs + package.json, provenance.py, gen-budget.py, generate-via-provider.sh — all probe-and-degrade / LOUD-SKIP). Images v1-deep (photoreal/vector/text-in-image + inpaint/outpaint/bg-removal/upscale round-trips); video routed with a real embed pipeline; 3D/audio routed light. Declarative fal MCP binding (set `FAL_KEY`) + `/wire-media-substrate` fallback + a direct-provider script. **The shared foundation `brand-identity-studio` consumes** (§0.2); DTCG token producer is `web-design:design-tokens-scaffolding` (media only consumes). Generative-media engineering judgment, not legal advice; every price `[unverified]`; no secrets stored.
