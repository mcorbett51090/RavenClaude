# Microsoft 365 Copilot — best-practice docs

Named, consumer-facing rules for extending and governing Microsoft 365 Copilot with this plugin's agents. Each file is **one rule** — read, applied, and cited as a whole. They are the consumer-facing distillation of the plugin's [15 house opinions](../CLAUDE.md) and the [`knowledge/`](../knowledge/) bank that backs them.

For the full reference material (limits tables, decision trees, Microsoft Learn source URLs) see [`../knowledge/`](../knowledge/); for the agents that enforce these rules see [`../agents/`](../agents/).

---

## Index

| Doc | Status | Use when |
|---|---|---|
| [`design-to-66-percent-of-the-declarative-agent-wall.md`](./design-to-66-percent-of-the-declarative-agent-wall.md) | Absolute rule | Authoring/reviewing a declarative agent — sizing against the 50/25/4096/45s hard limits, pinning the schema, and knowing when the no-loop wall forces a custom-engine agent |
| [`label-and-acl-trim-every-connector-property.md`](./label-and-acl-trim-every-connector-property.md) | Absolute rule | Building a Copilot (Graph) connector — semantic-labelling every property and ingesting real per-user ACLs instead of "everyone" |
| [`remediate-oversharing-before-enabling-copilot.md`](./remediate-oversharing-before-enabling-copilot.md) | Absolute rule | Rolling Copilot out over an existing tenant — running the remediation sequence first and not mistaking RSS/RCD for a security boundary |

---

## How these relate

`design-to-66-percent-of-the-declarative-agent-wall` is the *build* rule — what fits in a declarative agent and when to escalate to a custom-engine agent. The other two are *data-safety* rules that gate what the agent can ground on: `label-and-acl-trim-every-connector-property` is the per-connector control (label + per-user ACL), and `remediate-oversharing-before-enabling-copilot` is its tenant-level companion (the RCD/RSS → Purview → cleanup → enable sequence). All three carry a `Licensing impact:` line, and the security *verdict* for ACL/DLP design escalates to `ravenclaude-core/security-reviewer`.
