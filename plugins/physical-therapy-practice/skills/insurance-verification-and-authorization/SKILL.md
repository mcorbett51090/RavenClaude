---
name: insurance-verification-and-authorization
description: "Prevent denials at the front end — verify eligibility and benefits before the first visit, obtain and track authorizations and visit limits, manage the therapy threshold/KX trigger, and set point-of-service expectations so auth and coverage denials never originate at intake."
---

# Insurance Verification & Authorization

**Purpose:** stop authorization and coverage denials before they start — the cheapest place to prevent
a denial is at intake, not at appeal.

> **Compliance note:** payer authorization rules, visit limits, and the therapy threshold/KX modifier
> change and vary by payer. Treat specifics as `[verify against current payer policy and a certified
> coder]`.

---

## Steps

### 1. Verify eligibility and benefits before the first visit

Confirm active coverage, the PT benefit, visit limits, copay/coinsurance, and any referral
requirement **before** the patient arrives. A patient treated under lapsed or misunderstood coverage
is an avoidable write-off.

### 2. Obtain and track authorization

Where the payer requires prior authorization, obtain it and record the authorized visit count and
date range. Track visits used against the authorization so care never silently exceeds it — an
exceeded auth is a denial the clinic earned by not counting.

### 3. Manage the therapy threshold / KX trigger

Track cumulative therapy amounts so the threshold/KX attestation is applied on time and supported by
documentation. Coordinate the documentation with the compliance specialist
(see [`pt-billing-units-and-denials`](../pt-billing-units-and-denials/SKILL.md)).

### 4. Set point-of-service expectations

Communicate copay/coinsurance and any visit-limit reality to the patient up front. Surprise cost is a
top driver of mid-episode dropout — clarity at intake protects both collections and plan-of-care
adherence.

### 5. Hand a clean record to billing

The intake record (eligibility, auth number, visit limit, threshold status) is what lets billing
submit a clean claim. A denial traced to intake is fixed here, at the source.

---

## Output

An intake verification workflow, an authorization-tracking method, and the point-of-service script.
Feeds the [`denial-prevention-checklist`](../../templates/denial-prevention-checklist.md); deepen with
the [`referral-and-revenue-cycle-reference`](../../knowledge/referral-and-revenue-cycle-reference.md).
