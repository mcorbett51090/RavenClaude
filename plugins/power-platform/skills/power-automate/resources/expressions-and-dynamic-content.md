# Expressions and Dynamic Content

## Key Patterns

- **outputs('ActionName')** vs **body('ActionName')** vs **triggerOutputs()**
- Use **Compose** actions liberally to capture intermediate values for debugging and reuse.
- **coalesce()** for null-safe defaults.
- **if()**, **equals()**, **and()**, **or()** for conditions.
- Date/time: **formatDateTime()**, **addDays()**, **utcNow()**.
- String: **split()**, **join()**, **substring()**, **replace()**, **toLower()**.
- Arrays: **length()**, **first()**, **last()**, **take()**, **skip()**.

## Common Gotchas
- Dynamic content from previous actions may be null on certain paths — always guard with coalesce or if.
- For HTTP responses, prefer parsing with **Parse JSON** action early.
- Avoid deeply nested expressions; break them with Compose steps.

## Best Practice
Name your Compose actions descriptively (e.g., "Compose - Order Total") so the expression is self-documenting.