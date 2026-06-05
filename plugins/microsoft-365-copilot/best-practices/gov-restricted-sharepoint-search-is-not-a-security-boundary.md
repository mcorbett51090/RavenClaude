# Restricted SharePoint Search and RCD reduce Copilot's reach — they are not access-control boundaries

**Status:** Absolute rule
**Domain:** Copilot governance / oversharing
**Applies to:** `microsoft-365-copilot`

---

## Why this exists

Restricted SharePoint Search (RSS) and Restricted Content Discovery (RCD) are blast-radius reduction tools: RSS limits Copilot's SharePoint search to a curated set of sites; RCD restricts the content Copilot can discover and surface. Both are commonly presented to customers as "security controls" or "privacy settings" for Copilot — and they are not. A user who already has direct access to a document can still reach it outside Copilot, and Copilot itself will surface it if asked directly. RSS/RCD only narrow what Copilot discovers proactively; they do not prevent access by a determined user. Misrepresenting these as security boundaries creates false assurance and defers the actual remediation work (permission cleanup and Purview labeling).

## How to apply

The correct framing in every engagement:

```
RSS/RCD are BLAST-RADIUS REDUCTION tools.
They reduce what Copilot discovers proactively.
They do NOT prevent a user who has access from reaching content.
They are NOT a substitute for permission cleanup or Purview sensitivity labels.
```

The correct sequence:
1. **Blast-radius reduction (RSS/RCD)** — deploy immediately to limit proactive discovery while remediation proceeds.
2. **Purview sensitivity labels** — apply to label high-sensitivity content so DLP-for-Copilot can block processing.
3. **Permission cleanup** — remove overly broad access grants (broken inheritance, "Everyone except external users" links).
4. **Then enable Copilot** — with the above in place, the blast radius is contained.

**Do:**
- Deploy RSS/RCD as a **temporary** measure that accompanies, not replaces, the permission cleanup roadmap.
- Clearly document in the deployment runbook that RSS/RCD is a blast-radius control, not an access control.
- Set a 90-day review checkpoint to measure progress on permission cleanup and reduce reliance on RSS/RCD.

**Don't:**
- Tell a customer that enabling RSS/RCD means "Copilot is secure" — the statement is false.
- Use RSS/RCD as the sole governance control for a regulated tenant with data-residency or confidentiality obligations.
- Skip the permission cleanup phase because RSS/RCD is already in place — the underlying access exposure remains.

## Edge cases / when the rule does NOT apply

No exception. RSS/RCD are never access-control boundaries, regardless of the scenario. The framing "this is blast-radius reduction, not a security control" always applies.

## See also

- [`../agents/copilot-admin-governance.md`](../agents/copilot-admin-governance.md) — owns the oversharing remediation sequence and the correct framing of RSS/RCD
- [`./remediate-oversharing-before-enabling-copilot.md`](./remediate-oversharing-before-enabling-copilot.md) — the full pre-deployment remediation sequence this rule is part of

## Provenance

Codifies CLAUDE.md house opinion #9 ("Restricted SharePoint Search / Restricted Content Discovery are NOT security boundaries") and the `oversharing-remediation-playbook` skill; Microsoft Learn Restricted SharePoint Search documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
