# Customer-success analytics — best-practice docs

Named, citable rules for the `customer-success-analytics` plugin's specialists. Each file is **one rule** — read, applied, and cited whole. Grounded in the plugin's house opinions (CLAUDE.md §4) and its domain-neutral CS analytics craft.

---

## Index

_20 rules._

| Doc | Status | Use when |
|---|---|---|
| [`transparent-rule-based-tiering-before-ml-in-phase-one.md`](./transparent-rule-based-tiering-before-ml-in-phase-one.md) | Absolute rule | Designing a phase-one health tier — the explainability requirement is non-negotiable before any ML layer. |
| [`anchor-on-the-csp-native-score-then-add-signals-additively.md`](./anchor-on-the-csp-native-score-then-add-signals-additively.md) | Absolute rule | Building a custom health tier on top of a platform that already has its own health score. |
| [`direction-beats-absolute-level-model-trend-columns-explicitly.md`](./direction-beats-absolute-level-model-trend-columns-explicitly.md) | Absolute rule | Designing health-signal columns — trend must be materialized in the mart, not derived at query time. |
| [`renewal-proximity-times-engagement-not-proximity-alone.md`](./renewal-proximity-times-engagement-not-proximity-alone.md) | Absolute rule | Designing a renewal-risk model or auditing one that returns too many accounts as high-risk. |
| [`append-only-health-snapshots-preserve-the-trend-history.md`](./append-only-health-snapshots-preserve-the-trend-history.md) | Absolute rule | Designing the `fct_account_health_snapshot` schema — upsert-in-place destroys the trend history. |
| [`nulls-are-explicit-missing-signal-is-never-silently-zero.md`](./nulls-are-explicit-missing-signal-is-never-silently-zero.md) | Absolute rule | Writing tier rules or scoring logic where a source signal may be absent or not yet connected. |
| [`the-mart-is-the-single-source-of-metric-definitions.md`](./the-mart-is-the-single-source-of-metric-definitions.md) | Absolute rule | Any metric enters a CS dashboard — it must trace to a mart-layer definition, not BI-tool SQL. |
| [`validate-leading-signals-against-actual-churn-outcomes.md`](./validate-leading-signals-against-actual-churn-outcomes.md) | Primary diagnostic | A signal is proposed for the tier rule, or the tier has stopped predicting churn accurately. |
| [`no-raw-collaboration-message-bodies-in-the-warehouse.md`](./no-raw-collaboration-message-bodies-in-the-warehouse.md) | Absolute rule | Designing a collaboration-signal ingestion pattern — always derive, never land raw bodies. |
| [`the-acceptance-test-is-a-sort-not-a-slide.md`](./the-acceptance-test-is-a-sort-not-a-slide.md) | Absolute rule | Accepting a health model as ready for production — the sort test is the operative criterion. |
| [`identity-resolution-is-upstream-never-reimplement-it.md`](./identity-resolution-is-upstream-never-reimplement-it.md) | Absolute rule | Joining source systems in the mart layer — always consume the xref spine, never reimplement the matcher. |
| [`back-test-signals-before-adding-to-tier-rule.md`](./back-test-signals-before-adding-to-tier-rule.md) | Absolute rule | A candidate signal is proposed for the health tier rule before any back-test has been run. |
| [`expansion-tier-is-separate-from-churn-risk-tier.md`](./expansion-tier-is-separate-from-churn-risk-tier.md) | Absolute rule | Designing or reviewing a CS health mart that combines risk and opportunity in one composite. |
| [`data-pipeline-freshness-before-alarm.md`](./data-pipeline-freshness-before-alarm.md) | Primary diagnostic | A health score drops suddenly — verify pipeline freshness before triggering a CS action. |
| [`segment-overrides-before-global-threshold-changes.md`](./segment-overrides-before-global-threshold-changes.md) | Pattern | False-Red rate is high and the over-flagged accounts are concentrated in one segment. |
| [`champion-silence-is-a-first-class-churn-signal.md`](./champion-silence-is-a-first-class-churn-signal.md) | Pattern | Designing the signal set for a CS health tier — champion presence is not optional enrichment. |
| [`retune-the-tier-after-every-renewal-cycle.md`](./retune-the-tier-after-every-renewal-cycle.md) | Absolute rule | A full renewal cycle has completed — retune thresholds against the new outcome data. |
| [`domain-layer-hands-contract-to-data-platform-does-not-build-it.md`](./domain-layer-hands-contract-to-data-platform-does-not-build-it.md) | Absolute rule | Any CS analytics work item — classify as domain or technical before assigning. |
| [`pii-signals-require-security-reviewer-before-landing.md`](./pii-signals-require-security-reviewer-before-landing.md) | Absolute rule | Any signal source that may contain NPS verbatims, ticket bodies, or collaboration message content. |
| [`minimum-five-signals-maximum-seven-for-a-phase-one-tier.md`](./minimum-five-signals-maximum-seven-for-a-phase-one-tier.md) | Pattern | Selecting signals for a phase-one health tier — enforce the 5-7 signal discipline. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution (house opinions §4, anti-patterns §5, output contract §7).
- [`../knowledge/customer-success-decision-trees.md`](../knowledge/customer-success-decision-trees.md) — branching decision trees for signal selection, retune-vs-rebuild, and renewal call-list triage.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
