---
description: "Craft honest candidate materials (resume / LinkedIn Experience / About / cover / recruiter pack) as DIGEST + paste paths. No invented metrics; Raven/current role present tense; CoS does not own prose."
argument-hint: "[artifact: resume|linkedin-experience|linkedin-about|cover-letter|recruiter-pack] [optional: target role / JD path / evidence dir]"
---

# Craft candidate materials

You are running `/people-operations-hr:craft-candidate-materials` for `$ARGUMENTS`.

Follow [`../skills/craft-candidate-materials/SKILL.md`](../skills/craft-candidate-materials/SKILL.md) exactly — thin candidate-side packaging, not employer TA / not staffing-operations.

## Steps (do not skip)
1. Parse artifact type + evidence paths + target from `$ARGUMENTS` (default evidence: `/workspace/cli-out/resume-cursor-da-user-ops/`).
2. Read sources; list NEED-INPUT gaps — never invent metrics/%/$.
3. Draft paste pack under `/workspace/cli-out/` (blank line between every LinkedIn Experience bullet).
4. If artifact is linkedin-about (or pack includes About/Summary): run **About QA A1–A8** (and Summary QA) from SKILL.md — READY only if all PASS.
5. Write DIGEST with the skill schema (include About QA lines); READY only when paste-safe.
5. Return ≤~2k summary + absolute paths (People Ops → CoS). Raven/current role present tense; past roles past.

## Guardrails
- No fabrication; no BMA identity on fleet/PR packaging; no LinkedIn/apply push.
- Do not invoke `staffing-operations` or employer-side talent-acquisition funnel skills for this.
- CoS does not draft — if asked to draft inline in CoS chat, refuse and point here.
