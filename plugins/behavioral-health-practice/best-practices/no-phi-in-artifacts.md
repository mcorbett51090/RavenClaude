# No PHI in artifacts

Templates, examples, generated documents, prompts, and committed files use placeholders — `[Client]`, `[DOB]`, `[MRN]`, `[Member ID]`, `[Dx]` — never real names, dates of birth, member IDs, diagnoses, or record content. Protected health information lives in the EHR and the billing system, not in a plugin artifact. A real SSN, DOB, or member ID in a template is a breach risk and is flagged on sight. If an example needs to feel concrete, make the placeholder realistic in *shape* (format) without being real data.
