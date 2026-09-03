# Cross-boundary denial test procedure (documented, not yet executed in CI)

Identical procedure to [`../../cube-nextjs-dashboard-starter/test/cross-tenant-denial.md`](../../cube-nextjs-dashboard-starter/test/cross-tenant-denial.md)
— the enforcement layer (Cube's `access_policy`) and the honest "this is a procedure, not a
passing CI check" status are the same regardless of which starter mints the JWT. The only
difference is step 2: mint the JWT via `POST /api/cube-token` on this Astro app instead of the
Next.js one. See that file for the full steps and the reasoning against shipping a
false-green automated test today.
