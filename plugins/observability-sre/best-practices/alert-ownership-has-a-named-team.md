# Every alert has a named owning team — orphaned alerts are deleted

**Status:** Absolute rule
**Domain:** Observability / alerting
**Applies to:** `observability-sre`

---

## Why this exists

An alert without a clear owner is an alert that nobody has a responsibility to maintain, tune, or act on. Over time it accumulates false positives, its runbook goes stale, and on-call engineers learn to snooze it. The moment "has anyone looked at the FooAlert?" is answered with silence in an incident Slack channel, you have an orphaned alert eroding the signal-to-noise ratio of the entire on-call rotation. Every alert must have an owner who can be paged, held accountable for its quality, and who will delete it when it no longer earns its place.

## How to apply

Add `owner` and `team` labels to every alert rule. Enforce the label in CI (fail the pipeline if an alerting rule is missing the label). Review unowned alerts in the quarterly SLO review and delete or reassign them.

```yaml
# Prometheus alerting rule — owner label is required
groups:
  - name: my-service.availability
    rules:
      - alert: MyServiceHighErrorRate
        expr: |
          (
            rate(http_server_request_duration_count{status=~"5.."}[5m])
            / rate(http_server_request_duration_count[5m])
          ) > 0.01
        for: 5m
        labels:
          severity: page
          team: checkout-team          # required
          owner: checkout-oncall       # required — PagerDuty service or team ID
          slo: checkout_availability   # links to the SLO this alert protects
        annotations:
          summary: "MyService error rate > 1% for 5m"
          runbook: "https://wiki.example.com/runbooks/my-service/high-error-rate"
```

```python
# CI check: fail if any alert rule missing 'team' or 'owner' label
import yaml, sys, glob

errors = []
for path in glob.glob("alerts/**/*.yaml", recursive=True):
    doc = yaml.safe_load(open(path))
    for group in doc.get("groups", []):
        for rule in group.get("rules", []):
            if "alert" in rule:
                labels = rule.get("labels", {})
                if "team" not in labels or "owner" not in labels:
                    errors.append(f"{path}: alert '{rule['alert']}' missing team/owner label")

if errors:
    for e in errors: print(e)
    sys.exit(1)
```

**Do:**
- Enforce alert ownership labels in CI — a merged unlabeled alert creates tech debt immediately.
- Route PagerDuty / OpsGenie escalation policies to the `owner` label value automatically.
- Audit orphaned alerts in the quarterly SLO review and delete or reassign.

**Don't:**
- Use a shared "platform" or "ops" team as a catch-all owner — it diffuses accountability.
- Add an owner label without also updating the PagerDuty routing to actually page that team.
- Grandfather in existing unlabeled alerts indefinitely; give them a 30-day cleanup deadline.

## Edge cases / when the rule does NOT apply

Infrastructure-level alerts managed by a platform team (node memory, cluster capacity) can use the platform team as owner — this is legitimate shared ownership. The rule targets application-level alerts with no clear accountable team.

## See also

- [`../agents/sre-reliability-engineer.md`](../agents/sre-reliability-engineer.md) — owns alerting policy and the SLO-to-alert mapping.
- [`./every-page-is-actionable.md`](./every-page-is-actionable.md) — alert quality is enforced by ownership; owners are responsible for keeping pages actionable.

## Provenance

Codifies the alert ownership practice described in Google SRE Book Chapter 6 ("Monitoring Distributed Systems") and the "You Build It You Run It" principle from Amazon's operational model.

---

_Last reviewed: 2026-06-05 by `claude`_
