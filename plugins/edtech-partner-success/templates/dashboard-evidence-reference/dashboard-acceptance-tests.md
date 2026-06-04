# PSM Command Center — Tier 1 Acceptance Tests

> Manual checklist the PSM SME (the wife) runs to accept Tier 1. Eight binary tests; each test has setup steps, pass criteria, and fail criteria. Sign-off block at the bottom.
>
> Source priors:
> - The wife's success criterion is spec.md §"Success Criteria": "open the dashboard → know in ≤15 seconds who needs attention today, why, what to do, when the next required touchpoint is, and what the portfolio's health looks like."
> - The accessibility floor is WCAG 2.2 SC 1.4.1 (Level A) per [`operational-console-design.md`](../../../ravenclaude-core/best-practices/operational-console-design.md) §2.
> - The alarm-fatigue ceiling is ≤5% false-positive rate on `critical` per [`dashboard-ux.md`](../../../../docs/research/2026-06-04-psm-dashboard-research/dashboard-ux.md) §4 (Drew et al. PLOS One 2014; Nature npj Digital Medicine 2019).

---

## Test 1 — The 5-second test

**Spec source:** spec.md §"Success Criteria"; [`dashboard-ux.md`](../../../../docs/research/2026-06-04-psm-dashboard-research/dashboard-ux.md) §3 (NN/g 5-second usability test).

### Setup

1. Close any open browser tab pointed at the dashboard.
2. Open a stopwatch app.
3. Open the dashboard URL in a new tab.
4. Start the stopwatch the moment the page paints.
5. Without scrolling, filtering, or hovering, answer aloud:
   - **Q1:** Which one partner needs my attention right now?
   - **Q2:** Why? (one signal name)
   - **Q3:** What am I supposed to do about it?
   - **Q4:** When is the next required touchpoint with anyone?
6. Stop the stopwatch as you finish Q4.

### Pass criteria

- All four questions answered in ≤ 15 seconds, no scrolling, no filtering, no hovering.
- Q1's partner is the same one as W3 row 1 (the highest `priority_score`).
- Q2 names a real signal (renewal_timing / health_decline / open_escalations / …), not a vague "they're red."

### Fail criteria

- > 15 seconds total.
- Had to scroll to see the answer to Q3 (recommended action).
- Q4 required hovering to find the countdown number.
- The eye fixated on a "sea of green" tile for more than one fixation before finding the danger.

---

## Test 2 — The 8 spec questions

**Spec source:** spec.md lines 17–26 (the eight foundational questions the dashboard exists to answer).

### Setup

1. Open the dashboard fresh.
2. For each of the eight spec-questions below, time-to-answer must be ≤ 2 clicks from the home view. (Tier 1 ships the home view + below-fold portfolio table only; "click" includes a row-expand or drill chip, NOT a separate page load Tier 2 owns.)

| # | Spec question (spec.md lines 17–26) | Where Tier 1 answers it |
|---|---|---|
| 1 | Who needs attention today and why? | W3 Daily Action Center (home view) |
| 2 | What's the overall portfolio health? | W2 Portfolio Health Snapshot (home view) |
| 3 | Are renewals on track? | W1 Portfolio Summary "In renewal window" tile + W4 calendar entries |
| 4 | Are there any partners showing decline? | W2 "Accounts with declining usage" + W2 "Avg health" tiles |
| 5 | Are there any partners with no touchpoint 90+ days? | W2 "Accounts with no touchpoint 90+ days" tile |
| 6 | What's coming up — meetings / QBRs / renewals? | W4 Calendar / Upcoming Touchpoints list |
| 7 | What are my open escalations? | W1 "Open escalations" tile |
| 8 | What needs outreach this week? | W1 "Need outreach this week" tile |

### Pass criteria

- All 8 answers reachable in ≤ 2 clicks from the home view.
- Each answer surfaces a number, not a "see report" button.

### Fail criteria

- Any of the 8 needs > 2 clicks OR requires opening a separate page.
- Any tile shows "—" or "N/A" when it should show 0 (honest empty contract — see Test 3).

---

## Test 3 — Honest empty states

**Spec source:** [`operational-console-design.md`](../../../ravenclaude-core/best-practices/operational-console-design.md) §7; [`dashboard-ux.md`](../../../../docs/research/2026-06-04-psm-dashboard-research/dashboard-ux.md) §6. Distinguish first-run / filter-emptied / healthy-empty.

### Setup

Run the dashboard against three fixtures (Codex regenerates `report.html` per fixture; or open three copies):

- **Fixture A — First-run:** `partners: []` (empty book).
- **Fixture B — Filter-emptied:** if/when filters land (Tier 2), the test variant is a filter selecting zero partners; for Tier 1, simulate by removing every partner with `priority_score > 0`.
- **Fixture C — Healthy-empty:** every partner is green, zero open escalations, zero renewal-window partners.

### Pass criteria

- **Fixture A:** Each of W1/W2/W3/W4 renders a diagnostic-headline + supporting-copy + CTA, NOT "No data" or "—". W3 reads literally: *"No partners in the book yet. Drop a real export at plugins/edtech-partner-success/bi-report/data.json and re-run the generator."*
- **Fixture B:** The empty state is filter-aware and offers "clear filters" as the CTA.
- **Fixture C:** W1 "At-risk" tile reads *"0 — all partners above the at-risk band"* (celebratory, NOT a dash). W3 reads *"No partners need attention today — last refreshed at HH:MM TZ."*
- All three empty states share visual structure (the `.empty-state` surface from `dashboard-styles.css`).

### Fail criteria

- Any tile shows "—" / "N/A" / "0 results."
- Healthy-empty looks identical to first-run.
- The empty-state copy does not say *why* the surface is empty.

---

## Test 4 — Drill-down: URL state + back button + breadcrumbs

**Spec source:** [`dashboard-ux.md`](../../../../docs/research/2026-06-04-psm-dashboard-research/dashboard-ux.md) §5 + §8; [`operational-console-design.md`](../../../ravenclaude-core/best-practices/operational-console-design.md) §3–§4. Tier 1 ships a minimal drill (W3 row click expands the row inline; full Partner 360 is Tier 2). The test still applies to whatever drill IS shipped.

### Setup

1. Open the dashboard.
2. Click W3 row 1 (the highest-priority partner) to drill / expand.
3. Inspect the URL — it MUST now carry a query parameter naming the partner (e.g. `?partner=demo_riverbend_isd`).
4. Copy the URL.
5. Open a new browser tab and paste the URL — the drill view should restore to the same partner.
6. Click the browser **Back** button — the dashboard should return to the home view, not stay drilled.
7. Click **Forward** — the drill view should restore.
8. Confirm a breadcrumb / visible close affordance is present on the drill view (e.g. `Home › Demo: Riverbend ISD` with `×` close).

### Pass criteria

- URL updates on drill (query-string state per §8 "URL is the source of truth").
- Pasted URL restores the drilled view.
- Back/forward navigation works as expected.
- Visible close affordance present.

### Fail criteria

- URL doesn't change on drill.
- Back button does not return to home view.
- No close affordance — drilling without a way back per §5 "drilling without a way back is a usability bug."

---

## Test 5 — WCAG accessibility (deuteranopia + protanopia + axe-core)

**Spec source:** [`operational-console-design.md`](../../../ravenclaude-core/best-practices/operational-console-design.md) §2; WCAG 2.2 SC 1.4.1 Level A; [`dashboard-ux.md`](../../../../docs/research/2026-06-04-psm-dashboard-research/dashboard-ux.md) §4 (8% of men have CVD).

### Setup

1. Install a CVD simulator browser extension (e.g. "Colorblindly" for Chrome / "Let's get color blind" for Firefox). Or use Chrome DevTools `Rendering` panel → `Emulate vision deficiencies`.
2. Load the dashboard, populated fixture.
3. Apply **Deuteranopia** simulation. Scan the at-risk tile (W1) and the W3 priority-score badges.
4. Apply **Protanopia** simulation. Re-scan.
5. Run **axe-core** (the browser extension or the npm `@axe-core/cli` if available against the deployed URL).

### Pass criteria

- Under deuteranopia: the at-risk tile is still identifiable WITHOUT relying on the red color (the warning icon class — filled square — is the second channel per `dashboard-styles.css` §2).
- Under protanopia: the green/yellow/red priority-score badges remain distinguishable by silhouette (filled circle / hollow triangle / filled square per `dashboard-styles.css` §2).
- axe-core scan reports **zero serious or critical violations**. Moderate violations are noted in the sign-off block below for follow-up.

### Fail criteria

- A status indicator becomes indistinguishable from neutral under either simulation.
- axe-core reports any serious/critical violation (missing `aria-label`, color-only status, insufficient contrast, missing focus-visible).
- The W3 reason column relies on color to convey severity (it shouldn't — reason is text-only per the rendering contract).

---

## Test 6 — Freshness + manual-refresh

**Spec source:** [`dashboard-ux.md`](../../../../docs/research/2026-06-04-psm-dashboard-research/dashboard-ux.md) §7; [`operational-console-design.md`](../../../ravenclaude-core/best-practices/operational-console-design.md) §6 (Smashing Magazine 2025 — always show freshness; three-state Live / Stale / Paused).

### Setup

1. Open the dashboard.
2. Inspect the page header — confirm a `.freshness-chip` is visible naming "Updated N min ago" (the `as_of` from `data.json`).
3. **Simulate stale data:** wait until the `as_of` is > 60 minutes old, OR manually edit the test fixture to bump `as_of` back 6 hours, then re-open.
4. Confirm the chip transitions to the `.freshness-chip--stale` variant (amber, hollow-triangle icon).
5. Click the manual-refresh button next to the freshness chip.

### Pass criteria

- Freshness chip is present and reads "Updated N min ago" with the correct timestamp.
- Stale-data fixture renders the amber `--stale` variant (NOT silent freeze).
- Manual-refresh button triggers a regeneration / re-fetch and the chip transitions back to `--live` with the new `as_of`.
- The chip pulse animation respects `prefers-reduced-motion: reduce` (test by toggling OS-level "reduce motion" — pulse stops, chip remains visible).

### Fail criteria

- No freshness indicator anywhere on the page.
- Stale data looks identical to live data (per §7 "frozen dashboard that looks live is worse than no dashboard").
- Refresh button missing or non-functional.

---

## Test 7 — 5-day alarm-fatigue calibration (≤5% false-positive on Daily Action Center)

**Spec source:** [`dashboard-ux.md`](../../../../docs/research/2026-06-04-psm-dashboard-research/dashboard-ux.md) §4 alarm-fatigue mitigation pattern #5: "Calibrate thresholds for ≤5% noise rate. If >5% of 'red' turns out not to require action, the team will stop trusting red." Nature npj Digital Medicine 2019 — design to PPV, not recall.

### Setup

1. Open the dashboard at the start of each workday for **5 consecutive business days**.
2. For each W3 row that surfaces in the Daily Action Center, record whether the recommended action actually required action that day (a partner-facing touch, a follow-up, an escalation) OR was a false alarm (no action required — the signal fired but the situation was already in hand / a dead-zone suppression should have applied / the play didn't fit).
3. At the end of 5 days, compute:
   - `false_positive_rate = false_alarms / total_rows`

### Pass criteria

- `false_positive_rate ≤ 5%` over 5 days × ~10 rows/day ≈ 50 observations.
- No single signal type (e.g. `usage_decline`) accounts for > 50% of the false positives — if one does, the rubric for that signal needs retuning before Tier 1 is accepted.

### Fail criteria

- `false_positive_rate > 5%` — the team will start ignoring the Daily Action Center per the alarm-fatigue literature.
- The same partner appears in the top-5 three days in a row with no actual action taken (suggests the signal is "loud" but not actionable; needs decay tuning per the rubric).

### Notes

- Record observations in the table at the bottom of this file.
- If the test fails, the fix is **not** "render fewer rows" — it's "retune the signal weights or add suppression rules" (the priority-score rubric lives at `plugins/edtech-partner-success/knowledge/dashboard-priority-score-rubric.md`). Re-test for 5 more days.

---

## Test 8 — Timezone clarity

**Spec source:** [`dashboard-ux.md`](../../../../docs/research/2026-06-04-psm-dashboard-research/dashboard-ux.md) §9; [`operational-console-design.md`](../../../ravenclaude-core/best-practices/operational-console-design.md) §5; [`k12-psm-operating-cadence.md`](../../knowledge/k12-psm-operating-cadence.md) (time-zone discipline for multi-state books).

### Setup

1. Open the dashboard.
2. Inspect every visible date or timestamp:
   - The freshness chip "Updated N min ago"
   - Each W4 row's countdown ("15 days until next check-in")
   - Each W3 row's `due_date`
   - Any tooltip exposing a raw timestamp (`as_of`, `last_touchpoint_at`)
3. Confirm each carries a timezone label (e.g. `2026-06-04 14:32 PST` or `(your time)`).
4. For a multi-state fixture (Tier 0 includes 25 partners across states): confirm a partner in Eastern Time and a partner in Pacific Time render their due_dates in the **partner's local zone**, with the viewer's local zone in a tooltip.

### Pass criteria

- Every wall-clock time on the page carries a TZ label (zone abbrev or "your time").
- Per-partner times use the **partner's** TZ (matches §9 "Multi-site, single-region: Local time of the site").
- Hover/tooltip on a per-partner time also shows the viewer's local time.
- The freshness chip uses the viewer's local TZ (it's about the build, not a partner).

### Fail criteria

- Any "14:32" without a zone label.
- A partner in Eastern Time has their due_date rendered in Pacific because the page used the viewer's TZ.
- DST-straddling dates render the wrong wall-clock time (suggests offset-based rendering instead of zone-name-based).

---

## False-positive observation table (Test 7)

| Day | Date | W3 row partner | Reason | False alarm? (Y/N) | Notes |
|---|---|---|---|---|---|
| 1 | | | | | |
| 1 | | | | | |
| 1 | | | | | |
| 2 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

Compute at end of day 5:

- **Total rows observed:** ____
- **False alarms:** ____
- **False-positive rate:** ____%
- **Pass / Fail:** ____

---

## PSM SME sign-off

> The wife (PSM SME) is the only signer. Matt is the implementation lead, not the acceptor.

| Test | Result | Notes / follow-ups |
|---|---|---|
| 1. 5-second test | ☐ Pass ☐ Fail | |
| 2. 8 spec questions ≤ 2 clicks | ☐ Pass ☐ Fail | |
| 3. Honest empty states (A/B/C) | ☐ Pass ☐ Fail | |
| 4. Drill-down: URL + back + breadcrumb | ☐ Pass ☐ Fail | |
| 5. WCAG: deuteranopia + protanopia + axe | ☐ Pass ☐ Fail | axe-core findings: |
| 6. Freshness + manual-refresh | ☐ Pass ☐ Fail | |
| 7. ≤ 5% false-positive (5-day) | ☐ Pass ☐ Fail | Observed rate: ___% |
| 8. Timezone clarity | ☐ Pass ☐ Fail | |

**Overall:** ☐ Accepted (Tier 1 is what I open every morning) ☐ Not yet — see follow-ups

**Signed:** ______________________________ **Date:** ___________ TZ: _______

**PSM SME name:** ______________________________

---

### When all 8 tests pass

Tier 1 is done. Move the PR from draft to ready-for-review (matches the build plan §6.3 / §9 — "When the wife says 'yes, this is what I open every morning' — Tier 1 is done. Until then, it's draft.").

### When any test fails

- Test 1 / 2 fail → layout regression. Re-read [`operational-console-design.md`](../../../ravenclaude-core/best-practices/operational-console-design.md) §1; the top fold isn't doing its job.
- Test 3 fails → the honest-empty contract isn't wired. The fix is in the W3/W4 renderer empty branches.
- Test 4 fails → URL state plumbing missing. The fix is the drill query-param sync.
- Test 5 fails → ≥2-channel discipline broke. Audit `.status-badge--*` usages; every one must carry a `.status-icon--*` sibling.
- Test 6 fails → freshness chip missing or not wired to `as_of`. The fix is the page-header partial.
- Test 7 fails → rubric retune, NOT a UI fix. Update weights in `dashboard-priority-score-rubric.md` and re-run for 5 more days.
- Test 8 fails → timezone library not invoked. The fix is the date-formatting helper; never roll your own per §9.
