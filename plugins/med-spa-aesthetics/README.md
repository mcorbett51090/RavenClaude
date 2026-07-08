# med-spa-aesthetics

A RavenClaude plugin: a **medical-aesthetics (med spa) practice operations** specialist team for the three engines of a med spa — the practice P&L, the patient front line, and operational compliance structure.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Operations and financial decision-support — not legal, tax, or medical advice.** The agents make no clinical or legal determinations and store no patient PHI/PII. Benchmarks (injector productivity, service margins, consult conversion, membership norms) are volatile and practice-specific: each carries a retrieval date + `[verify-at-use]` and must be confirmed before it drives a target, a price, or a policy. Scope-of-practice, good-faith-exam, supervision, and consent questions are **state-specific determinations** flagged for the medical director and a licensed professional. The clinical treatment plan and cadence are the provider's call.

## What it's for

Running a med spa well: injector-hours and treatment-room-hours sold at high utilization, a service mix (injectables, energy devices, skincare, memberships) tilted toward contribution, capital-device bets made on honest payback math, a consult that converts, a calendar defended against no-shows and refilled by cadence rebooking, and a compliance structure that's mapped and routed — not improvised.

## Agents

| Agent | Use for |
| --- | --- |
| **med-spa-operations-lead** | Treatment-room & injector utilization, service mix, device payback, pricing per provider-hour, membership economics |
| **patient-coordinator-lead** | Consult-to-treatment conversion, booking, no-show / deposit policy, rebooking on the clinical cadence, membership enrollment |
| **aesthetics-compliance-advisor** | Scope of practice, good-faith exam / supervision, consent & adverse-event protocols, product handling — flags to a professional |

## What's inside

- **4 skills** — consult-to-treatment-conversion, treatment-room-and-injector-utilization, service-mix-injectables-devices-memberships, scope-of-practice-and-supervision.
- **Knowledge bank** — [`med-spa-decision-trees.md`](knowledge/med-spa-decision-trees.md) (4 Mermaid trees: add a service/device, design the membership, rebook on cadence, scope & supervision structure) + [`med-spa-reference-2026.md`](knowledge/med-spa-reference-2026.md) (dated reference, verify-at-use).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — med-spa KPI dashboard, service/device pro-forma.
- **2 commands** — `/model-device-payback`, `/design-membership`.

## Seams

Scope of practice, supervision, good-faith exam, consent sufficiency, corporate-practice-of-medicine / MSO structure, HIPAA/PHI handling → the medical director and a licensed professional (the agents map the structure and flag the call). The clinical treatment plan and cadence → the provider. Security/privacy verdicts → [`ravenclaude-core`](../ravenclaude-core/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install med-spa-aesthetics@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the scope, routing rules, house opinions, and the output contract.
