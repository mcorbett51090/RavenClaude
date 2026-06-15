# Audit DMARC alignment, not just SPF/DKIM pass/fail

**Rule.** DMARC passes only when SPF *or* DKIM passes **and** is *aligned* with
the visible `From:` domain. A "passing" SPF on an unrelated envelope/bounce domain
contributes nothing to DMARC. Always evaluate alignment.

**Why.** Most "we have SPF and DKIM but DMARC still fails" cases are alignment
failures, not missing records.

**Smell.** A report that says "SPF: pass, DKIM: pass" with no alignment column.

**Cite:** RFC 7489 (DMARC), RFC 7208 (SPF), RFC 6376 (DKIM).
