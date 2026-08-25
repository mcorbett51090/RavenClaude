---
name: wire-form-substrate
description: "Make the neutral forms guidance executable on the RavenPower stack: the ordered authority chain for a public write, where the challenge check sits, which fail directions are chosen, and the four honest gaps a reader must re-verify before relying on them."
---

# Skill: wire-form-substrate

> **Invoked by:** anyone working on `RavenPower-Website` forms, after [`../harden-a-form-submission/SKILL.md`](../harden-a-form-submission/SKILL.md) has produced the neutral walk.
>
> **When to invoke:** adding or changing a public write route on that estate; auditing an existing one; deciding where a new check belongs in the order.
>
> **Output:** a route that runs the authority chain in the right order, with its fail directions stated in the form spec.

⛔ **This is one of exactly two vendor-specific files in this plugin.** The other is [`../../knowledge/ravenpower-form-substrate.md`](../../knowledge/ravenpower-form-substrate.md). Gate 219 allowlists both, and a separability test deletes them on every run and requires the suite to stay green. **Nothing else in this plugin may name this stack.**

⛔ **This skill describes; it does not fix.** The gaps in §3 are documented state, not a task list, and this plugin changes nothing in that repository.

## The ordered authority chain for a public write

Run these in order. The order is not stylistic — each step exists to avoid doing expensive or trusting work before a cheaper check has ruled the request out.

| # | Step | Fail direction | Why it sits here |
| --- | --- | --- | --- |
| 1 | **Same-origin** (`Sec-Fetch-Site`, falling back to `Origin`) | closed | Cheapest possible rejection, before any parsing or database work |
| 2 | **Declared content-length** against the cap | closed | Rejects an oversized body before it is parsed; a forged declared length only costs the attacker the rejection |
| 3 | **Session** | closed on an authenticated route | Buffer the body after this, not before — an origin header is one flag away from being forged, a session cookie is not |
| 4 | **Double-submit CSRF token** | closed | Cannot move earlier: the token travels as a form field, so it is only readable after the parse |
| 5 | **Rate limit** (shared D1 fixed-window helper) | **ruled per route** — write it down | A limiter fault is not the same event as a limit breach |
| 6 | **Ownership** | closed | Resolve from the session, never from a body value |
| 7 | **Content-type allow-list** | closed | Declared-header allow-list — see §3 for the gap this leaves |
| 8 | **Size** (actual, not declared) | closed | The declared length was a hint; this is the fact |
| 9 | **Storage** | — | ⛔ Re-verify the binding exists before assuming this step works at all (§3) |

For an **anonymous** public form, steps 3, 4 and 6 are replaced by the challenge check plus the same-origin check. The challenge widget's mechanics — token lifetime, the replay rule, hostname scope — are owned by [`../../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md), and upload handling by [`../../../ravenclaude-core/rules/security.md`](../../../ravenclaude-core/rules/security.md) §File handling. Read those; do not reimplement them from this page.

## The one exception in the estate

`/intake` carries no challenge widget. Its authority is a signed link **or** an authenticated session that already owns the subscription. That is a stronger claim than a challenge token, not a weaker one — but it means the route's security depends entirely on the link-signing and ownership code, so any change there is a security change.

## Choose and record the fail direction, per route

Both directions are legitimate; an unstated one is not. In this estate the fail directions differ between routes **by design**, which means the only way to know one is to read that route.

⛔ **The challenge check currently fails open on an unset secret, with no signal emitted.** That is the concrete instance behind [`../../best-practices/degraded-bot-defense-must-be-loud.md`](../../best-practices/degraded-bot-defense-must-be-loud.md). The fix is a log line, a counter and an alert — not a change of direction.

## §3 — Four honest gaps. Re-verify each before you rely on it.

Every one of these describes **live, changeable state**. Run the command in [`../../knowledge/ravenpower-form-substrate.md`](../../knowledge/ravenpower-form-substrate.md) before citing any of them, and require the match to be inside the block it claims rather than in a comment that mentions one.

1. **The upload storage binding.** On `origin/main` at 2026-08-17 the bucket the upload route writes to was not bound, so a valid upload passed every check and died at the storage seam. An unmerged fix branch exists. Re-verify: `../../knowledge/ravenpower-form-substrate.md` §6b.
2. **Outbound mail domain.** `[unverified — carried from memory, not re-probed]` The recorded signature is a split — founder alerts deliver, customer mail does not.
3. **No aggregate error summary on the long intake form.** Carried from the audit that produced the substrate file; re-verify before citing.
4. **No scripted focus move to the live region on the call-request form.** Same provenance, same caveat.

## Not this skill

| You are actually doing | Go here |
| --- | --- |
| The neutral trust-boundary walk | [`../harden-a-form-submission/SKILL.md`](../harden-a-form-submission/SKILL.md) |
| The binding security verdict | [`../../../ravenclaude-core/agents/security-reviewer.md`](../../../ravenclaude-core/agents/security-reviewer.md) — zero-exception |
| Upload handling rules | [`../../../ravenclaude-core/rules/security.md`](../../../ravenclaude-core/rules/security.md) |
| Challenge-widget mechanics | [`../../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md) |
| Intake taxonomy and routing | [`../form-intake-and-triage-design/SKILL.md`](../form-intake-and-triage-design/SKILL.md) |

⛔ A separately-installed local convenience for wiring the challenge widget exists outside this marketplace and is **not** a routing target: it is unavailable to anyone who installs this plugin, so nothing here depends on it.
