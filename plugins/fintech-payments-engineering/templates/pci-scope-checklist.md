# PCI scope checklist (engineering posture)

- [ ] Raw PAN never touches our servers (PSP client-side tokenization)
- [ ] We store only tokens + last-4 (+ payout bank details, secured)
- [ ] Target SAQ-A (confirm with regulatory-compliance/legal)
- [ ] No PAN/CVV in logs, errors, analytics, or backups
- [ ] Money operations audit-logged (who/what/which payment)
- [ ] Security verdict routed to security-reviewer; attestation/regulation routed out
