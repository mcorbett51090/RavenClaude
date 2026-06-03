# Process-improvement best-practice docs

Named, citable rules for the `process-improvement` plugin's Lean Six Sigma methodology. Each file is one rule — read, applied, and cited as a whole. Grounded in the plugin's knowledge bank and skills; the cross-marketplace index lives in [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md).

---

## Index

_7 rules, in DMAIC flow. Each file is one named, citable rule; read and apply it whole._

| Doc | Status | Use when |
|---|---|---|
| [`operational-definition-before-you-measure.md`](./operational-definition-before-you-measure.md) | Absolute rule — if two people measuring the same thing can record different values, the variation is ambiguity, not the process. The definition precedes the first data point. | About to collect data; a metric name ("cycle time", "defect", "on-time") is being used without a precise start/stop, inclusion rule, and data source; before any Gage R&R / baseline. |
| [`measure-the-baseline-before-you-change-anything.md`](./measure-the-baseline-before-you-change-anything.md) | Absolute rule — an improvement without a measured baseline is an untestable claim. | Starting a DMAIC project; the team is about to implement a fix but no one has written down the current-state metric; a sponsor asks "how much did we improve?" after the fact. |
| [`prove-root-cause-with-data-before-improving.md`](./prove-root-cause-with-data-before-improving.md) | Absolute rule — a countermeasure attached to an unproven cause is a guess with a budget. Root cause is confirmed with data, not group consensus. | The fishbone and 5 Whys have produced candidate causes; the team is about to design a solution; anyone proposes a fix before the Analyze gate is reached. |
| [`optimize-the-constraint-not-a-sub-process.md`](./optimize-the-constraint-not-a-sub-process.md) | Pattern — speeding a non-bottleneck step doesn't speed the system; find the constraint with data and direct the effort there, then re-find it. | The goal is throughput/lead-time; the team is about to improve the easiest or most-complained-about step; a local cycle-time win didn't move end-to-end lead time. |
| [`separate-common-cause-from-special-cause.md`](./separate-common-cause-from-special-cause.md) | Pattern — apply this framing before any reaction to a metric movement. Tampering (reacting to common-cause variation) is one of the most prevalent and damaging process management mistakes. | A metric moved and a manager wants to react; a process is being monitored and a week is "bad"; a control chart has been built and someone wants to know whether to investigate. |
| [`pilot-before-you-roll-out.md`](./pilot-before-you-roll-out.md) | Pattern — prove the fix on a small, reversible slice (re-measuring the same metric) before betting the whole process; the pilot also rehearses the control plan. | An Improve-phase solution is ready; someone proposes an org-wide rollout off a plausible mechanism; the change could have unintended downstream effects. |
| [`a-fix-without-a-control-plan-didnt-happen.md`](./a-fix-without-a-control-plan-didnt-happen.md) | Absolute rule — an improvement without a control plan is a temporary deviation from the old process. Regression is the default; sustainment requires a system. | A DMAIC project is approaching close; any improvement is being declared "done"; a prior fix has regressed and the team is re-running the same analysis. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — the team constitution (house opinions §3, anti-patterns §4)
- [`../skills/`](../skills/) — the six skills that operationalize these rules in each DMAIC phase
- [`../templates/`](../templates/) — the artifacts the skills produce (charter, SIPOC, fishbone, FMEA, control plan)
- [`../knowledge/`](../knowledge/) — the DMAIC toolkit, SPC statistics, and decision-tree references with retrieval dates
- [`../../../docs/best-practices/_TEMPLATE.md`](../../../docs/best-practices/_TEMPLATE.md) — the section shape every doc here follows
