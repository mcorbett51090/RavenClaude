# Every detection maps to ATT&CK and has a tuning plan

**Status:** Pattern (strong default)
**Domain:** Detection engineering
**Applies to:** `incident-response-dfir`

---

## Why this exists

Two failure modes kill a detection program. First, **unmapped detections**: a pile of rules with no MITRE ATT&CK mapping is a pile you can't reason about — you can't tell what techniques you cover, where the gaps are, or whether a new rule is redundant. Second, **untuned detections**: a rule that fires on benign activity becomes noise, the noise becomes alert fatigue, and a fatigued analyst mutes or ignores it — so the rule that was supposed to catch the intrusion is functionally off. A detection is only real if its coverage is known and its false positives are managed.

## How to apply

For every detection, (1) map it to the ATT&CK tactic + technique/sub-technique it covers and tag the rule with it, and (2) ship a tuning plan with it: the documented benign sources, the allow-list/exception strategy, thresholds, and a target false-positive rate. Prefer TTP/behavior selectors over a single hash/IP (climb the pyramid of pain). Keep rules as version-controlled, reviewed, tested code.

**Do:**
- Tag every rule with its ATT&CK technique (`attack.t1059.001`) so coverage maps to a Navigator heatmap.
- Ship a `falsepositives` list + allow-list/threshold plan *with* the rule.
- Write true-positive and benign test cases; keep detections in version control (detection-as-code).

**Don't:**
- Ship a rule with no technique mapping (invisible to coverage analysis).
- Ship a rule with no tuning plan (it becomes fatigue and gets muted).
- Detect on a single brittle IOC (hash/IP) when a behavior selector is available.

## Edge cases / when the rule does NOT apply

- **A short-lived IOC-based block for an active campaign** (block this C2 IP right now) is legitimate and needn't wait for a full ATT&CK write-up — but log it as temporary and revisit for a durable TTP-level rule.
- **A technique with no ATT&CK entry** (novel behavior) still gets documented mapping-intent; map to the closest tactic and note the gap.

## See also
- [`../skills/engineer-a-detection/SKILL.md`](../skills/engineer-a-detection/SKILL.md)
- [`../knowledge/detection-and-hunting-reference.md`](../knowledge/detection-and-hunting-reference.md)
- [`../skills/hunt-for-a-threat/SKILL.md`](../skills/hunt-for-a-threat/SKILL.md)

## Provenance
Codifies MITRE ATT&CK-mapped detection engineering and the detection-as-code + alert-tuning discipline (SigmaHQ conventions, the pyramid of pain). Last reviewed 2026-07-01.

---

_Last reviewed: 2026-07-01 by `claude`_
