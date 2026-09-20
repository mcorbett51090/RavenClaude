---
name: craft-candidate-materials
description: >-
  Craft honest candidate materials — resume, LinkedIn Experience, LinkedIn About,
  cover letter, recruiter paste pack — as DIGEST + paste paths under /workspace.
  Reach for this when packaging Matthew (or fleet user) for a role; never invent
  metrics; Raven/current role present tense only; CoS does not own prose.
---

# Skill: Craft candidate materials

Thin contract skill for **candidate-side** packaging (resume / LinkedIn / cover / recruiter pack).  
Not a hiring-system skill — do **not** substitute `model-hiring-plan` or employer-side `talent-acquisition-strategist` funnel work.  
Not `staffing-operations` (B2B staffing KPIs).

## When to use
- Resume rewrite or role-targeted variant
- LinkedIn Experience bullets / About
- Cover letter or recruiter paste pack
- CoS tipped People Ops for talent materials (HARD gate)

## When NOT to use
- Org hiring plan, attrition, comp bands, pay equity → other people-operations-hr skills
- Staffing-firm fill-rate / desk capacity → `staffing-operations` (different plugin; never for personal materials)
- CoS inline draft — reject; this skill owns craft; CoS = 6-field tip + computerUse after READY

## Inputs (require)
1. **Artifact type:** `resume` | `linkedin-experience` | `linkedin-about` | `cover-letter` | `recruiter-pack`
2. **Evidence paths** under `/workspace` (resume SSOT, prior packs, JD if any)
3. **Target** (optional): role / company / JD path
4. **Locks** from CoS tip (must include no-invent-metrics)

Default evidence home (Matthew): `/workspace/cli-out/resume-cursor-da-user-ops/`

## Hard locks
- **No fabrication** — no invented metrics, %, $, headcount, CSAT/SLA, or unverified tools
- **Tense:** Raven / current role = **present**; prior employers = past
- **Identity:** no BMA / `mcorbett@bma.bm` on fleet, PRs, CODEOWNERS, or packaging
- **No push** — write paste packs + browser notes only; LinkedIn/apply = CoS computerUse after READY
- **No staffing-operations** invoke for this craft
- **No employer-side TA strategist** roleplay for candidate packaging
- **Resume structure HARD:** pitch-line Summary + importance-ordered Experience + Skills section (see below) — standing Matthew default


## Resume structure HARD defaults (Matthew STANDING 2026-09-20)

These are **not optional**. Every `resume` and every `recruiter-pack` that includes a resume MUST ship all three. Target packs (Cursor DA vs Power Platform, etc.) may **reorder** bullets/skills for the JD — they must **never drop** pitch Summary, importance order, or Skills.

### 1) Pitch-line Summary (HARD)
- One tight pitch (prefer **1–2 sentences**, ~≤220 chars for the lead clause) that answers: **what you build / for whom / proof shape** — scannable in 6 seconds.
- **Not** an essay stack of every tool. Detail lives in Experience.
- **Agentic AI variety = major highlight (HARD):** pitch MUST name agentic / multi-agent delivery as a primary highlight (e.g. Cursor/Claude/Grok orchestration, software-factory / specialist-bot shipping) — **not** a Power BI/Fabric-only summary. BI/Fabric/SQL may appear as proof craft, but must not crowd out agentic AI as a headline identity. Target packs may lead with JD craft (e.g. Cursor DA ops-reporting) **while keeping agentic AI visible as a major beat** — never erase it for a BI-only pitch.
- Target packs retarget the pitch to the JD (e.g. ops-reporting vs PP factory) without inventing claims.
- Run **Resume Summary QA** (A1/A3–A6) before READY; DIGEST must note `Pitch Summary: PASS|FAIL` and `Pitch agentic highlight: PASS|FAIL`.

### 2) Importance-ordered Experience bullets (HARD)
- Within each role, bullets are ordered **most important / most JD-relevant first** (ownership, production dependency, primary craft) → supporting → tooling last.
- Target packs reorder for the JD (e.g. Cursor DA: SQL/ops-reporting/DQ before agent stack; PP pack: Dataverse/Apps before orchestration).
- Do **not** bury the ownership signal in bullet 4+. ATS checklist “first bullet carries ownership” remains in force.
- DIGEST: `Experience order: importance-sorted for <target|general> — PASS|FAIL`.

### 3) Skills section (HARD)
- Resume **always** includes a Skills section (never omit).
- Order skills by **importance to the target** (or general default: primary craft → platforms → data → orchestration last when agentic is supporting).
- Only evidenced skills; no stuffing.
- DIGEST: `Skills: present + importance-ordered — PASS|FAIL`.

READY forbidden if any of Pitch Summary / Pitch agentic highlight / Experience order / Skills FAIL.

## Steps
1. **Read evidence first** — resume SSOT + prior DIGESTs/packs + tipped JD; list gaps as NEED-INPUT, do not fill with fiction.
2. **Choose artifact + voice** — scannable bullets; blank line between LinkedIn Experience bullets; About = short first-person honest. **If About/Summary: run About QA checklist before READY.**
3. **If resume/recruiter-pack:** enforce **pitch-line Summary + importance-ordered Experience + Skills** (HARD defaults). Target may reorder for JD; never omit.
4. **Draft paste pack** under `/workspace/cli-out/...` (prefer evidence folder).
5. **Write DIGEST** with schema below; Status=READY only if paste pack is CoS-paste-safe **and** structure HARD gates PASS.
6. **Return condensed summary + absolute paths** to People Ops → CoS (≤~2k).


## LinkedIn About QA checklist (P0 — HARD before READY)

Matthew LOCK 2026-09-20: About often “feels off.” **Do not mark `linkedin-about` (or recruiter-pack that includes About) READY until every row PASS or explicit NEED-INPUT.**

Run this checklist on every About draft (and on resume **Summary** when present — same gates, shorter).

| # | Gate | PASS if | FAIL → |
|---|------|---------|--------|
| A1 | **Recruiter 6-second scan** | First 2 sentences answer who / what domain / for whom without decoding jargon | Rewrite lead; move stack/tools later |
| A2 | **Length** | ~1,200–2,000 characters paste body preferred; hard ceiling ~2,600 (LinkedIn). Prefer 3–5 short paragraphs over one wall | Split paragraphs; cut filler |
| A3 | **Tense** | Current Raven / consulting = present; prior employers = past; no mixed tense in one clause | Fix tense |
| A4 | **Agentic vs Power Platform balance** | PP / Dataverse / Apps / Automate / BI / SQL / Fabric / stakeholder analytics visible in lead or para 2 — not buried after agent fleet lore. Agentic/Cursor/Claude/Grok = supporting orchestration, not the whole identity | Rebalance: PP craft first or equal; thin agent layer second |
| A5 | **No wall-of-jargon** | No dense dash/em-dash stacks of product names; no fleet codenames (Thing/Runes/Sage/etc.); max ~1 novel term per sentence; a hiring manager outside AI-agent Twitter can parse | Plain-language rewrite; kill codenames |
| A6 | **No fabrication** | Every tool/employer/scope claim has an evidence span in resume SSOT or tipped sources | Drop claim or NEED-INPUT |
| A7 | **Voice** | First person continuous prose; no bullets in About; no resume-speak third person | Fix voice |
| A8 | **Close** | Ends with clear present role + honest prior arc (no brag metrics) | Add/trim close |

DIGEST must include:
```text
About QA: A1..A8 PASS|FAIL (one line each) — overall PASS required for READY
```
If any FAIL → Status=NEED-INPUT or keep drafting; never READY.


## Fit ledger (per-role; before READY tailored materials)

Claim-by-claim map — never keyword-overlap alone (Research 2026-09-20):

```text
JD must/nice/red-flag → evidence span in SSOT | NULL
Status per claim: SUPPORTED | GAP | NEED-INPUT | INFERRED (≠ supported for READY)
```

READY tailored resume/cover only if every must-have is SUPPORTED or explicit NEED-INPUT listed for Matthew. Do not invent Fabric/ADF/metric ownership.

## Cover letter WRITE | SKIP

| WRITE when | SKIP when |
|------------|-----------|
| Required by posting; pivot/gap/title mismatch; senior/mission/small-co tie-break | Optional + strong resume match; high-volume one-click; would only emit boilerplate |

Structure if WRITE: why-here → 1–2 evidenced proofs → answer resume question → short close. No metrics absent from SSOT.

## ATS checklist (resume)

- [ ] Single-column; standard headings (Summary/Experience/Education/Skills)
- [ ] Contact in body; no tables/graphics/multi-column
- [ ] Mirror JD hard skills **only when evidenced**; no stuffing
- [ ] Current role present tense; prior past
- [ ] First bullet of latest role carries ownership signal

## About craft addenda (Research + Matthew P0)

In addition to About QA A1–A8:
- **A1b Preview fold:** first ~200–300 chars stand alone before LinkedIn “see more”
- **A1c Hook:** open with specific value/POV/problem — not “Hi I’m…” / title restatement (headline already has title)
- Dual-track (AI/Product Eng ↔ Power Platform/data): frame honestly; do not claim both as deep primary without SSOT

## Resume Summary QA
Apply A1, A3, A4, A5, A6 (length: 3–5 lines). Same DIGEST line: `Summary QA: …`

## Output schema (DIGEST)
```text
Status: READY | NEED-INPUT | BLOCKED
Artifact type: resume | linkedin-experience | linkedin-about | cover-letter | recruiter-pack
Paste pack path(s): /workspace/...
DIGEST path: /workspace/.../DIGEST-...
Sources used: (files + dates)
Verdict: YES-as-is | IMPROVE | REWRITE
Honesty locks held: no invented metrics/%/$; tense OK; no BMA on fleet packaging
About QA: A1..A8 PASS|FAIL (required when artifact includes About)
Summary QA: A1/A3–A6 PASS|FAIL (when resume Summary touched)
Pitch Summary: PASS|FAIL (required on resume / recruiter-pack)
Pitch agentic highlight: PASS|FAIL (agentic AI variety major — not BI/Fabric-only)
Experience order: importance-sorted for <target|general> — PASS|FAIL
Skills: present + importance-ordered — PASS|FAIL
Diff summary: (3–7 bullets)
Browser/Auth notes: (field order / blank-line paste — CoS only)
Non-claims: People Ops does not push LinkedIn/apply
Confidence: High|Med|Low — falsifier: ...
```

## Owner
People Ops runs this skill (Claude Max). Prompt Engineer crafts/amends the pack. CoS never drafts.
