# Content policy — <surface / abuse area>

> The policy a reviewer applies and a user is held to. Lead with the taxonomy; map each
> tier to a proportional action; attach an appeal path to every action; define how it's measured.

**Owner:** <name> · **Version:** <x.y> · **Effective:** <YYYY-MM-DD> · **Surface:** <where it applies>

## 1. Scope & intent
<What this policy covers, who it protects, and the one harm it exists to reduce.>

## 2. Policy taxonomy
| Category | One-line definition | In scope (examples) | Out of scope (examples) | Surfacing signals |
|---|---|---|---|---|
| <e.g. spam> | <…> | <…> | <…> | <velocity / content / graph …> |
| <e.g. harassment> | <…> | <…> | <…> | <…> |

### Severity tiers (per category)
| Tier | Definition | Example |
|---|---|---|
| Low / borderline | <…> | <…> |
| Medium | <…> | <…> |
| High | <…> | <…> |
| Critical / imminent harm | <…> | <…> |

## 3. Enforcement ladder (proportional)
| Severity × history | Action | Reversible? |
|---|---|---|
| Low, first | Warn / educate + de-amplify | Yes |
| Medium, first | Limit (rate-limit / restrict reach / remove item) | Yes |
| High, first | Remove + strike | Partly |
| High, repeat | Remove + temporary suspension | Yes |
| Repeat after suspension / Critical | Permanent ban / escalate | No |

> Proportionality rule: the action never exceeds the severity. See
> [`../knowledge/enforcement-decision-tree.md`](../knowledge/enforcement-decision-tree.md).

## 4. Appeal path (due process — required for every action)
- **Notice:** what was actioned and when.
- **Reason:** which category + tier was applied.
- **Route to contest:** <how the user appeals> · **Human-review SLA:** <e.g. 24h for suspend/ban>.
- **Overturn handling:** a sustained appeal reverses the action and feeds the overturn-rate metric.

## 5. Measurement hooks
| Metric | Target / floor | Alarm |
|---|---|---|
| Prevalence (violating impressions / 10k) | <target> | <threshold> |
| Enforcement precision / recall | <precision floor> / <recall floor> | <…> |
| Time-to-action SLA (per tier) | <p90 target> | <breach> |
| Appeal-overturn rate | <≤ target> | <> threshold> |

> See [`../knowledge/trust-safety-metrics.md`](../knowledge/trust-safety-metrics.md). Send any
> precision/recall number to `applied-statistics` for a CI before reporting it.

## 6. Seams
- PII / data-retention in moderation data → `data-governance-privacy`.
- Account-takeover / coordinated-account signals → `security-engineering`.
- The detector behind the policy → this plugin's `abuse-detection-engineer`.

## 7. Change log
| Version | Date | Change | Author |
|---|---|---|---|
| <x.y> | <YYYY-MM-DD> | <…> | <…> |
