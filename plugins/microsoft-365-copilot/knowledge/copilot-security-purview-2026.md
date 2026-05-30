# Copilot security — Purview DLP, oversharing, "not a boundary" (2026)

**Last reviewed:** 2026-05-30
**Confidence:** High on the DLP-gate + not-a-boundary framing (first-party). `[verify-at-build]` on citation-leakage + EXTRACT-right specifics.
**Read when:** securing the data Copilot can reach, or remediating oversharing before enabling Copilot. **This is data-layer design; the security verdict is `ravenclaude-core/security-reviewer`'s.**

---

## The cardinal rule: remediate oversharing BEFORE enabling Copilot

Copilot surfaces **everything a user can already technically reach**. Turning it on over an over-permissioned tenant turns latent oversharing into active discovery. House opinion #10 — the sequence:

```
1. RCD / RSS      reduce Copilot's BLAST RADIUS (reach reduction — NOT a boundary)
2. Purview        sensitivity labels + DLP-for-Copilot
3. Cleanup        site / library / item permission remediation (the real fix)
4. Enable         turn on Copilot
```

See the [`oversharing-remediation-playbook`](../skills/oversharing-remediation-playbook/SKILL.md) skill + the [`oversharing-remediation-runbook`](../templates/oversharing-remediation-runbook.md) template. **Licensing impact:** Restricted SharePoint Search / Purview DLP-for-Copilot are E5/Suite-gated — state it on every recommendation.

## RSS / RCD are NOT security boundaries

**Restricted SharePoint Search** and **Restricted Content Discovery** reduce *what Copilot crawls/surfaces*; they do **not** stop a user who already has access to the content via direct link or the site itself. House opinion #9 — never sell them as access control. They buy time to do the real permission cleanup. Grounding: [restricted content discovery](https://learn.microsoft.com/sharepoint/restricted-content-discovery).

## Purview DLP-for-Copilot

- **E5 / Microsoft 365 Copilot Suite-gated** `[verify-at-build]`.
- **Blocks *processing*, not citation titles/URLs** — a DLP policy can stop Copilot from *summarizing/processing* labeled content, but citation metadata (titles, links) can still leak. House opinion #11.
- The **EXTRACT** usage right (on the sensitivity label) governs whether Copilot can pull content into a response.
- **Sensitivity labels inherit** to Copilot responses built from labeled source content.

Grounding: [DLP for Copilot](https://learn.microsoft.com/purview/dlp-microsoft365-copilot-location-learn-about).

## The seam to the verdict

This plugin designs the *posture* (the sequence, the labels, the DLP policy shape). The **verdict** — is this ACL/DLP design actually sufficient, what's the injection risk over ingested content — is `ravenclaude-core/security-reviewer`'s (mandatory). Connector ACL ingestion mechanics are `graph-connector-engineer`'s.

## Refresh triggers
- DLP-for-Copilot licensing gate or citation-leakage behavior changes.
- RSS/RCD capabilities change (still verify they remain non-boundaries).
