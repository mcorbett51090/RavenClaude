---
name: run-covenant-and-collections-workflow
description: "Process a covenant violation, an architectural-review request, or a delinquent-assessment account by traversing the community-association decision tree (find the governing-document authority → for a violation: notice → cure period → hearing → fine/remedy, applied evenly and documented; for ARC: application vs the design guidelines → decision → record; for collections: reminder → late fee → demand notice → lien-referral / escalation-to-counsel gate), then return the processed decision, the due-process trail, and the escalation point. Reach for this when the user asks 'process this covenant violation', 'review this architectural change request', 'work our delinquency list', 'can we fine / lien this owner?', or 'what's our collections sequence?'. Even-handed, documented process is the whole point; lien/foreclosure mechanics route to counsel. Used by community-operations-specialist (primary) and association-management-lead (policy)."
---

# Skill: run-covenant-and-collections-workflow

> **Invoked by:** `community-operations-specialist` (primary — processing violations, ARC requests, and delinquency) and `association-management-lead` (setting the enforcement and collections **policy** the specialist runs).
>
> **When to invoke:** "process this covenant violation"; "review this architectural-change (ARC) request"; "work our delinquency / collections list"; "can we fine this owner?"; "when do we lien a delinquent account?"; "write our enforcement / collections policy"; any "how do we enforce or collect" question.
>
> **Output:** the processed decision (violation outcome, ARC approval/denial, or collections step) + the even-handed **due-process trail** documented for the file + the **escalation-to-counsel** point + the 1-2 conditions that change it. **Even-handed, documented process is the whole point.**

## Procedure

1. **Find the authority in the governing documents — you enforce what they grant.** For any enforcement or collection step, locate the **CC&R / bylaw** provision (and the state act) that authorizes it: the covenant being enforced, the **fine schedule** and the required **hearing**, the ARC's design-review authority, the **late-fee** amount, and the **assessment-lien** right. Traverse the enforcement/collections branches in [`../../knowledge/hoa-community-association-decision-tree.md`](../../knowledge/hoa-community-association-decision-tree.md). No documented authority → no enforcement.
2. **Enforce evenly — selective enforcement is the trap.** Whatever the process, apply it the **same way to every owner**. A covenant enforced against one owner but not the neighbor, or a fine levied without the required hearing, is how associations lose in court (and can waive the covenant). Consistency and documentation are the shield, not an option.
3. **Run the violation sequence — notice → cure → hearing → fine/remedy — and document each step.**
   - **Notice:** a written violation notice identifying the covenant, the specific violation, and the **cure period**.
   - **Cure period:** the owner's opportunity to fix it; log whether they did.
   - **Hearing:** if unresolved, the owner's **opportunity to be heard** before the board (due process — often required before a fine).
   - **Fine / remedy:** the fine per the schedule, self-help/abatement where authorized, or (for serious/continuing violations) referral to counsel. Record the evidence (photos, dates, correspondence) at every step.
4. **Process an architectural-review (ARC) request against the published guidelines.** Log the application, measure it against the **design guidelines/standards**, apply the **decision within any required timeframe** (an un-acted request can be deemed approved in some regimes — watch the clock), and record the **decision with its rationale**. Approve/deny **consistently** — an arbitrary or undocumented ARC denial is a lawsuit magnet.
5. **Work the delinquency list by the collections sequence — evenly, to the escalation gate.** Apply the board's collections policy step by step to **every** delinquent account: **payment reminder → late fee (per the schedule) → demand/intent-to-lien notice → the lien-referral / escalation-to-counsel gate**. Age the receivables, apply payments per the governing-document/statutory **payment-application** order (often oldest-first — verify), and **stop at the legal line**: recording a **lien**, foreclosing, and the **fair-housing / FDCPA / state-collection** rules are **counsel's** terrain, not yours to advise as legal steps.
6. **Escalate the policy and legal calls — don't improvise them.** A borderline enforcement decision, a request to waive a covenant, or a decision *whether* to lien/foreclose is a **board/lead policy call**; the lien/foreclosure **mechanics** and any statute question are **counsel's**. Process the workflow; route the decision.
7. **State the change conditions** — the 1-2 facts that change the outcome (e.g., "if the covenant hasn't been enforced against others, enforcing it now risks a selective-enforcement / waiver defense — flag to counsel"; "if the account crosses the lien threshold, it leaves the workflow for counsel").

## Worked example

> User: "A homeowner built a shed without ARC approval and is also 90 days behind on assessments. Process both."

- **Authority:** the CC&Rs require ARC approval for outbuildings and set a fine schedule with a hearing; the declaration grants a late fee and an assessment lien after 90 days — cite both.
- **Violation (shed):** issue the **notice** (unapproved structure, cite the covenant, give a cure period to submit an ARC application or remove it) → if uncured, offer the **hearing** → then the **fine/remedy** per the schedule. Document photos and dates. *Check first:* have other unapproved sheds been let slide? If so, flag the **selective-enforcement** risk to counsel before fining.
- **ARC path:** if the owner applies retroactively, measure the shed against the design guidelines and decide **consistently** with prior shed decisions; record the rationale.
- **Delinquency (90 days):** apply the sequence already run — reminder, late fee, **demand/intent-to-lien notice** — and note the account is **at the lien-referral gate**. Recording the lien and any foreclosure is **counsel's** step; route it with the aging and the notice trail.
- **Change condition:** if the owner cures the assessment balance, the account leaves the collections track; the ARC/violation matter continues on its own process.

## Guardrails

- **Enforce and collect evenly** — selective enforcement (or a fine without the required hearing) can waive the covenant and lose in court; consistency is the whole protection.
- **Find the governing-document / statutory authority for every step** — the covenant, the fine schedule + hearing, the late fee, the lien right. No authority → no step.
- **Document the due-process trail** — notice, cure period, hearing opportunity, decision, evidence — a violation or ARC decision that isn't in the file barely happened.
- **Watch the ARC clock** — an un-acted architectural request can be deemed approved in some regimes; decide within the timeframe.
- **Stop at the legal line** — recording a lien, foreclosure, and the **fair-housing / FDCPA / state-collection** rules are **counsel's**; process the workflow, route the legal decision. This is **not legal advice**.
- The enforcement/collections **policy** is the `association-management-lead`'s call; running it evenly is the `community-operations-specialist`'s — keep the seam clean.
- Volatile specifics (fine/hearing requirements, ARC deemed-approval timeframes, lien priority & procedure, payment-application order, FDCPA/fair-housing/state-collection rules) are **jurisdiction-specific** — carry a **retrieval date**, verify at use, and route to counsel. See [`../../knowledge/hoa-community-association-patterns-2026.md`](../../knowledge/hoa-community-association-patterns-2026.md).
