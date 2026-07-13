# Pin the license before the prompt

**Status:** Absolute rule
**Domain:** Legal / provenance
**Applies to:** `generative-web-media`

> Engineering guidance surfacing legal risk, NOT legal advice. Hard calls route to counsel via `ravenclaude-core/security-reviewer`. License facts dated; re-confirm.

---

## Why this exists

The most expensive generation mistake is discovered after the render: a beautiful FLUX.2 **[dev]** image, generated from the open weights, is **non-commercial** — worthless on a client site. The license is a property of the *provider/model choice*, not the image, so it must be decided **before** the prompt. The license gate outranks the Grok/aesthetic default: a great non-commercial asset is a liability, not an asset.

## How to apply

- Decide the commercial-use license from the brief **first**. Client site + `indemnity_required` → a Firefly-class indemnified provider.
- **FLUX-dev open weights = non-commercial** → blocked for client work; the paid BFL API is the only override.
- **Grok/xAI** = commercial-use OK but **no IP indemnity** → flag for risk-averse clients.
- Record the license class + indemnity status to the provenance ledger ([`../scripts/provenance.py`](../scripts/provenance.py)); audit before launch ([`../commands/audit-asset-licenses.md`](../commands/audit-asset-licenses.md)).
- Remember **license ≠ ownership** — a paid plan permits use/sale but does not confer enforceable copyright over the AI portions (Thaler).

**Do:** pin the license and indemnity before generating; record it.
**Don't:** route on aesthetics and discover the non-commercial trap after the render.

## Edge cases / when the rule does NOT apply

Internal/throwaway (non-client) work can route on aesthetics — but still log provenance, and re-check before any such asset is later repurposed for a client.

## See also

- [`../skills/license-and-provenance-ledger/SKILL.md`](../skills/license-and-provenance-ledger/SKILL.md)
- [`../knowledge/legal-and-provenance-2026.md`](../knowledge/legal-and-provenance-2026.md), [`../knowledge/provider-model-matrix-2026.md`](../knowledge/provider-model-matrix-2026.md)

## Provenance

Codifies `asset-provenance-guardian` house opinion; grounded in bfl.ai/licensing, copyright.gov/ai (retrieved 2026-07-13; **High** confidence on the FLUX trap + Thaler).

---

_Last reviewed: 2026-07-13 by `claude`_
