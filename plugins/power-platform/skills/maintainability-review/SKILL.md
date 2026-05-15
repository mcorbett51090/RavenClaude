# Maintainability & Evolution Review Skill

**Purpose:** Help teams build Power Platform solutions that remain healthy, understandable, and evolvable over time — not just ones that "work today."

## When to Use

- Before major releases or handoffs
- During architecture or code reviews
- When inheriting or taking over an existing solution
- When the Team Lead wants a forward-looking assessment

## Core Principles

1. **Future maintainers are real people** (often with less context than the original builders).
2. **Technical debt compounds** faster in low-code platforms than most teams expect.
3. **Evolution is inevitable** — design for change, not just delivery.
4. **Citizen developer + Pro developer handoff** is a common failure point.

## Review Dimensions

When performing a maintainability review, evaluate across these areas:

### 1. Understandability
- Naming clarity (tables, columns, flows, variables)
- Complexity of formulas and flows
- Documentation quality (especially decision rationale)
- How easy it is for a new person to understand *why* something was built this way

### 2. Modifiability
- Coupling between components
- Use of environment variables and connection references
- Layering and solution structure
- How hard it is to change one part without breaking others

### 3. Testability & Observability
- Presence of error handling and logging
- Ease of testing changes safely
- Visibility into runtime behavior

### 4. Upgrade & Evolution Readiness
- Use of deprecated patterns
- Awareness of upcoming platform changes
- How well the solution can absorb new features (Copilot, AI Builder, new Dataverse capabilities, etc.)
- Migration or extension paths

### 5. Ownership & Handoff
- Clarity of ownership boundaries
- Quality of runbooks / support documentation
- Separation between citizen-dev and pro-dev concerns

## Recommended Output

Status: Strong | Moderate concerns | Significant debt

Key strengths:
- ...

Areas of concern:
- ...

Recommended actions (prioritized):
1. ...
2. ...

Estimated effort to improve maintainability: Low / Medium / High

## Relationship to Other Skills

This skill complements `code-review` and `plan-with-team`. Use it when the focus shifts from "Does it work?" to "Will it still work well in 6–18 months?"