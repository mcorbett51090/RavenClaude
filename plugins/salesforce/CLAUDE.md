# salesforce — plugin constitution

This plugin ships a roster of Salesforce engineering specialists. It inherits the marketplace constitution at the repository root (`../../CLAUDE.md`) and the cross-tool conventions in `../../AGENTS.md`. Anything here is **salesforce-specific** and refines — never overrides — the root rules.

## What this plugin is

A focused set of agents for building on the Salesforce platform: bulk-safe Apex (triggers, async, SOQL/DML), declarative-automation triage (Flow vs Apex, automation density), Agentforce design under determinism and Trust Layer constraints, and cross-cutting platform architecture (data model, sharing, LDV, packaging, DevOps, integration). A forked reviewer enforces the house opinions as a pass/fail rubric.

## Agent roster

| Agent | Scope | Model |
| --- | --- | --- |
| `apex-engineer` | Apex / server-side: triggers, async, SOQL/SOSL, tests | sonnet |
| `flow-automation-architect` | Declarative automation, Flow-vs-Apex, automation density | sonnet |
| `agentforce-architect` | Agentforce topics/actions, determinism, Trust Layer | sonnet |
| `salesforce-platform-architect` | Data model, sharing, LDV, packaging, DevOps, integration | opus |
| `salesforce-reviewer` | The 15 house opinions as a pass/fail review rubric (forked) | opus |

## The 15 house opinions

These are baked into every agent and are the `salesforce-reviewer`'s rubric:

1. Bulkify everything — no SOQL or DML in a loop, ever.
2. One trigger per object; logic lives in a handler class.
3. Logic-less triggers — the trigger is a dispatch shell.
4. Recursion control is mandatory on every handler.
5. No hard-coded IDs (records, RecordTypes, profiles) — query or use custom metadata.
6. `with sharing` by default; justify every `without sharing`.
7. Enforce CRUD/FLS for user-context access (`WITH SECURITY_ENFORCED` / `Security.stripInaccessible`).
8. Bind every SOQL variable — no string concatenation in dynamic SOQL.
9. Test for bulk (200 records); assert outcomes, not coverage.
10. No `@isTest(SeeAllData=true)` — use a TestDataFactory.
11. Flow over Apex for simple automation; Apex past the declarative ceiling. Document the call.
12. One automation entry point per object.
13. Design for LDV from day one — selective, indexed queries.
14. Agentforce is non-deterministic — never where a deterministic automation belongs; gate with the Trust Layer.
15. Bundle metadata in 2GP packages; deploy in dependency order; never click-deploy to prod.

## Escalating out — cross-plugin seams

- **Security verdicts** — SOQL injection, secret handling, and FLS-as-a-security-control escalate to `ravenclaude-core/security-reviewer`. This plugin supplies the domain rubric; core owns the verdict. There is deliberately **no** security agent here.
- **Generic test authoring** escalates to `ravenclaude-core/tester-qa`; `apex-engineer` owns the Salesforce-specific bulk/assert discipline.
- **Azure-native integration** (middleware, Event Grid, queues crossing into Azure) coordinates with `azure-cloud/*`.
- **The accuracy / grounding / Structured Output protocols** are inherited from the root constitution.

## House conventions

- Every agent inherits the team constitution and references plugin-internal files only.
- Knowledge docs are citation-grounded and dated. Fast-moving Agentforce facts are tagged `[verify-at-build]`.
- Skills are deterministic, parameterized, and safe to run unattended.
- The advisory hook `hooks/flag-salesforce-anti-patterns.sh` greps written Apex for the grep-able anti-patterns (SOQL/DML in loop, hard-coded IDs, `SeeAllData=true`, missing `with sharing`) and prints non-blocking notes.

## Milestones

- **v0.1.0** — initial roster (5 agents), 9 knowledge docs, 5 skills, 5 templates, anti-pattern hook.
- **v0.4.1** — fixed a dead cross-plugin seam: `apex-engineer` escalated generic test authoring to `ravenclaude-core/test-author`, which does not exist (the core test agent is `tester-qa`). Renamed all 5 references — incl. the machine-read `works_with` frontmatter that drives routing — to `ravenclaude-core/tester-qa` (two-panel audit 2026-05-31).
