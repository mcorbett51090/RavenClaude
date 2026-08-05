# FORGE specialist-dispatch A/B — does a domain specialist out-red-team the generic worker?

**Date:** 2026-07-16 · **Decides:** whether to build the deferred "real specialist `agentType` dispatch" at FORGE's G4b/G5 gates. See the deferral note in `plugins/ravenclaude-core/skills/forge-pipeline/reference/gates-standard.md` ("Domain-prior lens").

## Why this exists

The v0.202.0 FORGE self-improvement run (PR #699) shipped a **domain-prior lens** — inject a domain-concern prior into the *generic* gate worker — and **deferred** dispatching a real domain specialist (`security-engineering:threat-modeler` at G5, `database-engineering:schema-architect` at G4b, …), gated on three preconditions. The first: **an observed FORGE run where a generic gate underperformed a specialist.** Per the repo's F7 discipline (don't build on hypothetical failure), this A/B tests precondition #1 head-on.

## Method (controlled + blind)

- **One fixed input:** a realistic, security-dense-*but-neutral* implementation plan on the maintainer's actual stack (Next.js + Supabase) — an authenticated document-upload + public share-link feature with genuine *unstated* security gaps. The plan deliberately does **not** pre-list threats (that would rig it toward the specialist).
- **Two arms, identical brief, same model (Opus), same output contract** (≥5 reproducible failure modes, each trigger/severity/mitigation). The **only** variable is the `agentType`:
  - **Arm A** = `general-purpose` — FORGE's status-quo generic G5 worker.
  - **Arm B** = `security-engineering:threat-modeler` — the specialist.
  - Neither arm was told it was being compared.
- **Blind judge:** a third Opus agent scored both reviews under neutral filenames (no idea which was which), on **objective** criteria — distinct HIGH-severity threat *classes* per arm, classes *unique* to each, and whether either missed a real HIGH gap — then applied a **pre-committed** rubric: `structural` (one arm finds ≥1 HIGH class the other misses) vs `marginal` (same HIGH coverage; differences only in depth/structure/low-severity).

## Result: `marginal`

| | Generic (Opus) | Specialist `threat-modeler` (Opus) |
|---|---|---|
| Distinct HIGH-severity classes | 5 | 5 |
| **HIGH classes the OTHER missed** | **0** | **0** |

Both arms independently found the **same six underlying HIGH-severity gaps**: IDOR/enumeration (sequential `bigint` share id on an unauth read route), stored-XSS from the app's own origin (unvalidated content served inline), upload-auth-missing (service-role open file drop), userId/tenancy spoofing (provenance unspecified), path-traversal/overwrite (raw filename as storage key), and the RLS cross-tenant metadata leak. `unique_to_one: []`, `unique_to_two: []`.

**The specialist's only advantages were marginal:** slightly better severity *calibration* (it rated the RLS leak HIGH where the generic had it MEDIUM), STRIDE tagging + trust-boundary framing, and a couple of *lower*-severity extras (header-injection LOW; a proxied-stream egress-DoS item). Tellingly, **both arms missed the same real gap** (CSRF on the cookie-auth upload) — so the specialist wasn't even systematically more complete.

## Decision: do **not** build real specialist dispatch

Precondition #1 — "an observed FORGE run where a generic gate underperformed a specialist" — **empirically does not hold** on this workload. On a deliberately security-dense plan, the generic Opus G5 worker found every HIGH-severity class the `threat-modeler` found. The ~5-item build (roster-availability check, a referential-integrity CI gate, the §0 heredoc advance-assert / FM2 fork, the schema-override brief, the deterministic classifier) is **not justified** by a marginal gain. The deferral in `gates-standard.md` stands — now backed by data, not priors.

The one thing the specialist adds — domain-concern framing + calibration — is **exactly what the shipped inject-prior lens already delivers**, without any dispatch machinery. FORGE's own G4a critic + G5 red-team reached this during the v0.202.0 run; this A/B confirms it empirically.

## Caveats (so the evidence isn't over-read)

- **One run per arm.** But the finding is *qualitative* (identical HIGH-class coverage, zero unique high-sev on either side), not a close count that noise could flip — a real structural advantage should have surfaced ≥1 unique HIGH class on a plan this dense, and it surfaced none.
- **Both arms on Opus** (the strongest generalist, and what FORGE's G5 uses at `xhigh`). A weaker G5 model *might* widen the specialist's edge — but FORGE doesn't run its adversarial gate on a weak model, so Opus-both is the representative test.

## To revisit

Re-run the A/B with (a) more reps per arm, and/or (b) a weaker G5 model, and/or (c) a different domain (e.g. a schema-fork tiebreak vs `database-engineering:schema-architect`, the *other* "cleanest-fit" candidate). Raw artifacts (the fixed plan, both red-teams, the blind verdict) were produced in an ephemeral session scratchpad on 2026-07-16; this document is the durable record.
