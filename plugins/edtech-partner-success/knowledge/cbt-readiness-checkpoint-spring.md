---
title: CBT (Computer-Based Testing) Readiness Checkpoint — Spring
audience: psm, edtech-partner-success-manager, learning-analytics-analyst, success-playbook-designer
status: stable
last_reviewed: 2026-06-04
refresh_triggers:
  - "A state adds or removes a CBT mandate (NY, TX, FL, CA priority)"
  - "Major rostering vendor announces CBT-window incident"
  - "State testing window dates shift"
  - "DOE issues new CBT guidance"
sources:
  - /tmp/research-k12-2026-updates.md §5 (state testing windows + NY mandatory CBT spring 2026) + §9 (CBT-readiness as new operating-cadence checkpoint)
---

# CBT (Computer-Based Testing) Readiness Checkpoint — Spring

> **Spring 2026 mandates computer-based testing (CBT) in NY** for grades 3-8 ELA + Math + Science (NYSED). It compresses the device + bandwidth + rostering + login failure window into a tight April-May 2026 envelope. Any rostering, assessment, LMS, or SSO vendor with NY districts is in the blast radius. The pattern will spread — PSMs need a March-cadence checkpoint.

## 1. Which states have CBT mandates (mid-2026)

| State | CBT scope | Testing window 2026 | Source |
|---|---|---|---|
| **New York** | **Grades 3-8 ELA + Math + Science, mandatory CBT spring 2026** | Late April – early May 2026 | NYSED `[verify-at-use — 2026-06-04]` |
| **Texas (STAAR)** | CBT primary; paper backup limited | Apr 7-30, 2026 | LingoAce summary `[verify-at-use against TEA]` |
| **Florida (FAST)** | Phased CBT rollout | 2025-26 schedule published by FDOE (PDF) `[verify-at-use]` | FDOE |
| **California (CAASPP)** | Long-standing CBT | CDE/CAASPP-ELPAC key-dates page `[verify-at-use]` | CDE |
| **Other states** | Mixed; trend toward CBT-primary | State-by-state | NCES + state DOE pages |

**Operationally consequential change for 2026:** NY's mandatory CBT spring 2026 is the most novel — it removes the paper-backup safety valve districts relied on for grades 3-8.

---

## 2. The March-cadence checkpoint — what to verify

For any vendor with **NY districts** in their book (or any district in a CBT-mandate state), the PSM should run this checkpoint **by mid-March 2026 / 4-6 weeks before the testing window opens.**

### 2.1 Device readiness
- Per-student device available within the testing window?
- Devices fresh-imaged with the testing app + dependencies?
- Battery / charging infrastructure scoped for testing-day demand?
- Backup devices identified for failures?

### 2.2 Bandwidth readiness
- District-level bandwidth tested under simulated testing load?
- Per-school readiness check passed?
- ISP-level coordination for the testing window?
- BYOD policy disabled for the test (if applicable)?

### 2.3 Rostering readiness
- Student roster matches enrollment as of the testing window?
- Teacher-to-classroom assignments current?
- Special accommodations (504/IEP) flagged correctly in the rostering feed?
- Pre-test rostering dry-run conducted with the state's test platform?

### 2.4 SSO / login readiness
- Students can authenticate to the test platform from their district credentials?
- Admin override path tested for credential failures?
- Help-desk staffing scoped for high-volume login-day calls?
- Account-lockout policies adjusted for test-day re-authentication patterns?

### 2.5 Vendor-side readiness (PSM-direct)
- Vendor's rostering API supports the state's testing-platform integration?
- Vendor has incident-response playbook for testing-day failures?
- Vendor's customer-success on-call coverage scoped for testing window?
- Vendor has primed status-page / customer-comm channels for transparency during testing window?

---

## 3. What to do in the 30 days before the window opens

Per the K-12 operating cadence ([`k12-psm-operating-cadence.md`](./k12-psm-operating-cadence.md)), the testing window itself is a **dead zone for non-essential touchpoints.** No QBR, no contract conversation, no expansion pitch.

**What the PSM should do instead, by week:**

| Week before window | PSM action |
|---|---|
| **Week -4** | Run the §2 checkpoint with the district's IT lead + testing coordinator. Flag any red items. |
| **Week -3** | Re-confirm green items; close any red items; verify backup paths. |
| **Week -2** | Vendor-side on-call check; customer-success team briefing on potential incidents. |
| **Week -1** | Status-page / channel readiness; communicate testing-window cadence to district. |
| **During window** | **Dead zone for non-essential.** PSM available for incident response only. |
| **Week +1** | Post-window retrospective with the district; capture any vendor-side improvement items. |

---

## 4. Incident-response framing if a CBT-window failure happens

If a vendor-side incident hits during the testing window (rostering sync failure, SSO outage, test-app crash, bandwidth saturation), the response framing matters as much as the technical fix.

### 4.1 Within the first hour
- **Acknowledge publicly via status page** within 15 minutes. Silence reads as cover-up.
- **PSM contacts district testing coordinator directly** within 30 minutes. Email is too slow.
- **Internal incident bridge** opened; on-call eng + on-call CS + comms in the same channel.

### 4.2 During the incident
- **Hourly customer comms** even if no new information.
- **PSM stays in front of the district**, not behind the vendor's comms team.
- **No "minimization" language** — districts have parents, school boards, and press calling.

### 4.3 After the incident
- **Written incident retrospective within 5 business days.**
- **PSM-facilitated post-mortem with the district** — not the vendor monologuing, but a joint review of what failed and what changes.
- **Make-good offer aligned to the district's actual harm** — make-good must be tangible (e.g., extended support, free training, contract credit), not a "we value the partnership" letter.

### 4.4 What NOT to do
- Don't escalate to "this was a state platform issue, not us" if vendor-side rostering or SSO was on the failure path.
- Don't promise specific compensation in the moment without deal-desk approval.
- Don't issue a press statement before the district's communications team has approved language.

---

## 5. Why this checkpoint is becoming load-bearing for 2026

Spring 2026 is the first full window with **NY mandatory CBT for grades 3-8.** It compresses what was a multi-week paper-test rollout into an April-May electronic-test envelope. The blast radius for vendor-side failure is large:

- Rostering vendors (Clever, ClassLink, OneRoster) — every student record must be correct at test time.
- LMS vendors (Schoology, Canvas, Google Classroom) — testing apps often launch from LMS context.
- SSO vendors — students re-authenticate at scale on testing day.
- Assessment vendors — their own platforms now sit under elevated visibility.
- Bandwidth/network vendors — bandwidth saturation is the silent fail mode.

A vendor-side incident during the testing window has multi-week recovery cost in district trust. The March-cadence checkpoint is cheap; the testing-day incident is expensive.

---

## 6. Anti-patterns

- **Treating CBT-readiness as the district's problem.** Vendor's rostering / SSO / LMS is in the integration spine; vendor is on the hook.
- **Skipping the checkpoint because "it's been fine the last 3 years."** Spring 2026 is novel for NY; "fine last 3 years" is paper-test data.
- **Running the checkpoint AT week -1.** Too late to close red items.
- **Scheduling a QBR or contract conversation during the testing window.** Dead zone; respect it.
- **Issuing a vendor-side make-good without deal-desk approval mid-incident.** Wait for the retrospective.

---

## See also

- [`k12-psm-operating-cadence.md`](./k12-psm-operating-cadence.md) — the broader testing-window dead-zone rule.
- [`k12-renewal-motion-90-60-30.md`](./k12-renewal-motion-90-60-30.md) — where CBT-readiness lands in the renewal motion.
- [`k12-adoption-arc-fall-spring-summer.md`](./k12-adoption-arc-fall-spring-summer.md) — Phase 7 spring rhythm.
- [`rostering-data-quality-typology.md`](./rostering-data-quality-typology.md) — rostering-side checks.
- [`sis-sso-rostering-integration-patterns.md`](./sis-sso-rostering-integration-patterns.md) — SSO + integration patterns.
- [`district-implementation-failure-modes.md`](./district-implementation-failure-modes.md) — failure-mode taxonomy.
