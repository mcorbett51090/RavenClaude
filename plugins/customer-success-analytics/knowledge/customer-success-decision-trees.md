# Customer-success analytics decision trees

Branching decision trees for CS health scoring, signal selection, and renewal-risk triage. Traverse top-to-bottom before picking a method. Last reviewed: 2026-06-05.

---

## Decision Tree: Churn signal selection — leading vs lagging

**When this applies:** the team is selecting which signals to include in the health tier, OR a signal is under review because it is not predicting churn with the expected lead time. Observable inputs: the signal's description, when in the customer lifecycle it typically fires, and whether it has been back-tested against historical churn events.

**Last verified:** 2026-06-05 against the plugin's knowledge bank (`cs-health-metrics-and-churn-indicators.md`) and standard CS analytics practice.

```mermaid
flowchart TD
    START[Evaluate a candidate signal] --> Q1{"Does the signal fire BEFORE<br/>the customer decides to churn?"}
    Q1 -->|NO| LAGGING["LAGGING SIGNAL<br/>use as confirmation not as tier input<br/>e.g. closed-lost opp, contract cancellation"]
    Q1 -->|YES| Q2{"Lead time >= 30 days<br/>before churn event?"}
    Q2 -->|NO| SHORT_LEAD["SHORT LEAD TIME<br/>include as a late-warning sub-indicator<br/>not the primary tier driver"]
    Q2 -->|YES| Q3{"Back-tested against historical<br/>churn events in this book?"}
    Q3 -->|NO| VALIDATE["VALIDATE FIRST<br/>back-test before adding to tier rule<br/>label as unvalidated-domain-default"]
    Q3 -->|YES| Q4{"Precision > 40% AND<br/>recall > 30% in back-test?"}
    Q4 -->|NO| SUB_INDICATOR["SUB-INDICATOR ONLY<br/>show in explainability panel<br/>do not include in tier rule expression"]
    Q4 -->|YES| TIER_INPUT["INCLUDE IN TIER RULE<br/>with documented threshold + window"]
```

**Rationale per leaf:**
- *Lagging Signal* — a signal that fires after the churn decision is made describes what happened, it does not predict what will happen; it belongs in post-mortem analysis, not live triage.
- *Short Lead Time* — a signal with less than 30 days of lead time gives the CS team too little runway to intervene; valuable as a last-warning indicator but not as the primary tier driver.
- *Validate First* — an unvalidated signal is a hypothesis; labeling it "domain default" makes the hypothesis explicit and sets an expectation for when the back-test will run.
- *Sub-Indicator Only* — a signal that fails the precision/recall bar provides observational context but lacks the predictive strength to drive tier classification; showing it in the explainability panel preserves its transparency without inflating false-positive rate.
- *Include in Tier Rule* — a back-tested, high-precision, high-recall signal with adequate lead time has earned its place in the rule expression.

**Tradeoffs summary:**

| Decision | CS impact | False-positive risk | Evidence bar | Use when |
|---|---|---|---|---|
| Lagging only | post-mortem use | n/a | n/a | Fires after churn decision |
| Short lead time | late warning | medium | none | Less than 30-day lead |
| Validate first | delayed inclusion | low | back-test pending | No validation yet |
| Sub-indicator only | transparency gain | low | fails precision/recall | Low predictive strength |
| Include in tier rule | drives triage | medium | back-test pass | Validated, adequate lead |

---

## Decision Tree: Health tier accuracy problem — retune or rebuild

**When this applies:** the CS team reports that the health tier is misfiring — yellow accounts are renewing fine while green accounts are churning, or the Red list is too long to triage. Observable inputs: number of false Reds, known churn events that were Green before churning, and whether the signals themselves have changed since the tier was tuned.

**Last verified:** 2026-06-05 against standard CS health-score drift and retune practice.

```mermaid
flowchart TD
    START[Tier is misfiring] --> Q1{"Is the false-Red rate above<br/>25% of the Red list?"}
    Q1 -->|YES| Q2{"Did a product change or new<br/>integration alter baseline signal levels?"}
    Q2 -->|YES| RECALIBRATE["RECALIBRATE THRESHOLDS<br/>the signal is still valid but the baseline shifted"]
    Q2 -->|NO| Q3{"Are the over-flagged accounts<br/>concentrated in one segment?"}
    Q3 -->|YES| SEGMENT_OVERRIDE["ADD SEGMENT OVERRIDE<br/>apply a different threshold for that segment"]
    Q3 -->|NO| LOOSEN["LOOSEN THRESHOLDS<br/>run parallel test before deploying to production"]
    Q1 -->|NO| Q4{"Are churned accounts that were<br/>Green present in the back-test?"}
    Q4 -->|NO| MAINTAIN["MAINTAIN current tier<br/>drift is within acceptable range"]
    Q4 -->|YES| Q5{"Do the missed-churn accounts share<br/>a common signal pattern?"}
    Q5 -->|YES| ADD_SIGNAL["ADD MISSING SIGNAL<br/>validate it first before adding to tier rule"]
    Q5 -->|NO| REBUILD["REBUILD SIGNAL SET<br/>the current signal mix is inadequate - architect review"]
```

**Rationale per leaf:**
- *Recalibrate Thresholds* — a product change or new data source can shift the baseline of a valid signal; the fix is threshold adjustment, not signal replacement.
- *Add Segment Override* — over-flagging concentrated in one segment (e.g., SMB vs. enterprise, or a specific vertical) indicates the threshold is not universal; a segment-specific rule is the targeted fix.
- *Loosen Thresholds* — a diffuse false-Red problem indicates the thresholds are too sensitive; loosen in a parallel test first to validate the false-positive reduction before promoting.
- *Maintain* — if the false-Red rate is acceptable and no known churns were missed, the tier is performing within its design parameters.
- *Add Missing Signal* — a common pattern among missed-churn accounts points to a specific signal that the current tier doesn't capture; validate it before adding.
- *Rebuild Signal Set* — when missed-churn accounts share no common pattern in the current signal set, the problem is structural; escalate to the `cs-analytics-architect` for a redesign.

**Tradeoffs summary:**

| Action | Disruption | Evidence needed | Time to implement | Use when |
|---|---|---|---|---|
| Recalibrate thresholds | low | baseline change confirmed | days | Product or integration change |
| Segment override | medium | segment pattern confirmed | days | Concentrated false positives |
| Loosen thresholds | medium | parallel-test result | weeks | Diffuse false positives |
| Maintain | none | drift check passes | — | Tier performing within range |
| Add missing signal | medium | back-test pass | weeks | Missed churns share a pattern |
| Rebuild signal set | high | architect review | months | No detectable pattern in missed churns |

---

## Decision Tree: Renewal-risk call list — which account to call first

**When this applies:** the CS leader has the filtered Red-tier list sorted by days-to-renewal and must decide the call order. Observable inputs: days-to-renewal, tier-driver signals, ACV, and whether a live decision-maker is confirmed.

**Last verified:** 2026-06-05 against the plugin's `renewal-and-account-lifecycle.md` knowledge file.

```mermaid
flowchart TD
    START[Red-tier account on the call list] --> Q1{"Named decision-maker confirmed<br/>alive in role THIS quarter?"}
    Q1 -->|NO| CONFIRM_DM["CONFIRM DECISION-MAKER FIRST<br/>no renewal motion to an empty seat"]
    Q1 -->|YES| Q2{"Days to renewal <= 60?"}
    Q2 -->|YES| Q3{"ACV in top quartile of book?"}
    Q3 -->|YES| CALL_TODAY["CALL TODAY<br/>high ACV plus short window - highest priority"]
    Q3 -->|NO| CALL_WEEK["CALL THIS WEEK<br/>short window but manageable ACV"]
    Q2 -->|NO| Q4{"Usage trend accelerating downward<br/>in last 30 days?"}
    Q4 -->|YES| Q5{"Is this a data-pipeline freshness issue?"}
    Q5 -->|YES| FIX_PIPELINE["FIX THE PIPELINE FIRST<br/>verify signal freshness before acting on stale data"]
    Q5 -->|NO| EARLY_INTERVENTION["EARLY INTERVENTION<br/>fire the save play now - do not wait for T-60"]
    Q4 -->|NO| MONITOR["MONITOR WEEKLY<br/>Red but stable - watch for inflection before escalating"]
```

**Rationale per leaf:**
- *Confirm Decision-Maker First* — a renewal or recovery motion to a departed champion is wasted effort and may trigger the wrong person; confirmation is always the first step.
- *Call Today* — high ACV plus a short renewal window is the highest blast-radius combination on the call list; it is the first call every time.
- *Call This Week* — short window with manageable ACV is urgent but not the absolute first call; schedule within the week.
- *Fix the Pipeline First* — a stale data feed can make a healthy account appear to be in free-fall; verify signal freshness before alarming the CS leader or the account.
- *Early Intervention* — accelerating downward trend outside the T-60 window is the scenario where early action has the most leverage; waiting until T-60 converts a recovery play into a panic play.
- *Monitor Weekly* — a stable Red (hit threshold but not accelerating) warrants attention but not an immediate call; weekly monitoring catches the inflection point without manufacturing urgency.

**Tradeoffs summary:**

| Action | Urgency | Cost if wrong | Approval gate? | Use when |
|---|---|---|---|---|
| Confirm decision-maker | pre-work | High - motion to empty seat | No | DM not confirmed this quarter |
| Call today | immediate | High if missed | No | High ACV plus T-60 or less |
| Call this week | urgent | Medium | No | T-60 or less, any ACV |
| Fix the pipeline | technical | Low - conservative | Data-platform | Freshness gap suspected |
| Early intervention | this week | High if late | Yes - success lead | Accelerating decline at T-90+ |
| Monitor weekly | deferred | Low if stable | No | Red but stable trend |

---

## Decision Tree: Expansion signal — is this account ready for a grow motion?

**When this applies:** the CS leader has a Yellow or Green account and wants to know whether to initiate an expansion (upsell / cross-sell / seat expansion) motion, or the `account-expansion-signal-design` skill is being applied. Observable inputs: usage trend direction, champion depth, NPS in the last 180 days, and days to renewal.

**Last verified:** 2026-06-05 against the plugin's `account-expansion-signal-design` skill and standard B2B CS practice.

```mermaid
flowchart TD
    START[Evaluate account for expansion motion] --> Q1{Is usage trend accelerating upward in the last 30 days?}
    Q1 -->|NO - flat or down| NOT_READY[NOT EXPANSION READY - maintain current cadence - revisit next quarter]
    Q1 -->|YES - usage trending up| Q2{Are there at least 2 named active champions confirmed this quarter?}
    Q2 -->|NO - single champion or none| SINGLE_CHAMP[EXPANSION WATCH - usage signal is positive but champion depth is fragile - deepen relationship before expand]
    Q2 -->|YES - 2 or more champions active| Q3{NPS >= 8 OR CSAT >= 4 in last 180 days?}
    Q3 -->|NO - neutral or negative sentiment| SENTIMENT_BARRIER[EXPANSION WATCH - usage strong but sentiment is a barrier - address open issues before grow motion]
    Q3 -->|YES - positive sentiment| Q4{Days to renewal > 180?}
    Q4 -->|NO - renewal within 180 days| RENEWAL_FIRST[RENEWAL FIRST - insufficient runway for expansion motion - secure renewal then revisit]
    Q4 -->|YES - enough runway| EXPANSION_READY[EXPANSION READY - book expansion QBR - initiate grow motion]
```

**Rationale per leaf:**
- *Not Expansion Ready* — flat or declining usage means the account is not extracting value from the current product; an expansion motion before value is demonstrated will be rejected.
- *Expansion Watch (single champion)* — one champion is a single point of failure; an expansion commitment from one person is fragile and hard to protect if that person leaves.
- *Expansion Watch (sentiment barrier)* — positive usage with negative sentiment means the account has unresolved pain; fixing the pain before expanding is better than expanding into a complaint.
- *Renewal First* — an expansion motion with less than 180 days of runway competes for attention with the renewal itself; secure the base before growing it.
- *Expansion Ready* — all four signals pass: usage is up, champion depth is sufficient, sentiment is positive, and there is enough contract runway to execute the motion.

**Tradeoffs summary:**

| Leaf | Primary blocker | CS action | Timeline |
|---|---|---|---|
| Not Expansion Ready | Usage not established | Maintain cadence; focus on adoption | Next quarter review |
| Watch — champion depth | Relationship fragility | Deepen champion network | This quarter |
| Watch — sentiment barrier | Unresolved pain | Address tickets and NPS drivers | Before next QBR |
| Renewal first | Contract runway | Secure renewal | Within 90 days |
| Expansion Ready | None | Book expansion QBR | This week |

---

## Decision Tree: New signal proposal — should this signal enter the tier, sub-indicators, or be excluded?

**When this applies:** a new signal is proposed for the CS health tier (by a stakeholder, a CS leader, or discovered during a tier retune) and the team needs to decide how to treat it. Observable inputs: whether the signal fires before or after the churn decision, whether a back-test exists, and the back-test precision/recall results.

**Last verified:** 2026-06-05 against the plugin's `churn-signal-backtest` skill and churn-signal-selection decision tree.

```mermaid
flowchart TD
    START[New signal proposed for the health tier] --> Q1{Does the signal fire BEFORE the customer decides to churn - is it leading?}
    Q1 -->|NO - fires after churn decision| LAGGING[EXCLUDE FROM TIER - use as post-mortem context only - lagging signals describe history not predict it]
    Q1 -->|YES - leading signal| Q2{Has it been back-tested against at least 30 completed renewals?}
    Q2 -->|NO - no back-test yet| PROVISIONAL[ADD AS PROVISIONAL - label unvalidated-domain-default - schedule back-test for next renewal cycle]
    Q2 -->|YES - back-test exists| Q3{Precision > 40% AND Recall > 30% at a usable threshold?}
    Q3 -->|YES - passes both bars| Q4{Does it add predictive power the current signal set lacks - no redundancy?}
    Q4 -->|YES - additive| TIER_RULE[ADD TO TIER RULE - document threshold and window - version the rule]
    Q4 -->|NO - redundant with existing signal| SUBINDICATOR_SWAP[ADD AS SUB-INDICATOR OR REPLACE - show in explainability panel or swap for the weaker existing signal]
    Q3 -->|NO - fails precision or recall| SUBINDICATOR_ONLY[ADD AS SUB-INDICATOR ONLY - show in explainability panel - do not include in tier expression]
```

**Rationale per leaf:**
- *Exclude* — lagging signals belong in post-mortem analysis, not the live tier; their presence inflates the signal count without improving prediction.
- *Provisional* — a plausible leading signal without a back-test is a hypothesis; labeling it provisional keeps it visible while the evidence is gathered.
- *Add to tier rule* — a validated, additive, high-precision-recall signal earns its place in the rule expression.
- *Sub-indicator or swap* — a validated signal that duplicates an existing one should replace the weaker signal or surface as a sub-indicator, not add count noise.
- *Sub-indicator only* — a signal that clears the leading bar but fails precision/recall still provides observational context; showing it in the explainability panel preserves transparency without inflating false-positive rate.

**Tradeoffs summary:**

| Decision | CS impact | Evidence bar | Signal count impact |
|---|---|---|---|
| Exclude | No change | Confirmed lagging | 0 |
| Provisional | Delayed inclusion | None yet | +1 provisional |
| Tier rule | Improved precision | Back-test pass, non-redundant | +1 active |
| Sub-indicator or swap | Transparency or quality gain | Back-test pass, redundant | 0 net |
| Sub-indicator only | Transparency gain | Leading but below bar | +1 visibility |

---

## Decision Tree: CS metric discrepancy — when numbers don't match

**When this applies:** a CS leader or stakeholder reports that a metric on the dashboard doesn't match their expectation, a prior report, or what they see in the source system. Observable inputs: the metric name, whether it is computed in the mart or the BI tool, and when the discrepancy was first observed.

**Last verified:** 2026-06-05 against the plugin's `cs-metric-audit` skill and mart architecture.

```mermaid
flowchart TD
    START[CS metric discrepancy reported] --> Q1{Is the metric computed in the mart or in the BI tool?}
    Q1 -->|BI tool - computed in dashboard layer| BI_BYPASS[MART BYPASS VIOLATION - move computation to mart - reference the mart-is-the-single-source rule]
    Q1 -->|Mart| Q2{Has the underlying source data been refreshed recently - pipeline freshness check?}
    Q2 -->|NO - source data is stale| FRESHNESS[PIPELINE FRESHNESS ISSUE - check pipeline run log - surface data-pending flag on affected metrics]
    Q2 -->|YES - source data is current| Q3{Does the metric involve a NULL-to-zero conversion anywhere in the pipeline or mart?}
    Q3 -->|YES - NULL silently converted| NULL_VIOLATION[NULL HANDLING VIOLATION - return explicit NULL - fix in mart model - review all affected accounts]
    Q3 -->|NO - nulls are explicit| Q4{Is the metric a trend or slope column - could it be computed at query time instead of materialized?}
    Q4 -->|YES - computed at query time| TREND_VIOLATION[TREND MATERIALIZATION VIOLATION - materialize in mart model - remove BI-layer window function]
    Q4 -->|NO - materialized trend| Q5{Is the grain correct - is there an unexpected fan-out or roll-up error?}
    Q5 -->|YES - grain mismatch| GRAIN_FIX[GRAIN ERROR - fix the join in the mart model - verify with row-count check]
    Q5 -->|NO - grain is correct| UNKNOWN[UNKNOWN CAUSE - run full cs-metric-audit skill - escalate to data-platform if mart model is correct]
```

**Rationale per leaf:**
- *BI bypass* — metrics computed in the BI tool diverge silently from mart definitions; the fix is always to move the computation into the mart.
- *Pipeline freshness* — the most common cause of sudden metric drops; always check before escalating to a mart fix.
- *NULL violation* — a NULL converted to zero makes a missing signal read as the worst possible value; this inflates risk scores for accounts where the source is simply not connected.
- *Trend materialization* — a trend computed at query time produces different results per query depending on session parameters; materialization is the only reliable fix.
- *Grain error* — a join that fans out (or incorrectly rolls up) produces inflated or deflated counts; the mart model's join logic is the fix.

---

## Decision Tree: Tier confidence question — can I trust the current tier output?

**When this applies:** a CS team is about to act on the health tier results (a QBR deck, a renewal call list, a save-play trigger) and wants to know how much confidence to place in the tier's current output. Observable inputs: time since last retune, back-test status of active signals, and pipeline freshness.

**Last verified:** 2026-06-05 against the plugin's tier-design and back-test skills.

```mermaid
flowchart TD
    START[Can I trust the current tier output for a high-stakes action?] --> Q1{Has the tier been retuned against a completed renewal cycle within the last 12 months?}
    Q1 -->|NO - never retuned or more than 12 months ago| LOW_CONFIDENCE[LOW CONFIDENCE - mark tier output as provisional - retune before acting on the list for high-stakes renewals]
    Q1 -->|YES - retuned within 12 months| Q2{Are all active signals validated - back-test pass AND no provisional-only signals driving Red accounts?}
    Q2 -->|NO - provisional signals in tier| MEDIUM_CONFIDENCE[MEDIUM CONFIDENCE - provisional signals add uncertainty - weight CS judgment more heavily on Red accounts driven by provisional signals only]
    Q2 -->|YES - all signals validated| Q3{Is source data fresher than 24 hours for the key signals in this snapshot?}
    Q3 -->|NO - stale source data| STALE_DATA[DATA FRESHNESS GAP - do not act until pipeline catches up - surface data-pending flag]
    Q3 -->|YES - data is fresh| Q4{Does the explainability panel show named drivers for every Red account in scope?}
    Q4 -->|NO - some Reds have no named drivers| EXPLAIN_GAP[EXPLAINABILITY GAP - do not present driverless Reds as confident signals - investigate mart before QBR]
    Q4 -->|YES - all Reds have named drivers| HIGH_CONFIDENCE[HIGH CONFIDENCE - tier output is reliable for this action - proceed]
```

**Rationale per leaf:**
- *Low confidence* — a tier that has never been measured against outcomes may have accumulated drift; provisional use only, with heavy CS-judgment overlay.
- *Medium confidence* — validated signals support moderate trust; provisional signals in the active rule require the CS rep to apply additional judgment on those specific accounts.
- *Stale data* — a tier computed on stale data is not a tier output; it is a projection from the last good snapshot; do not act.
- *Explainability gap* — a Red account with no named driver cannot be actioned by the CS rep and cannot be presented to the account; it indicates a mart defect.
- *High confidence* — all four conditions pass; the tier output is as reliable as it can be given the current design.

**Tradeoffs summary:**

| Confidence level | Pre-conditions | CS action | Override needed? |
|---|---|---|---|
| High | Retuned, validated, fresh, explainable | Act on tier output | No |
| Medium | Retuned but provisional signals present | Weight CS judgment on provisional-driven accounts | Soft override |
| Low | Never retuned | Treat as directional only | Yes — CS judgment primary |
| Stale data | Source data > 24h old | Wait for pipeline | Hard block |
| Explainability gap | Red has no named drivers | Do not present to account | Hard block |

---

## Decision Tree: PII signal classification — what can land in the CS mart?

**When this applies:** a new data source is being added to the CS health mart collection spec and the team needs to determine what form of the data is permitted to land in the warehouse. Observable inputs: the source system type (CRM, CS platform, support tool, collaboration tool) and the data elements in the export payload.

**Last verified:** 2026-06-05 against the plugin's `CLAUDE.md` §4 house opinion #11 and the `pii-signals-require-security-reviewer-before-landing` best practice.

```mermaid
flowchart TD
    START[New data source to add to CS mart] --> Q1{Does the export contain free-text fields - verbatims - message bodies - email bodies?}
    Q1 -->|YES - raw text present| Q2{Can the source system export a pre-derived form - sentiment score - keyword flag - volume only?}
    Q2 -->|YES - derived form available| DERIVED_OK[LAND DERIVED FORM ONLY - route to data-platform with derived-only spec - no raw text in mart]
    Q2 -->|NO - raw text is the only export| SECURITY_REVIEW[MANDATORY SECURITY-REVIEWER REVIEW - raw PII text requires explicit approval - default answer is do not land]
    Q1 -->|NO - no free text| Q3{Does the export contain direct identifiers - email address - phone number - personal name?}
    Q3 -->|YES - direct identifiers present| Q4{Are identifiers needed for identity resolution or CS-motion attribution?}
    Q4 -->|YES - needed for identity resolution| DATA_PLATFORM_ONLY[ROUTE TO DATA-PLATFORM IDENTITY RESOLUTION ONLY - identifiers go into bridge table - not into mart metrics]
    Q4 -->|NO - not needed| STRIP_IDENTIFIERS[STRIP IDENTIFIERS BEFORE LANDING - instruct data-platform to drop identifier fields from mart payload]
    Q3 -->|NO - no direct identifiers| LAND_OK[LAND AS-IS - standard mart spec - document source and grain]
```

**Rationale per leaf:**
- *Derived form only* — pre-computed sentiment scores and keyword counts are not PII; they carry no text that identifies a person or recreates the original statement.
- *Security reviewer required* — raw text (NPS verbatims, support bodies, Slack messages) requires an explicit legal/security verdict; the default in this plugin is do not land without that verdict.
- *Data-platform identity resolution only* — email addresses and phone numbers are needed only for matching, not for the metrics layer; they belong in the `bridge_account_xref` table, not in any fact or dimension the BI tool queries.
- *Strip identifiers* — if identifiers are in the export but not needed for resolution or attribution, drop them at ingestion; don't land what isn't needed.
- *Land as-is* — a payload with no free text and no direct identifiers is clean for the mart; standard spec applies.
