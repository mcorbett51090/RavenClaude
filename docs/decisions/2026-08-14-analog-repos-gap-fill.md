# Decision record — analog-repos gap fill (survey close-out)

**Date:** 2026-08-14 · **Owner:** Matt · **Method:** `/forge --depth standard` then `/forge keep going` (P5–P10)  
**Plugin version:** unchanged (`ravenclaude-core` **0.265.0** on `main`). F1/F2 are queued PRs, not this commit.

## 0. Status (authoritative)

- **Survey completed.** Verified set **N=13** (cap 30; shortfall 17). Dated catalog + C01–C15 matrix published under `docs/plans/2026-08-14-analog-repos-gap-fill/`.
- **Fill slots:** F1 hook in flight ([#928](https://github.com/mcorbett51090/RavenClaude/pull/928), CONFLICTING). F2 evals in flight ([#929](https://github.com/mcorbett51090/RavenClaude/pull/929), required checks SUCCESS). F3 = this docs promote (no hook/skill/agent).
- **No silent drops** vs P2 row ids L1–L5. Residuals tagged.
- **No weekly 5/30 refresh** of analog READMEs (FM-10). Re-rank only if Claude Code’s plugin-marketplace format changes, or on owner request.

## 1. Context — the lens

G0 asked for 30 gold-standard **product analogs** of RavenClaude, then fill every closeable gap. That is a different question from:

1. the protocol-30 in `plugins/ravenclaude-core/knowledge/github-gold-standard-repos.md`
2. the operator-7 corpus in `docs/decisions/2026-08-13-agent-github-operator-gap.md`
3. the domain-plugin roster in `docs/plugin-candidates-2026-07-08.md`

The fill generator is **already-visible local known-bads** (T3). Analogs attest. They do not mint `closeable`.

## 2. What this increment shipped

| Phase | Ships | Closes |
|---|---|---|
| P0–P2 | Closeable Test + gap register (run tier) | schema / tags |
| P3 | F1 WebFetch sanitizer | L1 — **QUEUED** #928 |
| P4 | F2 injection + minting evals | L2/L3 — **QUEUED** #929 |
| P5–P7 | Harvest 129 → verified 13 + matrix | claim 9 |
| P8–P9 | Families tagged; queue | claim 12 |
| P10 / F3 | This record + catalog/matrix/queue in `docs/` | survey landing |

## 3. Tiebreaks (do not reopen)

| ID | Verdict | Meaning |
|---|---|---|
| T1 | synthesis | Catalog **and** C01–C15 matrix. 30 is a harvest cap. |
| T2 | A | ≤3 fill PRs. Remainder queued. |
| T3 | visible-defects-first | Local judged holes first. Analog path is optional attestation. |

Critic/red-team: `.ravenclaude/runs/forge/analog-repos-gap-fill/{critic-brief,red-team}.md`. FM-1–FM-5 absorbed in the plan.

## 4. Re-measured gap table

| # | Gap | Status |
|---|---|---|
| L1 | WebFetch result unsanitized | **QUEUED** — #928 (rebase: branch CONFLICTING / 1 behind main) |
| L2 | Zero injection eval cases on HEAD | **QUEUED** — #929 (required checks green) |
| L3 | README cannot mint closeable | **QUEUED** — #929 |
| L4 | MCP result quarantine | **accepted-limit** — product-shaped default change |
| L5 | Operator-7 as product rows | **out-of-lens** — evidence-sample only |
| F-C02-hosts | wshobson extra hosts | **accepted-limit** — new host = product |
| F-C13-rubric | jeremylongshore 8-field rubric | **already** — our frontmatter + claims gates |
| F-C14-site | Hosted public catalog | **accepted-limit** — hosted site is a product |
| F-C08-ci | Analog CI badges | **already** / protocol-30 |
| F-C09-dir | `evals/` listing costume | **already** — F2 is the judged form |
| F-scorecard | Closeness skill | **QUEUED** — later forge; surface budget |
| F-loop | Ralph autonomous loop | **accepted-limit** — product |

## 5. Deferred (with reasons)

- **MCP `updatedToolOutput` matcher (L4 / Q1)** — product-shaped; needs its own House Rule 3 walkthrough after F1 lands.
- **Closeness scorecard skill (Q2)** — counted skill class; this run’s one class was the hook.
- **Knowledge-file promote of the 13-row table** — optional S0 skipped. `docs/plans/` is enough; a plugin knowledge file would force a version bump for no consumer-visible behavior.
- **Aperion Shield / MCP Governance as catalog rows** — slugs found (`AperionAI/shield-langflow`; no single MCP-governance canonical). Adjacent security sidecars, not marketplace analogs.
- **SBOM/provenance** — still deferred at v0.246.0; not re-opened.
- **Weekly analog-README sweep** — deleted (FM-10).

## 6. House Rule 3 walkthrough

Simulated `/plugin marketplace update` after **this** commit: nothing fires. Catalog, matrix, queue, and this record are docs. They are dormant until a human or agent reads them. No hook, no skill, no agent, no `RC_BASELINE` change, no installer change.

F1 (when rebased and merged) **does** rewrite every consumer WebFetch result. That walkthrough lives on #928, not here. Fail-open is the default-break mitigator.

## 7. Claim 9 / survey honesty

| claim | final status |
|---|---|
| 3 (four marketplaces) | settled — three verified; composio dropped as clone-cut |
| 4 (`wshobson/agents`) | settled `[obs]` — multi-host projector; extra hosts accepted-limit |
| 5 (OpenCode) | settled `[obs]` — adjacent full harness; **not** a catalog row |
| 9 (30 not verified at G1) | **verified set N=13 on 2026-08-14** |
| 6 / 7 / 12 | still owner-gated; implemented as CT + ≤3 fills + tags |

## 8. Provenance

FORGE artifacts live under `.ravenclaude/runs/forge/analog-repos-gap-fill/` (gitignored). Survey bodies were fetched with `gh api` only (F1 unmerged → FM-1 option b). No analog repo was cloned. No analog code was executed.
