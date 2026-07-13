# generative-web-media — best-practice docs

Named, citable rules for the `generative-web-media` team's specialists. Each file is **one rule**. Generative-media engineering judgment, not legal advice; every provider price is `[unverified — confirm on provider pricing page]`; no secrets stored.

---

## Index

_6 rules across the web output, the license, the anti-slop craft, brand consistency, the human gate, and cost._

| Doc | Status | Use when |
|---|---|---|
| [`never-ship-a-raw-image.md`](./never-ship-a-raw-image.md) | Absolute rule | Any image reaching the web — emit AVIF/WebP/fallback responsive `<picture>` with explicit dims, never a raw PNG. |
| [`pin-the-license-before-the-prompt.md`](./pin-the-license-before-the-prompt.md) | Absolute rule | Before generating for a client — decide the commercial-use license first; the FLUX-dev trap outranks aesthetics. |
| [`overlay-text-dont-bake-it.md`](./overlay-text-dont-bake-it.md) | Absolute rule | Any asset that needs text — render real HTML/SVG type over the image; keep generated images text-free. |
| [`style-reference-beats-seed-pinning.md`](./style-reference-beats-seed-pinning.md) | Pattern | Brand consistency — condition on a style-reference + exact-hex overlay, not a pinned seed. |
| [`human-curation-is-not-optional.md`](./human-curation-is-not-optional.md) | Absolute rule | Every asset before production — a human selects and signs off; the gate is a hard blocker. |
| [`route-cheap-draft-before-premium-final.md`](./route-cheap-draft-before-premium-final.md) | Pattern | Cost control — iterate on a cheap draft, spend once on a premium final, cap per-project spend. |

---

Each rule cites its provenance and carries a `Last reviewed` date. Volatile provider/price/license specifics live (dated, prices `[unverified]`) in [`../knowledge/`](../knowledge/).
