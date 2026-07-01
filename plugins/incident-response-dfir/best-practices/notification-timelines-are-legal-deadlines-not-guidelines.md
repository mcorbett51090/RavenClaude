# Notification timelines are legal deadlines, not guidelines

**Status:** Absolute rule
**Domain:** Breach response / regulatory notification
**Applies to:** `incident-response-dfir`

---

## Why this exists

When a breach involves personal or regulated data, the notification clock is a **legal obligation with a hard deadline**, not a best-effort nicety. The GDPR requires notifying the supervisory authority "without undue delay and, where feasible, not later than **72 hours** after having become aware" of a personal-data breach (Art. 33) — and the clock starts at *awareness*, not at incident closure. Miss it and the organization faces regulatory penalties on top of the breach itself. Different regimes and sectors have their own, sometimes tighter, timers. Treating these as flexible guidelines is how an incident becomes a compliance failure.

## How to apply

The moment triage flags regulated/personal data in scope, start the notification clock at *awareness* and map the obligations: which regimes apply (GDPR, sector rules, contractual terms, breach-notification laws by jurisdiction), who must be told (supervisory authority, affected data subjects, partners, cyber-insurer), what must be reported, and by when. **Flag legal review** — the agent maps and tracks; counsel makes the call. Document when awareness began, because that timestamp defines the deadline.

**Do:**
- Start the clock at *awareness* and record the timestamp that defines the deadline.
- Map every applicable obligation (authority notice, data-subject notice, contractual, insurer) with its own timer.
- Flag legal/DPO review early — this is a legal determination, not an engineering one.

**Don't:**
- Treat the 72h (or tighter) window as advisory or as starting at incident closure.
- Decide unilaterally whether a breach is "reportable" — that's counsel's call; surface the facts.
- Delay notification analysis until the technical response is finished; run it in parallel.

## Edge cases / when the rule does NOT apply

- **No regulated/personal data in scope** → no statutory notification clock, though contractual/customer-comms obligations may still apply.
- **Encrypted data with keys not compromised** may reduce or remove some notification duties under some regimes — but that's a *legal* determination; surface it, don't assume it.
- **Timers vary by jurisdiction and sector** (some are shorter than 72h, some require earlier authority contact) — map the specific applicable regime; this rule is the discipline, not the exact number.

## See also
- [`../skills/triage-and-classify-an-incident/SKILL.md`](../skills/triage-and-classify-an-incident/SKILL.md)
- [`../skills/run-the-incident-lifecycle/SKILL.md`](../skills/run-the-incident-lifecycle/SKILL.md)
- [`../templates/incident-response-plan.md`](../templates/incident-response-plan.md)
- Regulatory obligation depth / audit → `cybersecurity-grc/compliance-auditor`.

## Provenance
GDPR Art. 33 (72-hour breach notification to the supervisory authority) and Art. 34 (notification to data subjects). Other regimes (US state breach laws, sector rules, contractual terms) carry their own timers — **this is not legal advice; flag counsel.** Last reviewed 2026-07-01.

---

_Last reviewed: 2026-07-01 by `claude`_
