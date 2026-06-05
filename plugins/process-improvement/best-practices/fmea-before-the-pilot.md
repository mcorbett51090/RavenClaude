# Run an FMEA Before the Pilot

**Status:** Pattern
**Domain:** Process Improvement — Improve phase
**Applies to:** `process-improvement`

---

## Why this exists

A pilot proves a fix works in a controlled slice. An FMEA (Failure Mode and Effects Analysis) prevents the pilot from *introducing* a new failure mode into that slice. Teams that skip the FMEA run a pilot that solves the original problem and simultaneously breaks something adjacent — then spend the next DMAIC project cleaning up the damage. The FMEA's RPN (Risk Priority Number) scoring directs mitigation budget to the failure modes with the highest blast radius before the pilot runs.

## How to apply

Run a process FMEA in the Improve phase, **after** the solution is designed and **before** the pilot is deployed.

**FMEA scoring table (one row per potential failure mode):**

| Process step | Potential failure mode | Effect on output | Severity (1–10) | Potential cause | Occurrence (1–10) | Current control | Detection (1–10) | RPN | Action |
|---|---|---|---|---|---|---|---|---|---|
| … | … | … | … | … | … | … | … | S×O×D | Mitigate if RPN > threshold |

**Standard RPN threshold for action:** RPN ≥ 100 (or the top 20% of RPNs if no value exceeds 100) — document the threshold in the charter before scoring so it isn't moved post-hoc.

**Steps:**
1. List every step in the *proposed improved* process (not the current state).
2. Brainstorm failure modes at each step (cross-functional team: people who run it, not just analysts).
3. Score Severity, Occurrence, Detection on a 1–10 scale using a pre-agreed rubric.
4. Identify all RPN values above the action threshold.
5. Assign a mitigation, an owner, and a due date for each high-RPN item before the pilot starts.

**Do:**
- Score against a written rubric anchored to the *customer's* experience of severity (scale 9–10 = safety/regulatory; 1–2 = barely noticeable).
- Re-score RPNs after mitigations are in place to confirm they dropped below the threshold.
- Retain the FMEA in the project record — it becomes part of the control plan's ongoing review.

**Don't:**
- Run the FMEA on the *current* process only (that tells you what's already failing, not what the new design might introduce).
- Let the team inflate detection scores ("we'll catch it in QC") without a specific, tested control.
- Treat high-RPN findings as reasons to cancel the pilot — they are exactly what the FMEA is designed to surface and mitigate.

## Edge cases / when the rule does NOT apply

- **Just-do-it actions:** the change is trivial and reversible — an FMEA adds more ceremony than the risk warrants. A quick "what could go wrong?" mental check suffices.
- **Kaizen events:** a compressed FMEA ("failure mode / impact / who would catch it" in a 30-minute team exercise) replaces the full table when time is genuinely constrained.

## See also

- [`../agents/lean-six-sigma-blackbelt.md`](../agents/lean-six-sigma-blackbelt.md) — the agent that facilitates the FMEA
- [`./pilot-before-you-roll-out.md`](./pilot-before-you-roll-out.md) — the rule that follows this one: what the FMEA-cleared pilot looks like

## Provenance

Standard Improve-phase practice in DMAIC (AIAG FMEA Manual 4th/5th edition; ASQ Body of Knowledge). RPN threshold convention is MoreSteam / iSixSigma standard practice `[unverified — training knowledge; confirm the specific threshold with the client's quality system before quoting]`. _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
