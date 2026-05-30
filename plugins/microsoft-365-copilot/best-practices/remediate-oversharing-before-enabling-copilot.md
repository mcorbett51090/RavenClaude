# Remediate oversharing BEFORE enabling Copilot — and don't sell RSS/RCD as a security boundary

**Status:** Absolute rule — the sequence is non-negotiable; enabling Copilot first turns latent oversharing into active discovery.

**Domain:** Governance / Purview & oversharing

**Applies to:** `microsoft-365-copilot`

---

## Why this exists

Microsoft 365 Copilot surfaces **everything a user can already technically reach**. A tenant accumulates years of over-permissioned sites, "shared with everyone" libraries, and stale access — all latent until Copilot makes it instantly discoverable through natural-language search. Turning Copilot on over an un-remediated tenant is the single most common Copilot rollout incident. Two beliefs cause it: that you can flip Copilot on and clean up later, and that **Restricted SharePoint Search (RSS)** / **Restricted Content Discovery (RCD)** are access controls. They are not — they reduce Copilot's *reach*, but a user who already has a direct link or site access still gets in. This is house opinions #9, #10, and #11.

## How to apply

Run the sequence in order. RSS/RCD buy time for blast-radius reduction; Purview adds the data-layer controls; the real fix is permission cleanup; only then enable.

```text
1. RCD / RSS    Reduce Copilot's BLAST RADIUS (reach reduction — NOT a boundary)
2. Purview      Sensitivity labels + DLP-for-Copilot (E5 / Copilot Suite-gated)
3. Cleanup      Site / library / item permission remediation — the REAL fix
4. Enable       Turn on Copilot
```

**Do:**
- Run RCD/RSS → Purview → permission cleanup → enable, in that order.
- Treat RSS/RCD as blast-radius reduction that *buys time* for the cleanup — never as the boundary.
- State a `Licensing impact:` line: RSS and DLP-for-Copilot are E5 / Microsoft 365 Copilot Suite-gated (`[verify-at-build]`).
- Route the data-layer posture to `ravenclaude-core/security-reviewer` for the verdict; ACL mechanics to `graph-connector-engineer`.

**Don't:**
- Enable Copilot and "remediate later."
- Sell RSS/RCD as access control or a security boundary (#9).
- Promise DLP-for-Copilot stops citation leakage — it can block *processing* of labeled content, but citation titles/URLs can still leak (#11); the EXTRACT usage right governs whether content is pulled into a response.

## Edge cases / when the rule does NOT apply

A small, already-tightly-governed tenant (clean permissions, sensitivity labels in place) may pass the cleanup step quickly — but the *assessment* still runs; you confirm there's nothing to remediate rather than skipping the check. DLP-for-Copilot and sensitivity-label inheritance are data-layer controls that complement, but do not replace, the permission cleanup. RSS/RCD remain non-boundaries no matter how the capability evolves — re-verify, but assume they still are not access control (`[verify-at-build]`).

## See also

- [`../knowledge/copilot-security-purview-2026.md`](../knowledge/copilot-security-purview-2026.md) — the remediation sequence, DLP-for-Copilot gate, citation-leakage + EXTRACT-right specifics, "not a boundary"
- [`./label-and-acl-trim-every-connector-property.md`](./label-and-acl-trim-every-connector-property.md) — the per-connector ACL companion to tenant-level remediation
- [`../skills/oversharing-remediation-playbook/SKILL.md`](../skills/oversharing-remediation-playbook/SKILL.md) · [`../templates/oversharing-remediation-runbook.md`](../templates/oversharing-remediation-runbook.md)
- [`../agents/copilot-admin-governance.md`](../agents/copilot-admin-governance.md) — the agent that owns this sequence

## Provenance

Codifies house opinions #9, #10, and #11 from [`../CLAUDE.md`](../CLAUDE.md). Grounded in [`../knowledge/copilot-security-purview-2026.md`](../knowledge/copilot-security-purview-2026.md), sourced from the Microsoft Learn restricted-content-discovery and DLP-for-Copilot pages. The security *verdict* escalates to `ravenclaude-core/security-reviewer` per the plugin constitution.

---

_Last reviewed: 2026-05-30 by `claude`_
