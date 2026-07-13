# Creative brief for generative-web-media — <project / asset-kind / date>

> **The seam artifact.** This template emits the frozen JSON brief that `identity-systems-designer`
> hands to the **`generative-web-media`** plugin (a soft compose). `generative-web-media` OWNS raw
> generation + the license/indemnity decision — this brief only sets `indemnity_required` and the
> intent/constraints; it does **not** name a provider or re-declare a Firefly default (that is media's
> license gate's job, made per-asset). If `generative-web-media` is not installed, hand the same brief to
> a human operator as a copy-paste prompt-pack (see `logo-and-visual-system-direction` skill).
>
> **Precondition (gate):** a strategy artifact (`brand-strategy-brief.md`) MUST exist before this brief is
> authored — no visuals before strategy (best-practice: `strategy-before-visuals-or-it-reads-as-slop`).
> **Logos/wordmarks are NEVER regenerated in Firefly** — the deliverable is the curated Recraft/Ideogram
> vector (best-practice: `curate-the-vector-dont-regenerate-it`); Firefly-default applies only to
> fill/photographic imagery, and even then the per-asset indemnity call is media's.

---

## 1. The frozen brief schema (contract_version 1.0)

Emit **exactly** this shape — `generative-web-media` consumes these keys. Fill the values; keep the keys
and their types. One brief per `request_kind` (a logo run and an OG-image run are two briefs).

```json
{
  "contract_version": "1.0",
  "request_kind": "logo|wordmark|imagery|favicon-set|og-image|video|3d",
  "intent": "...",
  "constraints": ["..."],
  "negative_constraints": ["..."],
  "count": 8,
  "format_hints": ["svg-vector-preferred", "mono-safe"],
  "indemnity_required": true,
  "license_policy": "client-resale",
  "return": [
    "asset_uri",
    "provenance_record",
    "provider",
    "indemnity_status",
    "license_class"
  ]
}
```

## 2. Field-by-field (what to put where)

| Key | Type | Fill with | Notes |
|---|---|---|---|
| `contract_version` | string | `"1.0"` | Do not change unless the media plugin bumps the seam. |
| `request_kind` | enum | one of `logo` / `wordmark` / `imagery` / `favicon-set` / `og-image` / `video` / `3d` | Drives which provider media's license gate considers. Logos/wordmarks → vector providers (Recraft/Ideogram class), NOT Firefly regen. |
| `intent` | string | The specific creative brief, strategy-derived | Anti-slop: be specific ("like Stripe but warmer, avoid blue"), never "modern / clean / professional". |
| `constraints` | string[] | Positive requirements | e.g. `"identifiable in one flat color"`, `"legible at 16px favicon"`, `"reads in B&W"`. |
| `negative_constraints` | string[] | What to avoid — the "legible middle" escape | e.g. `"no gradient meshes"`, `"no generic swoosh"`, `"avoid #-blue palette"`. |
| `count` | integer | How many concepts to generate for human curation | Bulk-generate → the human curates ruthlessly (curation gate). Exploration is cheap; refinement is human. |
| `format_hints` | string[] | Output-format preferences | `"svg-vector-preferred"` + `"mono-safe"` for logos; raster hints for imagery. |
| `indemnity_required` | boolean | `true` for any client-facing / resold asset | This is the ONLY license lever this plugin sets. `true` tells media's license gate to choose an IP-indemnified provider for that asset. The provider **choice** is media's, per-asset. |
| `license_policy` | string | `"client-resale"` for a commissioned brand | Signals the deliverable will be assigned/resold to the commissioning client. |
| `return` | string[] | The provenance fields media must return | Keep all five — `provenance_record` + `indemnity_status` + `license_class` feed the `font-license-tracker` / `curation-and-authorship-log`, and the human-authorship + legal-sign-off gates depend on them. |

## 3. After media returns

1. Record `provider`, `indemnity_status`, and `license_class` per returned asset in the
   [`curation-and-authorship-log.md`](curation-and-authorship-log.md).
2. Run the **human-curation gate**: a human selects the concept(s) and logs a substantial
   human modification/arrangement (the copyright-preserving step — see
   `ai-logo-copyright-is-not-trademark-document-human-authorship`).
3. The **curated vector is the deliverable** — it is NEVER re-sent to Firefly for a "final" pass
   (regeneration = a new asset, voiding the curation the whole value promise rests on).
4. Route any client-facing IP/registrability claim to `ravenclaude-core:security-reviewer` before the
   brand book asserts it (legal-sign-off gate in `assemble-brand-book`).

---
_Prices/providers referenced downstream are `[unverified]`; confirm on the vendor pricing page. This brief
is decision-support, not legal advice. Seam owner: `identity-systems-designer` → `generative-web-media`._
