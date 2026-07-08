# Severity drives the response, not the noise

**Status:** Absolute rule
**Domain:** Triage & severity classification
**Applies to:** `incident-response-dfir`

---

## Why this exists

Alerts lie about their importance. A screaming, high-confidence alert on an isolated test sandbox is low severity; a single quiet anomaly on a domain controller may be a full-blown crown-jewel compromise. If the response tier is set by how *alarming* the alert looks — its confidence score, its color, its volume — the team over-responds to noise and under-responds to the quiet catastrophes. Severity must be a function of **business impact × scope**, so that scarce responder attention and escalation go where the actual risk is.

## How to apply

Classify every incident on two axes: **impact** (confidentiality/integrity/availability consequence, regulated-data exposure) and **scope** (one isolated host vs. wide/crown-jewel systems; contained vs. lateral movement). Take the higher of the two when uncertain. Severity then selects the response tier — who is engaged and the comms cadence — not the other way around.

**Do:**
- Rate by business impact × scope; a quiet alert on a critical asset outranks a loud one on a disposable box.
- Re-triage as facts change — a "single contained host" that turns out lateral is now critical.
- Escalate on regulated/personal-data exposure and start the notification clock at awareness.

**Don't:**
- Let an alert's confidence/volume/color set the severity.
- Anchor on the first classification and refuse to re-rate as scope grows.
- Under-classify to avoid paperwork, or over-classify and burn the team on false positives.

## Edge cases / when the rule does NOT apply

- **Regulatory exposure** can floor the severity higher regardless of technical impact — a small breach of regulated data is still a reportable event with a legal clock.
- **A confirmed false positive** exits the severity model entirely — route it to detection tuning, not the lifecycle.
- **Genuinely ambiguous scope** → classify to the *higher* plausible severity and downgrade later; the cost of over-response is hours, the cost of under-response is the window.

## See also
- [`../skills/triage-and-classify-an-incident/SKILL.md`](../skills/triage-and-classify-an-incident/SKILL.md)
- [`../knowledge/incident-lifecycle-decision-tree.md`](../knowledge/incident-lifecycle-decision-tree.md)
- [`notification-timelines-are-legal-deadlines-not-guidelines.md`](notification-timelines-are-legal-deadlines-not-guidelines.md)

## Provenance
Codifies the impact × scope severity model common across SOC/IR practice, aligned to the NIST SP 800-61 prioritization guidance (functional/informational impact + recoverability; r2's model, carried forward under the CSF 2.0-aligned r3 that supersedes it). Last reviewed 2026-07-08.

---

_Last reviewed: 2026-07-01 by `claude`_
