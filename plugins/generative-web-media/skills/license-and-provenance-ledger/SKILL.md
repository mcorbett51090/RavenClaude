---
name: license-and-provenance-ledger
description: "Pin each asset's commercial-use license before the prompt (flag the FLUX-dev non-commercial trap; Firefly-indemnified where indemnity_required; Grok has no IP indemnity), write the durable internal provenance ledger (prompt/model/provider/license/indemnity/date) since C2PA is routinely stripped, and add EU AI Act Art.50 disclosure copy for EU-facing sites. Not legal advice -> routes hard calls to security-reviewer. Facts dated [verify-at-use]."
---

# License & Provenance Ledger

Pin the license before the prompt, record durable provenance, surface the EU disclosure — without pretending to give legal advice.

> **Engineering guidance surfacing legal risk, NOT legal advice.** Hard/jurisdiction-specific calls route to counsel via `ravenclaude-core/security-reviewer`. Facts carry a retrieval date; re-confirm. See [`../../knowledge/legal-and-provenance-2026.md`](../../knowledge/legal-and-provenance-2026.md).

## Workflow

1. **Pin the license first.** Before generating, decide the commercial-use license from the brief. Client site + `indemnity_required` → Firefly-class indemnified. FLUX-dev open weights → **non-commercial, blocked** for client work (BFL API override only). Grok → commercial-use ok but **no IP indemnity** (flag for risk-averse clients).
2. **Record provenance** with [`../../scripts/provenance.py`](../../scripts/provenance.py) `record` — prompt, model, provider, license, indemnity, C2PA status, date. The **internal ledger is the durable record** because C2PA manifests are routinely stripped by platforms and recompression. Retain C2PA where present; do **not** add a `c2patool` re-embed binary. Schema: [`../../templates/asset-provenance-ledger-entry.json`](../../templates/asset-provenance-ledger-entry.json).
3. **State license ≠ ownership.** A paid plan permits use/sale; it does not confer enforceable US copyright over the AI portions (Thaler; human-authorship rule). Where enforceability matters, recommend a human-editing pass.
4. **Add EU Art.50 disclosure** for EU-facing sites — visible AI-disclosure copy that **surfaces + routes to counsel**, never asserts compliance (Art.50 enforceable 2 Aug 2026).
5. **Audit before launch** — `provenance.py audit --dir <media>` detects the FLUX-dev trap + missing records; wired into `/audit-asset-licenses`.

## The license classes

| Class | Meaning | Route |
|---|---|---|
| `commercial` | Provider's paid plan permits use/sale | Record indemnity status separately |
| `non-commercial` | FLUX-dev open weights etc. | **Blocked for client sites** without a paid override |
| `override` | Explicit human decision to use a flagged asset | Must be recorded with a reason |

## Anti-patterns

- Choosing the model, then discovering it's non-commercial (pin the license FIRST).
- Trusting C2PA as durable proof (it's stripped — the internal ledger is the record).
- Telling a client "you own this image" on the strength of a paid plan (license ≠ ownership).
- Disclosure copy that asserts legal compliance (surface + route, don't certify).

## See also

- [`../../knowledge/legal-and-provenance-2026.md`](../../knowledge/legal-and-provenance-2026.md), [`../../knowledge/provider-model-matrix-2026.md`](../../knowledge/provider-model-matrix-2026.md)
- Best-practice: [`../../best-practices/pin-the-license-before-the-prompt.md`](../../best-practices/pin-the-license-before-the-prompt.md)
- Command: [`../../commands/audit-asset-licenses.md`](../../commands/audit-asset-licenses.md)
