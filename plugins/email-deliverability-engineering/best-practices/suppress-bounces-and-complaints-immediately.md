# Suppress hard bounces and complaints immediately and permanently

**Rule.** Hard bounces (5xx/invalid recipient) and FBL/ARF complaints go to a
permanent suppression list the moment they occur. Never retry a hard bounce;
never re-mail a complainer.

**Why.** Sending to known-bad addresses and re-mailing complainers is the fastest
way to lose reputation, and keeping complaints under the provider ceiling (~0.3%)
is a 2024 bulk-sender requirement.

**Smell.** A bounce log with repeated sends to the same 5xx address.

**Cite:** RFC 5965 (ARF); 2024 sender rules (dated) in
`knowledge/sender-requirements-and-reputation.md`.
