# Immutability means audit BEFORE deploy — you can't trivially patch a shipped contract.

**Status:** Absolute rule. **Constitution:** §3 #1, §4.

## Use when
Any blockchain & web3 engineering deliverable where this question is in play — read, applied, and cited whole.

## The rule
A deployed contract's bytecode is permanent; there is no hotfix on a non-upgradeable contract, so the audit, invariant tests, and testnet exercise are the gate, not a post-launch nicety — a bug ships at the speed of a block and is exploited at the speed of a bot.

## Why it matters
This is house opinion §3 #1, distilled into a citable rule. Practitioners act on these deliverables, so a framing error here is not academic — it sends real operating decisions the wrong way. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Make every number in the deliverable carry a definition, a window, and a baseline (§3 #1).
- Cite a source + date for any external benchmark, or mark it `[unverified — training knowledge]` (§3 #8).
- When this rule and another both apply, route to [`web3-architect-lead`](../agents/web3-architect-lead.md) to sequence them — overlapping signals usually mean two drivers at once.
- Keep private keys / wallet data out of the deliverable; route professional/legal determinations to the qualified authority (§2).
- Close with a recommendation that has an owner, a date, and an expected metric movement.

## The anti-pattern this prevents
The §4 failure mode: acting as if "immutability means audit BEFORE deploy — you can't trivially patch a shipped contract." weren't true — the most common way an analysis quietly misleads the practitioner who acts on it. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §3 #1 — the house opinion this rule encodes.
- [`../knowledge/blockchain-web3-engineering-decision-trees.md`](../knowledge/blockchain-web3-engineering-decision-trees.md) — the decision trees that route to it.
