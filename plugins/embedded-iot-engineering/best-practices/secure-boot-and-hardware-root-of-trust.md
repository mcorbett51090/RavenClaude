# Secure boot needs a hardware root of trust

A connected device must verify its boot chain — each stage authenticates the next before handing off — and the root of trust must live in hardware (a secure element, TrustZone, or fuses), never in mutable flash. Keys are stored in secure storage, never in plaintext flash where they can be read or replaced. Secure boot anchored only in mutable flash is theater: the verification can be bypassed. Design the trust anchor explicitly and route the cryptographic specifics (algorithms, key sizes, rotation) to security review.
