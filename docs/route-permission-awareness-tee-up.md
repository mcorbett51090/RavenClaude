# Route / permission awareness — Copilot picks the wrong method: tee-up

> **Status:** TEE-UP (analysis, not started). Drafted 2026-05-31 in response to: *"ensuring an agent knows all possible routes to a goal, the permission each requires, what permissions it holds, and which it should actually do — without contamination. Copilot doesn't consistently use the correct method."*
>
> **This doc deliberately does NOT propose the reconciler I first reached for** — because grounding the question against the codebase revealed that piece is **explicitly forbidden by a documented house rule**, and a convention for it **already exists**. The honest finding changes the recommendation. Docs-only → commits to `main`.

## What already exists (verified 2026-05-31)

The four-part capability you described is **already designed**, mostly shipped, and mostly behavioral:

| Sub-question | Mechanism that exists | Where |
|---|---|---|
| **All routes to a goal** | (a) reactive "Try alternative paths before declaring blocked" (enumerate easiest→hardest, try in order); (b) proactive "Pre-action decision-tree traversal" of a plugin's `## Decision Tree` Mermaid graph. **54 decision trees** exist across the plugins. | `ravenclaude-core/CLAUDE.md` §CGP; `docs/best-practices/decision-trees-in-knowledge-files.md` |
| **Permissions the agent HOLDS** | SessionStart **capability banner** — injects detected auth (env-var *names*), CLI profiles, effective `.claude/settings.json` allow/ask/deny, every session. `.ravenclaude/environment-context.md` carries per-environment roles. | `capability-orientation.py` / `.sh` |
| **Permission each ROUTE requires** | The **`requires:` annotation convention** — a decision-tree leaf names the role/scope it needs; the agent cross-checks it against the capability banner before committing to that branch. Documented 2026-05-26. **27 of 54 trees already carry a prerequisite note.** | `decision-trees-in-knowledge-files.md` §"Node prerequisites: the `requires:` annotation" |
| **Which to do, no contamination** | "Default to the smaller-blast-radius leaf; escalate only when it demonstrably fails." Blast containment = container/worktree boundary + comfort-posture `security_deny` floor. | CGP; §Containment posture |

**The key finding:** this is not a missing capability. The `requires:` convention is the exact "route → required-permission, reconciled against held-permission" mechanism — it exists and is partially adopted.

## The load-bearing constraint: a reconciler/parser is FORBIDDEN

`decision-trees-in-knowledge-files.md` § "Forbidden infrastructure" is explicit. Do **NOT** add:
- a `DECISION_TREE:` parser/validator beyond prettier
- a tree-aware skill that programmatically traverses the Mermaid
- a `trees/` dir, a `.tree.yaml` extension, or a `decision-tree-evaluator` agent

> *"If the format needs tooling beyond Mermaid syntax linting, the format is wrong. The whole point is 'prose with discipline' — the agent reads the same markdown a human reads."*

And the `requires:` design note states the choice deliberately: *"convention, **not a parser**... **no central registry, no parser**."* So my first instinct — a deterministic `requires:`→held-permission reconciler wired into the banner — **would reverse a documented architectural decision.** It is off the table unless Matt explicitly chooses to overturn that rule (an option, but a real reversal, not a gap-fill).

## So why does Copilot still pick the wrong method?

With a deterministic reconciler ruled out, the honest diagnosis of the *Copilot-specific* inconsistency is **adoption + salience + host-fidelity**, not a missing engine:

1. **Coverage gap (the biggest, and rule-compatible to fix).** ~**27 of 54** trees have no `requires:` note; many goals have **no decision tree at all** (a plugin with rich best-practices but few/no `## Decision Tree` sections gives the model nothing structured to traverse). Where there's no tree and no `requires:`, the model is pattern-matching — exactly the failure you see. **This is authoring debt, not an engine gap, and filling it does not touch forbidden infrastructure.**
2. **Salience under Copilot.** The traversal + alternate-methods rules are **prose** in CLAUDE.md/agent files. Claude Code subagents read them as system-prompt; Copilot routes them as AGENTS.md context to Claude/GPT/Grok, where a weaker/different model is likelier to skip prose. The capability banner *is* enforced-injection on Claude Code (`SessionStart` hook) and **does** ride the Copilot adapter — but the *decision-tree priors* do not have an equivalent impossible-to-miss surface under Copilot.
3. **No "did you traverse the tree?" check exists on either host** — by design (forbidden). So fidelity rests entirely on the model following prose.

## Recommended moves (ranked; all rule-compatible)

**A. Close the `requires:` + decision-tree coverage gap (highest leverage, zero rule conflict).** Audit the 54 trees: (i) add a `requires:` note to every leaf that needs a permission/scope but lacks one (~27 trees); (ii) identify high-traffic goals in each plugin that have *no* tree and author one (this is the same "prose with discipline" the convention already blesses). This directly attacks #1 — it gives the model structured routes + prerequisites *to read* where today it has none. Gateable **only** via the existing prettier/Mermaid-lint + a light "every `requires:` names a real banner-checkable concept" *advisory* (not a parser — a lint that greps for the annotation's presence/shape, consistent with the frontmatter gate's spirit).

**B. Raise decision-tree-traversal salience under Copilot (medium, rule-compatible).** The capability banner already injects held-permissions on both hosts. Add **one line** to that banner pointing the agent at the active plugin's decision trees + the `requires:`-check discipline ("Before picking a method, traverse the plugin's `## Decision Tree` and check each branch's `requires:` against the permissions above"). This is *salience*, not *enforcement* — it reuses the one surface that already crosses to Copilot, and it's the banner's existing job ("stop the agent acting as if it has no access"). No parser, no traversal engine.

**C. A `requires:`-presence advisory lint (small, borderline — get Matt's read).** A PostToolUse/ CI advisory that flags a `## Decision Tree` whose leaves make a permission-gated recommendation but carry no `requires:` note — nudging authors to annotate. This is *arguably* within "Mermaid syntax linting" spirit (it lints the convention's completeness, doesn't traverse/evaluate the tree), but it's close enough to the forbidden line that **Matt should rule on it** before building. If he says it smells like the forbidden parser, drop it and rely on A+B.

**Explicitly NOT recommended (would reverse a documented decision):** a runtime reconciler that parses `requires:`, reads the banner, and emits "the one viable route." It's the cleanest *engineering* answer and the most direct hit on your Copilot problem — but it is precisely what "Forbidden infrastructure" prohibits. **If the Copilot pain is severe enough to justify overturning that rule, that's a legitimate call — but it's Matt's call to make explicitly, with the rule edited in the same PR, not a silent build.**

## Open questions for the build session

1. **Is the convention-over-enforcement rule still the right call given the Copilot pain?** If yes → do A + B (and maybe C). If Matt wants to overturn it → that's a separate, larger build (the reconciler) that must edit "Forbidden infrastructure" first and own the consequence (a parser the rule warned against).
2. **Scope of the coverage backfill (A).** All 14 plugins at once, or start with the ones Matt actually drives under Copilot (Power Platform, Azure, M365)? Recommend: pilot on the 2-3 highest-traffic plugins, measure whether Copilot's method-selection improves, then roll out.
3. **Does the advisory lint (C) cross the forbidden line?** Matt's read needed before building it.

## Why this is teed-up, not built

The instinct ("build a reconciler") collided with a **documented house rule that explicitly forbids it** — exactly the kind of thing that wastes a build if discovered mid-flight. The genuinely-useful, rule-compatible work (A: close the coverage gap; B: one banner line for Copilot salience) is real and shippable, but A is a sizable authoring effort best scoped deliberately, and C needs a human ruling on the forbidden-infrastructure boundary. Better to surface the constraint and the options than to build against a decision the prior maintainer made on purpose.
