# Never use `any` at API or component prop boundaries

**Status:** Absolute rule
**Domain:** TypeScript
**Applies to:** `frontend-engineering`

---

## Why this exists

`any` at an API response boundary or a component's props interface is a hole in the type system that silently propagates. The TypeScript compiler stops checking through `any` — which means a typo in a field name, a changed API shape, or a missing null check will only appear at runtime, in production, where it matters most. Typed API boundaries are the cheapest tests you have: they catch shape mismatches before the code ships.

## How to apply

```typescript
// Bad
async function getUser(id: string): Promise<any> {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
}

// Good: parse and validate at the boundary with zod
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  createdAt: z.coerce.date(),
});
type User = z.infer<typeof UserSchema>;

async function getUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  return UserSchema.parse(await res.json());  // throws on invalid shape
}

// Component props: never use `any`
// Bad
function UserCard({ user }: { user: any }) { ... }
// Good
function UserCard({ user }: { user: User }) { ... }
```

**Do:**
- Use `zod`, `io-ts`, or `valibot` to validate API response shapes at the fetch boundary.
- Generate TypeScript types from the OpenAPI spec (openapi-typescript) so the contract is the source of truth.
- Enable `"strict": true` and `"noImplicitAny": true` in `tsconfig.json`.
- Use `unknown` (not `any`) when you genuinely don't know the shape yet — `unknown` forces you to narrow before using.

**Don't:**
- Cast response objects: `const data = res.json() as User` — this silences the compiler without validating.
- Use `any[]` for event handlers to avoid typing the event type.
- Propagate `any` from a third-party library type by re-exporting it through your own interfaces.

## Edge cases / when the rule does NOT apply

Runtime-polymorphic plugin systems where the shape is genuinely unknown until runtime may use `unknown` (not `any`) with a type guard. Vendored third-party code that ships untyped definitions may need a local `.d.ts` stub as a temporary measure — document with a TODO.

## See also

- [`../agents/react-implementation-engineer.md`](../agents/react-implementation-engineer.md) — owns typed component interfaces.
- [`./typescript-strict-at-the-boundaries.md`](./typescript-strict-at-the-boundaries.md) — the broader strict-TypeScript rule this doc extends at the API/props boundary specifically.

## Provenance

TypeScript documentation ("The `any` type") and the `strict` mode rationale. Codifies CLAUDE.md §2 rule 3 ("TypeScript strict, and type the boundaries") for the `frontend-engineering` plugin.

---

_Last reviewed: 2026-06-05 by `claude`_
