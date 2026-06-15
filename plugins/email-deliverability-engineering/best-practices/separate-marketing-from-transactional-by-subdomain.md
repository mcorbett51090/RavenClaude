# Separate marketing from transactional by subdomain

**Rule.** Send marketing and transactional mail from distinct subdomains (e.g.
`mail.` vs `t.`) so reputation is isolated per stream.

**Why.** A marketing send that tanks reputation must not take password-reset and
receipt email down with it.

**Smell.** Newsletters and password resets sharing one domain/IP reputation.

**Cite:** plugin §4.4; domain-reputation mechanics in
`knowledge/sender-requirements-and-reputation.md`.
