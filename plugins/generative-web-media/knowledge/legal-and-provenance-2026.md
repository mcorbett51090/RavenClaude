# Legal & Provenance — 2026

> The single license/copyright/provenance/disclosure knowledge base for the marketplace. `asset-provenance-guardian` reads it; consumers reference it, never copy it (CLAUDE.md §0.2).
>
> **This is engineering guidance surfacing legal risk, NOT legal advice.** Hard calls, jurisdiction-specific questions, and any client-facing legal assertion route to counsel via `ravenclaude-core/security-reviewer`. Facts carry a retrieval date; re-confirm before relying on them.
>
> _Last reviewed: 2026-07-13 by `claude`. Sources cited inline._

---

## 1. Pure AI output is not copyrightable in the US

Purely AI-generated images are **not copyrightable** in the US under the human-authorship rule. SCOTUS **denied cert in *Thaler v. Perlmutter* on 2 Mar 2026**, leaving the DC-Circuit ruling intact. The US Copyright Office Part 2 report (29 Jan 2025) confirms **mixed works are registrable, but only the human-authored elements are protected**.

**Practical consequence:** you cannot claim enforceable copyright over the AI-generated portions of an asset. Where enforceability matters (a hero mark a client wants to defend), recommend a **substantive human-editing pass** so there is protectable human authorship — and say plainly that a raw generation is not a defensible original.

Sources: mayerbrown, finnegan (Thaler); copyright.gov/ai (Part 2). Confidence: **High**.

---

## 2. License ≠ copyright ownership

A provider's **commercial-use license lets you use and sell the output**; it does **not** confer enforceable copyright ownership over the AI-generated portions. These are different things:

- **Commercial-use license** (Firefly/Recraft/Grok paid plans) — permission to use/sell. This is what the guardian pins per asset.
- **Copyright ownership** — an enforceable right against copiers. Not conferred by a license; limited by §1 above.

Never tell a client "you own this image" on the strength of a paid plan. The correct statement: "your plan permits commercial use; enforceable ownership over the AI portions is limited — a human-editing pass strengthens it."

Sources: copyright.gov/ai; p20v.com guide. Confidence: **High**.

---

## 3. Provider risk ordering (indemnity)

- **Adobe Firefly = lowest legal risk** — trained on licensed/public-domain data and offers **IP indemnification on paid plans**. The **indemnified default when the brief sets `indemnity_required`**. (Do **not** quote specific indemnity cap figures — Low confidence.)
- **Midjourney** — active litigation exposure (Disney/Universal); higher risk for client work.
- **Grok / xAI** — **NO IP indemnity** (settled). Fine where competitive for non-indemnity work; flagged for risk-averse clients.
- **FLUX.2 [dev]** — open weights are **NON-COMMERCIAL**; the trap (see the matrix).

Sources: tensoria.fr firefly; terms.law midjourney. Confidence: Med-High (indemnity caps Low — don't quote).

---

## 4. C2PA Content Credentials are fragile — ledger anyway

**C2PA Content Credentials** are emitted by Firefly, DALL·E/Sora, Imagen, and others. But manifests are **routinely stripped** by social platforms and by recompression/resize. C2PA is **fragile provenance, not durable proof**.

**The layered rule (settled — CE-6):**
1. **Retain C2PA where present** (don't strip it).
2. **ALWAYS write an internal audit ledger** — prompt, model, provider, license class, indemnity status, date — regardless of C2PA. This internal record is the durable one.
3. **Do NOT add a `c2patool` re-embed binary** — the ledger is the durable record; a re-embed adds a binary dependency for provenance that platforms strip anyway.

The ledger schema: [`../templates/asset-provenance-ledger-entry.json`](../templates/asset-provenance-ledger-entry.json); the tool: [`../scripts/provenance.py`](../scripts/provenance.py).

Sources: contentauthenticity.org state-of-2026; aiipprotection.org stripping. Confidence: **High**.

---

## 5. EU AI Act Article 50 — transparency & disclosure

**EU AI Act Article 50** transparency/marking and deepfake-disclosure duties are **enforceable 2 Aug 2026**; penalties up to **€15M / 3% global turnover**. Scope: sites serving EU visitors must mark AI-generated/manipulated media as such.

**The guardian's role is to surface + route, not to certify compliance.** It adds visible AI-disclosure copy for EU-facing sites and states the obligation; it does **not** assert the site is legally compliant — that is counsel's call (`ravenclaude-core/security-reviewer`). Overreach here (copy that asserts compliance) is red-team RT7.

Disclosure copy pattern (surface, don't certify):

> "Some imagery on this site is generated or enhanced with AI tools. — (EU visitors: AI-transparency notice per EU AI Act Art. 50, effective 2 Aug 2026. This is a transparency notice, not a legal-compliance certification; confirm your obligations with counsel.)"

Sources: artificialintelligenceact.eu/article/50; gtlaw 2026. Confidence: **High** (the date + penalty; the exact per-site obligation is fact-specific → counsel).

---

## 6. The predictable failure taxonomy (why the gates exist)

| Failure | Guardrail |
|---|---|
| Garbled in-image **text** (most common) | **Overlay real HTML/SVG type — don't bake text into images** |
| Hands/anatomy, impossible reflections | Negative-prompt baseline + human curation |
| Off-brand drift | Style-reference conditioning + brand-hex overlay + brand review |
| License trap (FLUX-dev on a client site) | License-pinning + `/audit-asset-licenses` |
| Cost blowouts | Per-project generation budgets (`gen-budget.py`) |

Sources: lifehackedai failure-modes; p20v artifacts; zsky anti-slop. Confidence: Med-High.

---

## What routes to counsel (`security-reviewer`)

- Any client-facing assertion that an asset is legally clear / owned / compliant.
- A jurisdiction-specific question (beyond "EU Art.50 exists and is dated").
- A specific indemnity-coverage question for a specific claim.
- Handling of a secret or a prompt-injection-over-generated-content risk.
