# ravenclaude-core best practices

Named rules the `ravenclaude-core` agents surface to consumer-repo users. Each file is one rule — read, applied, and cited whole. These are grounded in the plugin's own constitution ([`../CLAUDE.md`](../CLAUDE.md)), knowledge files, and agent definitions; they are not generic coding advice.

For the marketplace-wide best-practice library (CI gates, hook authoring, versioning), see [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md).

---

## Index

| Doc | Status | Use when |
|---|---|---|
| [`route-before-spawning.md`](./route-before-spawning.md) | Pattern | The Team Lead is about to delegate — traverse the routing tree top-to-bottom before spawning any specialist, instead of keyword-matching the request to an agent name |
| [`three-epistemic-protocols.md`](./three-epistemic-protocols.md) | Absolute rule | Any agent is about to report blocked, write a consequential claim, or hand work back — apply the CGP / Claim-Grounding / Last-Mile triad |
| [`command-review-when-to-enable.md`](./command-review-when-to-enable.md) | Pattern | Deciding whether to turn on the command-review tribunal — required under multi-vendor routing, optional under pure Claude Code where native `auto` mode covers the floor |
| [`check-runtime-state.md`](./check-runtime-state.md) | Pattern | Before acting — read the event substrate (hook-events / posture-events / scenario-events via the Heimdall / Víðarr / Norns tabs) so you don't retry a denied command, re-propose a posture change, or cite a scenario blind to its history |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — the team constitution these rules distill
- [`../knowledge/agent-routing.md`](../knowledge/agent-routing.md) — the routing decision tree
- [`../knowledge/concerns-catalog.md`](../knowledge/concerns-catalog.md) — the tribunal's concern catalog
