# Template: Asset Brief — the FROZEN brand-token contract (v1.0)

This is the **frozen seam schema** that `brand-identity-studio` (and any brand/token producer) emits and `generative-web-media` consumes. It is **`contract_version: "1.0"` — frozen**: a change is a coordinated cross-plugin decision (CLAUDE.md §6), never a unilateral edit. The consumer returns the `return` fields.

## The schema (emit this verbatim)

```json
{
  "contract_version": "1.0",
  "request_kind": "logo|wordmark|imagery|favicon-set|og-image|video|3d",
  "intent": "...",
  "constraints": ["..."],
  "negative_constraints": ["..."],
  "count": 4,
  "format_hints": ["svg-vector-preferred", "mono-safe"],
  "indemnity_required": true,
  "license_policy": "client-resale",
  "return": ["asset_uri", "provenance_record", "provider", "indemnity_status", "license_class"]
}
```

## Field reference

| Field | Meaning |
|---|---|
| `contract_version` | `"1.0"` — the frozen contract version. |
| `request_kind` | One of `logo` / `wordmark` / `imagery` / `favicon-set` / `og-image` / `video` / `3d`. Routes the modality lane. |
| `intent` | Plain-language description of what the asset is for. |
| `constraints` | Positive requirements (subject, mood, palette-from-tokens, aspect ratio). |
| `negative_constraints` | Anti-slop baseline (no baked-in text, no watermark, no off-brand elements, no garbled hands). |
| `count` | How many variants to generate (feeds draft-vs-final + budget). |
| `format_hints` | e.g. `svg-vector-preferred`, `mono-safe`, `transparent-bg`, `avif-web`. |
| `indemnity_required` | `true` → route to a Firefly-class indemnified provider (Grok has no IP indemnity). |
| `license_policy` | e.g. `client-resale`, `internal-only`, `editorial`. Drives the license class the guardian pins. |
| `return` | The fields the consumer returns — `asset_uri`, `provenance_record`, `provider`, `indemnity_status`, `license_class`. |

## What the consumer returns

```json
{
  "asset_uri": "media/hero-1600.avif",
  "provenance_record": "media/provenance.jsonl#<entry>",
  "provider": "firefly",
  "indemnity_status": "provider-indemnified",
  "license_class": "client-resale"
}
```

## Notes

- **Brand tokens** are consumed from whatever source is present (a DTCG design-token file OR `ravenclaude-core:brand-extraction`'s `brand.json`) — reference them in `constraints`, don't inline a whole palette.
- Every price the consumer reports is `[unverified — confirm on provider pricing page]`.
- The consumer **never** produces the design-token file (that's `web-design:design-tokens-scaffolding`) — it only consumes tokens.
