---
name: email-auth-audit
description: "Audit a domain's email-authentication posture end to end — SPF, DKIM, DMARC (with alignment), MTA-STS, TLS-RPT, and BIMI — and produce a prioritized fix list. Reach for this when setting up auth for a new sending domain, diagnosing DMARC failures, or verifying readiness before ramping to p=reject. Covers the common silent failure modes: alignment, the SPF 10-DNS-lookup limit, +all, and multiple SPF records."
---

# Skill: Email-Auth Audit

An email-authentication setup that "has all the records" can still fail DMARC
silently. This skill audits the posture for *correctness and alignment*, not mere
presence, and returns a prioritized fix list. Used by both agents.

## Step 0 — One opinion up front: audit alignment, not just pass/fail

DMARC passes only when SPF **or** DKIM passes **and** is *aligned* with the
`From:` header domain. So the first question for every record is not "does it
exist?" but "does it produce an *aligned* pass?" Most "we have SPF and DKIM but
DMARC still fails" tickets are alignment failures.

## Step 1 — SPF (RFC 7208)

Check, in order:

1. **Exactly one** SPF TXT record on the domain. Two = `permerror`.
2. **DNS-lookup count ≤ 10.** Count every `include:`, `a`, `mx`, `ptr`,
   `exists`, `redirect` mechanism (recursively). Over 10 → `permerror` → DMARC
   fail. This is the single most common silent break.
3. **The `all` qualifier.** Want `-all` (fail) or at least `~all` (softfail).
   Flag `+all` (passes everyone) and `?all` (neutral — does nothing) immediately.
4. **SPF alignment.** Does the `Return-Path`/envelope-from domain align with the
   `From:` domain? (Strict vs relaxed per the DMARC `aspf` tag.)

## Step 2 — DKIM (RFC 6376)

1. **A published selector** with a public key at `<selector>._domainkey.<domain>`.
2. **Key strength** — 2048-bit is the norm; flag 1024-bit.
3. **Signing domain alignment** — the `d=` in the signature aligns with `From:`
   (relaxed vs strict per `adkim`). DKIM alignment is what survives forwarding.
4. **Rotation** — is there a rotation plan? Static keys are a standing risk.

## Step 3 — DMARC (RFC 7489)

1. **The record exists** at `_dmarc.<domain>` and parses.
2. **Policy (`p=`)** — `none` (monitor), `quarantine`, or `reject`. Note the
   current stage; the 2024 bulk-sender rules require at minimum `p=none`.
3. **Reporting (`rua=`)** — aggregate reports must go somewhere or you're blind.
4. **`pct`, `sp`, `adkim`, `aspf`** — partial enforcement %, subdomain policy,
   alignment modes.
5. **Readiness check** — before recommending a ramp, confirm via RUA that *every*
   legitimate sending stream produces an aligned pass.

## Step 4 — Transport + brand (where they earn it)

- **MTA-STS (RFC 8461)** — the policy file at
  `https://mta-sts.<domain>/.well-known/mta-sts.txt` + the `_mta-sts` TXT record.
- **TLS-RPT (RFC 8460)** — the `_smtp._tls` TXT record for TLS failure reporting.
- **BIMI** — the `default._bimi` record + the logo SVG; note that inbox display
  generally requires a VMC/CMC certificate.

## Step 5 — Output: a prioritized fix list

Rank fixes by impact on DMARC pass-rate:

1. **Blockers** — anything causing a `permerror` (multiple SPF, >10 lookups) or an
   alignment failure on a major stream.
2. **Enforcement gaps** — missing DMARC, `p=none` with no plan, no RUA.
3. **Hardening** — `~all`→`-all`, 1024→2048-bit DKIM, key rotation, MTA-STS/TLS-RPT.
4. **Brand** — BIMI (only after DMARC is at enforcement).

Every finding cites its RFC and states the corrected record. Hand the record
*application* to `devops-cicd`/the cloud plugins; this skill specifies, it doesn't
provision.

See [`../../knowledge/email-authentication-standards.md`](../../knowledge/email-authentication-standards.md)
for the mechanics behind each check.
