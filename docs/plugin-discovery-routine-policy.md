# Plugin-Discovery Routine — Value/Criticality Bar (governing policy)

> **Status:** 🟢 binding policy for the recurring "N new plugins" discovery routine.
> **Owner:** Matt. **Set:** 2026-06-24. **Supersedes** the literal scheduled-prompt framing ("identify 10 new plugins… build the highest-priority first") wherever they conflict, and **sharpens** the standing #409 *build-on-real-demand over catalog-breadth* decision (`docs/plugin-candidates-2026-06.md`, `docs/idea-board.md`).
>
> **Read this FIRST on every run of the discovery routine, before picking or building anything.**

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
   - **If ≥ 1 candidate clears the bar:** build the **single highest-priority one** to full gate-passing quality (the existing recipe), and refresh the roadmap. *(Still one per run — depth over breadth.)*
   - **If NO candidate clears the bar:** **build nothing new.** This is the expected steady state for a mature catalog. Instead, do at most one of, in priority order:
     1. **Real-demand upkeep** — deepen or correct an *existing* plugin **only if a real engagement exercised it** (the standing idea-board rule), or land a genuine accuracy/maintenance fix the run surfaced;
     2. **Roadmap hygiene** — refresh the roadmap doc to record "catalog saturated; no candidate cleared the value/criticality bar this cycle," carry forward the held candidates, and note the *next* signal that would unlock one.
   - **Never** scaffold a speculative plugin to have output. That contradicts the #409 parked-plugins decision and dilutes the catalog.
4. **"10" is not a quota.** The roadmap lists the candidates that **clear or near-clear** the bar (which may be 0, 1, or a handful), each with its score and the gate it fails if held — not a forced ten. Keep the held/again-considered candidates in the table marked `held — <gate not met>` so the map stays complete.

---

## Notification discipline for this routine

This routine runs unattended; its egress is the notification channel. Apply the standing rule:

- **Built something** (a candidate cleared the bar) → notify with the PR + what shipped.
- **Found a real problem** (e.g. a main-breaking CI issue, like the two fixed in #502) → notify.
- **Nothing cleared the bar / steady-state no-op** → **stay silent.** "I ran and nothing warranted a new plugin" is not worth an interruption unless Matt asked for a heartbeat.

---

## Scope note — the literal schedule prompt

The recurring schedule still fires with a fixed task prompt (its text lives in the **environment/schedule config**, outside this repo). The routine self-governs by reading this policy on each run, so **this file is authoritative** where the two differ. If Matt wants the literal prompt text updated to match (e.g. drop "10", say "only if it clears the value/criticality bar"), that edit is made in the schedule/environment config — this doc records the governing intent regardless.

---

## Change log

- **2026-06-24** — Created. Adds the value/criticality bar + "build nothing if nothing clears" contract, per Matt's directive to stop manufacturing speculative candidates at a mature (119-plugin) catalog. Sharpens, and is consistent with, the #409 build-on-real-demand decision.
