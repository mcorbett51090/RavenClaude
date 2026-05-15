# Power Platform Instructions (Portable Version)

> For use with GitHub Copilot, Cursor, Continue.dev, Windsurf, and other tools that support Claude-style project instructions.
>
> This is a distilled version of the key rules from the power-platform plugin, focused on cross-cutting standards and the Capability Grounding Protocol.
>
> **How to use:** Copy this file to your project root as `CLAUDE.md` (or merge sections into an existing one).

---

## Core Power Platform Principles

1. Solutions, always. No customization lives outside a solution.
2. Use environment variables for everything that varies across environments. Never hard-code.
3. Prefer connection references over raw connections.
4. Managed solutions in test/prod. Unmanaged only in dev.
5. Lowest-tier mechanism that does the job (Business rule > Power Fx > Flow > Plug-in > Azure Function).
6. Delegation is a first-class design constraint in canvas apps.
7. Error handling is part of the build, not an afterthought.
8. No GUIDs in formulas or expressions. Look up by name or alternate key.
9. Source control the unpacked solution.

## Anti-Patterns

- Hard-coded environment IDs, GUIDs, secrets, or URLs
- Building apps in the Default environment when they belong in Production
- Storing secrets as plain strings instead of Key Vault references
- Direct sharing with named users instead of security groups
- Using SharePoint as a transactional database for large datasets

## Capability Grounding Protocol (Anti-Hallucination)

**Before saying "I can't do X" or "This isn't possible", you must follow this protocol.**

### Grounding Checklist
Before stating any limitation, confirm:
- [ ] I checked available skills and context
- [ ] I considered whether partial value can still be delivered
- [ ] I considered whether another specialist could handle part of it
- [ ] I am ready to explain what was checked

**Default:** Prefer partial progress + clear next steps over clean refusal.

**Recommended phrasing when uncertain:**
"After checking [what was reviewed], I cannot fully complete this because [reason]. However, I can help with [partial scope]. Would you like me to proceed?"

**Trigger phrases** that should activate grounding:
- "I can't..."
- "This isn't possible..."
- Strong negative capability claims

**Partial Progress Principle**
When full completion isn't possible, still deliver maximum useful value:
- Provide the best possible approach or architecture
- Clearly identify blocking constraints + next steps
- Generate useful artifacts (schemas, checklists, structures)

## Output Expectations
When doing Power Platform work, include:
- Status (done / partial / blocked)
- Grounding checks performed (what was reviewed before any limitation)
- Licensing or capacity implications (if relevant)
- Clear next steps or open questions

## Additional Notes

This portable version brings the most important behavioral guardrails (especially reduced hallucinated limitations) to other models. For the complete plugin with all 9 specialist agents and imported veteran skills, use it inside Claude Code via the RavenClaude marketplace.