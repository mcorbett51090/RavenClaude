# Plugin-Discovery Routine — Value/Criticality Bar (governing policy)

> **Status:** 🟢 binding policy for the recurring "N new plugins" discovery routine.
> **Owner:** Matt. **Set:** 2026-06-24. **Supersedes** the literal scheduled-prompt framing ("identify 10 new plugins… build the highest-priority first") wherever they conflict, and **sharpens** the standing #409 *build-on-real-demand over catalog-breadth* decision (`docs/plugin-candidates-2026-06.md`, `docs/idea-board.md`).
>
> **Read this FIRST on every run of the discovery routine, before picking or building anything.**

---

## 2026-07-02 update — ONE plugin per run, built to GOLD STANDARD (loop until complete)

> **Owner:** Matt. **Set:** 2026-07-02. This is the current operating contract; it **overrides** the "10 candidates" framing of the literal schedule prompt and refines the run contract below.

Matt's directive (2026-07-02): **the routine no longer produces a batch. Each run works on exactly ONE plugin and loops — build → self-review → fix — until that plugin is fully built out to the gold-standard bar.** Depth over breadth, taken to its conclusion: a shallow "gate-passing minimum" plugin is **not** an acceptable run result anymore. The run is done when the single plugin is *gold standard*, not when it merely passes CI.

What changes vs. the prior contract:

- **Selection is unchanged.** Still pick the single highest-priority unbuilt candidate that clears the **Value/Criticality bar** below. If nothing clears the bar, still **build nothing** (steady-state no-op is a success) — the gold-standard loop only applies *once a candidate is chosen*.
- **Build target is raised** from "gate-passing minimum" (3 agents / 4 skills / no hooks) to the **Gold-standard bar** (§ "The gold-standard bar"). The 10-plugin batch shipped in #543 was deliberately built to the *minimum*; that is now the floor to iterate up from, not the finish line.
- **The run is a loop, not a single pass.** After each build increment, run the full gate suite **and** self-review against the gold-standard checklist; fix the highest-value gap; repeat. Only stop the loop when every checklist item is satisfied and all gates are green.
- **One plugin at a time, carried across runs.** If a plugin is not yet gold standard when the run's budget is exhausted, **do not start a new plugin.** Record progress in the plugin's `CHANGELOG.md` + the roadmap, and the *next* run resumes the same plugin until it reaches the bar. A new candidate is only selected once the current one is gold-standard-complete and merged.

### The gold-standard bar

A plugin is **gold standard** when every item holds (self-review against this list each loop):

1. **Agents (3–5)** — a lead + function specialists; each with the full scenario schema, a `description` ≤ 300 chars, a real ~60–100-line body (Mission / ordered discipline / decision-tree traversal pointer / escalation-&-seams / house opinions / output contract), and globally-unique `name`.
2. **Skills (≥ 5)** — each a genuine capability file with a workflow, a metrics table, and cross-links to sibling skills — not a stub.
3. **Knowledge bank** — a decision-trees file with **4 Mermaid trees** covering the domain's real branch points + a **dated reference** where every volatile figure carries a retrieval date + `[verify-at-use]` (and `[ESTIMATE]` where estimated).
4. **Best-practices** — README index + **≥ 7** durable rule files, each with Status / Why it exists / How to apply (with a concrete example).
5. **Templates (≥ 3)** and **commands (≥ 3)** — operator-facing artifacts + slash commands wired to the agents/skills/templates.
6. **An advisory hook** — a `PreToolUse`/`Stop` (or domain-appropriate) hook + `hooks.json` that catches the domain's top anti-pattern, `set -euo pipefail`, executable, `bash -n`-clean, idempotent, fail-open. *(This is the single biggest gap between #543's minimum and gold standard.)*
7. **A calculator/helper script where the domain has real math** (e.g. unit economics, ratios, rate models) under `scripts/`, ruff-clean, with the `.py` declared — optional only when the domain genuinely has no computable core.
8. **CLAUDE.md constitution** — scope, roster, routing, verify-at-use, and cross-plugin **seams** that link only to real sibling plugins; **README.md** and **CHANGELOG.md** current.
9. **All gates green** — `check-frontmatter.py`, `check-marketplace-claims.py --structural-only`, `check-md-links.py`, `prettier --check .`, version parity, layout allow-list, **and** the hook behavioral checks + `audit-gates.sh` for anything the plugin adds.
10. **Wired** into `.claude-plugin/marketplace.json` (parity-exact) and the `docs/architecture.md` Status table; roster count refreshed.

If a domain genuinely cannot support an item (e.g. no computable core → no script), that is recorded as a deliberate, justified exception in the plugin's `CHANGELOG.md` — not a silent omission.

---

## Why this exists

The marketplace is mature (119 plugins as of 2026-06-24). Coverage of the high-value engineering, platform, data/AI, and vertical-industry lanes is broad. The routine's old contract — *"build the single highest-priority unbuilt row each run"* — was right when there were obvious unowned lanes, but at this catalog size it has started reaching into **niche / speculative** territory (Demand 2/5 candidates such as bespoke robotics/bioinformatics/AR-VR sub-lanes) and **building one each cycle simply because it is next in line**.

Matt's directive (2026-06-24): **the routine should only include — and only build — new plugins that are genuinely *valuable* or *critical*.** Manufacturing a candidate to have output is no longer an acceptable run result. A run that correctly concludes "nothing clears the bar this cycle" is a **success**, not an empty run.

---

## The bar — when a candidate qualifies

A candidate plugin clears the bar if it is **valuable** (meets *all four* gates) **or critical** (the override).

### Valuable — ALL of these must hold

Scored on the routine's existing 1–5 axes (**Demand × Feasibility × Disjoint**, see any `docs/proposals/*-ten-new-plugin-candidates.md`):

| Gate | Threshold | Rationale |
|---|---|---|
| **Disjoint** | **≥ 4 / 5** | It owns a genuinely *unowned* lane. A near-duplicate or thin slice of an existing plugin does **not** qualify — extend the existing plugin instead. |
| **Demand** | **≥ 4 / 5** | A real, recurring practitioner need — not "someone might want it someday." Niche/hobby/long-tail (≤ 2) is held. |
| **Feasibility / durability** | **≥ 4 / 5** | The craft is durable enough to build to the gate-passing depth bar without shipping facts that rot. Volatile-fact domains are held until the durable core is separable. |
| **Composite priority** | **Demand + Feasibility + Disjoint ≥ 13 / 15** | A numeric floor on top of the per-axis minimums. |

### Critical — the override

A candidate is **critical** (clears regardless of the breadth concern, even if an axis dips) when **a concrete, present need exists**, e.g.:

- a **real engagement / project** needs it now (the #409 *build-on-real-demand* trigger), **or**
- a filed **issue, explicit Matt ask, or repeated user request** names the gap, **or**
- its absence is **actively blocking** real work already in flight.

"Critical" must cite the **specific signal** (engagement, issue #, request) in the run's roadmap entry. Absent a real signal, a candidate is judged on the *Valuable* gates only.

---

## The run contract — what the routine does each cycle

1. **Inventory** `plugins/` on disk and read the latest `docs/proposals/*-ten-new-plugin-candidates.md` (collision-avoidance; unchanged).
2. **Score** the unbuilt candidates against the bar above.
3. **Branch:**
   - **If ≥ 1 candidate clears the bar:** select the **single highest-priority one** and build it to the **gold-standard bar** via the build → self-review → fix **loop** (§ "2026-07-02 update"), not a single gate-passing pass. If a prior run left a plugin partway to gold standard, **resume that one** instead of selecting a new candidate. Refresh the roadmap. *(One plugin at a time, carried across runs — depth taken to completion.)*
   - **If NO candidate clears the bar:** **build nothing new.** This is the expected steady state for a mature catalog. Instead, do at most one of, in priority order:
     1. **Real-demand upkeep** — deepen or correct an *existing* plugin **only if a real engagement exercised it** (the standing idea-board rule), or land a genuine accuracy/maintenance fix the run surfaced;
     2. **Roadmap hygiene** — refresh the roadmap doc to record "catalog saturated; no candidate cleared the value/criticality bar this cycle," carry forward the held candidates, and note the *next* signal that would unlock one.
   - **Never** scaffold a speculative plugin to have output. That contradicts the #409 parked-plugins decision and dilutes the catalog.
4. **"10" is not a quota — and neither is "build a batch."** The roadmap lists the candidates that **clear or near-clear** the bar (which may be 0, 1, or a handful), each with its score and the gate it fails if held — not a forced ten. A run **builds at most one** plugin (to gold standard); the rest of the list is a prioritized map, not a work order. Keep the held/again-considered candidates marked `held — <gate not met>` so the map stays complete.

---

## Notification discipline for this routine

This routine runs unattended; its egress is the notification channel. Apply the standing rule:

- **Built something** (a candidate cleared the bar) → notify with the PR + what shipped.
- **Found a real problem** (e.g. a main-breaking CI issue, like the two fixed in #502) → notify.
- **Nothing cleared the bar / steady-state no-op** → **stay silent.** "I ran and nothing warranted a new plugin" is not worth an interruption unless Matt asked for a heartbeat.

---

## Scope note — the literal schedule prompt

The recurring schedule still fires with a fixed task prompt (its text lives in the **environment/schedule config**, outside this repo — it cannot be edited from within a repo session). The routine self-governs by reading this policy on each run, so **this file is authoritative** where the two differ: even while the literal prompt still says "identify 10 new plugins," a run that has read this doc builds **one plugin to gold standard**, not ten to the minimum.

**Drop-in replacement for the literal schedule prompt** (paste into the Claude Code web schedule config to make the prompt match this policy):

> Read `docs/plugin-discovery-routine-policy.md` first. Select the single highest-priority unbuilt plugin candidate that clears the Value/Criticality bar (or resume the one a prior run left unfinished). Build exactly that ONE plugin, and loop — build → run all gates → self-review against the gold-standard bar → fix the top gap — until it is fully built out to gold standard and all gates are green. Then commit and open a PR. If no candidate clears the bar and none is in progress, build nothing (record the no-op in the roadmap) and stay silent. Never start a second plugin until the current one is gold-standard-complete and merged.

---

## Change log

- **2026-07-02** — **One plugin per run, built to GOLD STANDARD via an iterate-until-complete loop**, per Matt's directive. Selection (the Value/Criticality bar) is unchanged; the build *target* rises from "gate-passing minimum" to the new gold-standard bar (adds required advisory hook, ≥5 skills, ≥7 best-practices, ≥3 templates/commands, a calculator script where the domain has one, and a build→self-review→fix loop). A plugin is carried across runs until it reaches the bar; no new candidate is started until the current one is gold-standard-complete. Records the drop-in replacement for the literal schedule prompt. Context: the #543 batch of 10 was built to the *minimum* — that is now the floor, not the finish line.
- **2026-06-24** — Created. Adds the value/criticality bar + "build nothing if nothing clears" contract, per Matt's directive to stop manufacturing speculative candidates at a mature (119-plugin) catalog. Sharpens, and is consistent with, the #409 build-on-real-demand decision.
