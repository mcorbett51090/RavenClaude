# Design EMC in, not test it in

**Rule.** Make the design-for-EMC choices — grounding, filtering, clock/edge-rate
management, shielding — at architecture and layout time, and identify the likely
regulatory regime early. Treat certification as an accredited test-lab verdict, not
something asserted.

**Why.** You can't fix a radiated-emissions failure with a firmware patch. EMC choices
are cheap in architecture and expensive after a failed scan. Pre-compliance engineering
de-risks the formal test; it doesn't replace the lab's pass/fail.

**Smell.** EMC treated as a post-layout test; a certification "pass" asserted by the
design team; grounding/filtering left entirely to a late spin.

**Cite:** plugin §4.6; the compliance/pre-compliance section in
`knowledge/eda-fab-and-compliance-2026.md`.
