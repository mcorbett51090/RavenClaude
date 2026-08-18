# Choosing a form platform: seven durable axes

**Retrieved / verified:** 2026-08-17.

⛔ **No pricing and no feature matrix appear on this page, deliberately.** Both go stale within a quarter `[unverified — volatile by nature; verify at use]`, and a stale comparison table reads authoritative long after it stopped being true. What survives a quarter is the *shape* of the question. Score the axes; look up the numbers on the day you decide.

The seven axes below are the ones that are expensive to change after you have shipped. Everything else — editor ergonomics, template galleries, integration counts — is cheap to live with or cheap to replace.

---

## Axis 1 — Egress: can you get the submission out, with a signature you can verify?

The question is not "does it have webhooks". It is:

- Does the outbound call carry a **signature you can verify** with a secret only you and the vendor hold, or is it an unauthenticated POST to a URL that anyone who learns it can forge?
- Is there a **replay defence** — a timestamp in the signed payload, or a delivery id you can deduplicate on?
- Is delivery **retried**, and can you tell a retry from a new submission?

A platform whose only egress is an unsigned POST means every downstream consumer must treat the payload as untrusted input from the open internet. That is survivable, but it is a cost you should book now rather than discover later. Route the verification design to [`../../web-commerce/skills/webhook-hardening/SKILL.md`](../../web-commerce/skills/webhook-hardening/SKILL.md).

## Axis 2 — Data residency: where does the submission physically live?

Not "where is the company", and not "where is their marketing site". Where do the submission rows and any attachments come to rest, and can you constrain it? This axis is binary for some organisations and irrelevant for others — establish which you are before you weigh it.

## Axis 3 — The DPA (and BAA, where relevant) on the plan you will actually buy

Vendors routinely offer a data-processing agreement on an enterprise tier and not below it. The axis is not "do they have a DPA"; it is "is the DPA available on the plan this project can actually buy, and does it cover the sub-processors they list?"

⛔ **This is a legal determination, not an engineering one.** Route the ruling to [`../../data-governance-privacy/CLAUDE.md`](../../data-governance-privacy/CLAUDE.md) and the owner. This plugin flags the question; it does not answer it.

## Axis 4 — Limits: submissions, attachments, retention

Three separate ceilings, and teams usually check only the first:

- **Submission volume** — including whether the limit is enforced by rejection or by silent truncation.
- **Attachment size and type** — including whether the platform validates the file at all, and what it does with one it will not accept. Hardening of anything you accept is owned upstream: [`../../ravenclaude-core/rules/security.md`](../../ravenclaude-core/rules/security.md).
- **Retention** — how long submissions are kept by default, whether that is configurable downward, and whether deletion is real or a flag. A platform whose default retention is "forever" is a growing liability on a form that collects anything personal.

## Axis 5 — Export and form-definition lock-in

Two different lock-ins, and the second is the one that bites:

- **Data export** — can you get every historical submission out, in a format that survives, without a support ticket?
- **Definition export** — can you get the *form itself* out? A form defined only inside a vendor's visual editor has to be rebuilt by hand to move. For a small form that is an afternoon; for a long structured intake it is a project.

## Axis 6 — Accessibility of the vendor's own rendered markup

If the platform renders the form, you have outsourced your accessibility conformance to a third party and you remain accountable for it. Test the *vendor's* output, not their marketing claim: label association, error identification and the error summary, focus behaviour after a failed submit, and target sizes.

The audit itself belongs to [`../../web-design/agents/accessibility-auditor.md`](../../web-design/agents/accessibility-auditor.md) — this axis exists so that the audit happens **before** the platform decision, not after.

## Axis 7 — Do you keep your own anti-abuse layer?

Some platforms bundle bot defense and give you no way to turn it off, tune it, or see what it rejected. That is fine until it starts rejecting real customers, at which point you have an unobservable filter in front of your own front door. Ask what you can see and what you can override. The ladder that should inform the answer is in [`./form-anti-abuse.md`](./form-anti-abuse.md).

---

## How to use the axes

Score each axis **blocking / costly / acceptable** for your context, and write the reason next to the score. The template is [`../templates/form-platform-evaluation-matrix.md`](../templates/form-platform-evaluation-matrix.md).

A **blocking** score on any single axis ends the evaluation for that candidate — there is no total that rescues a platform you cannot legally use or cannot get your data out of. This is deliberately not a weighted-sum model: weighted sums let three cheap wins outvote one disqualifier.

**When there is no form platform in the picture at all** — you are building the form yourself — axes 1, 4, 5 and 7 still apply, they are just questions about your own stack. The general database-and-hosting decision routes to [`../../data-platform/skills/stack-selection/SKILL.md`](../../data-platform/skills/stack-selection/SKILL.md).
