# forms-engineering — team constitution

A form is the entry point of a process. This plugin owns the part of that sentence nobody else in this marketplace owns: **the intake behind the form, the measurement contract in front of it, and the trust boundary underneath it.**

## §1. What this plugin is

`forms-engineering` is a **seam**, not a new owner. Three plugins already own most of what a form needs, deeply and with dates on their sources:

| Already owned | Owner |
| --- | --- |
| Client-side form construction, native form patterns, input types, validation UX | [`../web-design/agents/frontend-implementer.md`](../web-design/agents/frontend-implementer.md) |
| Form accessibility — labels, error association, required indication, validation timing, the conformance verdict | [`../web-design/agents/accessibility-auditor.md`](../web-design/agents/accessibility-auditor.md) |
| Funnel and conversion diagnosis, field-count evidence, trust signals | [`../web-design/skills/conversion-design/SKILL.md`](../web-design/skills/conversion-design/SKILL.md) |
| Control charts, control limits, common- vs special-cause response, control plans | [`../process-improvement/agents/lean-six-sigma-blackbelt.md`](../process-improvement/agents/lean-six-sigma-blackbelt.md) |
| Upload hardening; untrusted input at the boundary | [`../ravenclaude-core/rules/security.md`](../ravenclaude-core/rules/security.md) |
| Challenge-widget mechanics — lifetime, replay, verification, hostname scope | [`../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md) |

What is left, and what this plugin therefore owns: **intake taxonomy and triage routing**, **the form measurement contract and its hand-off to statistical process control**, **the server half of a submission that `web-design` routes out by rule**, and **form-platform selection on durable axes**.

## §2. House opinions

1. **The form is the entry point of a process.** Design the queue first, derive the fields from the routing decision, and treat a field nobody uses as liability rather than thoroughness.
2. **A rate without a denominator is not a number.** Completion and abandonment are exact complements on one written denominator, printed next to every figure.
3. **Cite, do not restate.** Where another plugin owns a rule, this plugin links to it. A second copy diverges the moment the original is updated, and the upstream files carry a `refresh_when:` clause that a copy would not. This is enforced by gate, not by intention.
4. **Start at the bottom of the anti-abuse ladder.** A challenge widget in front of a form receiving a handful of submissions a week buys a third-party dependency and an unresolved accessibility question in exchange for work a human would have done in seconds.
5. **A defense you cannot observe is a belief.** Fail-open and fail-closed are both legitimate; failing silently is not.
6. **Anti-forgery is not anti-duplicate.** They are different adversaries and they need different mechanisms.
7. **Say what would change your mind.** A measurement plan whose every possible outcome is consistent with success is not a plan.

## §3. Honesty constraints — both enforced by permanent CI gates

1. ⛔ **Applying statistical process control to form telemetry is OUR SYNTHESIS, not established practice.** Two targeted open-web searches (2026-08-17) returned SPC generalities and form-analytics generalities with zero intersection. Every surface that makes the join carries the verbatim marker, and [`./scripts/form_metrics.py`](./scripts/form_metrics.py) prints it on **stderr in every mode** so a user who never opens a document still sees it.
2. ⛔ **The challenge widget's WCAG conformance level is disputed by its own vendor's documentation** — one level on the overview page, another on the plans page. **No surface here states either level unqualified.** See [`./knowledge/form-anti-abuse.md`](./knowledge/form-anti-abuse.md) §4.

> [NOVEL SYNTHESIS — applying SPC to form telemetry is our synthesis, not established practice. We found no published work joining web-form telemetry to SPC/DMAIC (open-web search, 2026-08-17); the negative finding is bounded by that method and is not proof of universal absence.]

A third constraint is negative: **no vendor pricing and no feature matrix**, anywhere. Both go stale within a quarter and a stale comparison reads authoritative long after it stopped being true.

## §4. Zero agents, deliberately

This plugin ships **no agents**, and that is a ruling rather than an omission. The unowned residue here is a seam between three existing owners, and its security half is a review lane that even an admitted carve-out in this marketplace declined to fork — memory security ships as a skill invoked by core's reviewer, not as a second reviewer. A `forms-*` architect would sit beside `process-improvement/process-analyst` with a narrower mandate on the same rubric: dispatch ambiguity and rubric drift.

Reachability is bought instead by **reciprocal priors** in the five agent files that would otherwise miss this work, plus the `/design-form-intake` command.

**What would reopen it:** a named citable specialist body for forms-as-process, or a measured rot signal one release out — at which point exactly **one** first-contact agent is the correct remedy.

## §5. The substrate boundary

Exactly **two** files in this plugin are vendor-specific: `knowledge/ravenpower-form-substrate.md` and `skills/wire-form-substrate/SKILL.md`. Everything else is neutral.

⛔ **The dependency is ONE-WAY and that is what makes the split real.** The substrate layer may link into the neutral bank; **no neutral file may link into the substrate layer** — including this one, which is why those two paths above are written as plain code spans rather than links. A neutral→substrate link would make deleting the two files break the repo's link checker, and the separability test would fail. Gate 219 sub-check F enforces the direction.

That split is a **gate, not a folder**: Gate 219 allowlists exactly those two paths and rejects a vendor token anywhere else unless it sits on a line that links into `ravenclaude-core`. A separability test deletes both files and requires the full suite to stay green — so "separable" is falsifiable rather than asserted.

Every claim in the substrate layer that describes **live, changeable state** ships with its own re-verification command, and the match must be inside the block it claims rather than in a comment that mentions one.

## §6. Anti-patterns

- Restating an upload rule or a challenge-widget mechanic instead of linking it.
- Quoting a form rate with no denominator, or quoting completion and abandonment from different ones.
- Putting three-sigma limits on a form series below the stated floor, or widening the limits when the alarms turn out not to be real.
- Adding a honeypot without the assistive-tech and autofill exemptions, or without counting its rejections.
- Treating a CSRF token as a duplicate guard.
- Publishing a vendor price or a feature matrix.
- Presenting the SPC join as received practice.
- Drifting into `<label>` association, error timing or field layout — those belong to `web-design`.

## §7. Routing — what always leaves this plugin

| Question | Goes to |
| --- | --- |
| Is this change safe to ship? | [`../ravenclaude-core/agents/security-reviewer.md`](../ravenclaude-core/agents/security-reviewer.md) — **zero-exception**, the binding verdict is never ours |
| Is this form accessible? | [`../web-design/agents/accessibility-auditor.md`](../web-design/agents/accessibility-auditor.md) |
| How should this form look and behave? | [`../web-design/agents/frontend-implementer.md`](../web-design/agents/frontend-implementer.md) and [`../web-design/agents/ux-designer.md`](../web-design/agents/ux-designer.md) |
| What are the control limits, and is this signal real? | [`../process-improvement/agents/lean-six-sigma-blackbelt.md`](../process-improvement/agents/lean-six-sigma-blackbelt.md) |
| Is this difference statistically real? | [`../applied-statistics/CLAUDE.md`](../applied-statistics/CLAUDE.md) |
| Are we allowed to collect or keep this? | [`../data-governance-privacy/CLAUDE.md`](../data-governance-privacy/CLAUDE.md) **and the owner** |
| How do we verify this webhook? | [`../web-commerce/skills/webhook-hardening/SKILL.md`](../web-commerce/skills/webhook-hardening/SKILL.md) |
| How do we design the idempotency key? | [`../api-engineering/skills/idempotency-key-design/SKILL.md`](../api-engineering/skills/idempotency-key-design/SKILL.md) |
| Is this a survey rather than a form? | [`../ux-research/CLAUDE.md`](../ux-research/CLAUDE.md) |
