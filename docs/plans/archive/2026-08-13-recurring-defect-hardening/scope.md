# G0 — Scope: recurring-defect hardening (full sweep · prevent + remediate)

## Scoped intent
Enumerate **every problem class this repo has hit repetitively since creation** — engineering, process,
product, and consumer-facing — from the repo's own densely self-documented record (CLAUDE.md milestones,
docs/, git/PR history, the gate harness, the Muninn/KB substrate). For each recurring class: its
occurrences (dated), root cause, the fix(es) already applied, and what is **still live/open**. Then design
a **hardening plan** that, per class, (a) **prevents recurrence** with a mechanism that has teeth (a gate,
hook, or convention the repo's own tooling enforces — because this repo's own lesson is "a prose rule with
no gate is a wish"), and (b) **remediates the existing live instances** still on the backlog. Iterate the
plan with a critique loop — **different model each pass, converges when 3 consecutive passes find no
issue** — then produce a **build plan** under the same iterate-to-3-clean criteria. DoD: the build plan is
complete and I surface the decisions the owner must make.

## G0 answers (owner, this session)
- **Breadth:** "Both — the full sweep" (engineering + process + product + consumer recurring classes).
- **Fix target:** "Prevent + remediate existing" (a preventive mechanism per class AND fix the live
  instances still open).

## Owner + success signal
- **Owner:** Matt.
- **Success signal:** a converged hardening plan + build plan that, for each recurring defect class, names
  a teeth-bearing prevention mechanism and a remediation of live instances — and a short decision list the
  owner answers to green-light the build.

## In scope
- All recurring engineering/process defect classes (seed set, to be verified + expanded by research):
  macOS stock-toolchain doors; hollow/never-ran/green-for-wrong-reason gates; stale-claims-in-loaded-files;
  self-referential guards denying their own fix; count/version-mirror drift + generated-artifact cascades;
  cross-surface placement/existence regressions; fail-open-where-fail-closed-intended; guardrails whose
  escape is unreachable → tunnelled; building to an unverified contract; fix-one-instance-and-stop;
  source-scan gates matching prose.
- Product/consumer/cross-host recurring classes: dashboard placement/UX regressions; install/onboarding
  friction; cross-host support gaps + projection drift (Copilot/Codex/Gemini).
- The **count-drift** class specifically already has a completed cross-model FORGE plan pair (reuse, do not
  re-derive): `../../../../forge-count-ssot/.ravenclaude/runs/forge/count-ssot/{plan-A.md,plan-B.md}` —
  note the A/B divergence on RC_BASELINE (de-hardcode-via-independent-scanner vs. keep-hardcoded).

## Out of scope
- Actually BUILDING the mechanisms this run (the DoD is the build plan + decisions, not the build).
- One-off bugs that occurred once and never recurred (this is about *repetitive* classes).
- Rewriting the repo's constitution wholesale — mechanisms attach to the existing gate/hook harness.

## Fast triage
Large, but deeply repo-specific (needs the repo's own milestone record + gate harness + KBs) and
privacy-clean. **Local FORGE, deep depth**, with the owner-specified iterate-to-3-clean critique loop and
model rotation. Lands as committed docs under `docs/plans/2026-08-13-recurring-defect-hardening/` (design
+ build plan → main per AGENTS.md docs-straight-to-main), plus a decision list surfaced to the owner.
Ultraplan considered and declined: the task hinges on the repo's own self-record + gate harness (not
cloud-general research) and on the custom rotate-models iterate-to-clean loop, which is FORGE's own
adversarial mechanism.
