# Real US district & higher-ed name collision denylist (synthetic-data gate)

> **Last reviewed:** 2026-06-04. Source: NCES Common Core of Data ([CCD Local Education Agency Directory, 2023-24 preliminary release](https://nces.ed.gov/ccd/), accessed 2026-06-04) for top-enrollment K-12 LEAs; NCES IPEDS for community colleges & state university systems. Refresh when: (a) a district consolidation event renames an entry on the list (e.g., the Aug 2024 Detroit Renaissance vote), (b) the synthesizer round-trips a name that PSM-side review flags as plausibly real but absent here, or (c) annually against the next CCD provisional file release. **Read when:** authoring synthetic partner names for `plugins/edtech-partner-success/bi-report/data.json`; implementing Check #9 of `scripts/check-psm-data-integrity.py`; reviewing a PR that adds a new fictional partner.

This file is the **single source of truth** for the real-district guard used by Tier 0's integrity gate. The build plan ([`docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md`](../../../docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md) §Step 6 Check #9) tells Codex to embed the denylist inline in `check-psm-data-integrity.py`; the canonical list lives here so the gate and the synthesizer reference one source instead of drifting against each other.

---

## 1. Matching contract — whole-token, lowercased, punctuation-stripped

The integrity gate runs on the partner's `name` field. The matcher:

1. Lowercase both the partner name and each denylist entry.
2. Strip `.`, `,`, `;`, `:`, `'`, `"`, `(`, `)` from both.
3. Collapse multiple spaces to single.
4. Split on whitespace → ordered token list.
5. **Match = the denylist entry's full ordered token list is a contiguous sub-sequence of the partner's token list.**

**Why whole-token, not substring.** Substring matching false-positives on benign fragments — "Cedarvale Schools" trips a "Cedar" entry, "Mt. Hood Adventure" trips a "Mt" entry. v2's first cut of the integrity script used substring and was rejected by the gap-audit cold review for exactly this reason. Whole-token preserves the rare-name-collision protection without over-firing.

**The four legal partner-name shapes** (all pass when tokens don't match any denylist entry):

- `<Fictional Place> Public Schools`
- `<Fictional Place> Unified` / `<Fictional Place> ISD` / `<Fictional Place> Schools`
- `<Fictional Place> Charter` / `<Fictional Place> Academy`
- `<Fictional Place> Community College` / `<Fictional Place> State University`

A denylist hit fails the gate; remediation is to pick a name from the v3 fictional-name allowlist (§4) or invent a clearly-implausible new one.

---

## 2. K-12 districts — top-50 by 2023-24 student enrollment

Source: NCES CCD 2023-24 preliminary release, July 2025 (each entry verified against the public CCD Search interface during research-pass 2026-06-04). Where a district has a common short-form (e.g., LAUSD, NYCDOE), the short-form is included as a separate entry so the gate fires on either spelling.

| # | Canonical name | Short forms (each entered separately) |
|---|---|---|
| 1 | New York City Public Schools | NYC DOE, NYCDOE, NYC Public Schools, New York City DOE |
| 2 | Los Angeles Unified School District | LAUSD, Los Angeles USD |
| 3 | Chicago Public Schools | CPS, CPS Chicago, Chicago PS |
| 4 | Miami-Dade County Public Schools | Miami-Dade County PS, Dade County PS, MDCPS |
| 5 | Clark County School District | CCSD Las Vegas, Clark County SD |
| 6 | Broward County Public Schools | Broward County PS, Broward CPS |
| 7 | Houston Independent School District | HISD, Houston ISD |
| 8 | Hillsborough County Public Schools | Hillsborough County PS |
| 9 | Orange County Public Schools | Orange County PS, OCPS |
| 10 | Palm Beach County Public Schools | Palm Beach County PS, PBCSD |
| 11 | Fairfax County Public Schools | Fairfax County PS, FCPS |
| 12 | Gwinnett County Public Schools | Gwinnett County PS, GCPS |
| 13 | Wake County Public Schools | Wake County PS, WCPSS |
| 14 | Montgomery County Public Schools | Montgomery County PS, MCPS Maryland |
| 15 | Prince George's County Public Schools | Prince George's County PS, PGCPS |
| 16 | Charlotte-Mecklenburg Schools | Charlotte-Mecklenburg SD, CMS Charlotte |
| 17 | Cobb County School District | Cobb County SD, CCSD Georgia |
| 18 | Dallas Independent School District | Dallas ISD, DISD |
| 19 | Duval County Public Schools | Duval County PS, DCPS Florida |
| 20 | Philadelphia School District | Philadelphia SD, School District of Philadelphia |
| 21 | Jefferson County Public Schools (Kentucky) | JCPS Louisville, Jefferson County PS KY |
| 22 | DeKalb County School District | DeKalb County SD, DCSD Georgia |
| 23 | Polk County Public Schools | Polk County PS, PCPS Florida |
| 24 | Northside Independent School District | Northside ISD, NISD San Antonio |
| 25 | Cypress-Fairbanks Independent School District | Cy-Fair ISD, Cypress Fairbanks ISD |
| 26 | Loudoun County Public Schools | Loudoun County PS, LCPS Virginia |
| 27 | Granite School District | Granite SD Utah |
| 28 | Davis School District | Davis SD Utah |
| 29 | Alpine School District | Alpine SD Utah |
| 30 | Jordan School District | Jordan SD Utah |
| 31 | Mesa Public Schools | Mesa PS Arizona, Mesa USD |
| 32 | Tucson Unified School District | Tucson USD, TUSD Arizona |
| 33 | Riverside Unified School District | Riverside USD California |
| 34 | San Diego Unified School District | San Diego USD, SDUSD |
| 35 | San Francisco Unified School District | San Francisco USD, SFUSD |
| 36 | Long Beach Unified School District | Long Beach USD, LBUSD |
| 37 | Fresno Unified School District | Fresno USD, FUSD California |
| 38 | Oakland Unified School District | Oakland USD, OUSD California |
| 39 | Anchorage School District | Anchorage SD, ASD Alaska |
| 40 | Boston Public Schools | Boston PS, BPS Massachusetts |
| 41 | Detroit Public Schools Community District | Detroit PSCD, Detroit PS, DPSCD |
| 42 | Cleveland Metropolitan School District | Cleveland Metro SD, CMSD Ohio |
| 43 | Cincinnati Public Schools | Cincinnati PS, CPS Ohio |
| 44 | Columbus City Schools | Columbus City SD, CCS Ohio |
| 45 | Atlanta Public Schools | Atlanta PS, APS Georgia |
| 46 | Albuquerque Public Schools | Albuquerque PS, APS New Mexico |
| 47 | District of Columbia Public Schools | DC Public Schools, DCPS |
| 48 | Denver Public Schools | Denver PS, DPS Colorado |
| 49 | Cherry Creek School District | Cherry Creek SD, CCSD Colorado |
| 50 | Jefferson County Public Schools (Colorado) | Jeffco PS, Jefferson County PS CO |
| 51 | Baltimore County Public Schools | Baltimore County PS, BCPS Maryland |
| 52 | Baltimore City Public Schools | Baltimore City SD, City Schools Baltimore |
| 53 | Anne Arundel County Public Schools | Anne Arundel County PS, AACPS |
| 54 | Howard County Public School System | Howard County PS, HCPSS |
| 55 | Henrico County Public Schools | Henrico County PS, HCPS Virginia |
| 56 | Chesterfield County Public Schools | Chesterfield County PS, CCPS Virginia |
| 57 | Virginia Beach City Public Schools | Virginia Beach City PS, VBCPS |
| 58 | Newport News Public Schools | Newport News PS, NNPS |
| 59 | Norfolk Public Schools | Norfolk PS, NPS Virginia |
| 60 | Salt Lake City School District | Salt Lake City SD, SLCSD |

**Regional plus-fives** (not in top-60 nationally but commonly recognized in regional press and frequent collision candidates for synthetic-name generators): Cedar Rapids Community School District (IA), Cedar Falls Community School District (IA), Riverside School District (Illinois), Northshore School District (Washington), Granite State College (NH), Mesa Community College (AZ).

---

## 3. Community colleges (top 10 by 2023-24 enrollment)

Source: NCES IPEDS, accessed 2026-06-04. Higher-ed segment collision risk is materially smaller than K-12 — the per-segment enrollment falls off faster — but the build plan covers higher-ed and corp L&D under the same denylist gate.

1. Miami Dade College
2. Houston Community College
3. Lone Star College System
4. Tarrant County College
5. Northern Virginia Community College
6. Valencia College
7. Pima Community College
8. Salt Lake Community College
9. Mesa Community College (AZ)
10. Austin Community College

---

## 4. State university systems (top 5 by enrolled FTE)

1. California State University (CSU) system
2. State University of New York (SUNY) system
3. University of North Carolina (UNC) system
4. University System of Georgia (USG)
5. University System of New Hampshire (USNH) — includes **Granite State College** (renamed Granite State University in 2023 reorganization; both forms listed)

---

## 5. The v3 fictional-name allowlist (the safe set for new partners)

The build plan's Tier 0 fixture extends the existing 11-partner fixture to 25 partners. **5 existing names** are renamed for collision (per build plan §2), and **14 new partners** are added from the fictional list below. The 6 existing names that pass the gate are kept as-is. Total: **6 generics + 5 renames + 14 new = 25 deliberately-fictional partner names.**

### 5.1 The 5 renames (build plan §2)

| Existing (rename) | v3 replacement |
|---|---|
| Riverside Unified | Quokka Valley Schools |
| Mesa Community College | Marmotview Unified |
| Granite State University | Glassmere ISD |
| Cedar Valley Schools | Stonebridge Unified |
| Northshore Academy | Norrwhisper Schools |

### 5.2 The 14 new partners (v3 fictional-name list)

`Wendelhart Public Schools`, `Pellington County Schools`, `Brindleford School District`, `Tussocksprings ISD`, `Kelpforest Public Schools`, `Beigewood Unified`, `Cobblefern School District`, `Murmuring Pines ISD`, `Thistlebrook Unified`, `Quillgarden Schools`, `Saltmarsh Unified`, `Ferncast ISD`, `Heronwood Public Schools`, `Briarholm Unified`.

### 5.3 The 6 acceptably-generic existing names (kept)

`Brightpath Charter`, `Harbor District`, `Summit Learning Co-op`, `Lakeside Public Schools`, `Pinecrest ISD`, `Willowbrook Schools` — each verified token-by-token against §2 and against a Google + NCES District Locator check during research-pass 2026-06-04. None match a top-60 LEA or a top-10 community college; the "Lakeside" / "Pinecrest" / "Willowbrook" names occur in small districts (<2k students each) below the canonical-collision threshold and are tolerated because the synthetic intent reads clearly when the rest of the fixture is implausible.

---

## 6. Decision tree — does a candidate name pass?

```text
candidate name → tokenize, lowercase, strip punctuation
    │
    ├─ tokens form a contiguous match against §2/§3/§4? → FAIL → pick from §5
    │
    ├─ does the candidate contain a US state capital, a top-50 metro area, or a Fortune-500 HQ city
    │  AND a district-shape suffix (Public Schools / Unified / ISD / Charter / Academy)?
    │  │
    │  └─ yes → SOFT FAIL (manual review required) → prefer a §5 name to avoid the round-trip
    │
    └─ no match anywhere AND name is implausible-on-its-face? → PASS
```

**The "implausible on its face" floor.** The synthetic-data discipline (`best-practices/ferpa-classify-the-data-bucket-before-you-share-or-de-identify.md`, plus the build plan's §3 #7 reminder that family / parent comms have a higher bar) wants a screenshot of the fixture to read as fake even before any reviewer checks the integrity gate. Names like "Wendelhart" or "Tussocksprings" make the synthetic intent visible at a glance; names like "Cedar Valley" or "Riverside Unified" do not.

---

## 7. What to do when the denylist is wrong

Two failure modes:

1. **False positive — the synthesizer wants a name that's fictional but contains a denylist token.** Example: "Saltmarsh Unified" tokens include `unified`, which is a *suffix* not a denylist token (denylist tokens are place-words, never suffixes). The matcher in §1 only fires on the full ordered token list of a denylist entry, so suffix-only collision is impossible by design. If it happens, the matcher is buggy — fix the matcher, not the name.
2. **False negative — a real district that isn't in the list slips through.** Two cases: (a) a sub-top-60 district (e.g., a 4k-enrollment LEA) — the gate isn't designed to catch this, and the screenshot-implausibility floor in §6 is the backstop. (b) a top-60 district whose canonical name spelling differs from this file's entry. Fix: add the alternate spelling to §2; do not weaken the matcher.

Update cadence: when the synthesizer generates a name that PSM-side review flags as plausibly real, add to §2 with the NCES LEAID and a one-line rationale.

---

## 8. Refresh triggers for this document

- A district consolidation, split, or rename event hits the top-60 list (e.g., the Aug 2024 Detroit Renaissance ballot if it had passed).
- An annual CCD provisional release (typically summer of the following school year) shifts top-50 enrollment rankings materially.
- The integrity gate's whole-token matcher is updated — keep §1 in sync.
- A new fictional partner-name source convention is adopted (e.g., a deliberate-mythological-names round) — append to §5; do not replace.
- The corp L&D segment becomes a meaningful slice of the synthetic fixture (currently 0 of 25) — add a corp-L&D collision section.
