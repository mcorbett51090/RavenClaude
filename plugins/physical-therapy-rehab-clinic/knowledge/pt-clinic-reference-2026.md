# Outpatient PT / Rehab Clinic — 2026 Reference

> Dated reference for the `physical-therapy-rehab-clinic` team: the timed-vs-untimed CPT split, the Medicare therapy-threshold + KX concept, and common payor-rule patterns. The durable reasoning lives in [`pt-clinic-decision-trees.md`](pt-clinic-decision-trees.md); this file is the freshness-anchored "what the rules currently are."
>
> **ADVISORY ONLY — not medical, legal, or billing/coding advice.** **Every figure below carries a source placeholder + retrieval date and is `[verify-at-use]`. Advisory numbers are marked `[ESTIMATE]`.** CPT codes, the therapy threshold, the 8-minute-rule variant, and payor edits change at least annually — confirm against the current CMS / AMA CPT / specific-payor source before quoting to a client or billing a claim. No patient PII anywhere.
>
> _Last reviewed: 2026-06-22 by `claude`. Treat every unmarked specific as `[verify-at-use]`._

---

## 1. Timed vs untimed CPT codes (the foundational split)

Bill timed and untimed codes by different rules. **CPT codes and descriptors are owned by the AMA and change — confirm the current code set.** `[verify-at-use — Source: AMA CPT, retrieved ____]`

| Category | Bills as | Examples (illustrative — verify code + status) |
|---|---|---|
| **Untimed / service-based** | 1 unit per session, regardless of minutes | Evaluation / re-evaluation codes; some supervised modalities `[verify-at-use]` |
| **Timed / time-based** | 15-minute units under the 8-minute rule | Therapeutic exercise, manual therapy, neuromuscular re-education, gait training, therapeutic activities `[verify-at-use]` |

The eval-vs-treatment and timed-vs-untimed status of any given code is `[verify-at-use]` against the current CPT and payor policy.

## 2. The 8-minute rule — cumulative-minute brackets

The standard CMS cumulative pattern (confirm the current table + the payor's variant):

| Total timed minutes | Units `[verify-at-use]` |
|---|---|
| 8–22 | 1 |
| 23–37 | 2 |
| 38–52 | 3 |
| 53–67 | 4 |
| 68–82 | 5 |
| each additional +15 | +1 |

- A single timed service needs **≥ 8 minutes** for its first unit.
- **CMS (Medicare) uses the cumulative total;** some commercial payors use a per-service "rule of eights." **Which one applies is `[verify-at-use]`.** `[Source: CMS / payor policy, retrieved ____]`

## 3. Medicare therapy threshold + KX modifier (concept)

- Medicare formerly had a hard "therapy cap"; current policy uses a **threshold** above which the **KX modifier** attests that continued skilled therapy is medically necessary **and documented**, with a higher amount triggering targeted medical review. The **mechanism** is durable; the **dollar figures** move annually.
- Therapy-threshold amount (combined PT/SLP, and separate OT): **`[ESTIMATE]` — `[verify-at-use — Source: CMS MPFS / threshold update, retrieved ____]`**. Do not quote a specific dollar figure without this check.
- Targeted-medical-review threshold: **`[ESTIMATE]` — `[verify-at-use]`**.
- **The KX modifier is an attestation, not a billing trick** — the underlying documentation is the substance. See [`../agents/clinical-documentation-compliance.md`](../agents/clinical-documentation-compliance.md).

## 4. Common modifiers (PT/rehab)

| Modifier | Meaning (verify current payor edits) |
|---|---|
| **GP** | Service delivered under a **PT** plan of care (OT → GO, SLP → GN) `[verify-at-use]` |
| **KX** | Attests documented medical necessity above the therapy threshold `[verify-at-use]` |
| **59 / X{EPSU}** | A genuinely distinct procedural service against an NCCI edit `[verify-at-use]` |
| **CO / CQ** | Services furnished in whole/part by a PTA/OTA (payment differential) `[verify-at-use]` |

NCCI edit pairs and payment differentials change — `[verify-at-use — Source: CMS NCCI / payor policy, retrieved ____]`.

## 5. Common payor-rule patterns (verify each, every clinic)

- **8-minute-rule variant** differs by payor (CMS cumulative vs per-service). `[verify-at-use]`
- **Authorization / visit caps** vary by payor and plan. `[verify-at-use]`
- **Plan-of-care certification windows and signature requirements** vary by payor and by CMS rules. `[verify-at-use]`
- **Cancellation / missed-visit fee rules** vary by payor (and some prohibit billing the patient). `[verify-at-use]`
- **Denial reason codes and appeal windows** vary by payor. `[verify-at-use]`

## 6. Advisory operational benchmarks (clinic-specific — use your own baseline)

These are **`[ESTIMATE]`** ranges for orientation only; a clinic's real numbers come from its own data, not this table.

| Metric | Orientation `[ESTIMATE]` | Note |
|---|---|---|
| No-show / late-cancel rate | varies widely by clinic/market | Measure your own baseline; `[verify-at-use]` |
| Units or visits per clinician hour | clinic- and discipline-specific | Define the window + baseline before reading it |
| Net rate per visit by payor | from the clinic's contracts | Pull from the EOB/contract, not a benchmark |

---

## Re-verification checklist (before quoting any figure)

1. CPT code + timed/untimed status → AMA CPT, current year.
2. 8-minute-rule variant → the specific payor's policy.
3. Therapy threshold + targeted-review dollar figures → current CMS MPFS update.
4. Modifier edits + PTA/OTA differential → CMS NCCI / payor policy.
5. Certification windows + signature rules → payor / CMS.

Record the **source + retrieval date** on every figure you put in a client-facing deliverable, or mark it `[unverified — training knowledge]`.
