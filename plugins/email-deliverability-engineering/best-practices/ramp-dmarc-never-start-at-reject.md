# Ramp DMARC; never start at p=reject

**Rule.** Move `p=none` → `p=quarantine` (optionally with `pct` ramp) → `p=reject`,
and advance only once RUA aggregate reports confirm every legitimate sending
stream produces an *aligned* pass.

**Why.** Reaching `reject` before the reports confirm legitimate streams pass
blackholes real mail — third-party senders, forwarders, and mailing lists.

**Smell.** A brand-new DMARC record published directly at `p=reject`, or a ramp
driven by the calendar instead of the RUA data.

**Cite:** RFC 7489.
