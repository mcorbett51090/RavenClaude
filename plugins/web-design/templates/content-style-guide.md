# Content style guide — [Brand / site]

> Voice, tone, terminology, microcopy patterns. The single source of truth for what the site sounds like.

**Brand / site:** [...]
**Last updated:** [YYYY-MM-DD]
**Owner:** [...]

---

## Voice

[Voice = consistent identity. Define in 3-5 adjectives, each with a "we are" and "we are not" pair.]

| We are | We are not |
|---|---|
| [Adjective] | [opposite or near-opposite] |
| [Adjective] | [...] |
| [Adjective] | [...] |

### Example voice in action

**Topic:** [an explanation, an apology, a celebration]

✅ **On-voice:**
> [Example paragraph]

🔴 **Off-voice:**
> [Counter-example showing what we'd avoid]

## Tone

[Tone = situation-dependent. Voice stays constant; tone shifts.]

| Situation | Tone band | Notes |
|---|---|---|
| Marketing pages | Confident + friendly | Lead with outcome. |
| Success messages | Brief + warm | One sentence. No "Yay!" |
| Error messages | Helpful + specific | Name the fix, not the problem. |
| Legal copy | Plain + clear | Direct. No "hereby" / "aforementioned". |
| Support content | Patient + step-by-step | Numbered steps. |
| Empty states | Encouraging + actionable | "Here's how to start" + 1 CTA |

## Terminology

| Preferred | Avoid | Reason |
|---|---|---|
| Sign in | Log in / Login | Consistency across product |
| Customer | User / Account holder | Audience-appropriate |
| Email | E-mail | Modern usage |
| Account | Profile | Specific to our product |
| ... | ... | ... |

## Mechanics

- **Capitalization:** Sentence case for headings and body. Title Case only for proper nouns.
- **Oxford comma:** Yes / No (pick one and hold)
- **Numbers:** Numerals for 10+ (`12 customers`); words for under 10 (`three customers`)
- **Dates:** `MMMM D, YYYY` for US ("May 21, 2026"); `D MMMM YYYY` for UK ("21 May 2026")
- **Times:** 12-hour with `am`/`pm` lowercase (US); 24-hour for EU
- **Currency:** Symbol-first with no space (`$1,000`)
- **Quotation marks:** Smart quotes (" " ' ') in prose; straight quotes (" ' ) in code
- **Em vs en dash:** Em dash for breaks, en dash for ranges, hyphen for compound words
- **Abbreviations:** Spell out first use; abbreviate subsequently. `FAQ`, `URL`, `API` are fine without first-use expansion.

## Microcopy patterns

### CTAs (action verbs)

✅ "Create account" / "Start free trial" / "Get the report"
🔴 "Submit" / "Click here" / "Learn more" (without context)

### Error messages

Pattern: **[What went wrong, plainly] + [What to do].**

✅ "Email must include @. Try `name@example.com`."
✅ "Password needs 8+ characters."
🔴 "Invalid input."
🔴 "Error code 0x4F2B."

### Empty states

Pattern: **[What this is] + [How to start] + [single CTA].**

✅ "No projects yet. Create one to start tracking work. [+ New project]"
🔴 "No items."

### Success messages

Pattern: **[What happened] + [next step if any].**

✅ "Saved. Continue editing or close to return to dashboard."
🔴 "Success!"

### Loading states

Pattern: **[Verb] + [object] when meaningful; skeleton screen otherwise.**

✅ "Loading dashboard..." (only if it takes > 1s)
✅ Skeleton screen (preferred for known layouts)
🔴 Generic spinner with no context (only OK for < 500ms)

## Inclusive language

- Use "they / them" as the default singular pronoun
- Avoid gendered defaults ("guys," "manpower," "chairman")
- Don't use sensory language as wayfinding ("see the diagram below" — write "review the diagram in section 3")
- Avoid idioms that don't translate (especially if multi-locale): "ballpark figure," "low-hanging fruit"
- Use people-first language when relevant ("person with disabilities," not "the disabled")

## Locale-specific notes (multilingual sites)

[For each non-default locale, note differences in date format, currency, mechanics, terminology equivalents.]

## Don'ts (site-wide)

- No exclamation points in body copy
- No "we" without context (who is "we"?)
- No buzzwords ("synergy," "ecosystem," "revolutionary")
- No emoji in copy (unless explicit brand guideline says otherwise)
- No internal jargon in external-facing copy

---

**Change log**

| Version | Date | Author | Change |
|---|---|---|---|
| v1.0 | YYYY-MM-DD | [name] | Initial guide |
