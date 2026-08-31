---
name: form-intake-and-triage-design
description: "Design the intake behind a form so triage is deterministic: request taxonomy, the fields each request type actually needs, routing rules, per-type response clocks, self-serve-vs-escalate bright lines, and abandonment read as a process defect stream. Produces a form spec, not a wireframe."
---

# Skill: form-intake-and-triage-design

> **Invoked by:** `web-design/ux-designer` (before laying out a form whose submissions feed a queue), `ravenclaude-core/architect`, and directly via `/forms-engineering:design-form-intake`.
>
> **When to invoke:** a form exists (or is about to) whose submissions become work for someone; triage is being done by a human re-reading free text; requests arrive missing the one field the queue needs; "we get a lot of junk through the contact form"; a new request type is being bolted onto an existing form.
>
> **Output:** a populated [`../../templates/form-spec.md`](../../templates/form-spec.md) — request taxonomy, per-type required fields, routing rules, response clocks, escalation bright lines, and the defect classes the form will be measured on.

## The discipline in one sentence

A form is the **entry point of a process**, and most form problems are process problems wearing a UI costume.

## Not this skill

| You are actually doing | Go here |
| --- | --- |
| Laying out the form, labelling fields, choosing input types, validation UX | [`../../../web-design/agents/frontend-implementer.md`](../../../web-design/agents/frontend-implementer.md) |
| Label association, error identification, focus management, required-field indication | [`../../../web-design/agents/accessibility-auditor.md`](../../../web-design/agents/accessibility-auditor.md) |
| Field count and conversion evidence, funnel diagnosis, trust signals | [`../../../web-design/skills/conversion-design/SKILL.md`](../../../web-design/skills/conversion-design/SKILL.md) §3 |
| Designing a **survey** — question wording, scales, sampling | [`../../../ux-research/CLAUDE.md`](../../../ux-research/CLAUDE.md) |
| Legal intake, matter opening, engagement letters | [`../../../legal-ops-clm/CLAUDE.md`](../../../legal-ops-clm/CLAUDE.md) |
| Dataverse / Power Pages form surfaces | [`../../../power-platform/CLAUDE.md`](../../../power-platform/CLAUDE.md) |
| The measurement contract and the SPC hand-off | [`../form-telemetry-and-control/SKILL.md`](../form-telemetry-and-control/SKILL.md) |
| Anything about the trust boundary of the submission | [`../harden-a-form-submission/SKILL.md`](../harden-a-form-submission/SKILL.md) |

## Step 1 — Name the request types before you name a field

Do not start from the form. Start from the **queue**, and answer one question: *what distinct kinds of work arrive here?*

A usable taxonomy has three properties:

1. **Mutually exclusive at submit time** — the submitter can pick exactly one without guessing. If two types need the same first three questions, they are one type with a branch, not two types.
2. **Owned** — each type has a named destination. A type with no owner is a type that becomes "general enquiry".
3. **Small** — a taxonomy the submitter has to read past the fold is a taxonomy they will get wrong. Six or seven top-level types is usually the ceiling; beyond that, branch.

⛔ **"Other" is a measurement, not a category.** Ship it, count it, and read its share as the health metric for the taxonomy. A rising share of "other" means the taxonomy has stopped matching the work.

## Step 2 — Derive the fields from the routing decision, not from the form

For each request type, ask: **what does the receiving queue need in order to act without a reply?** That set — and only that set — is the required field list.

Two tests that keep the list honest:

- **The use test.** For every field, name what someone does with the answer. A field whose answer nobody reads is data you are storing and defending for nothing. That is data minimisation and it stands on its own merits, independent of any conversion argument.
- **The blocking test.** Would the queue actually stop and ask if this were blank? If not, it is optional. Marking optional fields required is how you buy abandonment for information nobody needed.

⛔ **Do not argue field count on conversion grounds here.** The evidence on field count is contested and lives, with its counter-evidence, in [`../../../web-design/skills/conversion-design/SKILL.md`](../../../web-design/skills/conversion-design/SKILL.md) §3. Argue it on the use test.

## Step 3 — Write the routing rules as data, not as prose

A routing rule is `(request type [+ field predicate]) → queue`, and it should be readable as a table by someone who has never seen the form. Prose routing ("urgent items go to the on-call person") becomes contested the first time something is ambiguous.

| Request type | Predicate | Destination | Response clock starts | Target |
| --- | --- | --- | --- | --- |
| _(one row per type; a type with no row is a defect, not a default)_ |

**Every type has a row.** A taxonomy entry with no routing rule is the mechanism by which requests disappear.

## Step 4 — Set the clock per type, and say when it starts

A single response target across all request types is either too slow for the urgent ones or a promise you cannot keep for the rest. Per type, fix:

- **When the clock starts** — at submission, at acceptance, or at first triage. These differ by hours and the difference is where most SLA disputes come from.
- **What stops it** — a first human response, or a resolution. Say which; they are different promises.
- **What happens on business-hours boundaries** — a target expressed in elapsed hours behaves very differently from one expressed in business hours.

## Step 5 — Draw the self-serve vs escalate line before anyone is on it

Two bright lines, written down:

- **Self-serve** — the request type is answerable by a documented artifact, and the form should offer that artifact **before** the submit button, not after. A form that collects a question the site already answers is a queue you built for yourself.
- **Escalate** — the predicate that takes a request out of the normal queue immediately. Write it as a condition on a field, not as a judgement call, or it will not fire consistently.

## Step 6 — Read abandonment as a defect stream, not as a conversion number

This is the point where intake design and analytics diverge, and it is worth being explicit about the difference.

- **As a conversion diagnostic** — abandonment measures lost demand, and the remedy is usually persuasion, clarity or friction removal. That reading belongs to [`../../../web-design/skills/conversion-design/SKILL.md`](../../../web-design/skills/conversion-design/SKILL.md).
- **As a process defect stream** — abandonment measures the gap between what the process demands and what the submitter can supply *at that moment*. The remedy is usually a change to the **process**: ask for the account number later, accept a photo instead of a reference, let the queue look it up.

The second reading is this skill's. It produces different fixes, and it is the one that survives the observation that some abandonment is correct.

⛔ Per-field drop-off is a **proxy** — the last field touched is not the field that caused the exit. Treat it as a hypothesis generator; see [`../../knowledge/form-telemetry-and-spc.md`](../../knowledge/form-telemetry-and-spc.md) §3.

## Step 7 — Choose the platform on durable axes, if there is one to choose

Seven axes, no feature matrix, no pricing: [`../../knowledge/form-platform-evaluation.md`](../../knowledge/form-platform-evaluation.md), scored with [`../../templates/form-platform-evaluation-matrix.md`](../../templates/form-platform-evaluation-matrix.md). A blocking score on one axis ends the evaluation; there is no total that rescues a platform you cannot get your data out of.

If the form accepts attachments, the handling rules are owned upstream — [`../../../ravenclaude-core/rules/security.md`](../../../ravenclaude-core/rules/security.md) §File handling — and the binding verdict is [`../../../ravenclaude-core/agents/security-reviewer.md`](../../../ravenclaude-core/agents/security-reviewer.md)'s.

## Step 8 — Hand off

Fill [`../../templates/form-spec.md`](../../templates/form-spec.md) and hand the telemetry half to [`../form-telemetry-and-control/SKILL.md`](../form-telemetry-and-control/SKILL.md) and the trust-boundary half to [`../harden-a-form-submission/SKILL.md`](../harden-a-form-submission/SKILL.md). An intake design with no measurement plan cannot tell you whether it worked.
