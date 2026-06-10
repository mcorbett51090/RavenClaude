---
name: technical-discovery
description: Run value-based technical discovery before any demo or POC — frame the deal with MEDDPICC, surface the prospect's pain and its quantified business impact, identify the decision criteria/process/champion, and capture it all in the discovery-notes template so the demo can be tailored to real pain. Reach for this when the user has (or just had) a discovery call, or is about to demo with no discovered pain. Used by `sales-engineer` (primary) and `poc-evaluation-lead`.
---

# Skill: technical-discovery

> **Invoked by:** `sales-engineer` (primary); `poc-evaluation-lead` re-runs it lightly to confirm the pain a POC must prove.
>
> **When to invoke:** "I have a discovery call coming up"; "we're about to demo but haven't really discovered"; "what should I be uncovering?"; any deal where the pain isn't yet named and quantified.
>
> **Output:** a MEDDPICC-framed discovery plan + the pain/metric/decision-criteria questions to ask, captured in [`../../templates/technical-discovery-notes.md`](../../templates/technical-discovery-notes.md).

## Procedure

1. **Frame the deal with MEDDPICC.** Walk [`../../knowledge/discovery-and-demo-playbook.md`](../../knowledge/discovery-and-demo-playbook.md): **M**etrics, **E**conomic buyer, **D**ecision criteria, **D**ecision process, **P**aper process, **I**dentify pain, **C**hampion, **C**ompetition. Mark which letters you already know and which are gaps — the gaps are your discovery agenda.
2. **Find the pain, then quantify it.** A pain with no business impact ("it's a bit slow") doesn't sell. Push to the **Metric**: what does the pain cost in time / money / risk / missed revenue, and who feels it? This is the number the demo and the business case hang on.
3. **Map the decision.** Who decides, against what criteria, by when, through what paper/procurement/security process? A technical win with no decision map stalls in procurement.
4. **Test for a champion, not just a contact.** A champion has power, has personal pain, and will sell for you internally. Distinguish champion vs coach vs blocker.
5. **Capture and confirm.** Write it into the discovery-notes template and reflect it back to the prospect ("so the critical issue is X, costing Y — did I get that right?"). Confirmed pain is the contract the demo is built against.

## Output

The filled discovery-notes template + the prioritized list of remaining MEDDPICC gaps + a one-line **critical business issue** statement the demo will be built to resolve. Hand off to `demo-design` only once pain is named and quantified.

## Anti-patterns this skill prevents

- Demoing into a vacuum (no discovered pain → a feature tour).
- A "pain" with no quantified business impact (nothing for the business case to stand on).
- Mistaking a friendly contact for a champion.
- Skipping the decision/paper process and getting ambushed by procurement or security late.
