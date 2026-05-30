# Reach for declarative before code — write Apex only past the declarative ceiling, and document the call

**Status:** Pattern — strong default for any new automation or customization; deviate only with a written reason.

**Domain:** Platform architecture / build-method selection

**Applies to:** `salesforce`

---

## Why this exists

Every line of Apex you write is a line you own forever: it needs a test class, a bulk assertion, a deploy gate, a code review, and a developer to change it next year. Declarative tools (Flow, validation rules, formula fields, Lightning App Builder, custom metadata) are upgraded by Salesforce, are visible to admins, and carry no governor-limit bookkeeping you have to author by hand. The platform's own guidance — and house opinion #11 — is "Flow over Apex for simple automation; Apex past the declarative ceiling." The failure mode of reaching for code first is an org where a junior admin can't change a field-update without a deployment, and where logic that a record-triggered Flow handles in three nodes is buried in a 200-line trigger handler nobody wants to touch. The opposite failure — forcing genuinely complex, performance-sensitive, or transaction-controlled logic into a sprawl of Flows — is just as real, which is why the rule has a documented ceiling.

## How to apply

Run the requirement down the build-method ladder and stop at the first rung that cleanly satisfies it. Write the call down so the next person knows it was a decision, not an accident.

```
1. Field default / formula / validation rule / rollup .... pure data shaping, no logic
2. Record-triggered Flow (before-save) ................... same-record field updates
3. Record-triggered Flow (after-save) ................... related-record DML, async paths
4. Screen Flow / Lightning App Builder .................. guided UI, page composition
5. Invocable Apex called FROM a Flow .................... a bounded complex step in a declarative shell
6. Apex trigger + handler .............................. past the declarative ceiling (below)
```

**Cross the ceiling into Apex when ANY of these is true** — and only then:

- Complex bulk operations beyond what Flow can express bulk-safely, or tight governor-limit budgets
- Transaction control: explicit rollback/savepoints, precise error handling, partial-success semantics
- Logic that must be unit-tested at the assertion level, called from multiple contexts, or version-controlled as code
- Web-service callouts with orchestration, or anything needing `Database` methods Flow doesn't expose

**Do:**
- Start at the top of the ladder; stop at the first rung that works without contortion.
- Keep a one-line "why Apex here" note on any code that crosses the ceiling (house opinion #11 — document the call).
- Use **invocable Apex from a Flow** to keep the orchestration declarative and only the hard step in code.

**Don't:**
- Reach for a trigger because Apex is what you know — the maintenance cost lands on the org, not you.
- Build a 40-element Flow to dodge writing 15 lines of well-tested, transaction-controlled Apex.
- Mix the same object's logic across both a Flow and a trigger with no single entry point (see the one-entry-point rule).

## Edge cases / when the rule does NOT apply

A team with deep Apex skill and no admin capacity may legitimately set a lower ceiling — but that is a written team decision, not a default. Some capabilities have no declarative form at all (custom REST endpoints, complex SOSL, dynamic Apex), so the ladder simply starts at Apex. And "declarative" is not automatically "simple": a Flow with dozens of elements, loops, and DML can be harder to reason about than equivalent Apex — at that density the ceiling has already been crossed and the work should move to code.

## See also

- [`flow-vs-apex-one-entry-point.md`](./flow-vs-apex-one-entry-point.md) — once you pick a tool, keep one entry point per object
- [`flow-before-save-for-same-record-field-updates.md`](./flow-before-save-for-same-record-field-updates.md) — the cheapest rung for same-record updates
- [`../knowledge/flow-vs-apex-decision.md`](../knowledge/flow-vs-apex-decision.md) — the full decision matrix and ceiling criteria
- [`../knowledge/platform-alm-agentforce-decision-trees.md`](../knowledge/platform-alm-agentforce-decision-trees.md) — the declarative-vs-programmatic tree
- [`../agents/flow-automation-architect.md`](../agents/flow-automation-architect.md) — the agent that owns the tool-choice call

## Provenance

Codifies house opinion #11 from [`../CLAUDE.md`](../CLAUDE.md) and the `flow-automation-architect` discipline. Grounded in [`../knowledge/flow-vs-apex-decision.md`](../knowledge/flow-vs-apex-decision.md) and Salesforce's "Architect's Guide to Record-Triggered Automation" and Flow-vs-Apex guidance. The declarative feature surface grows every release — re-check the ceiling criteria `[verify-at-build]`.

---

_Last reviewed: 2026-05-30 by `claude`_
