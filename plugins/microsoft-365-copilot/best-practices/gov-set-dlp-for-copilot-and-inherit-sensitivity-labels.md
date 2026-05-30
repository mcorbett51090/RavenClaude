# Use Purview DLP-for-Copilot and sensitivity-label inheritance as data-layer controls — knowing they block processing, not citation titles

**Status:** Primary diagnostic — when the question is "can Copilot see / extract / leak this labeled content?", check the EXTRACT right, the DLP-for-Copilot policy, and the citation-metadata caveat first; and never present these as a substitute for permission cleanup.

**Domain:** Governance / Purview & data protection

**Applies to:** `microsoft-365-copilot`

> **Security-sensitive.** This plugin designs the *posture* (labels, DLP policy shape, EXTRACT-right reasoning). Whether the design is *sufficient* — and the prompt-injection risk over grounded content — is a verdict for **`ravenclaude-core/security-reviewer`** (mandatory).

---

## Why this exists

Once Copilot is enabled, the data-layer controls people reach for are Microsoft Purview **sensitivity labels** and **DLP-for-Copilot** — and they are routinely over-trusted. Three facts govern correct use. First, **DLP-for-Copilot blocks *processing*, not citation metadata**: a policy can stop Copilot from summarizing/processing labeled content, but the citation *title and URL* can still surface — so "DLP protects it" is false if the worry is the title leaking. Second, the **EXTRACT usage right** on a sensitivity label is what actually governs whether Copilot can pull labeled content into a response; if a label grants EXTRACT, Copilot can use it regardless of how sensitive it looks. Third, **labels inherit**: a response built from labeled source content inherits the most restrictive label, which is good (the output stays protected) but also means an over-broad label can over-restrict outputs. And all of this is **E5 / Microsoft 365 Copilot Suite-gated**. These controls *complement* permission cleanup; they never replace it (#10), and they are not a security boundary the way ACLs are. This is house opinion #11.

## How to apply

Set labels with the EXTRACT right reasoned explicitly, apply DLP-for-Copilot for the processing block, and state the citation-leak caveat + the E5 gate on every recommendation. Route sufficiency to the security reviewer.

```text
Control                     What it does                         What it does NOT do
──────────────────────────────────────────────────────────────────────────────────────────
Sensitivity label + EXTRACT governs whether Copilot can pull     decide on its own that content
                            labeled content into a response       is "safe" — EXTRACT must be reasoned
DLP-for-Copilot policy      blocks Copilot PROCESSING of          stop citation TITLE/URL from
  (E5 / Copilot Suite)      labeled content                       surfacing  ← the leak caveat (#11)
Label inheritance           response inherits most-restrictive    substitute for source permission
                            source label (output stays protected)  cleanup (#10)
```

**Do:**
- Reason about the **EXTRACT** right on each label — it, not appearance, decides whether Copilot can use the content.
- Apply **DLP-for-Copilot** to block processing of the labels that must not be summarized.
- State the **citation-metadata caveat** (titles/URLs can still leak) and the **E5/Suite license gate** on every recommendation.
- Route the design's sufficiency + injection risk to `ravenclaude-core/security-reviewer` (mandatory).

**Don't:**
- Promise DLP-for-Copilot stops citation-title/URL leakage — it blocks *processing*, not metadata (#11).
- Treat labels/DLP as a replacement for the permission cleanup in the oversharing sequence (#10).
- Recommend these without the `Licensing impact:` line — they're E5 / Copilot Suite-gated.

## Edge cases / when the rule does NOT apply

The DA manifest's `sensitivity_label` property (v1.6+) applies **only when the agent embeds files** — it is not a tenant-wide DLP control and doesn't substitute for Purview policy. A tenant on a lower license tier **cannot use DLP-for-Copilot** at all — then the controls are permission cleanup + RSS/RCD reach reduction only, and you say so. Citation-leakage behavior and the exact license gate are `[verify-at-build]`. These are data-*processing* controls; the access boundary is still the ACL / SharePoint permission, which is the security reviewer's domain.

## See also

- [`./remediate-oversharing-before-enabling-copilot.md`](./remediate-oversharing-before-enabling-copilot.md) — the sequence these controls sit inside (Purview is step 2, cleanup step 3)
- [`./label-and-acl-trim-every-connector-property.md`](./label-and-acl-trim-every-connector-property.md) — the real access boundary (ACLs) DLP complements
- [`../knowledge/copilot-security-purview-2026.md`](../knowledge/copilot-security-purview-2026.md) · [`../agents/copilot-admin-governance.md`](../agents/copilot-admin-governance.md)
- [DLP for Microsoft 365 Copilot](https://learn.microsoft.com/purview/dlp-microsoft365-copilot-location-learn-about) — the processing-block scope + EXTRACT right

## Provenance

Codifies house opinion #11 (and complements #9/#10) from [`../CLAUDE.md`](../CLAUDE.md). Grounded in the Microsoft Learn DLP-for-Copilot location page and [`../knowledge/copilot-security-purview-2026.md`](../knowledge/copilot-security-purview-2026.md) (E5/Suite gate, processing-not-citation block, EXTRACT right, label inheritance), and the DA v1.6 `sensitivity_label` (embedded-files-only) schema note, retrieved 2026-05-30. Sufficiency verdict escalates to `ravenclaude-core/security-reviewer`. License/leak specifics `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
