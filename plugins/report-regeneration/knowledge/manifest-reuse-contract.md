# Manifest reuse contract — `report-regeneration`

**Status:** knowledge-bank deliverable (plan §9 — "manifest-reuse/recurrence contract (RT2-F7)"). Reference only — the manifest's shape and its role in the taxonomy live in [`core-architecture-spec.md`](core-architecture-spec.md) §3; this document does not restate the schema, it explains **the run-1-vs-run-2 contract that makes the manifest a first-class product rather than a per-run scratch file.**

**This document states a binding design contract, not a shipped feature.** As of this writing, `manifest_version` / `rsg_schema_version` / `template_id` exist in the schema and `build_manifest.py` stamps `manifest_version` on every run (verified this session). The **reuse/amend workflow** (loading a prior manifest as run-2's starting point, restricting human review to the delta) and the **feedback-instrumentation loop** (§5) are Phase-1 and Phase-0-setup deliverables respectively — not yet built in this codebase (`BUILD-STATE.md`'s "Next" list: "Manifest-dividend measurement (run-1 vs run-2 human-review time)" is still outstanding). Where this document describes behavior, it describes what the architecture requires the future implementation to do, marked as such.

---

## 1. The manifest is the product, not the inference

> **The manifest — not per-run inference — is the product.** On run 2 of a recurring template the manifest is reused and amended, so human-review cost falls (the "manifest dividend"). — `core-architecture-spec.md` §3

This inverts the naive framing of "an AI that regenerates reports." The plugin's durable output for a recurring client relationship is not "a script that infers structure well" — inference is cheap, re-runs every time, and is bounded by the 85–95% ceiling (see [`inference-failure-modes.md`](inference-failure-modes.md)). The durable output is **a versioned, human-reviewed Binding Manifest keyed to that specific template**, which gets cheaper to maintain, not re-derived from scratch, on every subsequent report of the same shape.

---

## 2. Run-1 vs run-2 mechanics (the dividend)

| | Run 1 (new template) | Run 2+ (recurring template, new period's data) |
|---|---|---|
| **Manifest origin** | Inference *proposes* a manifest from scratch; a human reviews and amends **every** binding | The **prior manifest for this `template_id` is reused as the starting point** and amended — not rebuilt |
| **Human-review scope** | The whole document | Only the delta: nodes the current run's deterministic checks disagree with, nodes whose confidence dropped, and any node newly introduced by a template edit since the manifest was built (see §4) |
| **`manifest_version`** | Stamped at `0.1.0` (or the caller's chosen starting semver) | **Bumped on every amendment** — `binding-manifest.schema.json`: "Semver of this manifest instance, bumped on every amendment. Versioning makes the manifest an auditable deliverable across recurring runs of the same template." |
| **Match key** | — | `template_id` — the RSG's `template_id` and the manifest's `template_id` are the same field, explicitly so "a cached manifest can be reused for a recurring template" (`rsg.schema.json`, `binding-manifest.schema.json`) |

**The measurable claim (binding — RT2-F7, plan §5 Phase 1):** measure **human-review minutes on run-1 vs run-2 of the same template with new data**; stated break-even target, e.g. run-2 human time **< 20%** of a hand-rebuild estimate. **If run-2 isn't cheap, the product premise has failed** — this is surfaced at the Phase-1 bet gate, not softened. As of this document, that measurement has not yet run (`BUILD-STATE.md` "Next" list, item 2).

**Named scope limit (R20 residual, plan §11):** "one-shot retargeting supported but explicitly not the value case." A template used exactly once still works — the pipeline doesn't require recurrence to function — but the manifest-dividend value proposition is specifically about **recurring** templates. State this assumption plainly to anyone evaluating the product's economics.

---

## 3. Versioning — what each field means and when it moves

| Field | Lives on | Meaning | Moves on |
|---|---|---|---|
| **`manifest_version`** | Binding Manifest | Semver of this manifest *instance* | Every human amendment (content change: a binding's class, confidence, or `data_query` changed) |
| **`rsg_schema_version`** | Binding Manifest | The RSG **schema** version this manifest was built against | An RSG schema-shape change (new required field, new anchor kind, new node role — not a content change) |
| **`schema_version`** | RSG | Semver of the RSG schema itself | Same trigger as `rsg_schema_version` above — they must move together |
| **`template_id`** | Both RSG and manifest | Stable identity of the source template | Never — this is the invariant key that makes reuse *findable* across runs |

**Cross-phase serialization rule (binding — `core-architecture-spec.md` §7, plan line 169):** any RSG **or** manifest **schema** change (i.e. `schema_version` / `rsg_schema_version`, not a routine `manifest_version` content amendment) **serializes** and re-triggers the Phase-1 Bet-1 smoke test across **both** output formats. A schema change made while working on the HTML lane cannot silently break the Office lane. This is the coordination tax the single-manifest-schema architecture pays for sharing one harness across two output engines (RT2-F3) — priced and accepted, not accidental.

**The distinction that matters for reuse:** a `manifest_version` bump (routine amendment) is exactly what run-2 reuse produces, constantly, and is cheap. A `schema_version`/`rsg_schema_version` bump (structural) is rare, cross-phase, and expensive — it is not what "the manifest dividend" is about.

---

## 4. What reuse actually means — and what it never means

**Reuse is at the structure/class level, not the value level.** A binding's `anchor`, `class`, and the *shape* of its `data_query` (e.g. "this node is a DAX query against measure X") are what a human's prior review decision attaches to and what carries forward. The **value itself is always fresh, every run** — `data_query.source_ref` repoints to the new period's source (a new file, a new dataset, new query args), and the harness re-executes it. Reuse never means "reuse last quarter's number."

**Reuse never means skipping verification.** This is the point most worth stating explicitly, because a careless reading of "the manifest is reused" could imply the fidelity harness runs lighter on a repeat. It does not: **the six-leg harness + period-coherence runs in full on every single run, reused-manifest or not.** What reuse shrinks is the *human classifier-review* burden on the manifest-construction side — it does not, and must never, shrink the *verification* burden on the output side. The earned-frozen rule in particular is re-tested fresh every run: even a binding carried forward as `frozen` from a prior manifest version still gets checked against the current run's deterministic detector (data-shaped-literal / taint-dictionary / new-dataset-value-domain), because the new dataset's value domain is, definitionally, new every run and could in principle collide with what was safely inert chrome text last time.

**V6 doubles as the template-drift detector on manifest reuse.** If the underlying template itself changed between run-1 and run-2 (a new section added, a table column inserted), the reused manifest has no binding for the new anchor. V6's independent, non-ML scan of the *output* for value-shaped tokens not covered by any manifest binding catches exactly this — a value-shaped token introduced by a template edit since the manifest was last amended fails V6's coverage check, forcing human attention precisely at the drift point rather than at the whole re-reviewed document (`core-architecture-spec.md` §5).

---

## 5. The feedback-instrumentation loop (G0-d) — tuning the rubric, not just the manifest

**Status: contract only — not yet implemented.** This is a Phase-0-setup deliverable (G0-d) whose mechanism (capture → classify → route) has not been built in this codebase as of this document (no `feedback`/`substantive`/`mechanical` handling found in `skills/report-gold-standard-rubric/rubric.py` this session).

**What it replaces.** Peer review is a downstream **human** step; the plugin emits a review-ready draft only. G0-d **replaces the old secured-human-grader hard gate** (plan §5-P0): instead of a Phase-0 blocker requiring an in-plugin grader before any build could proceed, the plan stands up a mechanism that instruments the **client's real peer-review feedback per report** as the calibration signal.

**Mechanism (as designed, plan §5-P0 G0-d):**

```
client peer-reviews the draft
        │
        ▼
capture the reviewer's demanded edits
        │
        ▼
classify each edit: substantive  vs  mechanical/QA
        │
        ├──▶ substantive edits: genuine human judgment the
        │    plugin was never claiming to replace — logged,
        │    not fed back as "the plugin was wrong"
        │
        └──▶ mechanical/QA edits: exactly the class of thing
             auto-QA should have caught — routed back into:
             ├── the Binding Manifest for this template_id
             │   (the next run of the SAME recurring template
             │   starts from a manifest that already reflects
             │   this correction — compounding the run-1-vs-run-2
             │   dividend across run-2-vs-run-3, etc.)
             └── the report-gold-standard-rubric's bars
                 (tunes what "Accurate"/"Dynamic"/"Inclusive"/
                 "Polished" require, over successive real reports)
```

**The measured question, over successive real reports:** *does auto-QA leave the reviewer giving only substantive feedback?* A trend toward zero mechanical/QA-catchable feedback is the signal that the harness + manifest have absorbed everything machine-checkable for that template, leaving the reviewer only the judgment calls the plugin was never claiming to make.

**Why this is not a hard pre-build blocker.** The old branch — "no independent grader ⇒ descope/escalate" — is struck (plan R7/R23, both marked **RESOLVED (rev. 2)**). This is now an **ongoing calibration instrument**, accruing value over real reports, not a gate that has to pass before Phase 1 can start.

---

## 6. Cross-references

- Manifest schema, node taxonomy, the six-leg harness: [`core-architecture-spec.md`](core-architecture-spec.md) §3–§5.
- Why the classifier tail this loop is compensating for is real and unclosed: [`inference-failure-modes.md`](inference-failure-modes.md).
- The gold-standard rubric's four dimensions + loop mechanics that G0-d feeds: `skills/report-gold-standard-rubric/SKILL.md`.
- The schema files themselves: `rsg.schema.json`, `binding-manifest.schema.json`.
