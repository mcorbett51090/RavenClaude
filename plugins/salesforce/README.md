# salesforce

Salesforce engineering specialists for the RavenClaude marketplace — bulk-safe Apex, declarative-automation triage, Agentforce determinism, platform/sharing/LDV architecture, and a Salesforce-specific review rubric.

## Install

```
/plugin marketplace add <this-marketplace>
/plugin install salesforce@ravenclaude
```

## Agents

| Agent | Use it when |
| --- | --- |
| `apex-engineer` | You're writing or fixing Apex — triggers, async jobs, SOQL/DML — and need it to survive a 200-record bulk load. |
| `flow-automation-architect` | You're deciding which automation tool to use, triaging automation density on an object, or weighing Flow vs Apex. |
| `agentforce-architect` | You're designing an Agentforce agent and need to respect determinism boundaries and the Einstein Trust Layer. |
| `salesforce-platform-architect` | You're designing a data model, sharing model, LDV strategy, packaging/DevOps pipeline, or integration pattern. |
| `salesforce-reviewer` | You want a PR or component reviewed against the 15 Salesforce house opinions as pass/fail. |

## Knowledge

Citation-grounded reference docs under `knowledge/`, each dated `2026-05-30` and carrying a `## Decision Tree:` Mermaid graph: governor limits & bulkification, async Apex patterns, the trigger-handler framework, Flow-vs-Apex, the sharing & security model, large-data-volume design, packaging & deployment, integration patterns, and Agentforce determinism & trust.

## Skills

Parameterized, deterministic helpers under `skills/`: `soql-authoring`, `lwc-component-scaffold`, `bulk-rest-api-client`, `data-loader-runbook`, `salesforce-release-pipeline`.

## Templates

Starter skeletons under `templates/`: trigger handler, Batch Apex class, LWC bundle, Apex test class, and an sfdx project manifest.

## Security

Security verdicts (SOQL injection, secret handling, FLS as a security control) escalate to `ravenclaude-core/security-reviewer` — this plugin supplies the domain rubric, core owns the verdict.

## License

MIT © Matt Corbett
