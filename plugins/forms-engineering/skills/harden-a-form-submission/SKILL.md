---
name: harden-a-form-submission
description: "Walk the trust boundary of a form submission on the server: client/server validation parity, honeypot design and its assistive-tech exemption, double-submit and submission idempotency, webhook signature verification, PII minimisation. Cites ravenclaude-core for uploads and challenge widgets; the binding verdict always routes to security-reviewer."
---

# Skill: harden-a-form-submission

> **Invoked by:** `ravenclaude-core/security-reviewer` (which keeps the binding verdict), `web-design/frontend-implementer` (which keeps the client half and hands the server half here), `api-engineering/api-security-engineer`.
>
> **When to invoke:** a public form POSTs to something; a form is being moved from a hosted platform to your own endpoint; duplicate submissions are appearing; a form starts collecting a category of personal data it did not before; an anti-abuse layer is being added or removed.
>
> **Output:** the trust-boundary section of [`../../templates/form-spec.md`](../../templates/form-spec.md), plus a named list of what is deliberately **not** defended and why.

## ⛔ The two hard boundaries, before anything else

1. **The binding security verdict is not this skill's.** It belongs to [`../../../ravenclaude-core/agents/security-reviewer.md`](../../../ravenclaude-core/agents/security-reviewer.md), zero-exception. This skill produces the walk and the findings; it does not sign off. That mirrors the routing rule `web-design`'s auditor already applies, and preserving it is the reason a standalone forms plugin is coherent at all.
2. **Two topics are owned upstream and are cited here, never restated.** Writing a second copy is how a single source of truth dies, and the upstream files carry a `refresh_when:` clause that a copy would not:
   - **Uploads** — filenames, traversal, type validation, size ceilings → [`../../../ravenclaude-core/rules/security.md`](../../../ravenclaude-core/rules/security.md) §File handling.
   - **Challenge widgets** — token lifetime, replay, server-side verification at submit, hostname scope → [`../../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md).

## Not this skill

| You are actually doing | Go here |
| --- | --- |
| Client-side form construction, input types, native validation attributes, validation UX | [`../../../web-design/agents/frontend-implementer.md`](../../../web-design/agents/frontend-implementer.md) |
| Label association, `aria-describedby` error wiring, required indication, validation timing | [`../../../web-design/agents/accessibility-auditor.md`](../../../web-design/agents/accessibility-auditor.md) |
| API-layer authorization — object-level, function-level, scope validation | [`../../../api-engineering/agents/api-security-engineer.md`](../../../api-engineering/agents/api-security-engineer.md) |
| Designing the idempotency key itself | [`../../../api-engineering/skills/idempotency-key-design/SKILL.md`](../../../api-engineering/skills/idempotency-key-design/SKILL.md) |
| Hardening the webhook you emit or consume | [`../../../web-commerce/skills/webhook-hardening/SKILL.md`](../../../web-commerce/skills/webhook-hardening/SKILL.md) |
| A GDPR / CCPA / PIPA determination, a DSAR, a retention ruling | [`../../../data-governance-privacy/CLAUDE.md`](../../../data-governance-privacy/CLAUDE.md) **and the owner** |
| Upload handling of any kind | [`../../../ravenclaude-core/rules/security.md`](../../../ravenclaude-core/rules/security.md) |

## Step 1 — Validation parity: the server re-validates everything

Client-side validation is a UX affordance. It tells a cooperating user what you expect. It defends nothing, because the client is not where the request comes from.

The property to assert is **parity**: for every constraint the client enforces, the server enforces the same one, and the server's version is authoritative. The failure mode is not "the server has no validation" — it is **drift**: the client's regex gets loosened for a customer with an unusual address and the server's does not, and now the client is stricter than the server in one place and looser in another, and nobody can say which.

Two rules that keep parity real:

- **One schema, two consumers.** Derive both from a single definition where the stack allows it. Two hand-maintained copies diverge on a schedule.
- **Validate at the boundary, encode at the output.** These are different operations solving different problems, and doing one does not do the other. Rejecting a payload that looks like markup is input validation; rendering it safely is output encoding. The general rule is [`../../../ravenclaude-core/rules/security.md`](../../../ravenclaude-core/rules/security.md) §Untrusted input.

## Step 2 — Pick the anti-abuse rung, from the bottom

The ladder — boring endpoint, rate limit, honeypot, content heuristics, challenge widget, human review — is in [`../../knowledge/form-anti-abuse.md`](../../knowledge/form-anti-abuse.md) §1. **Start at the bottom.** A challenge widget on a form receiving a handful of submissions a week buys a third-party dependency and an unresolved accessibility question in exchange for work a human would have done in seconds.

If you do use a challenge widget, its wiring, verification and replay rules are upstream — [`../../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md) — and its conformance level is **disputed by the vendor's own documentation**; see [`../../knowledge/form-anti-abuse.md`](../../knowledge/form-anti-abuse.md) §4 before you write a level into an accessibility statement.

## Step 3 — Honeypot, with the exemption written down

A honeypot only earns its place if it is invisible to assistive technology **and** to autofill. Both populations are human, and both are silently rejected by a naive implementation. The four properties are in [`../../best-practices/a-honeypot-must-be-invisible-to-assistive-tech-and-to-autofill.md`](../../best-practices/a-honeypot-must-be-invisible-to-assistive-tech-and-to-autofill.md).

Then **count the rejections**. A filter you cannot observe is a filter you cannot debug, and the first sign it is wrong will otherwise be a customer complaining they were ignored.

The time-trap variant ships `[unverified — premise not disconfirmed; no false-positive-rate study located, open-web search 2026-08-17]`. Log what it *would* have rejected before you let it reject anything.

## Step 4 — Anti-forgery and anti-duplicate are two problems

They are conflated constantly and the conflation ships forms protected against one and not the other. The comparison table is in [`../../knowledge/form-anti-abuse.md`](../../knowledge/form-anti-abuse.md) §5.

- **Anti-forgery**: a secret a third-party site cannot read, plus an origin check and cookie policy.
- **Anti-duplicate**: a token the server records as spent, or a natural key it deduplicates on, so a double-click, a retry and a back button produce one ticket rather than three.

Do both, or state in the spec which one you are choosing not to do and why. See [`../../best-practices/every-public-form-post-needs-a-double-submit-guard.md`](../../best-practices/every-public-form-post-needs-a-double-submit-guard.md).

## Step 5 — Verify the webhook, in both directions

If the submission leaves your boundary — to a queue, a CRM, an automation — or arrives from a platform:

- Verify the signature with a **constant-time comparison** against a secret held only by the two parties.
- Reject a payload whose signed timestamp is outside a tolerance you chose deliberately.
- Deduplicate on the delivery identifier; a redelivery is not a second submission.

Route the mechanism to [`../../../web-commerce/skills/webhook-hardening/SKILL.md`](../../../web-commerce/skills/webhook-hardening/SKILL.md); route the key design to [`../../../api-engineering/skills/idempotency-key-design/SKILL.md`](../../../api-engineering/skills/idempotency-key-design/SKILL.md).

## Step 6 — Minimise the PII, at the field level

Every personal field is something you store, defend, back up, and eventually have to delete on request. The practice-level rules:

- **Collect it because a named step uses it.** If no step uses it, the field is liability with no offsetting benefit.
- **Do not log the body.** Form bodies end up in request logs, error trackers and alert emails by default. Redact at the point of logging, not later.
- **Separate the notification from the record.** An alert email containing the whole submission turns every inbox it touches into a copy of your database.
- **Give retention a number and an owner** at design time. "Indefinitely, by omission" is the default nobody chose.

⛔ **Any legal determination — lawful basis, cross-border transfer, retention obligation, a DSAR — is not this skill's.** Route to [`../../../data-governance-privacy/CLAUDE.md`](../../../data-governance-privacy/CLAUDE.md) and the owner.

## Step 7 — Fail loudly when the defense degrades

A defense that fails open on a missing secret is a defensible choice. A defense that fails open **quietly** is not — you now have a form with no protection and a dashboard that says everything is fine. See [`../../best-practices/degraded-bot-defense-must-be-loud.md`](../../best-practices/degraded-bot-defense-must-be-loud.md).

## Step 8 — Write the exclusions down, then route the verdict

Close with an explicit list of what is **not** defended and why — the attacks you accepted, the rungs you skipped, the fields you kept. Then hand the whole walk to [`../../../ravenclaude-core/agents/security-reviewer.md`](../../../ravenclaude-core/agents/security-reviewer.md). The verdict is theirs.
