---
description: Plan the pre-Copilot oversharing remediation — run the RCD/RSS to Purview to permission-cleanup to enable sequence in order, treat RSS/RCD as blast-radius reduction (not a security boundary), and route the verdict to the security reviewer.
argument-hint: "[the tenant/scope, e.g. 'before we turn on Copilot for the whole org']"
---

# Remediate Copilot oversharing

You are running `/microsoft-365-copilot:remediate-copilot-oversharing`. Build the pre-Copilot remediation runbook for what the user described (`$ARGUMENTS`), following this plugin's `copilot-admin-governance` discipline — Copilot surfaces everything a user can already reach, so the cleanup comes *before* enablement.

## When to use this

Copilot is about to be enabled over a tenant that has accumulated over-permissioned sites, "shared with everyone" libraries, or stale access. Even a tightly-governed tenant runs the *assessment* — you confirm there's nothing to remediate rather than skipping the check.

## Steps

1. **Run the sequence in order:** RCD/RSS (blast-radius reduction) → Purview (sensitivity labels + DLP-for-Copilot) → permission cleanup (the real fix) → enable Copilot (`remediate-oversharing-before-enabling-copilot.md`). Never enable first and "remediate later."
2. **Treat RSS/RCD as reach reduction that buys time, never a security boundary** — a user with a direct link or site access still gets in; don't sell them as access control (`remediate-oversharing-before-enabling-copilot.md`).
3. **Add the Purview data-layer controls** — sensitivity labels + DLP-for-Copilot — knowing DLP can block *processing* of labeled content but citation titles/URLs can still leak, and the EXTRACT usage right governs what's pulled into a response (same file).
4. **Do the permission cleanup** — site/library/item remediation is the real fix; RCD/RSS only bought time for it (same file).
5. **Trim per-source connector ACLs in parallel** — the per-connector companion to tenant remediation: real per-item ACLs, never "everyone" (`label-and-acl-trim-every-connector-property.md`).
6. **State the licensing + route the verdict** — RSS and DLP-for-Copilot are E5 / Copilot Suite-gated (`[verify-at-build]`); the data-layer posture *verdict* routes to `ravenclaude-core/security-reviewer`. Use the `templates/oversharing-remediation-runbook.md` shape.

## Guardrails

- Never enable Copilot before remediating, and never present RSS/RCD as a security boundary or promise DLP-for-Copilot stops citation-title leakage.
- The security *verdict* is `ravenclaude-core/security-reviewer`'s (mandatory); ACL mechanics are `graph-connector-engineer`'s.
- State a `Licensing impact:` line. This plugin is advisory: emit the runbook + admin-center/Purview steps the admin runs in their own tenant — it doesn't change tenant settings.
