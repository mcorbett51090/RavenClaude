---
description: "Reshape a partner communication into a FERPA-safe, audience-appropriate message — classify the data bucket first, screen for the small-cohort residual, reshape per audience, and treat each language as a re-design with native-speaker review for legal-bearing comms."
argument-hint: "[the comm, e.g. 'turn this district update into a parent-facing message in English and Spanish']"
---

# Translate FERPA-safe comms

You are running `/edtech-partner-success:translate-ferpa-safe-comms`. Reshape the communication the user described (`$ARGUMENTS`) so it is privacy-safe and lands with its audience — the work the `ferpa-comms-translator` agent owns. The PSM's job is to *recognize the shape of the question* and route, not to render a legal opinion. Keep every example generic — no real student data.

## When to use this

You are turning a PSM-to-partner message into a parent / family / student / admin-facing comm, or producing a multilingual variant. NOT for internal analytics or QBR composition.

## Steps

1. **Classify the data into its FERPA bucket before anything else** (`ferpa-classify-the-data-bucket-before-you-share-or-de-identify.md`): sort into education records (protected), PII (protected), or directory information (disclosable *only* if the district formally designated that category and the parent hasn't opted out) — designations vary district to district, so don't assume.
2. **Screen for the small-cohort residual** (`screen-parent-comms-for-the-cohort-residual.md`): "the 3 students who chose option B" names nobody directly but identifies them in a small class; "students receiving the new intervention" structurally names everyone with that accommodation — FERPA prohibits identifiable-from-context disclosure, so de-identification is a claim you earn against the residual, not assert.
3. **Reshape per audience, don't re-send verbatim** (`ferpa-treat-each-language-variant-as-a-redesign-not-a-translation.md`): parents, school admins, district leadership, and students are four different rooms — name the audience precisely and redraft for the action you want, stripping PSM jargon.
4. **Treat each language as a re-design, not a re-render** (`ferpa-treat-each-language-variant-as-a-redesign-not-a-translation.md`): tune for cultural context that decides whether a family acts; meaningful access for limited-English-proficient families rides on Title VI (and several states name specific languages/thresholds) — get a native-speaker review for anything legal-bearing. `[verify-at-build — Title VI LEP obligations and FERPA de-identification specifics are regulatory; confirm current guidance]`
5. **Name who reviewed it** (`screen-parent-comms-for-the-cohort-residual.md`): "FERPA-compliant" asserted without naming the reviewer is an anti-pattern — state the review path.
6. **Escalate any genuine privacy/PII verdict to `ravenclaude-core/security-reviewer`** — this plugin supplies the domain screen, not the legal sign-off.

## Guardrails

- Never put real student data, names, or identifiers in examples — use `<district>`, "a mid-sized district", generic placeholders.
- The most common FERPA bear trap is the residual, not direct PII — a comm that names a small cohort by context is an incident.
- A literal translation of a legal-bearing comm can land flat or miss an obligation — each language gets a re-design and, when legal-bearing, a native-speaker check.
