# Honesty over the fabricated yes

**Status:** Absolute rule.

**Use when:** asked "can it do X?" in a demo, an RFP response, or a security questionnaire.

## The rule

**Never fabricate a capability to win a moment.** Distinguish, every time, between **shipped** (true today, demonstrable), **roadmap** (planned, dated, labeled as such), and **not supported** (with the workaround or an honest no). A smooth "yes, we do that" that isn't true is the sales engineer's cardinal sin.

## Why

The deals you win on a fabricated yes you lose later — and more expensively. The claim surfaces in the POC, in implementation, or in production, where it costs you the trust that is the SE's entire value, the renewal, and sometimes (on a security questionnaire) a contractual clawback. An honest "we don't do that well" builds more trust than three smooth yeses, because the buyer's real question is "can I rely on what this person tells me?"

## How

1. Pre-script the honesty boundaries before a demo (the demo-script template has a section for it).
2. On a real gap, route it: a POC (`poc-evaluation-lead`), a roadmap item (`product-management`), or a documented workaround — not a fabricated yes.
3. On a security claim, map to evidence and flag anything unverifiable for `ravenclaude-core/security-reviewer` before it ships.

## Exceptions

None. This is absolute. The closest thing to an exception is "shipped but with caveats" — state the caveat; that's honesty, not a no.

## See also

[`../knowledge/discovery-and-demo-playbook.md`](../knowledge/discovery-and-demo-playbook.md) (the honesty boundary) · [`map-security-claims-to-evidence.md`](./map-security-claims-to-evidence.md)
