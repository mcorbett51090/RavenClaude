# CBT readiness is a March checkpoint, not an April scramble

**Status:** Pattern
**Domain:** EdTech partner success (K-12)
**Applies to:** `edtech-partner-success`

---

## Why this exists

New York State mandated computer-based testing (CBT) for grades 3–8 ELA, Math, and Science in spring 2026 — the first full window was April–May 2026. Other states are on similar trajectories. Any platform used in K-12 testing windows (including platforms that integrate with the SIS, SSO, or rostering layer that the testing platform depends on) faces a readiness risk if the PSM has not run a checkpoint in March. A CBT failure during the testing window is a district-level crisis: it can trigger state-level escalations, produce community trust damage, and arrive at the PSM's inbox with no warning if the March cadence was skipped. Running the March checkpoint is cheaper than managing the April crisis.

## How to apply

Add a CBT readiness checkpoint to the Q3 (January–March) PSM cadence for any K-12 partner in a CBT-mandate state. The checkpoint has five components.

```
CBT readiness checkpoint — March (for NY and other CBT-mandate states):

  1. Device and bandwidth
     — Partner confirmed device inventory is sufficient for concurrent testing sessions?
     — Bandwidth confirmed adequate for peak concurrent load during the testing window?
     — If NO: escalate to partner IT and document in the partner profile.

  2. Rostering and SSO
     — All testing-eligible students have active, synced roster records?
     — SSO is confirmed working for the assessment platform AND for your product
       (SIS/SSO changes in January–March can silently break integrations)?
     — If NO: escalate to engineering + partner IT immediately.

  3. Vendor-side readiness
     — Vendor has confirmed no platform maintenance windows during the testing dates?
     — Testing-period status page is bookmarked and shared with the partner?

  4. Incident-response framing
     — Partner IT contact and escalation number are in the partner profile?
     — PSM has the vendor's incident-response playbook or SLA for testing-window issues?

  5. Communication
     — Partner admin has a written one-pager: what to do if a student can't log in
       during the testing window?
```

**Do:**
- Add the March CBT checkpoint to the standing Q3 cadence for all K-12 partners in CBT-mandate states.
- Document the checkpoint outcome in the partner profile with a date.
- Escalate any open rostering or SSO issue by March 15 — April fixes often don't make the testing window.

**Don't:**
- Wait for the partner to raise a CBT readiness concern — the PSM owns the proactive checkpoint.
- Skip the checkpoint because "we're not the testing vendor" — integration failures upstream of the testing platform are PSM territory.
- Assume last year's setup still works without a fresh verification in March.

## Edge cases / when the rule does NOT apply

Partners in states without a CBT mandate and partners in higher-ed or corporate L&D segments do not require this specific March checkpoint. The general principle — verify integration health before a high-stakes district event — applies broadly; the CBT content is specific to K-12 assessment windows.

## See also

- [`../agents/edtech-partner-success-manager.md`](../agents/edtech-partner-success-manager.md) — owns the Q3 cadence and adds the CBT checkpoint to the calendar.
- [`./rostering-sync-succeeded-is-not-the-same-claim-as-data-is-correct.md`](./rostering-sync-succeeded-is-not-the-same-claim-as-data-is-correct.md) — the companion rule on verifying rostering health, which is a CBT readiness dependency.

## Provenance

Grounded in the plugin's knowledge file `cbt-readiness-checkpoint-spring.md` (last reviewed 2026-06-04). The NY CBT mandate (spring 2026 first full window) is the triggering event; the March-checkpoint discipline is the PSM's operational response.

---

_Last reviewed: 2026-06-05 by `claude`_
