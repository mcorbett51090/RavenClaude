# Troubleshoot bottom-up, isolate before you fix

**Rule:** Walk the OSI stack bottom-up (L1 → L2 → L3 → L4 → L7), run the specific isolating command at each layer, and confirm a hypothesis with output before changing anything.

**Why:** most "routing problems" are a dead link, duplex mismatch, wrong VLAN, or stale ARP. Changing config "to see if it helps" mutates the system you're trying to reason about. Establish the working boundary, then bisect toward the break — the fault is usually where the symptom isn't.

**Anti-pattern:** jumping to L3/L7 ("must be DNS") and editing config before checking the link, the VLAN, and the route with a command.
